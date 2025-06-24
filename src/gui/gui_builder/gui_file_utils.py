"""
Utility functions for file handling, including file validation,
sanitization, upload, and CSV generation.
"""

from subprocess import run, PIPE, CalledProcessError
from csv import Error, writer, Sniffer
from html import escape
from os.path import getsize
from pathlib import Path
from pathvalidate import sanitize_filename
import gradio as gr


from src.config import (
    GUI_MAX_FILE_SIZE_UPLOAD,
    GUI_UPLOAD_FILE_EXT,
    SYS_UPLOAD_PATH,
    SYS_DOWNLOAD_PATH,
    SYS_DOWNLOAD_PREFIX,
    SYS_TEMPLATE_HTML,
    SYS_TEMPLATE_CSS,
    SYS_TEMPLATE_DOCX,
)
from src.gui.i18n.gui_text_en import HTML_DEFAULT_TITLE
from src.utils.log import logger


def load_css_file(file_path: str | Path) -> str:
    """Load CSS content from the given file path."""

    if not isinstance(file_path, (str, Path)):
        msg = f"Must be str or pathlib.Path object: '{file_path}'"
        logger.error(msg)
        raise TypeError(msg) from e
    if isinstance(file_path, str):
        file_path = Path(file_path).resolve()
    if not file_path.exists() or not file_path.is_file():
        msg = f"File not found: {file_path}"
        logger.warning(msg)
        raise FileNotFoundError(msg) from e

    try:
        return file_path.read_text(encoding="utf-8")
    except PermissionError:
        msg = f"Permission denied while accessing or writing to: {file_path}"
        logger.error(msg)
        raise PermissionError(msg) from e
    except Exception as e:
        msg = f"Error reading file {file_path}: {e}"
        logger.exception(msg)
        raise Exception(msg) from e


def convert_file_path(file: gr.File | str) -> Path:
    """Convert a file object or string to a Path object."""

    if isinstance(file, gr.File):
        return Path(file.name)  # type: ignore[reportAttributeAccessIssue]
    elif isinstance(file, str):
        return Path(file)
    else:
        error_msg = (
            f"Unexpected file type provided: {file}. Expected gr.utils.NamedString or str, "
            f"but got {type(file)}"
        )
        logger.error(error_msg)
        raise ValueError(error_msg)


def sanitize_csv_data(data: list[str]) -> list[str]:
    """Sanitize CSV data by escaping HTML special characters."""

    return [escape(item) for item in data]


def is_valid_file(file: Path) -> bool:
    """Check whether the file is valid based on size, type, and CSV structure."""

    file_name = file.name

    if getsize(file) > GUI_MAX_FILE_SIZE_UPLOAD:
        logger.warning(f"File {file_name} exceeds size limit")
        return False
    if not any(file_name.endswith(ext) for ext in GUI_UPLOAD_FILE_EXT):
        logger.warning(f"Invalid file type: {file_name}")
        return False
    if file_name.endswith(".csv"):
        try:
            with open(file, "r", encoding="utf-8") as f:
                sample = f.read(1024)
                Sniffer().has_header(sample)  # Validate CSV structure
        except (Error, UnicodeDecodeError):
            logger.error(f"Invalid CSV structure: {file_name}")
            return False

    return True


def get_path_session_id(
    session_id: str,
    base_path: Path | None = None,
) -> Path | str:
    """
    Get the upload path for a specific session ID.
    Returns SYS_UPLOAD_PATH if base_path is None.
    """

    if not session_id:
        msg = "session_id cannot be empty"
        logger.error(msg)
        return msg
    if not isinstance(session_id, str):
        try:
            session_id = str(session_id)
        except Exception as e:
            msg = f"session_id must be a string: {e}"
            logger.error(msg)
            return msg
    try:
        if base_path is None:
            base_path = Path(SYS_UPLOAD_PATH)
        base_path = base_path.resolve()
    except Exception as e:
        msg = f"Error setting 'base_path': {e}"
        logger.error(msg)
        return msg

    upload_path = Path(base_path, session_id).resolve()
    return upload_path


def create_path(path: str | Path):
    """Create the upload path if it does not exist."""

    if not isinstance(path, (str, Path)):
        raise TypeError("path must be str or pathlib.Path object")
    if isinstance(path, str):
        path = Path(path)
    if not path.exists():
        try:
            path.mkdir(parents=True, exist_ok=True)
        except PermissionError:
            logger.error(f"Permission denied while creating directory: {path}")
        except Exception as e:
            logger.exception(f"Unexpected error while creating directory {path}: {e}")


def upload_files(files: list[str] | str, session_id: str) -> list[str] | str | None:
    """Upload files to a session-specific folder, validate them first, then sanitize and save."""

    if files is None:
        return None
    if isinstance(files, str):
        files = [files]

    saved_paths = []
    upload_path = get_path_session_id(session_id)
    if isinstance(upload_path, str):
        logger.error(upload_path)
        return upload_path
    create_path(upload_path)

    for file in files:
        try:
            file_path = convert_file_path(file)
        except ValueError as e:
            logger.warning(e)
            continue
        except Exception as e:
            logger.exception(f"Unexpected error while processing file {file}: {e}")
            continue
        file_name = Path(file_path).name

        # validate and sanitize file name and path
        if not is_valid_file(file_path):
            logger.warning(f"Invalid file detected: {file_name}")
            continue
        try:
            sanitized_name = sanitize_filename(file_name)
        except ValueError as e:
            logger.warning(
                f"Security issue while sanitizing file name {file_name}: {e}"
            )
            continue

        dest_path = upload_path / sanitized_name

        # save file
        try:
            with file_path.open("rb") as src, dest_path.open("wb") as dst:
                buffer_size = 8192  # 8 KB buffer
                while chunk := src.read(buffer_size):
                    dst.write(chunk)
            saved_paths.append(str(dest_path))
            logger.info(f"Successfully saved file {file_name} to {session_id}")

        except FileNotFoundError:
            logger.error(f"File not found: {file_name}")
        except PermissionError:
            logger.error(
                f"Permission denied while accessing or writing to: {file_name}"
            )
        except Exception as e:
            logger.exception(f"Unexpected error while saving file {file_name}: {e}")

    return saved_paths


def generate_and_save_csv(
    session_id: str, data: list[list[str]], file_name: str = "output.csv"
) -> str:
    """Generates CSV content from the data."""

    download_dir = Path(SYS_DOWNLOAD_PATH, session_id)
    download_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"Generating CSV: {file_name}")

    # TODO try-catch
    # TODO use headers from input file as headers, if has_header ist toggled
    with open(file_name, mode="w", newline="", encoding="utf-8") as file:
        csvwriter = writer(file)
        csvwriter.writerow(["Header", "Input Value", "Output Value"])
        for row in data:
            csvwriter.writerow(row)

    return "output.csv"


def preview_csv_all_action(
    session_id: str,
    text_inputs: list[str],
    text_outputs: list[str],
    headers: list[str],
    has_headers_state: gr.State = gr.State(""),
):
    """
    Collects input values and output values, formats them into CSV,
    and triggers the download of the CSV file.
    """
    data = []
    logger.info(
        f"download_all_action inputs: header{headers}, inputs={list(text_inputs)}, "
        f"outputs={list(text_outputs)}, has_headers={has_headers_state}"
    )
    for text_input, output_text in zip(text_inputs, text_outputs):
        header = headers if has_headers_state else []
        data.append([header, text_input, output_text])

    # TODO try-catch
    return generate_and_save_csv(session_id, data)


def _extract_first_h1_from_markdown_raw(md_text: str) -> str:
    """
    Extracts the first top-level Markdown heading (# Heading)
    from a raw Markdown string or returns HTML_DEFAULT_TITLE.
    """

    for line in md_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
    return HTML_DEFAULT_TITLE


def _check_required_files_exist(file_path: str):
    """
    Checks if provided file exists. Raises FileNotFoundError if not found.
    """

    if not Path(file_path).exists():
        msg = f"Required file missing: {file_path}"
        logger.error(msg)
        raise FileNotFoundError(msg)


def _get_output_file_name(session_id_str: str, file_ext: str) -> str:
    """
    Generates a unique output file name based on session_id_str.
    """

    if len(session_id_str) > 6:
        session_id_str = session_id_str[:6]

    return f"{SYS_DOWNLOAD_PREFIX}{session_id_str}.{file_ext}"


def _save_html_from_md_pandoc(
    output_path_gen: Path, title: str, css_inlined_standalone: str, md_str: str
):
    """
    Generates and saves HTML generated from Markdown using Pandoc to the specified output path.
    """

    pandoc_args = [
        "pandoc",
        "-f",
        "markdown",
        "-t",
        "html5",
        "-o",
        str(output_path_gen),
        "--template",
        str(SYS_TEMPLATE_HTML),
        # "--css", str(SYS_TEMPLATE_CSS),
        "--metadata",
        f"title={title}",
        "--metadata",
        f"css_inlined_standalone={css_inlined_standalone}",
        "--standalone",
    ]
    try:
        run(
            pandoc_args,
            input=md_str.encode("utf-8"),  # strin if no file path given
            stdout=PIPE,
            stderr=PIPE,
            check=True,
        )
    except CalledProcessError as e:
        msg = (
            f"Pandoc failed with args {pandoc_args} and code {e.returncode}: {e.stderr}"
        )
        logger.error(msg)
        raise RuntimeError(msg) from e
    except Exception as e:
        msg = f"Error generating HTML from Markdown: {e}"
        logger.exception(msg)
        raise Exception(msg) from e


def generate_html_from_md(
    session_id: str, markdown: str | list[str], output_path: Path | None = None
) -> Path | str:
    """
    Generates a HTML file from a list of Markdown strings using Pandoc.
    """

    if not session_id or not markdown:
        msg = (
            "No 'session_id' provided"
            if not session_id
            else "No or empty 'md_list' provided"
        )
        logger.error(msg)
        raise ValueError(msg)

    if not output_path:
        output_path = Path(SYS_DOWNLOAD_PATH)

    # TODO re-raise
    _check_required_files_exist(SYS_TEMPLATE_HTML)
    _check_required_files_exist(SYS_TEMPLATE_CSS)

    session_id_str = str(session_id)
    output_file_name = _get_output_file_name(session_id_str, "html")
    output_path_gen = get_path_session_id(session_id_str, output_path)
    if isinstance(output_path_gen, str):
        msg = f"Invalid output path: {output_path_gen}"
        logger.error(msg)
        return msg
    create_path(output_path_gen)
    output_path_gen = output_path_gen / output_file_name

    # TODO try-catch Path read css and _save_html_from_md_pandoc()
    md_str = "".join(markdown) if isinstance(markdown, list) else markdown
    css_inlined_standalone = Path(SYS_TEMPLATE_CSS).read_text(encoding="utf-8")
    title = _extract_first_h1_from_markdown_raw(md_str)
    try:
        _save_html_from_md_pandoc(
            output_path_gen, title, css_inlined_standalone, md_str
        )
    except Exception as e:
        msg = f"Error generating HTML from Markdown: {e}"
        logger.exception(msg)
        return msg

    if not output_path_gen.exists():
        msg = f"Output file not created: {output_path_gen}"
        logger.error(msg)
        return msg

    return output_path_gen


def generate_pdf_from_html(
    session_id: str, markdown: str | list[str], output_path: Path | None = None
) -> Path | str:
    """Generates a PDF file from a Markdown string or list of strings."""

    html_path = generate_html_from_md(session_id, markdown, output_path)
    if isinstance(html_path, str):
        msg = f"Invalid output path: {html_path}"
        logger.error(msg)
        return msg
    pdf_path = html_path.with_suffix(".pdf")

    # TODO check for installed latex engine and switch to installed
    # TODO use reference latex instead of html css with pandoc, or wkhtmltopdf
    pandoc_args = [
        "pandoc",
        str(html_path),
        "-o",
        str(pdf_path),
        "--pdf-engine=pdflatex",
        "--metadata",
        f"title={HTML_DEFAULT_TITLE}",
    ]

    try:
        run(
            pandoc_args,
            stdout=PIPE,
            stderr=PIPE,
            check=True,
        )
    except CalledProcessError as e:
        msg = (
            f"Pandoc failed with args {pandoc_args} and code {e.returncode}: {e.stderr}"
        )
        logger.error(msg)
        raise RuntimeError(msg) from e
    except Exception as e:
        msg = f"Error generating HTML from Markdown: {e}"
        logger.exception(msg)
        raise Exception(msg) from e

    return pdf_path


def generate_docx_from_html(
    session_id: str, markdown: str | list[str], output_path: Path | None = None
) -> Path | str:
    """Generates a DOCX file from a Markdown string or list of strings."""

    html_path = generate_html_from_md(session_id, markdown, output_path)
    if isinstance(html_path, str):
        msg = f"Invalid output path: {html_path}"
        logger.error(msg)
        return msg
    docx_path = html_path.with_suffix(".docx")

    # TODO check for installed latex engine and switch to installed
    pandoc_args = [
        "pandoc",
        str(html_path),
        "-o",
        str(docx_path),
        "--pdf-engine=pdflatex",
        f"--reference-doc={SYS_TEMPLATE_DOCX}",
        "--metadata",
        f"title={HTML_DEFAULT_TITLE}",
    ]

    try:
        run(
            pandoc_args,
            stdout=PIPE,
            stderr=PIPE,
            check=True,
        )
    except CalledProcessError as e:
        msg = (
            f"Pandoc failed with args {pandoc_args} and code {e.returncode}: {e.stderr}"
        )
        logger.error(msg)
        raise RuntimeError(msg) from e
    except Exception as e:
        msg = f"Error generating DOCX from Markdown: {e}"
        logger.exception(msg)
        raise Exception(msg) from e

    return docx_path
