import json
import os

import uvicorn
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import Request
from starlette.middleware.cors import CORSMiddleware

from services import motif_search, motif_count

from dotenv import load_dotenv

load_dotenv()

app = FastAPI()


# load a env variable from os
origins = json.loads(os.environ['ALLOW_ORIGINS'])

print(origins)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
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


@app.post("/cypher")
async def search_motif(req: Request):
    req = await req.json()
    server = req['server']
    version = req['version']
    motif = req['motif']
    lim = req['lim']
    token = req['token']
    return motif_search.motif_to_cypher(server, version, token, motif, lim)

    try:
        return motif_search.search_motif(data_server, data_version, token, motif, lim)
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
