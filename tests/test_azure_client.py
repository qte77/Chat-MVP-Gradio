import pytest
from unittest.mock import patch

from src.chat.data_models import AzureResponseFormat_EN
from src.chat.azure_client import (
    validate_json_response,
    parse_json_response,
    query_azure_ai,
)


@pytest.mark.parametrize(
    "response, expected",
    [
        (
            '{"Abstract": "Text", "Description": "Text", "Sources": []}',
            (
                True,
                "'response' adheres to schema type '<class 'src.chat.data_models.AzureResponseFormat_EN'>'.",
            ),
        ),
        ('{"invalid_field": "Test"}', (False, "Error validating model response: ...")),
        (
            None,
            (False, "Response is of type: <class 'NoneType'>. Nothing to validate."),
        ),
    ],
)
def test_validate_json_response(response, expected):
    valid, msg = validate_json_response(response, AzureResponseFormat_EN)
    assert valid == expected[0]
    # FIXME metaclass received
    # assert msg == expected[1]


@pytest.mark.parametrize(
    "response, expected",
    [
        (
            '{"Abstract": "Text", "Description": "Text", "Sources": []}',
            "Abstract:\nText\nDescription:\nText\nSources:\n",
        ),
        ('{"invalid_field": "Test"}', "Exception while parsing model response: ..."),
        (None, "Response is of type: <class 'NoneType'>. Nothing to validate."),
    ],
)
def test_parse_json_response(response, expected):
    result = parse_json_response(response, AzureResponseFormat_EN)
    assert result == expected

@pytest.mark.parametrize("prompt, expected", [
    ("What is the weather like?", "Sunny"),
    ("Invalid prompt", "Unexpected error occurred while querying Azure AI: ...")
])
@patch('src.chat.azure_client.AzureOpenAI')
def test_query_azure_ai(mock_azure_client, prompt, expected):
    # Mocking Azure OpenAI client response
    mock_response = {
        'choices': [{'message': {'content': 'Sunny'}}]
    }
    mock_azure_client.return_value.chat.completions.create.return_value = mock_response

    result = query_azure_ai(prompt)
    assert result == expected
