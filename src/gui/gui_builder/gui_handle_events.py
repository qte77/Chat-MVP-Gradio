"""
Event handlers and utility functions for Gradio GUI components, including file uploads,
preview toggling, dynamic group management, and Azure AI text submission.
"""

from pathlib import Path
import gradio as gr

from src.chat.azure_client import query_azure_ai
from src.chat.azure_config import set_chat_system_prompt
from src.config import (
    GUI_INFO_DURATION,
    GUI_MAX_DYN_GROUPS,
)
from src.gui.gui_builder.gui_actions import generate_output, generate_file_preview
from src.gui.gui_builder.gui_file_utils import (
    upload_files,
    generate_html_from_md,
    generate_pdf_from_html,
    generate_docx_from_html,
)
from src.gui.i18n import gui_text_en as txt
from src.utils.log import logger


# TODO handle multiple file_input
def handle_event_file_processing(
    file_input: str,
    session_id: str,
    has_headers: bool,
    last_uploaded_files: str,
) -> tuple[
    dict[str, str] | None, list[str] | None, list[str] | None, int, str, str | list[str]
]:
    """Processes file, generates preview, and sets group count."""
    default_return = (
        {"data": [], "headers": [], "__type__": "update"},  # gr.DataFrame.update
        [],  # group_header_titles
        [],  # input_values
        int(0),  # group_count
        str("Error: Invalid file, session ID or upload path"),  # output_box
        [],  # uploaded_files
    )
    if not file_input or not session_id:
        return default_return
    uploaded_files = upload_files(file_input, session_id)
    if not uploaded_files or isinstance(uploaded_files, str):
        return default_return
    preview_dataframe, group_header_titles, input_values = generate_file_preview(
        uploaded_files, session_id, has_headers
    )
    headers_count = 0 if group_header_titles is None else len(group_header_titles)
    group_count = min(headers_count, GUI_MAX_DYN_GROUPS)

    # TODO refactor to carry multiple files
    uploaded_files_output_box = Path(uploaded_files[0]).name
    last_uploaded_files = uploaded_files[0]  # full path, list for gr.State compat

    return (
        preview_dataframe,
        group_header_titles,
        input_values,
        group_count,
        uploaded_files_output_box,
        last_uploaded_files,
    )


def toggle_preview(is_visible: bool) -> tuple[dict[str, bool], dict[str, bool], bool]:
    """Toggle the visibility of the preview gallery."""
    is_visible = not is_visible
    value = (
        txt.GUI_BTN_UPL_PREV_CSV_OFF_LBL
        if is_visible
        else txt.GUI_BTN_UPL_PREV_CSV_ON_LBL
    )
    return (
        gr.update(visible=is_visible),
        gr.update(value=value),
        is_visible,
    )


def toggle_edit_system_prompt_output(
    edit_system_prompt_visible: bool,
) -> tuple[dict[str, bool], dict[str, str], bool]:
    """Toggle the visibility of the generated output section."""

    is_visible = not edit_system_prompt_visible
    value = txt.GUI_BTN_EDIT_SYS_PROMPT if is_visible else txt.GUI_BTN_EDIT_SYS_PROMPT
    return (
        gr.update(visible=is_visible),
        gr.update(value=value),
        is_visible,
    )


def update_system_prompt(new_system_prompt: str):
    """Udpates the system prompt in environemnt."""
    set_chat_system_prompt(new_system_prompt)


def toggle_generated_output(
    combined_output_box_visible: bool,
) -> tuple[dict[str, bool], dict[str, str], dict[str, str], bool]:
    """Toggle the visibility of the generated output section."""

    is_visible = not combined_output_box_visible
    value = (
        txt.GUI_BTN_OUTPUT_PREVIEW_OFF_LBL
        if is_visible
        else txt.GUI_BTN_OUTPUT_PREVIEW_ON_LBL
    )
    return (
        gr.update(visible=is_visible),  # MD
        gr.update(visible=is_visible),  # TXT
        gr.update(value=value),  # BTN LBL
        is_visible,  # row visible state
    )


def handle_generate_output(
    headers: list[str],
    text_inputs: list[str],
    text_outputs: list[str],
    last_uploaded_files: list[str],
) -> str:
    """
    Handles the click event for the generate output button by
    processing all text inputs and outputs.
    """

    try:
        return generate_output(headers, text_inputs, text_outputs, last_uploaded_files)
    except Exception as e:
        msg = f"Error while generating output: {e}"
        logger.exception(msg)
        return msg


def toggle_use_headers(has_headers: bool) -> bool:
    """Toggle use_headers state and update button label."""

    return not has_headers


def add_text_group(current_group_count: int) -> int:
    """Add a new text group, respecting GUI_MAX_DYN_GROUPS."""
    if current_group_count >= GUI_MAX_DYN_GROUPS:
        gr.Info(
            f"Maximum {GUI_MAX_DYN_GROUPS} groups reached!", duration=GUI_INFO_DURATION
        )
        return current_group_count
    gr.Info("Added a new text group!", duration=GUI_INFO_DURATION)
    return current_group_count + 1


def remove_text_group(current_group_count: int) -> int:
    """Remove the last text group, ensuring at least one remains."""
    gr.Info("Removed the last text group.", duration=GUI_INFO_DURATION)
    return max(1, current_group_count - 1)


def toggle_collapse(state: dict[str, bool], group_id: str) -> dict[str, bool]:
    """Toggle collapse state for a text group."""
    new_state = dict(state)
    new_state[group_id] = not new_state.get(group_id, False)

    return new_state


def set_toggle_btn_value(state: dict[str, bool], group_id: str) -> dict[str, str]:
    """Return updated button label based on the collapse state of the given group."""
    is_collapsed = state.get(group_id, False)
    new_label = (
        txt.GUI_BTN_TGL_COLLAPSE_LBL if not is_collapsed else txt.GUI_BTN_TGL_EXPAND_LBL
    )

    return gr.update(value=new_label)


def handle_text_submission(text: str) -> str | None:
    """Send text to Azure AI and return its response."""
    try:
        return query_azure_ai(text)
    except Exception as e:
        msg = f"Error while querying Azure AI: {e}"
        logger.exception(msg)
        return msg


def flatten_inputs_and_generate_output(
    *texts: str,
) -> tuple[str, str]:
    """
    Flattens the input texts and generates output based on
    the provided headers, input texts, and output texts.
    """

    len_headers = int(texts[0])
    len_inputs = int(texts[1])
    len_outputs = int(texts[2])
    offset_headers = 3
    offset_headers_len = len_headers + offset_headers
    offset_inputs_len = offset_headers_len + len_inputs
    offset_outputs_len = offset_inputs_len + len_outputs
    headers = list(texts[offset_headers:offset_headers_len])
    input_text = list(texts[offset_headers_len:offset_inputs_len])
    output_text = list(texts[offset_inputs_len:offset_outputs_len])
    last_uploaded_files = list(texts[offset_outputs_len:])

    # FIXME SoC into separate button, e.g. preview Doc
    generated_output = handle_generate_output(
        headers, input_text, output_text, last_uploaded_files
    )
    return generated_output, generated_output


def handle_generate_html_from_md(
    session_id: str, md_list: list[str], output_path: Path | None = None
) -> str:
    """
    Handles the generation of HTML from Markdown content.
    """

    # TODO refactor to use named params insetad of flattened inputs
    # TODO remove debug logger
    logger.debug(
        f"[{session_id[:6]}] Generating HTML from Markdown: "
        f"'{md_list[0:6]}' saved to '{output_path}'"
    )

    try:
        html_path = generate_html_from_md(session_id, md_list, output_path)
    except Exception as e:
        msg = f"Error while generating HTML from Mardown: {e}"
        logger.exception(msg)
        return msg

    if not Path(html_path).exists():
        msg = f"Generated HTML not found at {html_path}"
        logger.error(msg)
        return msg

    return str(html_path)


def handle_generate_pdf_from_html(
    session_id: str, md_list: list[str], output_path: Path | None = None
) -> str:
    """
    Handles the generation of HTML from Markdown content.
    """

    try:
        pdf_path = generate_pdf_from_html(session_id, md_list, output_path)
    except Exception as e:
        msg = f"Error while generating PDF from Mardown: {e}"
        logger.exception(msg)
        return msg

    if not Path(pdf_path).exists():
        msg = f"Generated PDF not found at {pdf_path}"
        logger.error(msg)
        return msg

    return str(pdf_path)


def handle_generate_docx_from_html(
    session_id: str, md_list: list[str], output_path: Path | None = None
) -> str:
    """
    Handles the generation of DOCX from Markdown content.
    """

    try:
        docx_path = generate_docx_from_html(session_id, md_list, output_path)
    except Exception as e:
        msg = f"Error while generating PDF from Mardown: {e}"
        logger.exception(msg)
        return msg

    if not Path(docx_path).exists():
        msg = f"Generated DOCX not found at {docx_path}"
        logger.error(msg)
        return msg

    return str(docx_path)
