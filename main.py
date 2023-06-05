import json
import os

import uvicorn
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import Request
from starlette.middleware.cors import CORSMiddleware

from services import motif_search, motif_count

from dotenv import load_dotenv

from utils.data_conversion import parse_node_fields, parse_roi_fields, parse_edge_fields, get_wildcard

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
    return motif_search.search_motif(server, version, token, motif, lim)

@app.get("/count/motif={motif}")
def get_motif_count(motif: str):
    return motif_count.get_absolute(motif)


@app.get("/rel_count/motif={motif}")
def get_relative_motif_count(motif: str):
    return motif_count.get_relative(motif)


@app.post("/fetch_node_fields")
async def fetch_node_fields(req: Request):
    from neuprint import Client, fetch_custom, fetch_all_rois
    req = await req.json()
    server = req['server']
    version = req['version']
    token = req['token']
    client = Client(server, dataset=version, token=token)

    neuron_types_query = 'MATCH(n:Neuron) WHERE EXISTS(n.type) RETURN DISTINCT n.type'
    neuron_attributes_query = "MATCH (n: Neuron) UNWIND keys(n) AS property WITH DISTINCT property, apoc.meta.type(n[property]) AS type WHERE type <> 'PointValue' RETURN property, type"
    cell_body_fibers_query = "MATCH(n:Neuron) WHERE n.cellBodyFiber <> 'null' RETURN DISTINCT n.cellBodyFiber"

    neuron_types = fetch_custom(neuron_types_query)['n.type'].values.tolist()
    neuron_types_with_wildcard = get_wildcard(neuron_types)
    cell_body_fibers = fetch_custom(cell_body_fibers_query)['n.cellBodyFiber'].values.tolist()

    neuron_attributes = fetch_custom(neuron_attributes_query)
    allRois = fetch_all_rois()

    node_fields = {}
    for property, type in neuron_attributes.itertuples(index=False):
        if property == "type":
            node_fields[property] = parse_node_fields(property, type, neuron_types_with_wildcard)
        elif property == "cellBodyFiber":
            node_fields[property] = parse_node_fields(property, type, cell_body_fibers)
        else:
            if parse_node_fields(property, type):
                node_fields[property] = parse_node_fields(property, type)

    for roi in allRois:
        if roi not in node_fields.keys():
            node_fields[roi] = parse_roi_fields(roi)

    return node_fields

@app.post("/fetch_edge_fields")
async def fetch_edge_fields(req: Request):
    from neuprint import Client, fetch_all_rois
    req = await req.json()
    server = req['server']
    version = req['version']
    token = req['token']
    client = Client(server, dataset=version, token=token)
    allRois = fetch_all_rois()

    edge_fields = {
        "weight": {
            "label": "weight",
            "type": "number",
            "operators": ["greater", "less", "equal"],
            "valueSources": ["value"],
        }
    }
    for roi in allRois:
        edge_fields[roi] = parse_edge_fields(roi)

    return edge_fields
def start():
    uvicorn.run("main:app", host="127.0.0.1", port=4242, reload=True, log_level="info", app_dir="/")


if __name__ == "__main__":
    start()
