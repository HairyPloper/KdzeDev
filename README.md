# KdzeDev

KdzeDev is a self-hosted workspace for designing and running teams of AI
agents. Workflows are built as visual graphs: each node has a focused task, and
connections pass results between agents. Workflow definitions remain readable
YAML files, while Docker provides a repeatable local environment.

The project is intended as a personal foundation that can be simplified,
extended, and managed independently. A model provider can be configured once
for the whole application and overridden for individual agents when needed.

## Start with Docker

Install Docker Desktop and use Linux containers. Then copy the example
configuration:

```powershell
Copy-Item .env.example .env
```

Open `.env` and configure these values for your model provider:

- `MODEL_PROVIDER`
- `MODEL_NAME`
- `BASE_URL`
- `API_KEY`

Build and start the application from the repository folder:

```powershell
docker compose up -d --build
```

Open [KdzeDev](http://localhost:5173). Provider usage, credits, and rate limits
are controlled by the account associated with the configured API key.

For restart commands, configuration examples, and maintenance instructions,
see [Setup and maintenance](docs/SETUP.md).

## Repository layout

| Path | Purpose |
| --- | --- |
| `frontend/` | Visual workflow editor and launch interface |
| `yaml_instance/` | Saved workflow definitions |
| `functions/` | Runtime functions and edge processors |
| `data/vuegraphs.db` | Local application data used by Docker |
| `WareHouse/` | Generated run artifacts |
| `logs/` | Runtime logs |

Application data stays on the local machine through Docker-mounted folders.
Keep `.env` private because it contains API credentials.

## Included example

`Kdze_new_business_idea` is included as an example of a multi-role workflow.
It can be opened, edited, and launched from the UI; its definition is stored in
[yaml_instance/Kdze_new_business_idea.yaml](yaml_instance/Kdze_new_business_idea.yaml).

## Documentation

- The in-app **Tutorial** introduces nodes, connections, and workflow runs.
- [English user guide](docs/user_guide/en/index.md) documents the editor and runtime.
- [Workflow authoring](docs/user_guide/en/workflow_authoring.md) explains YAML structure and execution behavior.
- [Setup and maintenance](docs/SETUP.md) covers Docker, storage, and configuration.

## License

[Apache License 2.0](LICENSE)
