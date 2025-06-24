"""
Gradio UI components for the app, defining the
interface with file uploads, dynamic text groups, and file previews.
"""

from secrets import token_hex
import gradio as gr


from src.config import SYS_SAMPLE_CSV_PATH, GUI_CSS_FILE
from src.utils.log import logger
from src.gui.gui_builder.gui_bind_events import (
    bind_upload_logic,
    bind_has_headers_toggle,
    bind_toggle_collapse_events,
    bind_text_submission_events,
    bind_groups_add_remove_events,
    bind_preview_csv_toggle,
    bind_edit_system_prompt_events,
    bind_generate_preview_output_events,
    bind_txt_to_md_update_events,
)
from src.gui.gui_builder.gui_create_controls import (
    create_upload_download_controls,
    create_preview_csv_section,
    create_preview_doc_section,
    create_edit_system_prompt_section,
    render_all_text_groups,
)
from src.gui.gui_builder.gui_file_utils import load_css_file
from src.gui.i18n.gui_text_en import (
    GUI_BTN_ADD_GRP_LBL,
    GUI_BTN_DEL_GRP_LBL,
    GUI_BROWSER_TAB_TITLE,
    GUI_PAGE_TITLE,
    GUI_FOOTER,
)


# region setup groups


def setup_upload_group(
    session_id_state: gr.State,
    group_count: gr.State,
    group_header_titles: gr.State,
    collapsed_state: gr.State,
    input_values: gr.State,
    has_headers_state: gr.State,
    last_uploaded_files_state: gr.State,
) -> tuple[
    gr.Button, gr.Button, gr.DownloadButton, gr.DownloadButton, gr.DownloadButton
]:
    """Setup upload group UI and bind events."""

    with gr.Group(elem_id="upload-group"):
        controls = {
            **create_upload_download_controls(False),  # collapsed_state.value
            **create_preview_csv_section(),
            **create_edit_system_prompt_section(),
        }
        toggle_upload_btn_grp = [(controls["toggle_btn"], "text-group-upload")]

        bind_toggle_collapse_events(toggle_upload_btn_grp, collapsed_state)
        bind_upload_logic(
            controls,
            session_id_state,
            group_header_titles,
            input_values,
            group_count,
            has_headers_state,
            last_uploaded_files_state,
        )
        bind_edit_system_prompt_events(
            controls["edit_system_prompt_btn"],
            controls["edit_system_prompt_output"],
            controls["edit_system_prompt_visible"],
        )
        bind_preview_csv_toggle(
            controls["toggle_preview_btn"],
            controls["preview_output"],
            controls["preview_visible"],
        )
        bind_has_headers_toggle(controls["toggle_headers_btn"], has_headers_state)

        return (
            controls["submit_all_btn"],
            controls["show_generated_output_btn"],
            controls["download_html_dwnbtn"],
            controls["download_pdf_dwnbtn"],
            controls["download_docx_dwnbtn"],
        )


def setup_text_groups(
    session_id_state: gr.State,
    group_count: gr.State,
    collapsed_state: gr.State,
    group_header_titles: gr.State,
    input_values: gr.State,
    submit_all_btn: gr.Button,
    show_generated_output_btn: gr.Button,
    download_html_dwnbtn: gr.DownloadButton,
    download_pdf_dwnbtn: gr.DownloadButton,
    download_docx_dwnbtn: gr.DownloadButton,
    last_uploaded_files_state: gr.State,
):
    """Set up dynamic text groups UI and bind events."""

    with gr.Group(elem_id="preview-output-group"):
        combined_output_md_box, combined_output_txt_box, combined_output_row_visible = (
            create_preview_doc_section()
        )

    # FIXME bind only generate output event for doc
    # bind preview csv and doc in setup_text_groups()
    # bind_preview_doc_toggle(controls)

    @gr.render(inputs=[group_count, collapsed_state, group_header_titles, input_values])
    def render_text_groups(n_groups, collapsed, titles, input_vals):
        """
        Dynamically renders 'group_count' of text input/output groups
        based on the other given parameters.
        """

        # Render all text groups (headers, input fields, outputs)
        toggle_buttons, submit_buttons, header_states, text_inputs, text_outputs = (
            render_all_text_groups(n_groups, collapsed, titles, input_vals)
        )
        # Bind toggle collapse events (to show/hide groups)
        bind_toggle_collapse_events(toggle_buttons, collapsed_state)
        # Bind submit and download button events
        bind_generate_preview_output_events(
            session_id_state,
            header_states,
            text_inputs,
            text_outputs,
            show_generated_output_btn,
            download_html_dwnbtn,
            download_pdf_dwnbtn,
            download_docx_dwnbtn,
            combined_output_md_box,
            combined_output_txt_box,
            combined_output_row_visible,
            last_uploaded_files_state,
        )
        bind_txt_to_md_update_events(
            combined_output_md_box,
            combined_output_txt_box,
        )
        bind_text_submission_events(
            submit_buttons,
            text_inputs,
            text_outputs,
            submit_all_btn,
        )


def setup_groups_add_remove_group(group_count: gr.State):
    """Set up add and remove buttons for dynamic text groups."""

    with gr.Row():
        add_text_group_btn = gr.Button(GUI_BTN_ADD_GRP_LBL)
        remove_text_group_btn = gr.Button(GUI_BTN_DEL_GRP_LBL)

        bind_groups_add_remove_events(
            add_text_group_btn, remove_text_group_btn, group_count
        )


# endregion setup groups

# region build gui


def build_ui() -> gr.Blocks:
    """Build and return the Gradio Blocks UI for the app."""

    custom_css = load_css_file(GUI_CSS_FILE)
    if custom_css is None:
        logger.warning("No custom CSS given. Continuing without ...")
    else:
        logger.info(f"Using custom CSS given: {GUI_CSS_FILE} ...")

    with gr.Blocks(
        title=GUI_BROWSER_TAB_TITLE,
        analytics_enabled=None,
        css=custom_css,
        # theme=gr.themes.Monochrome(),  # type: ignore[reportPrivateImportUsage]
    ) as app:
        session_id_state: gr.State = gr.State(lambda: token_hex(16))
        group_count: gr.State = gr.State(1)
        collapsed_state: gr.State = gr.State({})
        group_header_titles: gr.State = gr.State([])
        input_value_state: gr.State = gr.State([])
        has_headers_state: gr.State = gr.State({})
        last_uploaded_files_state = gr.State(SYS_SAMPLE_CSV_PATH)

        # FIXME gradio or svelte overriding hml/md css
        # gr.HTML(value=GUI_PAGE_TITLE, elem_id="main-title")
        gr.Markdown(value=f"# {GUI_PAGE_TITLE}", elem_id="main-title")
        (
            submit_all_btn,
            show_generated_output_btn,
            download_html_dwnbtn,
            download_pdf_dwnbtn,
            download_docx_dwnbtn,
        ) = setup_upload_group(
            session_id_state,
            group_count,
            group_header_titles,
            collapsed_state,
            input_value_state,
            has_headers_state,
            last_uploaded_files_state,
        )
        setup_text_groups(
            session_id_state,
            group_count,
            collapsed_state,
            group_header_titles,
            input_value_state,
            submit_all_btn,
            show_generated_output_btn,
            download_html_dwnbtn,
            download_pdf_dwnbtn,
            download_docx_dwnbtn,
            last_uploaded_files_state,
        )
        setup_groups_add_remove_group(group_count)
        gr.HTML(GUI_FOOTER, elem_id="footer")

    return app


# endregion build gui
