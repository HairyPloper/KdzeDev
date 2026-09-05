"""Exercise Kdze's bounded QA route without calling a model provider."""

from collections import Counter
from pathlib import Path

import pytest
import runtime  # noqa: F401 -- register schemas before reading the workflow
import yaml

from entity.graph_config import GraphConfig
from entity.messages import Message, MessageRole
from functions.edge_processor.kdze_review import kdze_qa_review
from runtime.node.executor.agent_executor import AgentNodeExecutor
from workflow.graph import GraphExecutor
from workflow.graph_context import GraphContext


@pytest.mark.parametrize(
    "review",
    [
        "QA_STATUS: READY",
        "QA_STATUS: READY  \nDetails",
        "**QA_STATUS: READY**\nDetails",
        "`QA_STATUS: READY`\nDetails",
        "\ufeffQA_STATUS: READY\nDetails",
        "\n\nQA_STATUS: READY\nDetails",
    ],
)
def test_ready_status_accepts_safe_whitespace_and_markdown(review):
    assert kdze_qa_review(review, {}).startswith("KDZE_REVIEW: READY\n")


@pytest.mark.parametrize(
    "review",
    ["", "READY", "QA_STATUS: READY maybe", "Quoted decision:\nQA_STATUS: READY", "```\nQA_STATUS: READY\n```"],
)
def test_invalid_status_requests_one_revision_and_preserves_review(review):
    result = kdze_qa_review(review, {})
    assert result.startswith("KDZE_REVIEW: REVISE\n")
    assert "missing or malformed" in result
    assert result.endswith(review)


def test_only_one_revision_is_available_per_run():
    state = {}
    assert kdze_qa_review("QA_STATUS: NEEDS_CHANGES", state).startswith("KDZE_REVIEW: REVISE\n")
    result = kdze_qa_review("QA_STATUS: NEEDS_CHANGES", state)
    assert result.startswith("KDZE_REVIEW: LIMIT_REACHED\n")
    assert "not QA approval" in result
    assert kdze_qa_review("QA_STATUS: NEEDS_CHANGES", {}).startswith("KDZE_REVIEW: REVISE\n")


@pytest.mark.parametrize(
    "decisions,expected_rounds,final_status,expected_calls",
    [
        (["READY"], 1, "READY", 13),
        (["NEEDS_CHANGES", "READY"], 2, "READY", 17),
        (["NEEDS_CHANGES", "NEEDS_CHANGES"], 2, "LIMIT_REACHED", 17),
        ([None, None], 2, "LIMIT_REACHED", 17),
    ],
)
def test_saved_graph_has_one_bounded_qa_revision(
    monkeypatch, tmp_path, decisions, expected_rounds, final_status, expected_calls
):
    monkeypatch.setenv("ENGINE_MAX_ITERATIONS", "100")
    monkeypatch.setenv("MODEL_PROVIDER", "openai")
    monkeypatch.setenv("MODEL_NAME", "gpt-4o")
    path = Path(__file__).resolve().parents[1] / "yaml_instance/Kdze_new_business_idea.yaml"
    definition = yaml.safe_load(path.read_text(encoding="utf-8"))["graph"]
    graph = GraphContext(GraphConfig.from_dict(definition, "qa_test", tmp_path))
    calls = Counter()
    received = {}

    def fake_agent(self, node, inputs):
        calls[node.id] += 1
        handoff = "\n".join(message.text_content() for message in inputs)
        received.setdefault(node.id, []).append(handoff)
        if node.id == "Ceki":
            decision = decisions[min(calls[node.id] - 1, len(decisions) - 1)]
            header = f"QA_STATUS: {decision}  " if decision else "Missing decision"
            handoff = (
                f"{header}\nLatest QA review {calls[node.id]} for stable ideas I1 and I2.\n"
                "Open issue: clarify the booking confirmation."
            )
        return [Message(role=MessageRole.ASSISTANT, content=handoff)]

    monkeypatch.setattr(AgentNodeExecutor, "execute", fake_agent)
    GraphExecutor(graph).run(
        "Kdze has 4 founders in Budapest with named skills, 10 hours each per week, "
        "a EUR 1,000 test budget, and an interest in local services."
    )

    assert graph.has_cycles
    assert sum(calls.values()) == expected_calls
    for name in ("Koki", "Pepi", "Šomi", "Ceki"):
        assert calls[name] == expected_rounds
    for name in ("Viki", "Anton", "Makarony", "Toške", "Pako", "Pijeki", "Dinča", "Dado", "Miki"):
        assert calls[name] == 1
    assert calls["gospodarice"] == 0
    assert received["Miki"][0].startswith(f"KDZE_REVIEW: {final_status}\n")
    assert f"Latest QA review {expected_rounds}" in received["Miki"][0]
    if expected_rounds == 2:
        assert received["Koki"][1].startswith("KDZE_REVIEW: REVISE\n")
        assert "clarify the booking confirmation" in received["Koki"][1]
