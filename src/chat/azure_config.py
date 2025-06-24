"""
Configuration for Azure OpenAI integration using pydantic-settings.
Loads environment variables from a .env file automatically.
"""

from json import dumps
from os import environ
from typing import ClassVar, List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import HttpUrl, Field, field_validator, ValidationError
from pydantic.types import StringConstraints
from typing_extensions import Annotated

from src.chat.data_models import AzureResponseFormat_EN

from src.config import (
    CHAT_DRY_RUN_NO_LOAD_ENV,
    CHAT_SYSTEM_MESSAGE,
)
from src.utils.log import logger
from src.gui.i18n.gui_text_en import GUI_TXT_CHAT_DRY_RUN_NO_LOAD_ENV_INFO


class AzureConfig(BaseSettings):
    """Azure OpenAI API settings loaded from env or .env file automatically."""

    AZURE_ENDPOINT: HttpUrl
    AZURE_KEY: str = Field(..., min_length=10)
    AZURE_API_VERSION: Annotated[
        str, StringConstraints(pattern=r"^\d{4}-\d{2}-\d{2}(-preview)?$", min_length=10)
    ] = "2024-12-01-preview"
    AZURE_MODEL_NAME: str | list[str] = Field(
        "gpt-4.1", description="Single model name or list of model names"
    )
    AZURE_DEPLOYMENT: str

    VALID_MODELS: ClassVar[list[str]] = [
        "gpt-4.5",
        "gpt-4.1",
        "gpt-4.1-nano",
        "gpt-4.1-mini",
    ]

    @classmethod
    def validate_single_model_name(cls, model_name: str) -> str:
        """
        Validates if the provided model name is in the list of valid Azure models.
        """
        if model_name not in AzureConfig.VALID_MODELS:
            msg = f"Invalid model '{model_name}', must be one of {cls.VALID_MODELS}."
            logger.error(f"Raising '{msg}'")
            raise ValueError(msg)
        return model_name

    @field_validator("AZURE_MODEL_NAME", mode="before")
    @classmethod
    def validate_model_names(cls, values: str | List[str]) -> str | List[str]:
        """Validate and normalize the AZURE_MODEL field before model initialization."""

        if isinstance(values, str):
            return cls.validate_single_model_name(values)

        elif isinstance(values, list):
            validated_model_names = []
            try:
                for model_name in values:
                    validated_model_names.append(cls.validate_single_model_name(model_name))
            except Exception as e:
                logger.exception(f"Error validating model name {model_name}: {e}")

            return validated_model_names

        else:
            msg = "AZURE_MODEL_NAME must be a string or list of strings."
            logger.error(f"Raising '{msg}'")
            raise TypeError(msg)

    @field_validator("AZURE_ENDPOINT", mode="before")
    @classmethod
    def fix_escaped_colon(cls, v: str) -> str:
        """
        Replace incorrectly escaped '\x3a' with ':' in the endpoint URL.
        """
        if isinstance(v, str) and r"\x3a" in v:
            v = v.replace(r"\x3a", ":")
        return v

    # fall back to .env, if no env present
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # ignore unknown env vars
    )


def _load_chat_config() -> AzureConfig | None:
    """Load and return the Azure chat configuration."""

    try:
        return AzureConfig()  # type: ignore[reportCallIssue]
    except ValidationError as e:
        msg = f"Error loading AzureConfig: {e}"
        logger.error(msg)
        return None
    except Exception as e:
        msg = f"Exception while loading AzureConfig: {e}"
        logger.exception(msg)
        return None


def load_chat_config_to_env(chat_config: AzureConfig | None = None):
    """
    Loads AzureConfig into environment. Does not override existing values.
    """

    environ["CHAT_SYSTEM_MESSAGE"] = CHAT_SYSTEM_MESSAGE

    chat_config = chat_config or _load_chat_config()
    if chat_config is None:
        msg = "AzureConfig could not be loaded because 'chat_config' is 'None'."
        logger.warning(msg)
        raise ValueError(msg)
    if not isinstance(chat_config, AzureConfig):
        msg = "'chat_config' is not an instance of 'AzureConfig'."
        logger.error(msg)
        raise TypeError(msg)

    for k, v in chat_config.model_dump().items():
        if k not in environ:
            environ[k] = str(v)


def generate_full_chat_system_prompt() -> str:
    """Returns CHAT_SYSTEM_MESSAGE from environment."""

    if CHAT_DRY_RUN_NO_LOAD_ENV:
        prompt = GUI_TXT_CHAT_DRY_RUN_NO_LOAD_ENV_INFO
    else:
        prompt = environ["CHAT_SYSTEM_MESSAGE"]

    response_announce = "\n\nStructured JSON response output schema:\n\n"
    json_schema_pretty = dumps(AzureResponseFormat_EN.model_json_schema(), indent=4)
    json_schema_pretty = json_schema_pretty.replace(r"\n", "\n")

    return f"{prompt}{response_announce}{json_schema_pretty}"


def set_chat_system_prompt(chat_system_message: str = ""):
    """Sets CHAT_SYSTEM_MESSAGE in environment."""
    environ["CHAT_SYSTEM_MESSAGE"] = chat_system_message
