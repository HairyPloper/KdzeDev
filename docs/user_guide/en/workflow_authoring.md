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

Set `type: agent` and configure the model under `config`:
`name: gpt-4o`, `provider: openai`, `base_url: ${BASE_URL}`,
and `api_key: ${API_KEY}`. Put the agent's instructions in `role`.
The UI labels `role` as **System Prompt**.

Keep credentials in `.env`. Variable resolution uses root-level `vars` first,
then environment variables, then values loaded from `.env`.
Recreate the backend container after changing its environment.

## Connecting the team

The current order is Viki → Anton → Makarony → Toške → Pako → Pijeki → Dinča → Dado → Miki.
Viki is the start node; Miki is the end node.

Each connection has `from`, `to`, `trigger: true`, and `carry_data: true`.
No edge conditions are needed for this sequence. Each person should pass along
the founder constraints and findings needed by the next person.

## Validate and run

Validate saved workflow files without calling a model:

```powershell
docker compose exec backend python -m tools.validate_all_yamls
```

Reopen the workflow in the editor after external YAML edits, then use Launch
to enter the task and run it. Configuration validation checks structure;
a successful model call also requires usable API credentials.

## Reference

- [Web UI guide](web_ui_guide.md)
- [Agent nodes](nodes/agent.md)
- [Execution logic](execution_logic.md)
- [Memory](modules/memory.md)
- [Tools](modules/tooling/README.md)
- [Schema API](config_schema_contract.md)
