"""Azure OpenAI API client for sending prompts and receiving responses."""

from httpx import RequestError, HTTPStatusError
from openai import AzureOpenAI, OpenAIError
from pydantic import BaseModel, ValidationError

from src.chat.azure_config import AzureConfig, generate_full_chat_system_prompt
from src.chat.data_models import AzureResponseFormat_EN

from src.config import (
    CHAT_TEMPERATURE,
    CHAT_MAX_COMPLETION_TOKENS,
    CHAT_RESPONSE_FORMAT,
)
from src.utils.log import logger


def validate_json_response(
    response: str | None, schema: type[BaseModel] = AzureResponseFormat_EN
) -> tuple[bool, str]:
    """
    Validates a JSON response string against a specified Pydantic model schema.

    Args:
        response (str | None): The JSON response string to validate. If None or an
            invalid type is provided, the validation will fail.
        schema (type[BaseModel]): The Pydantic model class to validate the response
            against. Defaults to `AzureResponseFormat_EN`.

    Returns:
        tuple: A tuple containing:
            - A boolean value indicating whether the validation was successful (`True`)
                or failed (`False`).
            - A message providing additional details about the validation result,
                including any errors encountered.

    Raises:
        ValidationError: If the JSON response does not conform to the schema.
        Exception: For unexpected errors during validation.
    """

    if not isinstance(response, str):
        msg = f"Response is of type: {type(response)}. Nothing to validate."
        logger.info(msg)
        return False, msg

    try:
        schema.model_validate_json(response)
        msg = f"'response' adheres to schema type '{type(schema)}'."
        return True, msg
    except ValidationError as e:
        msg = f"Error validating model response: {e}"
        logger.error(msg)
        return False, msg
    except Exception as e:
        msg = f"Error validating model response: {e}"
        logger.exception(msg)
        return False, msg


def parse_json_response(
    response: str | None, schema: type[BaseModel] = AzureResponseFormat_EN
) -> str:
    """
    Parses and converts a validated JSON response into a human-readable string format.

    Args:
        response (str | None): The JSON response string to be parsed. If `None` or an
            invalid type is provided, the parsing will fail.
        schema (type[BaseModel]): The Pydantic model class used to validate the response.
            Defaults to `AzureResponseFormat_EN`.

    Returns:
        str: A formatted string containing the parsed data. In case of an error during
            parsing or validation, an error message is returned instead.

    Notes:
        - The response will be validated against the specified schema before parsing.
        - If the schema contains lists, the list items will be prefixed with a hyphen
            (`-`) and joined with newlines.
        - If the validation or parsing fails, an error message is logged and returned.
    """

    if not isinstance(response, str):
        msg = f"Response is of type: {type(response)}. Nothing to validate."
        logger.info(msg)
        return msg

    try:
        parsed_str_list = []
        schema.model_validate_json(response).model_dump()
        for k, v in schema.model_validate_json(response).model_dump().items():
            parsed_str_list.append(f"{k}:")
            if isinstance(v, list):
                parsed_str_list.append("\n".join([f"- {val}" for val in v]))
            else:
                parsed_str_list.append(f"{v}")
        return "\n".join(parsed_str_list)
    except Exception as e:
        msg = f"Exception while parsing model response: {e}"
        logger.exception(msg)
        return msg


def query_azure_ai(prompt: str, chat_config: AzureConfig | None = None) -> str | None:
    """
    Sends a prompt to the Azure OpenAI API and retrieves the response.

    Args:
        prompt (str): The prompt or query to send to the Azure OpenAI API.
        chat_config (AzureConfig | None): The configuration for the Azure API client.
            If not provided, the default `AzureConfig` is used.

    Returns:
        str | None: The response text from the Azure OpenAI API as a string. If an error
            occurs during the API request, an error message is returned instead. If the
            response content is not in the expected format, it returns an error message.

    Notes:
        - The function configures and sends a request to the Azure OpenAI API,
            including the prompt and necessary parameters such as temperature, model,
            and token limits.
        - In case of an API error, various exceptions (e.g., `RequestError`,
            `HTTPStatusError`, `OpenAIError`) are caught and logged.
        - If the response is valid and contains a string, it will be returned.
            If it contains any unexpected content, it will return the raw response.

    Example:
        result = query_azure_ai("What is the weather like today?")
        print(result)  # Outputs the AI's response to the prompt.
    """

    if not prompt:
        msg = "No prompt provided"
        logger.warning(msg)
        return msg

    if chat_config is None:
        chat_config = AzureConfig()  # type: ignore

    messages = [
        {"role": "system", "content": generate_full_chat_system_prompt()},
        {"role": "user", "content": prompt},
    ]

    logger.info(f"Trying {messages} at {chat_config.AZURE_ENDPOINT}")

    try:
        client = AzureOpenAI(
            api_version=chat_config.AZURE_API_VERSION,
            azure_endpoint=str(chat_config.AZURE_ENDPOINT),
            api_key=chat_config.AZURE_KEY,
        )
        response = client.chat.completions.create(
            messages=messages,  # type: ignore[reportArgumentType]
            response_format={"type": CHAT_RESPONSE_FORMAT},
            max_completion_tokens=CHAT_MAX_COMPLETION_TOKENS,
            temperature=CHAT_TEMPERATURE,
            model=chat_config.AZURE_DEPLOYMENT,
        )
    except HTTPStatusError as e:  # non 2xx
        msg = f"HTTP error occurred while querying Azure AI: {e}"
        logger.error(msg)
        return msg
    except RequestError as e:
        msg = f"Request error occurred while querying Azure AI: {e}"
        logger.error(msg)
        return msg
    except OpenAIError as e:
        msg = f"OpenAI API error occurred: {e}"
        logger.error(msg)
        return msg
    except ValueError as e:  # input format error
        msg = f"Value error occurred: {e}"
        logger.error(msg)
        return msg
    except Exception as e:
        msg = f"Unexpected error occurred while querying Azure AI: {e}"
        logger.exception(msg)
        return msg

    content = response.choices[0].message.content
    if isinstance(content, str):
        valid_response, valid_msg = validate_json_response(content)
        if valid_response:
            return parse_json_response(content)
        else:
            return valid_msg
    else:
        return content
