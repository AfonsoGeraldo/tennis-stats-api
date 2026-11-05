from fastapi import FastAPI
import sys
sys.path.append('../src')
from db_utils import get_engine
from stats import get_elo_ranking 

engine = get_engine()

app = FastAPI(title="Tennis Stats API")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/rankings/elo")
def rankings(rating_type: str = 'Overall', limit: int = 10):
    df = get_elo_ranking(rating_type, limit, engine)
    return df.to_dict(orient="records")
