# Workflow authoring

Use the visual editor to create and connect nodes. Your current workflow is
[yaml_instance/Kdze_new_business_idea.yaml](../../../yaml_instance/Kdze_new_business_idea.yaml).

## Structure

A workflow has a `graph` block containing:

- `id` and `description`: identify the workflow.
- `initial_instruction`: shared task guidance.
- `nodes`: teammates and their configuration.
- `edges`: connections and message handoffs.
- `start` and `end`: entry and terminal node IDs.

Optional root-level `version` and `vars` fields record the schema version and
substitution variables. See [field specifications](field_specs.md) and the
[generated schema template](../../../yaml_template/design.yaml) for the full configuration.

## Agent settings

Set `type: agent` and put the agent's instructions in `config.role`.
Omit `name`, `provider`, `base_url`, and `api_key` to inherit `MODEL_NAME`,
`MODEL_PROVIDER`, `BASE_URL`, and `API_KEY` from the backend environment.
Empty or null fields also inherit. Set any field explicitly to override just
that setting for one agent, for example `name: gpt-4o`.
The UI labels `role` as **System Prompt**.

Keep credentials in `.env`. Variable resolution uses root-level `vars` first,
then environment variables, then values loaded from `.env`.
Recreate the backend container after changing its environment.
When changing an agent to a different service, configure a matching endpoint,
model, and API key as well. See [global model setup](../../SETUP.md#global-agent-settings).

## Connecting the team

The agent order is Viki → Anton → Makarony → Toške → Pako → Koki → Pepi → Šomi → Ceki → Pijeki → Dinča → Dado → Miki.
Viki is the start node; Miki is the end node.

Each connection has `from`, `to`, `trigger: true`, and `carry_data: true`.
Each person passes along the founder constraints and findings needed by the next person.

The graph is forward-only. Ceki, Pijeki, Dinča, and Dado provide QA, cost, risk,
and legal findings without sending work backward. Every active teammate runs
once, for 13 model calls excluding provider retries.

Some edges use `trigger: false`, `carry_data: true`, and `keep_message: true`.
These context edges do not run a node early. They deliver Viki's factual founder
brief and Pako's canonical finalist definitions directly to later nodes. Miki
therefore receives separate messages from Viki, Pako, Ceki, Pijeki, Dinča, and
Dado instead of relying on one repeatedly summarized handoff. The disconnected
`gospodarice` node has no incoming or outgoing edges and does not run.

## Validate and run

Validate saved workflow files without calling a model:

```powershell
docker compose exec backend python -m tools.validate_all_yamls
```

Reopen the workflow in the editor after external YAML edits, then use Launch.
For this workflow, enter the real team members and skills, shared test budget
and currency, hours available, location/market, resources, interests, and things
to avoid. Replace template text such as `[amount and currency]` with a real value.
The UI rejects command-only prompts and unfilled placeholders; an attached brief
also satisfies the check. Configuration validation checks structure;
a successful model call also requires usable API credentials.

## Reference

- [Web UI guide](web_ui_guide.md)
- [Agent nodes](nodes/agent.md)
- [Execution logic](execution_logic.md)
- [Memory](modules/memory.md)
- [Tools](modules/tooling/README.md)
- [Schema API](config_schema_contract.md)
