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
API usage has separate billing from ChatGPT subscriptions. The model is chosen
in each agent's configuration; the business idea team uses `gpt-4o`.

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
