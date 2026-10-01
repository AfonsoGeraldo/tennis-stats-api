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