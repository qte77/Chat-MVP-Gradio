"""
GUI controls for the Gradio-based interdface, including upload controls, preview sections,
and dynamic text groups. Provides functions to create and manage interactive UI components.
"""

import gradio as gr

from src.config import (
    GUI_UPLOAD_FILE_TYPES,
    FT_GUI_ENABLE_UPLOAD_COLLAPSE,
)
from src.chat.azure_config import generate_full_chat_system_prompt
from src.gui.i18n import gui_text_en as txt


def create_upload_download_controls(
    is_collapsed: bool,
) -> dict[str, gr.Textbox | gr.UploadButton | gr.Button | gr.DownloadButton]:
    """Create upload-related controls and return references."""

    with gr.Row(elem_classes="collapsible-header"):
        # TODO SoC/SRP formatting ### to css
        gr.Markdown(value=f"### {txt.GUI_GRP_UPLOAD_HEAD}")

        toggle_btn = gr.Button(
            value=txt.GUI_BTN_TGL_COLLAPSE_LBL,
            scale=0,
            elem_id="toggle-collapse-btn-upload",
            elem_classes="toggle-collapse-btn",
            visible=FT_GUI_ENABLE_UPLOAD_COLLAPSE,
        )

    with gr.Row(
        elem_classes="collapsible-content"
        if not is_collapsed
        else "collapsible-content collapsed"
    ):
        with gr.Column(scale=5):
            # uploaded file
            output_box = gr.Textbox(
                label=txt.GUI_TXT_UPLOAD_LBL,
                interactive=False,
                show_copy_button=True,
                lines=4,
            )
        with gr.Column(scale=1):
            with gr.Row(elem_classes="centered-row"):
                # Column 1: Upload and Submit
                with gr.Column(scale=1, elem_classes="centered-col bordered-col"):
                    # gr.Markdown(
                    #     value=txt.GUI_GRP_UPLOAD_SEC_HEAD_INPUTS,
                    #     elem_classes="section-header",
                    # )
                    upload_button = gr.UploadButton(
                        label=txt.GUI_BTN_UPLOAD_LBL,
                        file_types=GUI_UPLOAD_FILE_TYPES,
                        file_count="multiple",
                        elem_classes="upload-btn",
                        scale=0,
                    )
                    load_sample_button = gr.Button(
                        value=txt.GUI_BTN_LOAD_SAMPLE_LBL,
                        elem_classes="load-sample-btn",
                        scale=0,
                    )
                    toggle_preview_btn = gr.Button(
                        value=txt.GUI_BTN_UPL_PREV_CSV_ON_LBL,
                        elem_classes="toggle-btn",
                        scale=0,
                    )
                    toggle_headers_btn = gr.Button(
                        value=txt.GUI_BTN_UPL_CSV_TOGGLE_HEAD_LBL,
                        elem_classes="toggle-btn",
                        scale=0,
                    )
                    edit_system_prompt_btn = gr.Button(
                        value=txt.GUI_BTN_EDIT_SYS_PROMPT,
                        elem_classes="toggle-btn",
                        scale=0,
                    )
                    submit_all_btn = gr.Button(
                        value=txt.GUI_BTN_SUBMIT_ALL_LBL,
                        elem_classes="toggle-btn",
                        scale=0,
                    )

                # Column 2: Generate and Download
                with gr.Column(scale=1, elem_classes="centered-col"):
                    gr.Markdown(
                        value=txt.GUI_GRP_UPLOAD_SEC_HEAD_OUTPUTS,
                        elem_classes="section-header",
                    )
                    show_generated_output_btn = gr.Button(
                        value=txt.GUI_BTN_OUTPUT_PREVIEW_ON_LBL,
                        elem_classes="toggle-btn",
                        scale=0,
                    )
                    download_html_dwnbtn = gr.DownloadButton(
                        label=txt.GUI_BTN_DOWNLOAD_HTML,
                        elem_classes="toggle-btn",
                        scale=0,
                    )
                    download_pdf_dwnbtn = gr.DownloadButton(
                        label=txt.GUI_BTN_DOWNLOAD_PDF,
                        elem_classes="toggle-btn",
                        scale=0,
                    )
                    download_docx_dwnbtn = gr.DownloadButton(
                        label=txt.GUI_BTN_DOWNLOAD_DOCX,
                        elem_classes="toggle-btn",
                        scale=0,
                    )

    return {
        "toggle_btn": toggle_btn,
        "output_box": output_box,
        "upload_button": upload_button,
        "load_sample_button": load_sample_button,
        "toggle_preview_btn": toggle_preview_btn,
        "toggle_headers_btn": toggle_headers_btn,
        "edit_system_prompt_btn": edit_system_prompt_btn,
        "submit_all_btn": submit_all_btn,
        "show_generated_output_btn": show_generated_output_btn,
        "download_html_dwnbtn": download_html_dwnbtn,
        "download_pdf_dwnbtn": download_pdf_dwnbtn,
        "download_docx_dwnbtn": download_docx_dwnbtn,
    }


def create_preview_csv_section() -> dict[str, gr.DataFrame | gr.State]:
    """Create the preview CSV section and its toggle state."""
    with gr.Row():
        preview_visible = gr.State(False)
        preview_output = gr.DataFrame(
            label=txt.GUI_TXT_CSV_UPLOAD_PREVIEW,
            elem_classes="preview-frames",
            show_label=True,
            interactive=False,
            visible=False,
        )
    return {
        "preview_output": preview_output,
        "preview_visible": preview_visible,
    }


def create_edit_system_prompt_section() -> dict[str, gr.Textbox | gr.State]:
    """Create the preview CSV section and its toggle state."""
    with gr.Row():
        edit_system_prompt_visible = gr.State(False)
        edit_system_prompt_output = gr.Textbox(
            value=generate_full_chat_system_prompt(),
            label=txt.GUI_TXT_EDIT_SYS_PROMPT,
            interactive=True,
            show_copy_button=True,
            visible=False,
            lines=3,
        )
    return {
        "edit_system_prompt_visible": edit_system_prompt_visible,
        "edit_system_prompt_output": edit_system_prompt_output,
    }


def create_preview_doc_section() -> tuple[gr.Markdown | gr.HTML, gr.Textbox, gr.State]:
    """Create the preview Doc section and its toggle state."""

    with gr.Row():
        combined_output_row_visible = gr.State(False)
        combined_output_md_box = gr.Markdown(
            elem_classes="preview-frames",
            visible=False,
            show_copy_button=True,
        )
        combined_output_txt_box = gr.Textbox(
            label=txt.GUI_TXT_MARKDOWN_EDITOR_LBL,
            placeholder=txt.GUI_TXT_MARKDOWN_EDITOR_PLACEHOLDER,
            lines=15,
            interactive=True,
            visible=False,
            show_copy_button=True,
        )
    return combined_output_md_box, combined_output_txt_box, combined_output_row_visible


def create_single_text_group(
    i: int,
    group_id: str,
    is_collapsed: bool,
    title: str,
    input_val: str,
) -> tuple[tuple[gr.Button, str], gr.Button, gr.State, gr.Textbox, gr.Textbox]:
    """Create a single text group with toggle button, input/output textboxes, and submit button."""

    header_state = gr.State(title)
    input_state = gr.State(input_val)

    toggle_label = (
        txt.GUI_BTN_TGL_COLLAPSE_LBL if not is_collapsed else txt.GUI_BTN_TGL_EXPAND_LBL
    )

    with gr.Group(elem_id=group_id, elem_classes="text-group"):
        with gr.Row(elem_classes="collapsible-header"):
            gr.Markdown(
                # TODO SoC/SRP formatting ### to css
                value=f"### {txt.GUI_GRP_CHAT_HEAD} {i}: {header_state.value}",
                elem_id=f"header-{i}",
            )
            toggle_btn = gr.Button(
                value=toggle_label,
                scale=0,
                elem_id=f"toggle-collapse-btn-{i}",
                elem_classes="toggle-collapse-btn",
            )
        with gr.Column(
            elem_classes="collapsible-content"
            if not is_collapsed
            else "collapsible-content collapsed"
        ):
            with gr.Row():
                text_output: gr.Textbox = gr.Textbox(
                    label=txt.GUI_TXT_BX_OUT_LBL,
                    interactive=False,
                    show_copy_button=True,
                    lines=3,
                )
            with gr.Row():
                text_input = gr.Textbox(
                    label=txt.GUI_TXT_BX_IN_LBL,
                    scale=6,
                    value=input_state.value,
                    show_copy_button=True,
                )
                with gr.Column(scale=1, elem_classes="centered-col"):
                    submit_button = gr.Button(
                        txt.GUI_BTN_SUBMIT_LBL, elem_classes="submit-btn"
                    )

    return (toggle_btn, group_id), submit_button, header_state, text_input, text_output


def render_all_text_groups(
    n_groups: int,
    collapsed: dict[str, bool],
    titles: list[str],
    input_vals: list[str],
) -> tuple[
    list[tuple[gr.Button, str]],
    list[gr.Button],
    list[gr.State],
    list[gr.Textbox],
    list[gr.Textbox],
]:
    """Render dynamic text groups and return event-targetable components."""

    def get_value_or_default(lst: list[str], idx: int, default: str) -> str:
        return lst[idx] if idx < len(lst) else default

    groups = [
        create_single_text_group(
            i=i,
            group_id=f"text-group-{i}",
            is_collapsed=collapsed.get(f"text-group-{i}", False),
            title=get_value_or_default(titles, i - 1, txt.GUI_GRP_DYN_HEAD),
            input_val=get_value_or_default(input_vals, i - 1, ""),
        )
        for i in range(1, n_groups + 1)
    ]

    toggle_buttons, submit_buttons, header_state, text_inputs, text_outputs = zip(
        *groups
    )

    return (
        list(toggle_buttons),
        list(submit_buttons),
        list(header_state),
        list(text_inputs),
        list(text_outputs),
    )
