"""
Functions for generating CSV file previews and extracting column data for Gradio UI components.
"""

from csv import Error, reader
from pathlib import Path
import gradio as gr

from src.config import (
    SYS_UPLOAD_PATH,
    GUI_UPLOAD_MAX_ROWS,
)
from src.utils.log import logger
from src.gui.gui_builder.gui_file_utils import (
    convert_file_path,
    is_valid_file,
    sanitize_csv_data,
    sanitize_filename,
)
from src.gui.i18n import gui_text_en as txt


def generate_output(
    headers: list[str],
    text_inputs: list[str],
    text_outputs: list[str],
    last_uploaded_files: list[str],
) -> str:
    """Process all text input/output values and produce a combined output."""

    # TODO handle multiple file
    file_name = Path(last_uploaded_files[0]).name

    combined = [f"# {file_name}\n\n"]
    for i, (head, inp, outp) in enumerate(
        zip(headers, text_inputs, text_outputs), start=1
    ):
        combined.append(f"## {i}. {head}\n\n{inp}: {outp}\n\n")
    combined.append(f"\n_{txt.GUI_TXT_DOC_DISCLAIMER}_")
    return "".join(combined)


def generate_file_preview(
    files: list[str] | None, session_id: str, has_headers: bool
) -> tuple[dict[str, str] | None, list[str] | None, list[str] | None]:
    """
    Generate a preview for the first valid CSV file, extracting headers, rows, and
    first/second column values. Returns a tuple of (headers, rows) for Dataframe
    display and (first_column, second_column) values for text groups, or None if no
    valid files are provided.
    Info: only_first_file_used = True
    """

    if files is None:
        return None, [txt.GUI_GRP_DYN_HEAD], None
    if isinstance(files, str):
        files = [files]

    only_first_file_used = True
    upload_dir = Path(SYS_UPLOAD_PATH, session_id)
    no_col_input_found = "no column input found"

    csv_rows = []
    first_column_values = []
    second_column_values = []
    csv_headers: list[str] = []

    for file in files:
        max_len = 0

        try:
            file_path = convert_file_path(file)
        except ValueError as e:
            logger.warning(e)
            continue
        except Exception as e:
            logger.exception(f"Unexpected error while processing file {file}: {e}")
            continue

        if not is_valid_file(file_path):
            continue

        file_name = Path(file_path).name

        try:
            sanitized_name = sanitize_filename(file_name)
            file_path = upload_dir / sanitized_name

            # TODO display file size
            # file_size = getsize(file_path) / 1024  # Size in KB
            # previews.append((str(file_path), f"{sanitized_name}: {file_size:.2f} KB"))

            with file_path.open("r", encoding="utf-8") as f:
                if file_name.endswith(".csv"):
                    csvreader = reader(f)

                    # TODO short version
                    # all_rows = list(csvreader)
                    # if has_headers:
                    #     csv_headers = sanitize_csv_data(all_rows[0])
                    #     csv_rows = [
                    #         sanitize_csv_data(row)
                    #         for row in all_rows[1 : (GUI_UPLOAD_MAX_ROWS - 1)]
                    #     ]
                    # else:
                    #     csv_rows = [
                    #         sanitize_csv_data(row) for row in all_rows[:GUI_UPLOAD_MAX_ROWS]
                    #     ]
                    # max_len = max(len(csv_headers), len(csv_rows))

                    for i, row in enumerate(csvreader):
                        if i >= GUI_UPLOAD_MAX_ROWS:
                            csv_rows.append(["..."])
                            break
                        if i == 0 and has_headers:
                            csv_headers = sanitize_csv_data(row)
                            max_len = len(csv_headers)
                            continue
                        if row and row[0]:
                            sanitized_row = sanitize_csv_data(row)
                            first_column_values.append(sanitized_row[0])
                            second_column_values.append(
                                sanitized_row[1]
                                if len(sanitized_row) > 1
                                else no_col_input_found
                            )
                            csv_rows.append(sanitized_row)
                        else:
                            csv_rows.append(sanitize_csv_data(row))
                        max_len = max(max_len, len(row))

            # Normalize header and rows to match max length
            if has_headers:
                if len(csv_headers) < max_len:
                    csv_headers += [""] * (max_len - len(csv_headers))
            else:
                csv_headers = [str(i + 1) for i in range(max_len)]
            normalized_csv_rows = [
                row + [""] * (max_len - len(row)) if len(row) < max_len else row
                for row in csv_rows
            ]
            csv_rows = normalized_csv_rows

        except UnicodeDecodeError as e:
            logger.error(f"Encoding error while reading file {file_path}: {e}")
            csv_rows = [["Preview unavailable (encoding issue)"]]
        except Error as e:
            logger.error(f"CSV parsing error in file {file_path}: {e}")
            csv_rows = [["Preview unavailable (CSV error)"]]
        except Exception as e:
            logger.exception(
                f"Unexpected error while generating preview for {file_path}: {e}"
            )
            csv_rows = [["Preview unavailable (unexpected error)"]]

        if only_first_file_used:
            break
        else:
            csv_rows = []
            first_column_values = []
            second_column_values = []

    if not csv_rows:
        csv_rows = [["Preview unavailable (no valid files)"]]

    return (
        gr.update(value=csv_rows, headers=csv_headers),
        first_column_values,
        second_column_values,
    )
