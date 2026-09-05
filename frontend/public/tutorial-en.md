# KdzeDev guide

Build your team in the workflow editor, then open Launch to run it.

## 1. Your business idea team

Select **Kdze_new_business_idea** from the workflow list.

The goal is to help a group of friends find a business idea for their planned company, **Kdze**.

**Viki → Anton → Makarony → Toške → Pako → Koki → Pepi → Šomi → Ceki → Pijeki → Dinča → Dado → Miki**

Viki writes the founder brief. Anton finds problems. Makarony suggests ideas.
Toške identifies customers. Pako checks feasibility. Koki plans the simplest
technical setup. Pepi outlines the customer experience. Šomi clarifies the
offer and language needs. Ceki defines quality checks. Pijeki estimates costs.
Dinča challenges assumptions. Dado flags legal questions for the pilots.
Miki chooses a candidate and proposes a seven-day test that accounts for those questions.

At launch, describe your skills, interests, available time, location, and budget.
Unknown details should stay marked as unknown. The team has no research tools
configured, so treat customer demand and financial estimates as hypotheses.

## 2. Create nodes

Give each node a unique ID, select its type, and add a short description.
Mark the first node as a start node and the final node as an end node.
For this team, Viki starts and Miki ends.

### Agent node

An agent calls a language model. Use these settings for the current team:

| Field | Value |
| --- | --- |
| ID | The teammate's name |
| Type | agent |
| Name | gpt-4o (the model name) |
| Provider | OpenAI |
| Base URL | ${BASE_URL} |
| API Key | ${API_KEY} |
| System Prompt | The teammate's task and expected handoff |
| Context Window | Leave at the current default for your first test |
| Log Output | Enabled |

Keep the real API key in the backend's `.env` file.
Tools, thinking, memories, skills, and custom retry settings are optional.
The current team does not need them for its first run.

### Human node

Pause for a person's input, such as approval or revisions.

### Python node

Run Python code in the workflow workspace inside the backend container.

### Passthrough node

Forward messages without calling a model.

### Literal node

Supply fixed text, such as shared instructions, without calling a model.

### Loop counter node

Limit how many times a loop repeats.

### Loop timer node

Limit a loop by elapsed time.

### Subgraph node

Run another workflow file. Your current team uses one workflow.

## What is an edge

An edge connects an upstream node to a downstream node.
Connect each person to the next person in the order above.
Enable **Trigger** and **Carry Data** so the next teammate runs and receives the previous handoff.

Keep each handoff concise and include the founder constraints and findings the next person needs.

## Edge condition

A condition decides whether an edge is followed, using keywords or a function.
Leave conditions empty for the team's first sequential run.

## 3. Launch

Save the workflow and open Launch. Select your workflow and enter the founder brief.
Start the run and follow the node outputs. Review Miki's recommendation and test plan
before deciding which idea to pursue.

The pixel characters belong to the visualization and do not require model calls.
Workflow files hold agent behavior; saved visual layouts are stored separately.

## 4. Saving and troubleshooting

Workflow definitions are saved in `yaml_instance/`. Visual layouts are stored in
`data/vuegraphs.db`. Generated files are stored in `WareHouse/`.

If you edit YAML outside the app, reopen or reload the workflow.
If credentials change, recreate the backend container:

```powershell
docker compose up -d --force-recreate backend
```

For connection errors, check that both containers are running.
For model errors, check the model name, provider credentials, and error shown in the run log.
