# Phase 1 — Data Exploration: Decisions

## Data
- Source: Jeff Sackmann's `tennis_atp` (`atp_matches_YYYY.csv`, `atp_players.csv`)
- Seasons: 2023, 2024, 2025 — complete seasons only (2026 excluded because it is still in progress)
- Seasons are combined into one DataFrame and sorted by `tourney_date` and `match_num`, so matches are in chronological order (required for Elo)

## Tables and columns

**Tournaments** (built from the match files — there is no separate tournaments file)
- tourney_id (PK), tourney_name, tourney_date, tourney_level, surface

**Matches**
- tourney_id + match_num (composite PK), round, winner_id (FK), winner_rank, loser_id (FK), loser_rank, score, UncompletedMatch

**Players** (from `atp_players.csv`)
- player_id (PK), name_first, name_last, hand, ioc, height
- To consider: `dob` (date of birth), to show player age

## Data checks
- `tourney_id` + `match_num` is unique across all matches → valid primary key for Matches
- 445 tournaments, each with exactly one set of attributes → `tourney_id` is a valid primary key for Tournaments
- Every `winner_id` and `loser_id` exists in `atp_players` → foreign keys from Matches to Players are possible

## Decisions
- Keep all matches; flag incomplete ones instead of deleting them, so each feature (Elo, stats, head-to-head) can decide what to exclude
- Walkovers (`W/O`) and retirements (`RET`) currently share one flag (`UncompletedMatch`) — to revisit in Phase 5, since Elo may need to treat them differently
- Player attributes (hand, height, country) come from `atp_players`, not the match files, to avoid repeating them in every match (normalisation)
- Rank at the time of the match (`winner_rank`, `loser_rank`) stays in Matches, because it changes over time

# Phase 2 — Database Design: Decisions

## Naming
- Table names in singular PascalCase: `Player`, `Tournament`, `TennisMatch` (each row is one entity; `Match` avoided because MATCH is used in SQL Server graph syntax)
- Columns in snake_case, with keys named in full (`player_id`, `tourney_id`) rather than `id`, so joins stay readable and PK/FK names match

## Keys
- `Tournament`: PK `tourney_id`
- `Player`: PK `player_id`
- `TennisMatch`: surrogate PK `match_id` (IDENTITY), plus UNIQUE (`tourney_id`, `match_num`) — one-column PK keeps joins simple, while the unique constraint still protects the natural key
- Foreign keys from `TennisMatch` to `Tournament` (`tourney_id`) and to `Player` (`winner_id`, `loser_id`)

## Columns
- Dates (`tourney_date`, `dob`) stored as `DATE`; conversion from the CSV's numeric format happens in Phase 3
- Two flags, `is_wo` and `is_retirement` (`BIT`, default 0), instead of one, so the Elo engine can treat walkovers and retirements differently
- Nullable columns chosen after checking the data (e.g. ranks, height, dob can be missing)

## Schema
- Defined in `sql/schema.sql`, which is the source of truth: database changes go through the script, never by hand

# Phase 3 — Ingestion Pipeline: Decisions

## Structure
- Extract, transform, and load functions live in `src/ingestion.py`; `src/run_ingestion.py` orchestrates them
- Extract functions only read raw files; each transform function returns a DataFrame shaped exactly like one table
- Every function returns `None` or `False` on failure, and the orchestrator stops at the first failed step
- Run from the project root: `python src/run_ingestion.py`

## Re-run strategy
- Full refresh: all tables are emptied and reloaded on every run, chosen because the data is static and small (~9,000 matches)
- Tables are cleared only after extract and transform succeed, so a failed run never leaves the database empty
- Deletion order: `TennisMatch` first, then `Tournament` and `Player` (children before parents); load order is the reverse
- `TRUNCATE` is not used because SQL Server does not allow it on tables referenced by foreign keys
- The `TennisMatch` identity is reseeded after clearing, so `match_id` restarts on each run
- Clearing runs in a single transaction (`engine.begin()`), so it either fully succeeds or rolls back
- Known limitation: the loads are not in one shared transaction, so a failure mid-load can leave the database partially filled until the next successful run (improvement planned for Phase 7)

## Data handling
- 48 players without `name_last` are dropped in `build_players`. None of them appear in the 2023–2025 matches. If a future season includes such a player, the TennisMatch load will fail on the foreign key, and this decision must be revisited
- 102 players have a `dob` that cannot be parsed; they become NULL. None appear in the 2023–2025 matches
- `tourney_id` widened to `VARCHAR(50)` (in both `Tournament` and `TennisMatch`) because Davis Cup IDs are up to 32 characters

## Schema
- `schema.sql` drops and recreates the database (forcing single-user mode to close open connections), so it can be rerun at any time
- This is acceptable only because it is a local development database

## Verification
- Row counts after loading match the source: 445 tournaments, 9,006 matches, all players minus 48
- Running the pipeline twice gives identical counts, confirming the re-run strategy works