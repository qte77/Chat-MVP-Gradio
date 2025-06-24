"""
Entry point for the Gradio demo app, initializing and launching
the UI on Azure Web App. Imports UI components from gradio.py,
logging from log.py, and configuration from config.py.
"""

from gradio import Info

from src.__init__ import __version__
from src.chat.azure_config import load_chat_config_to_env
from src.config import (
    CHAT_DRY_RUN_NO_LOAD_ENV,
    GUI_INFO_DURATION,
    PROJECT_NAME,
    PROJECT_SHORT_DESCRIPTION,
    SERVER_PORT,
    SERVER_NAME,
)
from src.gui.gui import build_ui
from src.utils.log import logger


def main():
    """Main function to initialize and launch the Gradio app."""

    try:
        logger.opt(raw=True).info("\n# ▶️  ─────────────────────────────  \n")
        logger.info(
            f"Starting App [{PROJECT_NAME}] {PROJECT_SHORT_DESCRIPTION} [v{__version__}] ... "
        )
        if not CHAT_DRY_RUN_NO_LOAD_ENV:
            try:
                load_chat_config_to_env()
            except Exception as e:
                msg = f"Unexpected problem while loading AzureConfig: {e}"
                Info(
                    message=msg,
                    duration=GUI_INFO_DURATION,
                )
                logger.exception(msg)
        app = build_ui()
        logger.info(f"Launching Gradio on {SERVER_NAME}:{SERVER_PORT} ... ")
        app.launch(
            server_name=SERVER_NAME,
            server_port=SERVER_PORT,
            share=False,
            debug=False,
            pwa=True,
        )
    except KeyboardInterrupt:
        logger.warning("KeyboardInterrupt caught. Shutting down...")
    except Exception as e:
        logger.exception(f"Error launching Gradio app: {e}", exc_info=True)
    finally:
        logger.info("🛑 Exiting Gradio app 🛑")
        logger.opt(raw=True).info("# ⏹️  ─────────────────────────────\n")


if __name__ == "__main__":
    main()
