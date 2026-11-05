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

## Open issues
- 48 players have no `name_last`, but the schema defines it as NOT NULL. The load will fail until this is resolved (make the column nullable, or drop these players if none appear in matches).
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

# Phase 4 — Stats Layer: Decisions

## Structure
- Stats functions live in `src/stats.py`: `get_surface_win_rates`, `get_head_to_head`, `get_head_to_head_summary`, `get_recent_form`
- Each function answers one question and will back one API endpoint in Phase 6

## SQL vs pandas
- Filtering, joining, and aggregating are done in SQL (e.g. `GROUP BY surface`), and results are loaded with `pd.read_sql`, because the data already lives in the database and SQL is built for this
- Python handles what SQL makes awkward, or what doesn't need the database at all
- `get_head_to_head_summary` is a separate, pure-pandas function: it receives the match list and counts wins (`value_counts` on `winner_id`), so it needs no database and is easy to test

## Which matches count
- Walkovers (`is_wo = 1`) are excluded from every stat: they were never played
- Retirements are counted: a real (partial) match was played and there is a real winner (e.g. Cincinnati 2025 final, Alcaraz vs Sinner, `5-0 RET`, counts as a win)

## Query safety
- All queries use bound parameters (`:player_id`, `:last` with `params=`), never f-strings, to prevent SQL injection once values come from API callers

## Ordering
- Matches are ordered by `tourney_date`, then `match_num`, because all matches in a tournament share the tournament's start date
- Assumption: `match_num` follows round order within a tournament (verified on the 2023 Australian Open, R128 → F; not checked for round-robin or Davis Cup formats). The Elo engine relies on the same assumption

## Return values
- `None` means a step failed (connection or query error) → the API will return 500
- An empty DataFrame means the query worked but found nothing (no matches, or unknown player) → the API will return 404
- `get_head_to_head_summary` returns plain Python `int`s in a dictionary, so it serialises to JSON directly

## Verification
- `get_surface_win_rates` matches an independent SQL query run in SSMS
- Head-to-head Alcaraz vs Sinner (2023–2025): 8–4 in 12 matches, matching a hand count of the match list
- `get_recent_form` matches the same query run in SSMS

## Notes for Phase 6
- Validate `last` in the API (e.g. between 1 and 50) and return 400 for invalid values

# Phase 5 — Elo Engine: Decisions

## Rating rules
- Every player starts at 1500 the first time they appear
- Fixed K = 32 for every match, chosen for simplicity and testability; a K that shrinks with matches played is a possible later improvement
- Expected score: E_A = 1 / (1 + 10^((R_B − R_A) / 400))
- Update: winner gains K × (1 − E_winner); the loser loses the same amount

## Which matches count
- Walkovers are excluded (never played), retirements are counted (real match, real winner), consistent with the Phase 4 stats

## Rating types
- One overall rating, plus one rating per surface (Hard, Clay, Grass)
- Each match updates the overall rating and the rating for its surface
- Matches in tournaments without a surface (15 tournaments) update only the overall rating

## Order
- Matches are processed in chronological order: `tourney_date`, then `match_num` (same assumption as Phase 4)

## Storage
- Full history in `EloRating`: one row per player, per match, per rating type, storing the rating after the match
- The rating before a match is the player's previous row (e.g. with `LAG()`), so it is not stored
- Natural key (`player_id`, `match_id`, `rating_type`) protected by a UNIQUE constraint; `rating_type` restricted by a CHECK constraint
- Ratings stored as `DECIMAL(7,2)` to avoid accumulating rounding errors

## Pipeline
- Elo code lives in `src/elo.py`, separate from ingestion: ingestion moves data, Elo computes new data from it
- Elo runs as the last step of `run_ingestion`, reading matches from the database (it needs the `match_id`s generated by SQL Server)
- `EloRating` is cleared first in `clear_tables`, since it references `TennisMatch`, and ratings are recomputed on every run

## Known limitations
- The data starts in January 2023, so every player starts at 1500 at that point; ratings in the first months are a warm-up and less reliable
- Surface ratings settle more slowly than the overall rating, especially on grass (short season)

## Implementation
- `src/elo.py`: `expected_score`, `update_ratings`, `compute_elo`, `read_elo_matches`
- `update_ratings` raises `ValueError` on invalid input instead of returning None: it is a pure calculation, so bad input is a bug in the caller and should fail loudly
- Ratings are kept at full precision during the calculation; rounding happens only on storage (DECIMAL(7,2)) and display
- `compute_elo` sorts its input by `tourney_date` and `match_num` itself, so its correctness doesn't depend on the caller
- `compute_elo` expects only played matches; excluding walkovers is the job of the extract step (`read_elo_matches`, `is_wo = 0`)
- Current ratings live in dictionaries during the loop (`player_id → rating`, and one dictionary per surface); the history is collected in a list of rows and turned into a DataFrame at the end
- Elo runs as step 5 of `run_ingestion`, after the loads, reusing `load_table`; `clear_tables` deletes `EloRating` first

## Ranking
- `get_elo_ranking(rating_type, limit, engine)` in `stats.py` returns each player's latest rating of the given type (via `ROW_NUMBER() OVER (PARTITION BY player_id ...)`), highest first
- All players are included, active or not: a player who stopped playing keeps his last rating (e.g. Jack Draper, last match August 2025, ranked #6). An activity filter is a possible later improvement

## Verification
- `update_ratings` reproduces the hand calculations: +4.8 (favourite wins), +16 (equal players), +27.2 (upset)
- `compute_elo` tested on small hand-made DataFrames: rating carried between matches, shuffled input gives identical results, surface ratings independent from overall
- Full data: 8,944 played matches → 35,670 rating rows (17,888 overall + 17,782 surface; 53 matches without a surface update only the overall rating)
- Running the pipeline twice gives the same counts
- Full rebuild from `schema.sql` followed by the pipeline reproduces all four tables
- Sanity check: the overall top 10 (Sinner, Alcaraz, Djokovic, Zverev, Auger-Aliassime, Draper, Fritz, De Minaur, Bublik, Musetti) matches the expected elite for late 2025. Sinner ranks above Alcaraz, unlike the official ATP year-end ranking, because Elo measures results against opponents' strength rather than ranking points

## Notes for later phases
- The CSV files are not in the repository (`data/*.csv` is ignored), so a fresh clone has no data: the README must explain where to download them and where to put them (Phase 7)
- The orchestrator could check the read step before the build step, to stop with one clear error instead of a cascade