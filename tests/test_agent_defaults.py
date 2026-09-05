"""Global agent settings remain overridable without leaking into saved YAML/schema."""

from copy import deepcopy
import json
from unittest.mock import patch

import pytest
import runtime  # noqa: F401 -- register schemas before parsing nodes

from entity.config_loader import load_design_from_mapping
from entity.configs.base import ConfigError
from entity.configs.node.agent import AgentConfig
from runtime.node.agent.providers.openai_provider import OpenAIProvider


@pytest.fixture(autouse=True)
def environment(monkeypatch):
    for name in ("MODEL_PROVIDER", "MODEL_NAME", "BASE_URL", "API_KEY"):
        monkeypatch.delenv(name, raising=False)
    # Integration tests must not read the developer's real credentials.
    monkeypatch.setattr("entity.config_loader.load_dotenv_file", lambda: None)


def set_globals(monkeypatch):
    values = {
        "MODEL_PROVIDER": "openai", "MODEL_NAME": "global-model",
        "BASE_URL": "https://example.invalid/v1", "API_KEY": "test-global-secret",
    }
    for name, value in values.items():
        monkeypatch.setenv(name, value)


def test_builtin_fallbacks():
    config = AgentConfig.from_dict({}, path="agent")
    assert (config.provider, config.name) == ("openai", "gpt-4o")
    assert config.base_url is None and config.api_key is None


@pytest.mark.parametrize("empty", [None, "", "  "])
def test_empty_ui_fields_inherit(monkeypatch, empty):
    set_globals(monkeypatch)
    config = AgentConfig.from_dict(
        dict.fromkeys(("provider", "name", "base_url", "api_key"), empty), path="agent",
    )
    assert (config.provider, config.name, config.base_url, config.api_key) == (
        "openai", "global-model", "https://example.invalid/v1", "test-global-secret",
    )


def test_model_override_does_not_replace_other_settings(monkeypatch):
    set_globals(monkeypatch)
    config = AgentConfig.from_dict({"name": "local-model"}, path="agent")
    assert config.name == "local-model"
    assert config.provider == "openai"
    assert config.base_url == "https://example.invalid/v1"
    assert config.api_key == "test-global-secret"


def test_all_fields_can_be_overridden(monkeypatch):
    set_globals(monkeypatch)
    config = AgentConfig.from_dict({
        "provider": "gemini", "name": "local-model",
        "base_url": "https://other.invalid", "api_key": "test-local-secret",
    }, path="agent")
    assert (config.provider, config.name, config.base_url, config.api_key) == (
        "gemini", "local-model", "https://other.invalid", "test-local-secret",
    )


def test_defaults_are_read_when_loading_not_importing(monkeypatch):
    monkeypatch.setenv("MODEL_NAME", "first-model")
    assert AgentConfig.from_dict({}, path="agent").name == "first-model"
    monkeypatch.setenv("MODEL_NAME", "second-model")
    assert AgentConfig.from_dict({}, path="agent").name == "second-model"


@pytest.mark.parametrize("field", ["provider", "name", "base_url", "api_key"])
def test_invalid_local_types_are_rejected(field):
    with pytest.raises(ConfigError, match=field):
        AgentConfig.from_dict({field: 42}, path="agent")


@pytest.mark.parametrize("env,field", [("MODEL_NAME", "name"), ("MODEL_PROVIDER", "provider")])
def test_blank_required_environment_and_local_escape(monkeypatch, env, field):
    monkeypatch.setenv(env, " ")
    with pytest.raises(ConfigError, match=env):
        AgentConfig.from_dict({}, path="agent")
    assert getattr(AgentConfig.from_dict({field: "explicit"}, path="agent"), field) == "explicit"


def test_schema_does_not_capture_environment_or_force_local_defaults(monkeypatch):
    set_globals(monkeypatch)
    specs = AgentConfig.field_specs()
    for name in ("provider", "name", "base_url", "api_key"):
        payload = specs[name].to_json()
        assert payload["required"] is False
        assert "default" not in payload
    exported = json.dumps([field.to_json() for field in specs.values()])
    assert "test-global-secret" not in exported
    assert "global-model" not in exported
    assert "openai" in specs["provider"].enum


def test_workflow_inheritance_and_placeholder_override_preserve_raw_yaml(monkeypatch):
    set_globals(monkeypatch)
    monkeypatch.setenv("OTHER_API_KEY", "test-other-secret")
    raw = {"graph": {
        "id": "test", "start": ["shared"], "end": ["custom"],
        "nodes": [
            {"id": "shared", "type": "agent", "config": {"role": "Shared task"}},
            {"id": "custom", "type": "agent", "config": {
                "name": "custom-model", "api_key": "${OTHER_API_KEY}",
                "role": "Custom task",
            }},
        ],
        "edges": [{"from": "shared", "to": "custom"}],
    }}
    execution_input = deepcopy(raw)
    design = load_design_from_mapping(execution_input)
    shared, custom = [node.config for node in design.graph.nodes]
    assert shared.name == "global-model" and shared.api_key == "test-global-secret"
    assert custom.name == "custom-model" and custom.api_key == "test-other-secret"
    assert custom.base_url == shared.base_url
    # Inheritance must not materialize model defaults or credentials into YAML.
    assert execution_input["graph"]["nodes"][0]["config"] == {"role": "Shared task"}
    assert "test-global-secret" not in json.dumps(execution_input)


def test_provider_client_receives_resolved_settings_without_network(monkeypatch):
    set_globals(monkeypatch)
    config = AgentConfig.from_dict({}, path="agent")
    with patch("runtime.node.agent.providers.openai_provider.OpenAI") as client:
        OpenAIProvider(config).create_client()
    client.assert_called_once_with(api_key="test-global-secret", base_url="https://example.invalid/v1")
