import json

import uvicorn
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import Request
from requests.exceptions import HTTPError
from starlette.middleware.cors import CORSMiddleware

from services import motif_search, motif_count

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"Hello": "World!"}


@app.get("/401")
def four_zero_one():
    raise HTTPException(status_code=401, detail="401: Unauthorized")


@app.post("/search")
async def search_motif(req: Request):
    req = await req.json()
    motif = req['motif']
    lim = req['lim']
    token = req['token']
    try:
        return motif_search.search_hemibrain_motif(motif, lim, token)
    except HTTPError as e:
        raise HTTPException(status_code=e.response.status_code, detail=json.loads(e.response.text))
    except Exception as e:
        raise HTTPException(status_code=500, detail={'error': str(e)})


@app.get("/count/motif={motif}")
def get_motif_count(motif: str):
    return motif_count.get_absolute(motif)


@app.get("/rel_count/motif={motif}")
def get_relative_motif_count(motif: str):
    return motif_count.get_relative(motif)


def start():
    uvicorn.run("main:app", host="127.0.0.1", port=4242, reload=True, log_level="info", app_dir="/")


if __name__ == "__main__":
    start()
