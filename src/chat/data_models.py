"""
Defines the structure for Azure responses.
Uses Pydantic for data validation and model creation.
"""

from pydantic import BaseModel, HttpUrl


class AzureResponseFormat_EN(BaseModel):
    """
    Represents the structure of an Azure response format,
    including an abstract, description, and sources.

    Attributes:
        abstract (str): A brief summary or abstract of the response.
        description (str): A detailed description of the response.
        sources (list[HttpUrl]): A list of URLs pointing to the sources
            related to the response.
    """

    Abstract: str
    Description: str
    Sources: list[HttpUrl]
