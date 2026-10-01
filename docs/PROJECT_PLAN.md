# Tennis Stats API — Project Plan

## Goal

Build a complete, portfolio-quality system around real ATP match data:

**ingest → store → process → expose → visualize**

The final product answers the questions fans and analysts actually ask (surface performance, head-to-head, recent form, player strength) through a REST API I designed and built, backed by a SQL Server database, with a custom Elo rating engine as the centrepiece and a dashboard on top.

---

## Progress

- [x] Phase 0 — Setup
- [x] Phase 1 — Explore the data
- [ ] Phase 2 — Database design
- [ ] Phase 3 — Ingestion pipeline
- [ ] Phase 4 — Stats layer
- [ ] Phase 5 — Elo engine
- [ ] Phase 6 — API
- [ ] Phase 7 — Quality
- [ ] Phase 8 — Dashboard

Estimated effort: ~40–65 sessions of 45 minutes (roughly 2–3 months).

---

## Final Deliverable

- **SQL Server database** with tables I designed (`Players`, `Tournaments`, `Matches`, `EloRatings`)
- **Ingestion pipeline** that loads ATP data and can be re-run without duplicating data
- **Stats layer**: surface win rates, head-to-head, recent form
- **Elo rating engine** written in pure Python, processing all matches chronologically
- **REST API (FastAPI)** with Swagger docs, proper status codes, and input validation
- **Dashboard (Streamlit)** consuming my own API
- **Engineering quality**: modules, logging, error handling, automated tests, Git with feature branches, full README

### Planned endpoints

| Method | Endpoint | Returns |
|---|---|---|
| GET | `/players/{id}` | Player profile and career stats |
| GET | `/players/{id}/surfaces` | Win rate by surface (clay, grass, hard) |
| GET | `/players/{id}/form?last=10` | Recent form (last N matches) |
| GET | `/h2h?player1={id}&player2={id}` | Head-to-head record and match history |
| GET | `/rankings/elo?surface=` | Elo ranking, overall or per surface |

---

## Data Source

- **Source:** Jeff Sackmann's `tennis_atp` repository on GitHub — historical ATP match data, one CSV file per season.
- **License:** Creative Commons BY-NC-SA — fine for a non-commercial portfolio project, attribution required.
- **Approach:** static data. Load a defined set of seasons; the pipeline stays re-runnable so more seasons can be added later.

---

## Phases

Each phase ends with something working and committed, on its own branch. No moving to the next phase until the current one works and I can explain it.

### Phase 0 — Setup
- Repo, virtual environment, `.gitignore`, `requirements.txt`
- Folder structure: `src/`, `data/`, `notebooks/`, `tests/`, `docs/`
- README skeleton and this plan

### Phase 1 — Explore the data
- Download a few seasons of match CSVs
- Explore in a notebook: which columns matter, how players are identified, data quality issues (missing values, walkovers, retirements)
- Output: a short list of decisions that feed the database design

### Phase 2 — Database design
- Design `Players`, `Tournaments`, `Matches` tables: keys, types, relationships
- Create them in SQL Server
- Output: a documented schema

### Phase 3 — Ingestion pipeline
- Read CSVs → clean with pandas → load into SQL Server
- Idempotent: re-running must not create duplicates
- Error handling and logging

### Phase 4 — Stats layer
- Functions for surface win rates, head-to-head, recent form
- Each result verified by hand against a known case

### Phase 5 — Elo engine
- Implement the Elo rating algorithm
- Process all matches in chronological order
- Store rating history (overall, optionally per surface)
- Sanity check against real-world rankings

### Phase 6 — API
- FastAPI endpoints on top of Phases 4 and 5
- Path and query parameters, validation, proper status codes (200, 400, 404)
- Auto-generated Swagger docs at `/docs`

### Phase 7 — Quality
- Automated tests with `pytest`
- Logging instead of `print`
- Consistent error handling across modules
- Finished README: setup, how to run, example API calls, data attribution

### Phase 8 — Dashboard
- Streamlit app that consumes my own API (not the database directly)
- Player page, head-to-head comparison, Elo ranking view

---

## Working Rules

1. I write the code; Claude reviews, asks questions, and explains concepts.
2. Try first, read the error and the docs, and time-box being stuck (15–20 minutes) before asking.
3. A phase is done when it works and I can explain it without notes.
4. Small, descriptive commits; one branch per phase, merged when the phase is done.
5. Finished and solid beats ambitious and half-done.
