"""Route Kdze's single, bounded QA revision."""

MAX_REVISION_ROUNDS = 1


def _first_status_line(data: str) -> str:
    """Return a normalized first non-empty line without Markdown decoration."""
    for raw_line in data.lstrip("\ufeff").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("- "):
            line = line[2:].strip()
        return line.strip("`*_").strip()
    return ""


def kdze_qa_review(data: str, global_state: dict) -> str:
    """Return one QA revision to Koki, then always continue to costing."""
    state = global_state.setdefault("kdze_qa_review", {})
    reviews = state.get("reviews", 0) + 1
    revisions = state.get("revisions", 0)
    status_line = _first_status_line(data)
    valid = status_line in ("QA_STATUS: READY", "QA_STATUS: NEEDS_CHANGES")

    if status_line == "QA_STATUS: READY":
        decision = "READY"
        instruction = (
            "Proceed to Pijeki. QA planning readiness does not verify demand, "
            "tests, costs, or legal compliance."
        )
    elif revisions < MAX_REVISION_ROUNDS:
        decision = "REVISE"
        revisions += 1
        instruction = (
            "Return to Koki once. Koki, Pepi, and Šomi should address only the "
            "specific in-scope QA issues, then Ceki reviews the revised plan."
        )
    else:
        decision = "LIMIT_REACHED"
        instruction = (
            "Proceed to Pijeki with unresolved issues. The one QA revision has "
            "been used; this is not QA approval."
        )

    if not valid:
        instruction += (
            " The first status line was missing or malformed, so readiness is "
            "unconfirmed."
        )

    state.update(reviews=reviews, revisions=revisions, decision=decision)
    return (
        f"KDZE_REVIEW: {decision}\n"
        f"QA review {reviews}; {revisions}/{MAX_REVISION_ROUNDS} revision used.\n"
        f"{instruction}\n\n"
        f"Latest Ceki handoff:\n{data}"
    )
