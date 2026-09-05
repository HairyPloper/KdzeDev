# KdzeDev

A personal workspace for building and running teams of AI agents in a visual editor.

## Start with Docker

1. Install Docker Desktop and use Linux containers.
2. Copy `.env.example` to `.env` if you do not already have one.
3. Set `API_KEY` in `.env` to your OpenAI API key.
4. From the repository folder, run:

```powershell
docker compose up -d --build
```

Open [KdzeDev](http://localhost:5173). API credentials are needed when you run agents.
See [setup and maintenance](docs/SETUP.md) for restart commands and storage details.

## Business idea team

Open `Kdze_new_business_idea` in the editor. The team helps a group of friends
find a business idea for their planned company, **Kdze**, and uses `gpt-4o`:

| Agent | Task |
| --- | --- |
| Viki | Summarize the founders' goals and constraints |
| Anton | Find customer problems |
| Makarony | Suggest business ideas |
| Toške | Identify potential customers |
| Pako | Check practicality and shortlist ideas |
| Koki | Plan the simplest backend or operational setup |
| Pepi | Outline frontend, UI/UX, and customer touchpoints |
| Šomi | Clarify the offer and identify language needs |
| Ceki | Define QA checks for the pilot |
| Pijeki | Estimate costs and revenue |
| Dinča | Challenge assumptions and identify risks |
| Dado | Review legal questions and requirements for each pilot |
| Miki | Recommend an idea and a seven-day validation plan |

At launch, describe your skills, interests, location, time, and budget.
The team passes its findings along in the order above. Its recommendations are
hypotheses to test with real customers; this workflow has no web research tools configured.

Edit the team in the UI or in
[yaml_instance/Kdze_new_business_idea.yaml](yaml_instance/Kdze_new_business_idea.yaml).

## Guides

- The **Tutorial** page in the app explains nodes, connections, and launching.
- [English reference](docs/user_guide/en/index.md) covers the editor and runtime.

## License

[Apache License 2.0](LICENSE).
