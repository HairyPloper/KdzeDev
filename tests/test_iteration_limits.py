"""Environment inheritance, local overrides, and actual loop execution limits."""

from types import SimpleNamespace
from unittest.mock import Mock

import pytest
import runtime  # noqa: F401 -- register node schemas before loading configs

from entity.configs.base import ConfigError
from entity.configs.node.loop_counter import LoopCounterConfig
from runtime.node.executor.loop_counter_executor import LoopCounterNodeExecutor
from utils.iteration_limits import engine_cycle_default, loop_counter_default
from workflow.cycle_manager import CycleInfo, CycleManager
from workflow.executor.cycle_executor import CycleExecutor


@pytest.fixture(autouse=True)
def clear_iteration_environment(monkeypatch):
    monkeypatch.delenv("LOOP_COUNTER_MAX_ITERATIONS", raising=False)
    monkeypatch.delenv("ENGINE_MAX_ITERATIONS", raising=False)


def test_builtin_defaults():
    assert LoopCounterConfig.from_dict({}, path="node.config").max_iterations == 10
    assert LoopCounterConfig(path="node.config").max_iterations == 10
    assert CycleInfo("cycle", set(), set(), []).get_max_iterations() == 100


def test_node_inherits_environment_and_keeps_explicit_override(monkeypatch):
    monkeypatch.setenv("LOOP_COUNTER_MAX_ITERATIONS", "3")
    for data in ({}, {"max_iterations": None}):
        assert LoopCounterConfig.from_dict(data, path="config").max_iterations == 3
    assert LoopCounterConfig(path="config").max_iterations == 3
    assert LoopCounterConfig.from_dict({"max_iterations": 2}, path="config").max_iterations == 2
    monkeypatch.setenv("LOOP_COUNTER_MAX_ITERATIONS", "4")
    assert LoopCounterConfig.from_dict({}, path="config").max_iterations == 4


@pytest.mark.parametrize("raw", ["0", "-1", "1.5", "invalid", ""])
@pytest.mark.parametrize("name,reader", [
    ("LOOP_COUNTER_MAX_ITERATIONS", loop_counter_default),
    ("ENGINE_MAX_ITERATIONS", engine_cycle_default),
])
def test_invalid_environment_is_rejected(monkeypatch, raw, name, reader):
    monkeypatch.setenv(name, raw)
    with pytest.raises(ValueError, match=name):
        reader()


@pytest.mark.parametrize("raw", [0, -1, 1.5, True, "invalid", ""])
def test_invalid_local_override_is_rejected(raw):
    with pytest.raises(ConfigError, match="max_iterations"):
        LoopCounterConfig.from_dict({"max_iterations": raw}, path="node.config")


def test_bad_environment_has_config_path_and_explicit_override_still_works(monkeypatch):
    monkeypatch.setenv("LOOP_COUNTER_MAX_ITERATIONS", "bad")
    with pytest.raises(ConfigError, match="node.config.max_iterations.*LOOP_COUNTER"):
        LoopCounterConfig.from_dict({}, path="node.config")
    assert LoopCounterConfig.from_dict({"max_iterations": 2}, path="config").max_iterations == 2


def test_schema_leaves_inheritance_field_empty():
    field = LoopCounterConfig.field_specs()["max_iterations"].to_json()
    assert field["required"] is False
    assert "default" not in field
    assert "LOOP_COUNTER_MAX_ITERATIONS" in field["description"]


def test_nodes_emit_at_inherited_or_local_limit(monkeypatch):
    monkeypatch.setenv("LOOP_COUNTER_MAX_ITERATIONS", "3")
    executor = LoopCounterNodeExecutor(SimpleNamespace(global_state={}, log_manager=Mock()))
    for node_id, data, limit in [("inherited", {}, 3), ("local", {"max_iterations": 2}, 2)]:
        node = Mock(id=node_id)
        node.as_config.return_value = LoopCounterConfig.from_dict(data, path=node_id)
        for _ in range(limit - 1):
            assert executor.execute(node, []) == []
        messages = executor.execute(node, [])
        assert len(messages) == 1
        assert messages[0].metadata["loop_counter"]["max"] == limit
        assert executor.execute(node, []) == []  # default reset behavior preserved


def test_engine_default_and_internal_override(monkeypatch):
    monkeypatch.setenv("ENGINE_MAX_ITERATIONS", "3")
    cycle = CycleInfo("cycle", set(), set(), [])
    assert cycle.get_max_iterations() == 3
    cycle.iteration_count = 3
    assert not cycle.is_within_iteration_limit()
    cycle.max_iterations = 5
    assert cycle.get_max_iterations() == 5
    assert cycle.is_within_iteration_limit()


def test_retriggered_cycle_stops_at_environment_limit(monkeypatch):
    monkeypatch.setenv("ENGINE_MAX_ITERATIONS", "3")
    executor = CycleExecutor(Mock(), {}, [], CycleManager(), Mock())
    executor._detect_cycles_in_scope = Mock(return_value=[])
    executor._build_topological_layers_in_scope = Mock(return_value=[])
    executor._execute_scope_layers = Mock(return_value=set())
    executor._is_initial_node_retriggered = Mock(return_value=True)
    cycle = CycleInfo("cycle", {"a"}, set(), [])
    assert executor._execute_cycle_with_iterations("cycle", ["a"], "a", cycle.get_max_iterations()) == set()
    assert executor._execute_scope_layers.call_count == 3


def test_nested_cycles_use_environment_limit(monkeypatch):
    monkeypatch.setenv("ENGINE_MAX_ITERATIONS", "7")
    executor = CycleExecutor(Mock(), {}, [], CycleManager(), Mock())
    executor._validate_cycle_entry = Mock(return_value="a")
    executor._execute_cycle_with_iterations = Mock(return_value=set())
    executor.parallel_executor.execute_items_parallel = lambda items, callback, describe: [callback(item) for item in items]
    layers = [[{"type": "cycle", "cycle_id": "inner", "nodes": ["a", "b"]}]]
    executor._execute_scope_layers(layers, "outer", ["a", "b", "c"])
    executor._execute_cycle_with_iterations.assert_called_once_with(
        "inner", ["a", "b"], "a", max_iterations=7,
    )
