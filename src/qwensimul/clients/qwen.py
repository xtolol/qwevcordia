"""Local Qwen connection checks through Ollama; action proposals remain a stub."""

from json import JSONDecodeError
from math import isfinite
from time import perf_counter

import httpx
import ollama
from pydantic import ValidationError

from qwensimul.clients.checks import ConnectionCheckResult, failed_check, http_error_code


def normalized_model_name(model: str) -> str:
    """
    Purpose: Match untagged Ollama model names to their implicit latest tag.
    Params:
        model: An Ollama model name, optionally containing a registry or namespace.
    Return: The model name with an explicit tag.
    """
    if ":" not in model.rsplit("/", 1)[-1]:
        return model + ":latest"
    return model


class QwenClient:
    """A reusable, lazily created Ollama client with standalone smoke checks."""

    def __init__(
        self, host: str, model: str, timeout_seconds: float = 120.0
    ) -> None:
        """
        Purpose: Store explicit settings without connecting to Ollama.
        Params:
            self: The Qwen adapter instance.
            host: The Ollama HTTP(S) host from validated settings.
            model: The installed Qwen model name.
            timeout_seconds: The positive, finite timeout for each SDK request.
        Return: None.
        """
        self._host = host.strip()
        self._model = model.strip()
        self._timeout_seconds = timeout_seconds
        self._client: ollama.Client | None = None
        self._closed = False

    def check_connection(self) -> ConnectionCheckResult:
        """
        Purpose: Verify model availability and one completed Qwen inference call.
        Params:
            self: The Qwen adapter instance.
        Return: A safe report of success or an expected connection failure.
        """
        started_at = perf_counter()
        if (
            self._closed or not self._host or not self._model
            or not isfinite(self._timeout_seconds) or self._timeout_seconds <= 0
        ):
            return failed_check("qwen", started_at, "configuration_error")

        if self._client is None:
            try:
                self._client = ollama.Client(
                    host=self._host, timeout=self._timeout_seconds
                )
            except (ValueError, httpx.InvalidURL):
                return failed_check("qwen", started_at, "configuration_error")

        inference_started = False
        try:
            installed_models = self._client.list()
            model_found = False
            for installed_model in installed_models.models:
                if not installed_model.model or not installed_model.model.strip():
                    return failed_check("qwen", started_at, "invalid_response")
                if normalized_model_name(installed_model.model) == normalized_model_name(self._model):
                    model_found = True
            if not model_found:
                return failed_check("qwen", started_at, "model_missing")

            inference_started = True
            response = self._client.chat(
                model=self._model,
                messages=[{"role": "user", "content": "Reply with only OK."}],
                stream=False,
                think=False,
                options={"num_predict": 64},
            )
            if (
                response.done is not True
                or not response.model or not response.model.strip()
                or not response.message.content or not response.message.content.strip()
            ):
                return failed_check("qwen", started_at, "invalid_response")
            return ConnectionCheckResult(
                service="qwen",
                success=True,
                elapsed_seconds=perf_counter() - started_at,
                model=response.model,
                input_tokens=response.prompt_eval_count,
                output_tokens=response.eval_count,
            )
        except httpx.TimeoutException:
            return failed_check("qwen", started_at, "timeout")
        except (ConnectionError, httpx.TransportError):
            return failed_check("qwen", started_at, "unreachable")
        except ollama.ResponseError as error:
            if inference_started and error.status_code == 404:
                return failed_check("qwen", started_at, "model_missing")
            return failed_check("qwen", started_at, http_error_code(error.status_code))
        except (ValidationError, JSONDecodeError):
            return failed_check("qwen", started_at, "invalid_response")

    def close(self) -> None:
        """
        Purpose: Release SDK resources and prevent subsequent checks.
        Params:
            self: The Qwen adapter instance.
        Return: None; repeated calls have no effect.
        """
        if self._closed:
            return
        self._closed = True
        if self._client is not None:
            self._client.close()
            self._client = None

    def propose_action(self, prompt: str, action_schema: dict) -> dict:
        """
        Purpose: Eventually request one structured character action from Qwen.
        Params:
            self: The Qwen adapter instance.
            prompt: The character-specific context and instructions.
            action_schema: The schema the future action response must satisfy.
        Return: A structured action in the future; this unimplemented stub returns None.
        """
        pass
