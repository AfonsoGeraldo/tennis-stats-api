# Tennis Stats API

> 🚧 Work in progress — see [the project plan](docs/PROJECT_PLAN.md) for current status.

A Python system that turns historical ATP match data into answers: surface performance, head-to-head records, recent form, and a custom Elo rating of player strength — served through a REST API and visualised in a dashboard.

## What it will do

- **Ingest** ATP match data into a SQL Server database
- **Process** it with pandas into player and match statistics
- **Rate** players with a custom Elo engine, processing every match chronologically
- **Expose** the results through a REST API built with FastAPI
- **Visualise** them in a Streamlit dashboard that consumes the API

## Tech stack

- Python (pandas, requests, SQLAlchemy, pyodbc)
- Microsoft SQL Server
- FastAPI *(planned)*
- pytest *(planned)*
- Streamlit *(planned)*

## Project structure

```
tennis-stats-api/
├── data/          # Raw ATP CSVs (not tracked in Git)
├── docs/          # Project plan and documentation
├── notebooks/     # Data exploration
├── src/           # Application code
├── tests/         # Automated tests
├── requirements.txt
└── README.md
```

## Setup

1. Clone the repository
2. Create and activate a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

*More setup and usage instructions will be added as the project develops.*

## Data source and attribution

Match data comes from Jeff Sackmann's [`tennis_atp`](https://github.com/JeffSackmann/tennis_atp) repository, licensed under [Creative Commons Attribution-NonCommercial-ShareAlike 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/). This is a non-commercial portfolio project.
