"""Offline checks for configuration precedence, validation, paths, and secrets."""

import os
from pathlib import Path
import tempfile
import traceback
import unittest
from unittest.mock import patch

from pydantic import SecretStr

from qwensimul.config import ConfigurationError, Settings, load_settings


class SettingsTests(unittest.TestCase):
    """Exercise configuration using isolated directories and environments."""

    def setUp(self) -> None:
        """
        Purpose: Isolate configuration from real credentials and local files.
        Params:
            self: The test case instance.
        Return: None.
        """
        temporary_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temporary_dir.cleanup)
        self.project_dir = Path(temporary_dir.name).resolve()
        environment_patch = patch.dict(os.environ, {}, clear=True)
        environment_patch.start()
        self.addCleanup(environment_patch.stop)

    def write_env(self, content: str) -> None:
        """
        Purpose: Write a synthetic .env file for the current test.
        Params:
            self: The test case instance.
            content: Configuration text without real credentials.
        Return: None.
        """
        (self.project_dir / ".env").write_text(content, encoding="utf-8")

    def test_missing_env_uses_defaults_without_creating_data(self) -> None:
        """
        Purpose: Verify usable defaults and side-effect-free loading.
        Params:
            self: The test case instance.
        Return: None.
        """
        settings = load_settings(self.project_dir)
        self.assertEqual(str(settings.ollama_host).rstrip("/"), "http://localhost:11434")
        self.assertEqual(settings.qwen_model, "qwen3.5:4b")
        self.assertIsNone(settings.typesafe_api_key)
        self.assertEqual(settings.max_rounds, 20)
        self.assertEqual(settings.data_dir, self.project_dir / "data")
        self.assertEqual(settings.qwen_timeout_seconds, 120.0)
        self.assertEqual(settings.jev_timeout_seconds, 30.0)
        self.assertFalse(settings.data_dir.exists())
        self.assertEqual(dict(os.environ), {})

    def test_env_file_loads_typed_values(self) -> None:
        """
        Purpose: Verify .env values are parsed, trimmed, and validated.
        Params:
            self: The test case instance.
        Return: None.
        """
        self.write_env(
            'OLLAMA_HOST=http://127.0.0.1:12345\nQWEN_MODEL=" alternate:model "\n'
            'TYPESAFE_API_KEY=" fake-key "\nMAX_ROUNDS=7\nDATA_DIR=outputs\n'
            'QWEN_TIMEOUT_SECONDS=60.5\nJEV_TIMEOUT_SECONDS=10\n'
        )
        settings = load_settings(self.project_dir)
        self.assertEqual(str(settings.ollama_host).rstrip("/"), "http://127.0.0.1:12345")
        self.assertEqual(settings.qwen_model, "alternate:model")
        self.assertIsInstance(settings.typesafe_api_key, SecretStr)
        self.assertEqual(settings.typesafe_api_key.get_secret_value(), "fake-key")
        self.assertEqual(settings.max_rounds, 7)
        self.assertEqual(settings.data_dir, self.project_dir / "outputs")
        self.assertEqual(settings.qwen_timeout_seconds, 60.5)
        self.assertEqual(settings.jev_timeout_seconds, 10.0)
        self.assertEqual(dict(os.environ), {})

    def test_environment_overrides_file_including_empty_key(self) -> None:
        """
        Purpose: Verify process overrides and explicit clearing of the Jev key.
        Params:
            self: The test case instance.
        Return: None.
        """
        self.write_env("QWEN_MODEL=file:model\nMAX_ROUNDS=8\nTYPESAFE_API_KEY=file-key\n")
        os.environ.update({"QWEN_MODEL": "env:model", "TYPESAFE_API_KEY": ""})
        before = dict(os.environ)
        settings = load_settings(self.project_dir)
        self.assertEqual(settings.qwen_model, "env:model")
        self.assertEqual(settings.max_rounds, 8)
        self.assertIsNone(settings.typesafe_api_key)
        self.assertEqual(dict(os.environ), before)

    def test_empty_environment_value_does_not_fall_back_to_file(self) -> None:
        """
        Purpose: Reject empty required overrides rather than silently falling back.
        Params:
            self: The test case instance.
        Return: None.
        """
        self.write_env("QWEN_MODEL=valid:model\n")
        os.environ["QWEN_MODEL"] = ""
        with self.assertRaisesRegex(ConfigurationError, "QWEN_MODEL"):
            load_settings(self.project_dir)

    def test_default_project_dir_is_independent_of_working_dir(self) -> None:
        """
        Purpose: Verify default .env discovery does not follow the working directory.
        Params:
            self: The test case instance.
        Return: None.
        """
        self.write_env("QWEN_MODEL=project:model\nDATA_DIR=outputs\n")
        unrelated_dir = self.project_dir / "unrelated"
        unrelated_dir.mkdir()
        (unrelated_dir / ".env").write_text("QWEN_MODEL=wrong:model\n", encoding="utf-8")
        previous_dir = Path.cwd()
        try:
            os.chdir(unrelated_dir)
            with patch("qwensimul.config.PROJECT_DIR", self.project_dir):
                settings = load_settings()
        finally:
            os.chdir(previous_dir)
        self.assertEqual(settings.qwen_model, "project:model")
        self.assertEqual(settings.data_dir, self.project_dir / "outputs")

    def test_absolute_data_path_is_preserved(self) -> None:
        """
        Purpose: Verify an explicit absolute output directory is not rebased.
        Params:
            self: The test case instance.
        Return: None.
        """
        output_dir = self.project_dir / "absolute-output"
        os.environ["DATA_DIR"] = str(output_dir)
        self.assertEqual(load_settings(self.project_dir).data_dir, output_dir)

    def test_existing_file_is_rejected_as_data_dir(self) -> None:
        """
        Purpose: Prevent output configuration from targeting an existing file.
        Params:
            self: The test case instance.
        Return: None.
        """
        output_file = self.project_dir / "output.txt"
        output_file.write_text("keep this file", encoding="utf-8")
        os.environ["DATA_DIR"] = str(output_file)
        with self.assertRaisesRegex(ConfigurationError, "DATA_DIR"):
            load_settings(self.project_dir)
        self.assertEqual(output_file.read_text(encoding="utf-8"), "keep this file")

    def test_invalid_values_report_variable_names(self) -> None:
        """
        Purpose: Reject malformed hosts, blank fields, and invalid numeric bounds.
        Params:
            self: The test case instance.
        Return: None.
        """
        cases = {
            "OLLAMA_HOST": ["", "localhost:11434", "ftp://localhost", "http://localhost:99999"],
            "QWEN_MODEL": ["", "   "],
            "MAX_ROUNDS": ["", "0", "-1", "1.5", "many"],
            "DATA_DIR": ["", "   ", "bad\x00path"],
            "QWEN_TIMEOUT_SECONDS": ["0", "-1", "nan", "inf", "soon"],
            "JEV_TIMEOUT_SECONDS": ["0", "-1", "nan", "inf", "soon"],
        }
        for name, invalid_values in cases.items():
            for value in invalid_values:
                with self.subTest(name=name, value=value):
                    self.write_env(f"{name}='{value}'\n")
                    with self.assertRaisesRegex(ConfigurationError, name):
                        load_settings(self.project_dir)

    def test_blank_key_is_optional(self) -> None:
        """
        Purpose: Allow the example file and Qwen-only work without a Jev key.
        Params:
            self: The test case instance.
        Return: None.
        """
        for value in ["", "   "]:
            with self.subTest(value=value):
                self.write_env(f'TYPESAFE_API_KEY="{value}"\n')
                self.assertIsNone(load_settings(self.project_dir).typesafe_api_key)

    def test_keys_are_literal_and_excluded_from_output(self) -> None:
        """
        Purpose: Preserve literal credentials and keep them out of serialization.
        Params:
            self: The test case instance.
        Return: None.
        """
        secret = "fake-${OTHER_KEY}-sentinel"
        os.environ["OTHER_KEY"] = "unexpected-expansion"
        self.write_env(f"TYPESAFE_API_KEY='{secret}'\n")
        settings = load_settings(self.project_dir)
        self.assertEqual(settings.typesafe_api_key.get_secret_value(), secret)
        self.assertNotIn(secret, str(settings))
        self.assertNotIn(secret, repr(settings))
        self.assertNotIn("typesafe_api_key", settings.model_dump())
        self.assertNotIn(secret, settings.model_dump_json())

    def test_errors_and_tracebacks_do_not_expose_credentials(self) -> None:
        """
        Purpose: Keep rejected URL credentials and API keys out of error output.
        Params:
            self: The test case instance.
        Return: None.
        """
        secret = "fake-secret-sentinel"
        hosts = [
            f"http://user:{secret}@localhost:11434",
            f"http://localhost:11434?key={secret}",
            f"http://localhost:11434#{secret}",
            f"invalid-{secret}",
        ]
        for host in hosts:
            with self.subTest(host=host):
                self.write_env(f"OLLAMA_HOST={host}\nTYPESAFE_API_KEY={secret}\nMAX_ROUNDS=bad\n")
                try:
                    load_settings(self.project_dir)
                except ConfigurationError as error:
                    self.assertIn("OLLAMA_HOST", str(error))
                    self.assertIn("MAX_ROUNDS", str(error))
                    self.assertNotIn(secret, "".join(traceback.format_exception(error)))
                else:
                    self.fail("Invalid configuration was accepted.")

    def test_unreadable_env_reports_safe_error(self) -> None:
        """
        Purpose: Report read failures without exposing exception contents.
        Params:
            self: The test case instance.
        Return: None.
        """
        with patch("qwensimul.config.dotenv_values", side_effect=PermissionError("secret")):
            with self.assertRaises(ConfigurationError) as raised:
                load_settings(self.project_dir)
        self.assertNotIn("secret", str(raised.exception))
        self.assertIn("Unable to read .env", str(raised.exception))

    def test_windows_utf8_bom_is_supported(self) -> None:
        """
        Purpose: Support .env files written with a Windows UTF-8 byte order mark.
        Params:
            self: The test case instance.
        Return: None.
        """
        (self.project_dir / ".env").write_text("QWEN_MODEL=bom:model\n", encoding="utf-8-sig")
        self.assertEqual(load_settings(self.project_dir).qwen_model, "bom:model")

    def test_settings_direct_defaults_resolve_data_path(self) -> None:
        """
        Purpose: Keep direct settings construction consistent with default loading.
        Params:
            self: The test case instance.
        Return: None.
        """
        with patch("qwensimul.config.PROJECT_DIR", self.project_dir):
            self.assertEqual(Settings().data_dir, self.project_dir / "data")
