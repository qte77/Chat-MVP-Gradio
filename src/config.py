"""
Configuration settings for the Gradio demo app on Azure Web App.
Defines system parameters (e.g., paths, port, logging), GUI settings
(e.g., file upload limits, dynamic group constraints), Chat and
feature toggles.
"""

from os import getenv

# MARK: Project
PROJECT_NAME = "Chat-MVP-Gradio"
PROJECT_SHORT_DESCRIPTION = "GPT-4.1 PWA"


# MARK: System
SYS_ROOT_PATH = getenv("SYS_ROOT_PATH", "/home/site/wwwroot")
SYS_LOG_PATH = getenv("SYS_LOG_PATH", f"{SYS_ROOT_PATH}/logs")
SYS_UPLOAD_PATH = f"{SYS_ROOT_PATH}/uploads"
SYS_DOWNLOAD_PATH = f"{SYS_ROOT_PATH}/downloads"
SYS_APP_RUNTIME_LOG_FILE = f"{SYS_LOG_PATH}/app_runtime.log"
SYS_ASSETS_PATH = f"{SYS_ROOT_PATH}/assets"
SYS_SAMPLE_CSV_PATH = f"{SYS_ASSETS_PATH}/datasets/chat_upload_sample.csv"
SYS_TEMPLATE_FOLDER = f"{SYS_ASSETS_PATH}/templates"
SYS_TEMPLATE_HTML = f"{SYS_TEMPLATE_FOLDER}/template.html.tpl"
SYS_TEMPLATE_CSS = f"{SYS_TEMPLATE_FOLDER}/template.html.css"
SYS_TEMPLATE_DOCX = f"{SYS_TEMPLATE_FOLDER}/template.docx"
SYS_DOWNLOAD_PREFIX = "Output_"
SYS_LOG_FORMAT_FOLDING = (
    " {time:YYYY-MM-DD HH:mm:ss} | {level.icon}  [{level}] | "
    "{name}:{function}:{line} | {message}"
)


# MARK: Server
SERVER_PORT = int(getenv("PORT", "8000"))
# FIXME Bandit - B104: hardcoded_bind_all_interfaces
# secure "192.168.0.1"
SERVER_NAME = "0.0.0.0"


# MARK: GUI
GUI_CORP_NAME = "MYCORP"
GUI_INFO_DURATION = 2
GUI_MAX_DYN_GROUPS = 10
GUI_MAX_FILE_SIZE_UPLOAD = 10 * 1024 * 1024  # 10MB
GUI_UPLOAD_FILE_EXT = [".csv", ".tsv", ".xlsx", ".txt"]
GUI_UPLOAD_FILE_TYPES = ["text"]
GUI_UPLOAD_MAX_ROWS = 500
GUI_CSS_FILE = f"{SYS_ROOT_PATH}/src/gui/gui.css"


# MARK: Chat
# CHAT_RESPONSE_TIMEOUT = 30
CHAT_DRY_RUN_NO_LOAD_ENV = False
CHAT_SYSTEM_MESSAGE = (
    "You are a helpful assistant. "
    "Please answer the user's questions as best as you can."
)
CHAT_MAX_COMPLETION_TOKENS = 800
CHAT_TEMPERATURE = 0.7
CHAT_TOP_P = 1.0
CHAT_FREQ_PENALTY = 0.0
CHAT_PRES_PENALTY = 0.0
CHAT_STREAM = True
CHAT_RESPONSE_FORMAT = "json_object"


# MARK: Feature Toggles
FT_GUI_ENABLE_UPLOAD_COLLAPSE = False
