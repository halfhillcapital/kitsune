import os
from dataclasses import dataclass, field
from functools import lru_cache


class MissingEnvironmentVariableError(Exception):
    def __init__(self, key: str):
        super().__init__(f"Missing required environment variable: {key}")


def required_env(key: str, default: str | None = None) -> str:
    """
    Gets an environment variable or raises a custom error if it's not set.

    Args:
        key: The name of the environment variable.
        default: The default value to return if the environment variable is not found.

    Returns:
        The value of the environment variable as a string.

    Raises:
        MissingEnvironmentVariableError: If the environment variable is not found.
    """
    value = os.getenv(key)
    if value is None:
        if default is None:
            raise MissingEnvironmentVariableError(key)
        return default
    return value


#TODO: Hacky way to read prompts from files, should be refactored later
#TODO: Add frontmatter to the prompt files to specify metadata like description, tags, etc.
def required_prompts(file: str) -> str:
    """
    Reads the content of a markdown file in the prompts folder.

    Args:
        file: The name of the prompt file.
    Returns:
        The content of the file as a string.
    """
    filepath = os.path.join(os.getcwd(), "prompts", file)
    with open(filepath, "r") as f:
        return f.read()


@dataclass(frozen=True)
class Config:
    """Configuration for the Kitsune application."""
    name: str = "Kitsune"
    version: str = "0.1.0"

    LOCAL_URL: str = field(default_factory=lambda: required_env("LOCAL_URL", "http://localhost:11434"))
    LOCAL_MODEL: str = field(default_factory=lambda: required_env("LOCAL_MODEL", "gpt-3.5-turbo"))

    OPENROUTER_URL: str = field(default_factory=lambda: required_env("OPENROUTER_URL", "https://openrouter.ai/api/v1"))
    OPENROUTER_API_KEY: str = field(default_factory=lambda: required_env("OPENROUTER_API_KEY"))

    LINKUP_URL: str = field(default_factory=lambda: required_env("LINKUP_URL", "https://api.linkup.so/v1"))
    LINKUP_API_KEY: str = field(default_factory=lambda: required_env("LINKUP_API_KEY"))

    TAVILY_URL: str = field(default_factory=lambda: required_env("TAVILY_URL", "https://api.tavily.com"))
    TAVILY_API_KEY: str = field(default_factory=lambda: required_env("TAVILY_API_KEY"))


@lru_cache(maxsize=1)
def get_config() -> Config:
    return Config()


def reset_config_cache() -> None:
    get_config.cache_clear()