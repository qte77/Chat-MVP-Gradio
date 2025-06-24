"""
GUI string constants for the Gradio demo app, defining titles,
labels, and button text for the user interface.
"""

from src.__init__ import __version__
from src.config import GUI_CORP_NAME, PROJECT_NAME, PROJECT_SHORT_DESCRIPTION


GUI_BROWSER_TAB_TITLE = f"{GUI_CORP_NAME} {PROJECT_NAME}"
GUI_PAGE_TITLE = (
    f"{GUI_CORP_NAME} [{PROJECT_NAME}] {PROJECT_SHORT_DESCRIPTION} [v{__version__}]"
)
GUI_FOOTER = f"Created for {GUI_CORP_NAME}"
GUI_GRP_UPLOAD_HEAD = "Upload a file"
GUI_GRP_CHAT_HEAD = ""
GUI_GRP_DYN_HEAD = "Input your query"
GUI_GRP_UPLOAD_SEC_HEAD_INPUTS = "Inputs"
GUI_GRP_UPLOAD_SEC_HEAD_OUTPUTS = "Outputs"
GUI_BTN_ADD_GRP_LBL = "Add Text Group"
GUI_BTN_DEL_GRP_LBL = "Remove Text Group"
GUI_BTN_UPLOAD_LBL = "Upload CSV"
GUI_BTN_LOAD_SAMPLE_LBL = "Load Sample"
GUI_BTN_UPL_CSV_TOGGLE_HEAD_LBL = "Toggle headers"
GUI_BTN_UPL_PREV_CSV_ON_LBL = "Show Preview"
GUI_BTN_UPL_PREV_CSV_OFF_LBL = "Hide Preview"
GUI_BTN_OUTPUT_PREVIEW_ON_LBL = "Show Generated Output"
GUI_BTN_OUTPUT_PREVIEW_OFF_LBL = "Hide Generated Output"
GUI_BTN_DOWNLOAD_HTML = "Download HTML"
GUI_BTN_DOWNLOAD_PDF = "Download PDF"
GUI_BTN_DOWNLOAD_DOCX = "Download DOCX"
GUI_BTN_EDIT_SYS_PROMPT = "Edit System Prompt"
GUI_BTN_SUBMIT_LBL = "Submit"
GUI_BTN_SUBMIT_ALL_LBL = "Submit all"
GUI_BTN_TGL_COLLAPSE_LBL = "[-] Collapse"
GUI_BTN_TGL_EXPAND_LBL = "[+] Expand"
GUI_TXT_CSV_UPLOAD_PREVIEW = "File Preview"
GUI_TXT_UPLOAD_LBL = "Uploaded File Paths"
GUI_TXT_MARKDOWN_PREVIEW_LBL = "Markdown Preview"
GUI_TXT_MARKDOWN_EDITOR_LBL = "Markdown Editor"
GUI_TXT_MARKDOWN_EDITOR_PLACEHOLDER = "Enter your Markdown here..."
GUI_TXT_EDIT_SYS_PROMPT = "System Prompt"
GUI_TXT_UPLOAD_NOT_VALID_LBL = "No valid files uploaded."
GUI_TXT_BX_IN_LBL = "Query"
GUI_TXT_BX_OUT_LBL = "Response"
GUI_TXT_DOC_DISCLAIMER = f"{GUI_CORP_NAME} @2025 No Warranty."
GUI_TXT_CHAT_DRY_RUN_NO_LOAD_ENV_INFO = (
    "Chat dry run mode enabled. No environment variables loaded."
)
HTML_DEFAULT_TITLE = "Document"
