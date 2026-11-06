from fastapi import FastAPI, Query, HTTPException
import sys
sys.path.append('../src')
from db_utils import get_engine
from stats import get_elo_ranking, get_surface_win_rates, get_recent_form

app = FastAPI(title="Tennis Stats API")

engine = get_engine()
VALID_RATING_TYPES = ['Overall', 'Hard', 'Grass', 'Clay']

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/rankings/elo")
def rankings(rating_type: str = 'Overall', limit: int = Query(10, ge=1, le=50)):

    rating_type = rating_type.capitalize()
    valid_ratings = VALID_RATING_TYPES

    #400 - Erro de quem está a aceder
    if rating_type not in valid_ratings:
        raise HTTPException(status_code=400, detail=f"rating type must be one of {valid_ratings}")

    df = get_elo_ranking(rating_type, limit, engine)

    #500 - Erro na função
    if df is None:
        raise HTTPException(status_code=500, detail="Could not get rankings.")

    #404 - Not found
    if df.empty:
        raise HTTPException(status_code=404, detail="No rankings found.")

    #200 - Sucesso (default)
    return df.to_dict(orient="records")

@app.get("/players/{player_id}/surfaces")
def surfaces(player_id: int):
    df = get_surface_win_rates(player_id, engine)

    if df is None:
        raise HTTPException(status_code=500, detail="Could not get surface win rates for the selected player.")
    
    if df.empty:
        raise HTTPException(status_code=404, detail="No matches found for the selected player between 2023-2025.")
    
    return df.to_dict(orient="records")

@app.get("/players/{player_id}/form")
def recent_form(player_id: int, last: int = Query(10, ge=1, le=50)):
    
    df = get_recent_form(player_id, last, engine)
    if df is None:
        raise HTTPException(status_code=500, detail="Could not get recent form for the selected player.")
    
    if df.empty:
        raise HTTPException(status_code=404, detail="No matches found for the selected player between 2023-2025.")
    
    return df.to_dict(orient="records")    
