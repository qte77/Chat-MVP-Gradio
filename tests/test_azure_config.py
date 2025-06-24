"""
Unit tests for the AzureConfig class and related chat configuration utilities.
"""

from os import environ
from pytest import raises
from pydantic import ValidationError

from src.chat.azure_config import (
    AzureConfig,
    load_chat_config_to_env,
    set_chat_system_prompt,
    generate_full_chat_system_prompt,
)

TEST_DEPLOYMENT = "deployment-id"
TEST_KEY = "1234567890"
TEST_URL = "https://test.openai.azure.com/"


def test_valid_single_model_name():
    """Test that AzureConfig accepts a valid single model name."""
    config = AzureConfig(
        AZURE_ENDPOINT=TEST_URL,  # type:ignore[reportArgumentType]
        AZURE_KEY=TEST_KEY,
        AZURE_DEPLOYMENT=TEST_DEPLOYMENT,
        AZURE_MODEL_NAME="gpt-4.1",
    )
    assert config.AZURE_MODEL_NAME == "gpt-4.1"


def test_valid_model_name_list():
    """Test that AzureConfig accepts a valid list of model names."""
    config = AzureConfig(
        AZURE_ENDPOINT=TEST_URL,  # type:ignore[reportArgumentType]
        AZURE_KEY=TEST_KEY,
        AZURE_DEPLOYMENT=TEST_DEPLOYMENT,
        AZURE_MODEL_NAME=["gpt-4.5", "gpt-4.1-mini"],
    )
    assert config.AZURE_MODEL_NAME == ["gpt-4.5", "gpt-4.1-mini"]


def test_invalid_model_name_raises():
    """Test that AzureConfig raises ValidationError for an invalid model name."""
    with raises(ValidationError) as excinfo:
        AzureConfig(
            AZURE_ENDPOINT=TEST_URL,  # type:ignore[reportArgumentType]
            AZURE_KEY=TEST_KEY,
            AZURE_DEPLOYMENT=TEST_DEPLOYMENT,
            AZURE_MODEL_NAME="gpt-3.5",
        )
    assert "Invalid model" in str(excinfo.value)


def test_invalid_model_list_raises():
    """Test that AzureConfig raises ValidationError for a list containing an invalid model name."""
    with raises(ValidationError) as excinfo:
        AzureConfig(
            AZURE_ENDPOINT=TEST_URL,  # type:ignore[reportArgumentType]
            AZURE_KEY=TEST_KEY,
            AZURE_DEPLOYMENT=TEST_DEPLOYMENT,
            AZURE_MODEL_NAME=["gpt-4.1", "gpt-unknown"],
        )
    assert "Invalid model" in str(excinfo.value)


def test_api_version_validation():
    """Test that AzureConfig accepts a valid API version format."""
    config = AzureConfig(
        AZURE_ENDPOINT=TEST_URL,  # type:ignore[reportArgumentType]
        AZURE_KEY=TEST_KEY,
        AZURE_DEPLOYMENT=TEST_DEPLOYMENT,
        AZURE_API_VERSION="2024-12-01",
    )
    assert config.AZURE_API_VERSION == "2024-12-01"


def test_invalid_api_version_format():
    """Test that AzureConfig raises ValidationError for an invalid API version format."""
    with raises(ValidationError):
        AzureConfig(
            AZURE_ENDPOINT=TEST_URL,  # type:ignore[reportArgumentType]
            AZURE_KEY=TEST_KEY,
            AZURE_DEPLOYMENT=TEST_DEPLOYMENT,
            AZURE_API_VERSION="12-01-2024",
        )


def test_fix_escaped_colon():
    """Test that AzureConfig correctly fixes an escaped colon in the endpoint URL."""
    config = AzureConfig(
        AZURE_ENDPOINT="https\x3a//test.openai.azure.com/",  # type:ignore[reportArgumentType]
        AZURE_KEY=TEST_KEY,
        AZURE_DEPLOYMENT=TEST_DEPLOYMENT,
    )
    assert str(config.AZURE_ENDPOINT) == TEST_URL


def test_load_chat_config_to_env(monkeypatch):
    """Test that load_chat_config_to_env sets environment variables from AzureConfig."""
    config = AzureConfig(
        AZURE_ENDPOINT=TEST_URL,  # type:ignore[reportArgumentType]
        AZURE_KEY="testkey12345",
        AZURE_DEPLOYMENT=TEST_DEPLOYMENT,
    )
    monkeypatch.delenv("CHAT_SYSTEM_MESSAGE", raising=False)

    load_chat_config_to_env(config)
    assert environ["AZURE_ENDPOINT"] == TEST_URL
    assert environ["AZURE_KEY"] == "testkey12345"
    assert environ["AZURE_DEPLOYMENT"] == TEST_DEPLOYMENT
    assert "CHAT_SYSTEM_MESSAGE" in environ


def test_chat_system_prompt():
    """Test that set_chat_system_prompt and get_chat_system_prompt work as expected."""
    set_chat_system_prompt("Hello from system.")
    # FIXME incorporate pydantic model
    assert generate_full_chat_system_prompt() == "Hello from system."
