"""
Event binding functions for Gradio GUI components, connecting UI controls to their logic handlers.
"""

import gradio as gr

from src.config import (
    SYS_SAMPLE_CSV_PATH,
)
from src.gui.gui_builder.gui_handle_events import (
    handle_event_file_processing,
    handle_text_submission,
    set_toggle_btn_value,
    toggle_collapse,
    toggle_preview,
    toggle_edit_system_prompt_output,
    toggle_generated_output,
    toggle_use_headers,
    update_system_prompt,
    add_text_group,
    remove_text_group,
    handle_generate_html_from_md,
    handle_generate_pdf_from_html,
    handle_generate_docx_from_html,
    flatten_inputs_and_generate_output,
)


def bind_upload_logic(
    controls: dict,
    session_id_state: gr.State,
    group_header_titles: gr.State,
    input_values: gr.State,
    group_count: gr.State,
    has_headers_state: gr.State,
    last_uploaded_files_state: gr.State,
):
    """Bind logic to upload, load sample and toogle headers buttons."""

    output_states = [
        controls["preview_output"],
        group_header_titles,
        input_values,
        group_count,
        controls["output_box"],
        last_uploaded_files_state,
    ]

    # Upload > Preview > Prefill
    controls["upload_button"].upload(
        fn=handle_event_file_processing,
        inputs=[
            controls["upload_button"],
            session_id_state,
            has_headers_state,
            last_uploaded_files_state,
        ],
        outputs=output_states,
    )

    # Sample > Preview > Prefill
    controls["load_sample_button"].click(
        fn=handle_event_file_processing,
        inputs=[
            gr.State(SYS_SAMPLE_CSV_PATH),
            session_id_state,
            has_headers_state,
            last_uploaded_files_state,
        ],
        outputs=output_states,
    )

    # Check Has Headers > Preview
    controls["toggle_headers_btn"].click(
        fn=handle_event_file_processing,
        inputs=[
            controls["upload_button"],  # last_uploaded_files_state,
            session_id_state,
            has_headers_state,
            last_uploaded_files_state,
        ],
        outputs=output_states,
    )


def bind_preview_csv_toggle(
    toggle_preview_btn: gr.Button,
    preview_output: gr.DataFrame,
    preview_visible: gr.State,
):
    """Bind the preview toggle button logic."""

    toggle_preview_btn.click(
        fn=toggle_preview,
        inputs=preview_visible,
        outputs=[
            preview_output,
            toggle_preview_btn,
            preview_visible,
        ],
    )


def bind_edit_system_prompt_toggle(
    edit_system_prompt_btn: gr.Button,
    edit_system_prompt_output: gr.Textbox,
    edit_system_prompt_visible: gr.State,
):
    """Bind the preview toggle button logic."""

    edit_system_prompt_btn.click(
        fn=toggle_edit_system_prompt_output,
        inputs=edit_system_prompt_visible,
        outputs=[
            edit_system_prompt_output,
            edit_system_prompt_btn,
            edit_system_prompt_visible,
        ],
    )


def bind_show_editor_toggle(
    show_generated_output_btn: gr.Button,
    header_states: list[gr.State],
    text_inputs: list[gr.Textbox],
    text_outputs: list[gr.Textbox],
    last_uploaded_files: gr.State,
    combined_output_md_box: gr.Markdown | gr.HTML,
    combined_output_txt_box: gr.Textbox,
    combined_output_row_visible: gr.State,
):
    """Bind the preview toggle button logic."""

    show_generated_output_btn.click(
        fn=flatten_inputs_and_generate_output,
        # gradio expects flattened inputs to fn
        inputs=[
            gr.State(len(header_states)),
            gr.State(len(text_inputs)),
            gr.State(len(text_outputs)),
            *header_states,
            *text_inputs,
            *text_outputs,
            last_uploaded_files,
        ],
        outputs=[combined_output_md_box, combined_output_txt_box],
    )

    show_generated_output_btn.click(
        fn=toggle_generated_output,
        inputs=[combined_output_row_visible],
        outputs=[
            combined_output_md_box,
            combined_output_txt_box,
            show_generated_output_btn,
            combined_output_row_visible,
        ],
    )


def bind_download_html(
    session_id: gr.State,
    download_html_dwnbtn: gr.DownloadButton,
    # header_states: list[gr.State],
    # text_inputs: list[gr.Textbox],
    # text_outputs: list[gr.Textbox],
    # last_uploaded_files: gr.State,
    combined_output_md_box: gr.Markdown | gr.HTML,
    # combined_output_txt_box: gr.Textbox,
):
    """Bind the donwload HTML button logic."""

    # TODO check if md box already filled, fill if not
    # download_html_dwnbtn.click(
    #     fn=flatten_inputs_and_generate_output,
    #     # gradio expects flattened inputs to fn
    #     inputs=[
    #         gr.State(len(header_states)),
    #         gr.State(len(text_inputs)),
    #         gr.State(len(text_outputs)),
    #         *header_states,
    #         *text_inputs,
    #         *text_outputs,
    #         last_uploaded_files,
    #     ],
    #     outputs=[combined_output_md_box, combined_output_txt_box],
    # )

    download_html_dwnbtn.click(
        fn=handle_generate_html_from_md,
        inputs=[session_id, combined_output_md_box],
        outputs=[download_html_dwnbtn],
    )


def bind_download_pdf(
    session_id: gr.State,
    download_pdf_dwnbtn: gr.DownloadButton,
    combined_output_md_box: gr.Markdown | gr.HTML,
):
    """Bind the donwload PDF button logic."""

    download_pdf_dwnbtn.click(
        fn=handle_generate_pdf_from_html,
        inputs=[session_id, combined_output_md_box],
        outputs=[download_pdf_dwnbtn],
    )


def bind_download_docx(
    session_id: gr.State,
    download_docx_dwnbtn: gr.DownloadButton,
    combined_output_md_box: gr.Markdown | gr.HTML,
):
    """Bind the donwload DOCX button logic."""

    download_docx_dwnbtn.click(
        fn=handle_generate_docx_from_html,
        inputs=[session_id, combined_output_md_box],
        outputs=[download_docx_dwnbtn],
    )


def bind_txt_to_md_update_events(
    combined_output_md_box: gr.Markdown | gr.HTML, combined_output_txt_box: gr.Textbox
):
    """Bind the text to markdown update events."""
    combined_output_txt_box.change(
        fn=lambda x: x, inputs=combined_output_txt_box, outputs=combined_output_md_box
    )


def bind_has_headers_toggle(toggle_headers_btn: gr.Button, has_headers_state: gr.State):
    """Bind the CSV has headers toggle button logic."""
    toggle_headers_btn.click(
        fn=toggle_use_headers,
        inputs=has_headers_state,
        outputs=has_headers_state,
    )


def bind_toggle_collapse_events(
    toggle_buttons: list[tuple[gr.Button, str]],
    collapsed_state: gr.State,
):
    """Bind toggle buttons to update collapsed state for each group."""

    for toggle_btn, group_id in toggle_buttons:

        def handle_click(state, group_id=group_id):
            new_state = toggle_collapse(state, group_id)
            label_update = set_toggle_btn_value(new_state, group_id)
            return label_update, new_state

        toggle_btn.click(
            fn=handle_click,
            inputs=[collapsed_state],
            outputs=[toggle_btn, collapsed_state],
        )


def bind_edit_system_prompt_events(
    edit_system_prompt_btn: gr.Button,
    edit_system_prompt_output: gr.Textbox,
    edit_system_prompt_visible: gr.State,
):
    """Bind the events for editing the system prompt."""

    bind_edit_system_prompt_content(
        edit_system_prompt_output,
    )
    bind_edit_system_prompt_toggle(
        edit_system_prompt_btn,
        edit_system_prompt_output,
        edit_system_prompt_visible,
    )


def bind_edit_system_prompt_content(
    edit_system_prompt_output: gr.Textbox,
):
    """Bind the events for editing the system prompt content."""

    edit_system_prompt_output.change(
        fn=update_system_prompt, inputs=edit_system_prompt_output
    )


def bind_generate_preview_output_events(
    session_id_state: gr.State,
    header_states: list[gr.State],
    text_inputs: list[gr.Textbox],
    text_outputs: list[gr.Textbox],
    show_generated_output_btn: gr.Button,
    download_html_dwnbtn: gr.DownloadButton,
    download_pdf_dwnbtn: gr.DownloadButton,
    download_docx_dwnbtn: gr.DownloadButton,
    combined_output_md_box: gr.Markdown | gr.HTML,
    combined_output_txt_box: gr.Textbox,
    combined_output_row_visible: gr.State,
    last_uploaded_files: gr.State,
    # has_headers_state: gr.State = gr.State(""),
):
    """Bind the events for generating and displaying the output from text inputs."""

    bind_show_editor_toggle(
        show_generated_output_btn,
        header_states,
        text_inputs,
        text_outputs,
        last_uploaded_files,
        combined_output_md_box,
        combined_output_txt_box,
        combined_output_row_visible,
    )
    bind_download_html(
        session_id_state,
        download_html_dwnbtn,
        combined_output_md_box,
    )
    bind_download_pdf(
        session_id_state,
        download_pdf_dwnbtn,
        combined_output_md_box,
    )
    bind_download_docx(
        session_id_state,
        download_docx_dwnbtn,
        combined_output_md_box,
    )


def bind_text_submission_events(
    # session_id: str,
    submit_buttons: list[gr.Button],
    text_inputs: list[gr.Textbox],
    text_outputs: list[gr.Textbox],
    submit_all_btn: gr.Button,
):
    """Bind each submit button and 'Submit All' if provided."""

    for submit_btn, text_input, text_output in zip(
        submit_buttons, text_inputs, text_outputs
    ):
        submit_btn.click(
            fn=handle_text_submission,
            inputs=text_input,
            outputs=text_output,
            concurrency_limit=5,
        )

    if submit_all_btn:
        bind_submit_all_button(submit_all_btn, text_inputs, text_outputs)


def bind_submit_all_button(
    submit_all_btn: gr.Button,
    text_inputs: list[gr.Textbox],
    text_outputs: list[gr.Textbox],
):
    """Bind the 'Submit All' button to submit all text inputs in batch."""

    def submit_all(*texts: str) -> list[str | None]:
        return [handle_text_submission(text) for text in texts]

    submit_all_btn.click(
        fn=submit_all,
        inputs=text_inputs,
        outputs=text_outputs,
        concurrency_limit=5,
    )


def bind_groups_add_remove_events(
    add_text_group_btn: gr.Button,
    remove_text_group_btn: gr.Button,
    group_count: gr.State,
):
    """Bind click events for adding and removing text groups to their respective buttons."""

    add_text_group_btn.click(  # pylint: disable=no-member
        add_text_group, group_count, group_count
    )
    remove_text_group_btn.click(  # pylint: disable=no-member
        remove_text_group, group_count, group_count
    )
