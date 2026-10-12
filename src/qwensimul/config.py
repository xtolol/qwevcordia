"""
Load validated settings without changing the process environment or exposing keys.
"""

import os
from pathlib import Path

from dotenv import dotenv_values
from pydantic import (
    AnyHttpUrl,
    BaseModel,
    ConfigDict,
    Field,
    SecretStr,
    ValidationError,
    ValidationInfo,
    field_validator,
)

PROJECT_DIR = Path(__file__).resolve().parents[2]

# Fixed messages keep rejected values, including credentials, out of errors.
SETTING_ERRORS = {
    "OLLAMA_HOST": "must be an HTTP(S) URL without credentials, query, or fragment",
    "QWEN_MODEL": "must be a nonempty model name",
    "TYPESAFE_API_KEY": "must be a string or omitted",
    "MAX_ROUNDS": "must be a positive integer",
    "DATA_DIR": "must be a nonempty directory path, not an existing file",
    "QWEN_TIMEOUT_SECONDS": "must be a positive finite number of seconds",
    "JEV_TIMEOUT_SECONDS": "must be a positive finite number of seconds",
}


class ConfigurationError(ValueError):
    """Configuration failure whose message contains no supplied values."""


class Settings(BaseModel):
    """Validated settings; the Jev key is optional until Jev is requested."""

    model_config = ConfigDict(
        populate_by_name=True,
        validate_default=True,
        frozen=True,
        str_strip_whitespace=True,
        hide_input_in_errors=True,
    )

    ollama_host: AnyHttpUrl = Field(
        default="http://localhost:11434", validation_alias="OLLAMA_HOST"
    )
    qwen_model: str = Field(
        default="qwen3.5:4b", min_length=1, validation_alias="QWEN_MODEL"
    )
    typesafe_api_key: SecretStr | None = Field(
        default=None, validation_alias="TYPESAFE_API_KEY", repr=False, exclude=True
    )
    max_rounds: int = Field(default=20, gt=0, validation_alias="MAX_ROUNDS")
    data_dir: Path = Field(default=Path("data"), validation_alias="DATA_DIR")
    qwen_timeout_seconds: float = Field(
        default=120.0, gt=0, allow_inf_nan=False,
        validation_alias="QWEN_TIMEOUT_SECONDS",
    )
    jev_timeout_seconds: float = Field(
        default=30.0, gt=0, allow_inf_nan=False,
        validation_alias="JEV_TIMEOUT_SECONDS",
    )

    @field_validator("ollama_host")
    @classmethod
    def validate_ollama_host(cls, value: AnyHttpUrl) -> AnyHttpUrl:
        """
        Purpose: Reject URL components that can carry accidental credentials.
        Params:
            cls: The settings model class.
            value: The parsed HTTP(S) URL.
        Return: The validated URL.
        """
        if value.username or value.password or value.query or value.fragment:
            raise ValueError("Use a URL without credentials, query, or fragment.")
        return value

    @field_validator("typesafe_api_key", mode="before")
    @classmethod
    def normalize_api_key(cls, value: object) -> object:
        """
        Purpose: Treat an empty key as absent and trim surrounding whitespace.
        Params:
            cls: The settings model class.
            value: The supplied key, before secret validation.
        Return: A trimmed key, None for an empty key, or the original input.
        """
        if isinstance(value, str):
            value = value.strip()
            if not value:
                return None
        return value

    @field_validator("data_dir", mode="before")
    @classmethod
    def resolve_data_dir(cls, value: object, info: ValidationInfo) -> Path:
        """
        Purpose: Resolve output paths consistently without creating directories.
        Params:
            cls: The settings model class.
            value: The supplied directory string or Path.
            info: Validation context containing an optional project directory.
        Return: An absolute directory path; raise ValueError for invalid paths.
        """
        if isinstance(value, str):
            value = value.strip()
            if not value or "\x00" in value:
                raise ValueError("Use a nonempty directory path.")
        elif not isinstance(value, Path):
            raise ValueError("Use a directory string or Path.")

        project_dir = PROJECT_DIR
        if info.context is not None:
            project_dir = info.context["project_dir"]
        try:
            path = Path(value)
            if not path.is_absolute():
                path = project_dir / path
            path = path.resolve()
            if path.exists() and not path.is_dir():
                raise ValueError("The data directory is an existing file.")
        except (OSError, RuntimeError):
            raise ValueError("Unable to resolve the data directory.") from None
        return path


def load_settings(project_dir: Path | None = None) -> Settings:
    """
    Purpose: Load project .env settings, with process environment taking priority.
    Params:
        project_dir: The directory containing .env and the base for relative
            data paths. None uses the project directory of this source checkout.
    Return: Validated Settings; raise ConfigurationError with safe error details.
    """
    try:
        root = PROJECT_DIR if project_dir is None else project_dir.resolve()
        # Disable interpolation so keys remain literal and no ambient values
        # are silently substituted into configuration.
        file_values = dotenv_values(root / ".env", encoding="utf-8-sig", interpolate=False)
    except (OSError, UnicodeError, RuntimeError):
        raise ConfigurationError("Unable to read .env; check its path and encoding.") from None

    values: dict[str, str | None] = {}
    for name in SETTING_ERRORS:
        if name in os.environ:
            values[name] = os.environ[name]
        elif name in file_values:
            values[name] = file_values[name]

    try:
        return Settings.model_validate(values, context={"project_dir": root})
    except ValidationError as error:
        messages: list[str] = []
        for detail in error.errors(include_input=False, include_context=False, include_url=False):
            name = str(detail["loc"][0])
            messages.append(f"{name}: {SETTING_ERRORS[name]}")
        raise ConfigurationError("Invalid configuration: " + "; ".join(messages)) from None
