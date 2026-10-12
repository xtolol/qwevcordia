"""Hosted Jev connection checks; institutional judgments remain a stub."""

from math import isclose, isfinite
from time import perf_counter

from pydantic import SecretStr, ValidationError
from typesafe_sdk import (
    Choice,
    ChoiceAnswer,
    RetryPolicy,
    TypeSafeAPIConnectionError,
    TypeSafeAPIError,
    TypeSafeAPIResponseValidationError,
    TypeSafeAPITimeoutError,
    TypeSafeClient,
    TypeSafeError,
)

from qwensimul.clients.checks import ConnectionCheckResult, failed_check, http_error_code


class JevClient:
    """A reusable TypeSafe client with secret credentials and no automatic retries."""

    def __init__(self, api_key: str | None, timeout_seconds: float = 30.0) -> None:
        """
        Purpose: Store credentials and timeout without connecting to Jev.
        Params:
            self: The Jev adapter instance.
            api_key: The TypeSafe API key, or None when Jev is not configured.
            timeout_seconds: The positive, finite timeout for each SDK request.
        Return: None.
        """
        self._api_key = SecretStr(api_key.strip()) if api_key is not None else None
        self._timeout_seconds = timeout_seconds
        self._client: TypeSafeClient | None = None
        self._closed = False

    def check_connection(self) -> ConnectionCheckResult:
        """
        Purpose: Verify Jev access with one standalone, structurally valid Choice.
        Params:
            self: The Jev adapter instance.
        Return: A safe report of success or an expected connection failure.
        """
        started_at = perf_counter()
        if (
            self._closed or self._api_key is None
            or not self._api_key.get_secret_value()
            or not isfinite(self._timeout_seconds) or self._timeout_seconds <= 0
        ):
            return failed_check("jev", started_at, "configuration_error")

        if self._client is None:
            try:
                self._client = TypeSafeClient(
                    api_key=self._api_key.get_secret_value(),
                    base_url="https://api.typesafe.ai",
                    model="jev-latest",
                    timeout=self._timeout_seconds,
                    retry=RetryPolicy(max_retries=0),
                )
            except TypeSafeError:
                return failed_check("jev", started_at, "configuration_error")

        try:
            response = self._client.system_one(
                state="The described object is red.",
                questions={
                    "color": Choice(
                        instructions="Which color is explicitly described?",
                        criteria={"red": "The color red.", "blue": "The color blue."},
                    )
                },
            )
            answer = response.answers.get("color")
            if not response.model.strip() or not isinstance(answer, ChoiceAnswer):
                return failed_check("jev", started_at, "invalid_response")
            if answer.choice not in {"red", "blue"} or set(answer.probabilities) != {"red", "blue"}:
                return failed_check("jev", started_at, "invalid_response")
            for probability in answer.probabilities.values():
                if not isfinite(probability) or not 0 <= probability <= 1:
                    return failed_check("jev", started_at, "invalid_response")
            if not isfinite(answer.confidence) or not 0 <= answer.confidence <= 1:
                return failed_check("jev", started_at, "invalid_response")
            if not isclose(sum(answer.probabilities.values()), 1.0, rel_tol=0, abs_tol=0.001):
                return failed_check("jev", started_at, "invalid_response")
            return ConnectionCheckResult(
                service="jev",
                success=True,
                elapsed_seconds=perf_counter() - started_at,
                model=response.model,
                input_tokens=response.usage.input_tokens,
                output_tokens=response.usage.output_tokens,
                request_id=response.request_id,
            )
        except TypeSafeAPITimeoutError:
            return failed_check("jev", started_at, "timeout")
        except TypeSafeAPIConnectionError:
            return failed_check("jev", started_at, "unreachable")
        except (TypeSafeAPIResponseValidationError, ValidationError):
            return failed_check("jev", started_at, "invalid_response")
        except TypeSafeAPIError as error:
            return failed_check("jev", started_at, http_error_code(error.status))
        except TypeSafeError:
            return failed_check("jev", started_at, "service_error")

    def close(self) -> None:
        """
        Purpose: Release SDK resources and prevent subsequent checks.
        Params:
            self: The Jev adapter instance.
        Return: None; repeated calls have no effect.
        """
        if self._closed:
            return
        self._closed = True
        if self._client is not None:
            self._client.close()
            self._client = None

    def choose(self, state: dict, question: str, choices: list[dict]) -> dict:
        """
        Purpose: Eventually request and normalize a Jev institutional judgment.
        Params:
            self: The Jev adapter instance.
            state: The supplied evidence and policy context.
            question: The institutional question to evaluate.
            choices: The explicit judgment options.
        Return: A judgment in the future; this unimplemented stub returns None.
        """
        pass
