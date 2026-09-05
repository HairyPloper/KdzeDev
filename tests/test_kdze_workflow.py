"""Exercise Kdze's forward-only workflow without calling a model provider."""

from collections import Counter
from pathlib import Path

import runtime  # noqa: F401 -- register schemas before reading the workflow
import yaml

from entity.graph_config import GraphConfig
from entity.messages import Message, MessageRole
from runtime.node.executor.agent_executor import AgentNodeExecutor
from workflow.graph import GraphExecutor
from workflow.graph_context import GraphContext


def test_kdze_workflow_runs_each_teammate_once_and_preserves_sources(
    monkeypatch, tmp_path
):
    monkeypatch.setenv("ENGINE_MAX_ITERATIONS", "100")
    monkeypatch.setenv("MODEL_PROVIDER", "openai")
    monkeypatch.setenv("MODEL_NAME", "gpt-4o")
    path = Path(__file__).resolve().parents[1] / "yaml_instance/Kdze_new_business_idea.yaml"
    definition = yaml.safe_load(path.read_text(encoding="utf-8"))["graph"]
    graph = GraphContext(GraphConfig.from_dict(definition, "kdze_test", tmp_path))
    calls = Counter()
    received = {}

    def fake_agent(self, node, inputs):
        calls[node.id] += 1
        received[node.id] = {
            message.metadata.get("source"): message.text_content()
            for message in inputs
        }
        return [
            Message(
                role=MessageRole.ASSISTANT,
                content=f"OUTPUT FROM {node.id}",
            )
        ]

    monkeypatch.setattr(AgentNodeExecutor, "execute", fake_agent)
    GraphExecutor(graph).run(
        "Four founders in Serbia; named skills; RSD 100,000 budget; "
        "10 hours each per week."
    )

    active = {
        "Viki", "Anton", "Makarony", "Toške", "Pako", "Koki", "Pepi",
        "Šomi", "Ceki", "Pijeki", "Dinča", "Dado", "Miki",
    }
    assert not graph.has_cycles
    assert set(calls) == active
    assert all(calls[name] == 1 for name in active)
    assert calls["gospodarice"] == 0

    assert set(received["Pako"]) == {"Viki", "Makarony", "Toške"}
    assert set(received["Ceki"]) == {"Pako", "Šomi"}
    assert set(received["Pijeki"]) == {"Viki", "Pako", "Ceki"}
    assert set(received["Dinča"]) == {"Pako", "Pijeki"}
    assert set(received["Dado"]) == {"Pako", "Dinča"}
    assert set(received["Miki"]) == {
        "Viki", "Pako", "Ceki", "Pijeki", "Dinča", "Dado",
    }


def test_kdze_workflow_has_no_review_processors_or_cameo_edges():
    path = Path(__file__).resolve().parents[1] / "yaml_instance/Kdze_new_business_idea.yaml"
    graph = yaml.safe_load(path.read_text(encoding="utf-8"))["graph"]

    assert "QA review gate" not in {node["id"] for node in graph["nodes"]}
    assert not any(edge.get("process") for edge in graph["edges"])
    assert not any(
        edge["from"] == "gospodarice" or edge["to"] == "gospodarice"
        for edge in graph["edges"]
    )
