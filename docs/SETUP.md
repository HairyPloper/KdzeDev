# Docker setup and maintenance

## Start

Use Docker Desktop with Linux containers. Host Python and Node.js are not required.

From PowerShell in the repository folder:

```powershell
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
notepad .env
docker compose config --quiet
docker compose up -d --build
docker compose ps
```

Set `API_KEY` in `.env` and keep `BASE_URL=https://api.openai.com/v1`.
Create a key in your [OpenAI API account](https://platform.openai.com/api-keys).
API usage has separate billing from ChatGPT subscriptions. The business idea
team inherits its model settings from `.env`, with optional per-agent overrides.

Open the [web UI](http://localhost:5173). The backend exposes
[health status](http://localhost:6400/health/ready) and
[API documentation](http://localhost:6400/docs).

Both ports bind to localhost. This Compose setup runs the development editor
without an application login and is intended for local use.

## Everyday commands

```powershell
# View logs.
docker compose logs -f --tail 100

# Stop the app.
docker compose down

# Start it again.
docker compose up -d

# Apply changes to .env.
docker compose up -d --force-recreate backend

# Apply Python source changes.
docker compose restart backend

# Rebuild after dependency or Dockerfile changes.
docker compose up -d --build
```

Frontend source changes reload automatically. After changing frontend dependencies,
run `docker compose up -d --build --renew-anon-volumes frontend`.

To change the UI port, set `FRONTEND_PORT=5174` in `.env`, run
`docker compose up -d`, and open http://localhost:5174.

## Global agent settings

Configure all agents from `.env`:

```dotenv
MODEL_PROVIDER=openai
MODEL_NAME=gpt-4o
BASE_URL=https://api.openai.com/v1
API_KEY=your-openai-key
```

`MODEL_PROVIDER` selects the registered client adapter (`openai` or `gemini`).
OpenAI-compatible services such as Groq also use the `openai` adapter.
For Groq, set `MODEL_NAME=llama-3.3-70b-versatile`,
`BASE_URL=https://api.groq.com/openai/v1`, and use your Groq key in `API_KEY`.
See [Groq's compatibility guide](https://console.groq.com/docs/openai).

Each node field overrides its matching global setting independently:

| Agent field | Global default |
| --- | --- |
| `provider` | `MODEL_PROVIDER` (fallback `openai`) |
| `name` | `MODEL_NAME` (fallback `gpt-4o`) |
| `base_url` | `BASE_URL` (otherwise the adapter's built-in endpoint) |
| `api_key` | `API_KEY` (otherwise the adapter's authentication behavior) |

Omitted, empty, or null fields inherit. The business workflow inherits all four.
In the UI, leave these fields empty to inherit, or fill in an override.
For example, to use OpenAI for one agent while the rest use Groq:

```yaml
config:
  provider: openai
  name: gpt-4o
  base_url: https://api.openai.com/v1
  api_key: ${OPENAI_API_KEY}
  role: Your instructions for this agent.
```

Set that separate `OPENAI_API_KEY` in `.env`. Changing only `provider` does not
switch the other three settings; keep the endpoint, model, and credential matched.
Use placeholders for credential overrides, so workflow files contain no secrets.
Global defaults come from the backend environment; root-level YAML `vars` apply
when explicitly referenced with placeholders.

Apply `.env` changes with `docker compose up -d --force-recreate backend` when
no workflow is running, then refresh the UI. Switching defaults does not rewrite
existing explicit node overrides.

## Iteration defaults

Set these positive integers in `.env`:

```dotenv
LOOP_COUNTER_MAX_ITERATIONS=10
ENGINE_MAX_ITERATIONS=100
```

Loop-counter nodes inherit `LOOP_COUNTER_MAX_ITERATIONS` when their
`config.max_iterations` is omitted or `null`. In the UI, leave **Maximum
Iterations** empty to inherit, or enter a number to override it for that node.
Existing explicit values stay local overrides.

`ENGINE_MAX_ITERATIONS` is the separate safety cap for each engine cycle,
including nested cycles. A node override does not override the engine cap.
If a counter needs more than 100 triggers, increase the engine cap as needed.
Neither setting limits the number of agents or repeats a sequential workflow.
The business idea team has one QA gate configured in
`functions/edge_processor/kdze_review.py`. It allows one targeted return through
Koki, Pepi, Šomi, and Ceki. Pijeki, Dinča, and Dado are advisory and never send
the graph backward. The workflow therefore makes 13 model calls normally and
17 when the QA revision is used, excluding provider retries. Leave the engine
cap at 100; increasing it does not increase the QA allowance. A lower engine
cap can stop the workflow before the final handoff.

After editing `.env`, apply it with
`docker compose up -d --force-recreate backend`. Blank, zero, negative, and
non-integer values are rejected when the relevant configuration is loaded.

## Where your work is saved

The repository is mounted into the backend at `/app`, so these files persist on your host:

| Path | Contents |
| --- | --- |
| `yaml_instance/` | Your workflow definitions |
| `data/vuegraphs.db` | SQLite database for saved visual graphs and layouts |
| `WareHouse/` | Generated files and execution artifacts |
| `logs/` | Server logs |
| `.env` | Local provider credentials |

Active execution state is held in server memory. Restarting the backend interrupts
active runs; files already written to disk remain. Back up your workflow files,
database, and outputs if you want to preserve them. Keep credentials out of Git.

## Checks inside Docker

```powershell
docker compose exec backend python -m tools.validate_all_yamls
docker compose exec frontend npm run build
docker compose exec backend python -m pytest --ignore=tests/test_websocket_send_message_sync.py -q
```

Workflow validation does not call a model. The WebSocket test module is excluded
because its existing mock session serialization can hang; the remaining backend
tests can run independently.

## Code map

| Path | Purpose |
| --- | --- |
| `compose.yml`, `Dockerfile`, `frontend/Dockerfile` | Container setup |
| `pyproject.toml`, `uv.lock` | Backend dependencies used by Docker |
| `frontend/` | Visual editor, launch view, English UI, character sprites |
| `server_main.py`, `server/` | HTTP and WebSocket backend |
| `workflow/`, `runtime/` | Scheduling and node execution |
| `entity/`, `schema_registry/`, `check/` | Configuration and validation |
| `functions/` | Tools available to agents |
| `yaml_template/` | Schema reference for authoring |
| `tests/`, `tools/` | Tests and maintenance utilities |

Use the [English reference](user_guide/en/index.md) when extending the editor or runtime.
