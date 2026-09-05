# KdzeDev: local setup and maintenance

KdzeDev is your independently maintained fork at https://github.com/HairyPloper/KdzeDev.
The original project is ChatDev / DevAll. Its Apache-2.0 license, author credits,
historical announcements, and research citations remain attributed to upstream.
Published upstream packages and skills keep their real names; they do not install
this fork. Use this checkout to run KdzeDev.

## ChatGPT Pro and OpenAI access

This application calls the OpenAI API through the Python OpenAI SDK. It supports
Responses and Chat Completions, using `API_KEY` and `BASE_URL` from `.env`.
There is no ChatGPT login or Codex provider in this repository.

Your ChatGPT Pro subscription can be used with Codex by signing in with ChatGPT
in the Codex app, IDE extension, or CLI (`codex login`). That can help you develop
this repository. It does not pay for this application's Platform API calls.
API keys use separate, usage-based Platform billing. See the official
[authentication guide](https://learn.chatgpt.com/docs/auth) and
[plan details](https://learn.chatgpt.com/docs/pricing).

To run the existing agent workflows against OpenAI:

1. Create an [OpenAI Platform API key](https://platform.openai.com/api-keys)
   and configure billing in your Platform account.
2. Put the key in the local `.env` file as `API_KEY`; leave
   `BASE_URL=https://api.openai.com/v1`.
3. In each agent node, select `provider: openai`, a model available to your API
   project in `name`, `api_key: ${API_KEY}`, and `base_url: ${BASE_URL}`.
   The existing `KdzeDev_v1.yaml` uses `gpt-4o`; other examples may use different
   models/providers and require their own configuration.

The variable is named `API_KEY` in this project, not `OPENAI_API_KEY`.
The model is selected per agent node, not globally in `.env`. Keep the key in
`.env` rather than in a workflow file. `.env` is ignored by Git and Docker builds.
Multi-agent runs can make many billable requests; start with a small task.

Using Pro for the workflow engine itself would require a separate integration
with supported Codex tooling and a review of its authentication and execution
model. It is not an environment-variable switch in the current provider.

## Docker on Windows

Run Docker Desktop with Linux containers. You do not need host Python or Node.js
for this route. From PowerShell in the repository root:

```powershell
# Create once; preserve an existing .env.
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
notepad .env
docker compose config --quiet
docker compose up -d --build
docker compose ps
```

Open http://localhost:5173. Backend health is at http://localhost:6400/health/ready
and API documentation is at http://localhost:6400/docs. The UI can start with a
placeholder key, but model execution requires working provider credentials.

The browser sends `/api` and `/ws` requests to Vite on port 5173. Vite proxies
them to `http://backend:6400` inside Docker. Do not use `backend` as a browser
hostname. Compose keeps model credentials on the backend service and waits for
backend health before starting the frontend.

Both published ports bind to localhost. This is a local development setup with
a Vite development server, file execution tools, and no application login.
Add authentication and a production frontend/server configuration before
exposing it to other users.

Useful commands:

```powershell
docker compose logs -f --tail 100
docker compose restart backend
docker compose up -d --build
docker compose down
```

Restart the backend after Python source changes; frontend changes hot reload.
After editing `.env`, run `docker compose up -d --force-recreate backend` to
refresh the container environment. Rebuild when dependencies or Dockerfiles change.
To use another UI port, add `FRONTEND_PORT=5174` to `.env`, run
`docker compose up -d`, and open http://localhost:5174.

The backend mounts this checkout at `/app`, so workflows, generated `WareHouse/`
files, and runtime data persist on your host. The Python environment lives at
`/opt/venv` to avoid mixing Windows and Linux dependencies. Frontend dependencies
live in a container volume. After changing frontend dependencies, rebuild and run
`docker compose up -d --build --renew-anon-volumes frontend`.

Some examples use extra services, MCP servers, model providers, or graphical
programs. Those need separate setup; a running web UI does not make every sample
self-contained. When a model server runs on your Windows host, use
`host.docker.internal` instead of `localhost` in its backend URL.

## Repository map

| Location | Responsibility |
| --- | --- |
| `compose.yml`, `Dockerfile`, `frontend/Dockerfile` | Local containers and dependency installation |
| `server_main.py`, `server/` | FastAPI entry point, HTTP/WebSocket routes, sessions, storage |
| `frontend/` | Vue 3 interface, Vite proxy, English UI text |
| `workflow/` | Graph scheduling and orchestration |
| `runtime/node/agent/providers/` | Model integrations; OpenAI and Gemini |
| `runtime/node/` | Agent, Python, loop, human-input, and other node executors |
| `entity/`, `schema_registry/`, `check/` | Workflow configuration types and validation |
| `yaml_instance/`, `yaml_template/` | Runnable examples and authoring templates |
| `functions/`, `mcp_example/` | Agent tools and MCP integration examples |
| `tests/`, `.github/workflows/` | Regression tests and YAML validation CI |

`yaml_instance/KdzeDev_v1.yaml` is the renamed software-development workflow.
Old links or saved selections using its former filename need to select it again.
English guides are under `docs/user_guide/en/`.

## Maintain the fork

`origin` points to your KdzeDev repository. Work on branches, review diffs, and
commit your changes there. If you want to receive upstream updates, add an
upstream remote once and review incoming changes before merging:

```powershell
git remote add upstream https://github.com/OpenBMB/ChatDev.git
git fetch upstream
git log --oneline HEAD..upstream/main
```

Run existing checks inside the backend container and build the frontend:

```powershell
docker compose exec backend python -m pytest
docker compose exec backend python -c "import runtime; from check.check import load_config; load_config('yaml_instance/KdzeDev_v1.yaml')"
docker compose exec frontend npm run build
```

## Findings from the initial scan

Docker builds, backend health, the frontend API proxy, and the frontend build
passed. The renamed `KdzeDev_v1.yaml` passes actual schema validation. No paid
model request was made; `.env` was created with placeholder credentials.

66 regression tests passed. The seven WebSocket tests cannot complete as a group:
the first test hangs while serializing an unconfigured mock session snapshot.
The affected test and WebSocket implementation are unchanged by the rename.
To run the other tests while this is investigated:

```powershell
docker compose exec backend python -m pytest --ignore=tests/test_websocket_send_message_sync.py
```

Direct schema validation passed for 36 of 41 YAML files with the example `.env`.
The other five need configuration or existing schema repairs:

- `GameDev_with_manager.yaml`: blank agent model/provider configuration.
- `deep_research_executor_sub.yaml`: missing `MODEL_NAME`.
- `demo_mem0_memory.yaml`: missing `MEM0_API_KEY`.
- `subgraphs/react_agent.yaml`: tooling must be a list.
- `subgraphs/reflexion_loop.yaml`: memory store lacks a config block.

The existing `tools/validate_all_yamls.py` launches `python -m check.check`, but
that module has no command-line entry point, so the launcher does not actually
validate the files. Use `load_config` as shown above. Import `runtime` first to
avoid the existing circular import when loading the checker directly.

Do not commit `.env`, generated output, or runtime data. The bundled historical
screenshots illustrate upstream behavior and may still show upstream branding.
