from pydantic import BaseModel


class Config(BaseModel):
    """
    Configuration model for the application.

    Attributes:
        OLLAMA_BASE_URL (str): The base URL for the Ollama service.
        OPENAI_API_KEY (str): The API key for the OpenAI service.
        OPENAI_BASE_URL (str): The base URL for the OpenAI API (optional, defaults to official API).
        PRIMARY_MODEL (str): The name of the primary model to use.
        SECONDARY_MODEL (str): The name of the secondary model to use.
        EMBEDDING_MODEL (str): The name of the embedding model to use.
        summaryPrompt (str): The prompt template for generating summaries.
        summaryOptions (dict): Additional options for summary generation.
    """

    OLLAMA_BASE_URL: str = ""
    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    PRIMARY_MODEL: str = ""
    SECONDARY_MODEL: str = ""
    EMBEDDING_MODEL: str = ""
    summaryPrompt: str = ""
    summaryOptions: dict = {}


class ConfigData(BaseModel):
    """
    Container for configuration data.

    This model is used to wrap configuration data in a dictionary format.

    Attributes:
        data (dict): A dictionary containing configuration key-value pairs.
    """

    data: dict
