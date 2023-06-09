import json
import os

import uvicorn
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import Request
from starlette.middleware.cors import CORSMiddleware


from dotenv import load_dotenv

from utils.data_conversion import parse_node_fields, parse_roi_fields, parse_edge_fields, get_wildcard

load_dotenv()
# have to load the dot env before importing the next line as the logging
# code is looking for an possible value in the .env file in order to start
# the logging.

from services import motif_search, motif_count

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
    neuron_classes_query = 'MATCH(n:Neuron) WHERE EXISTS(n.class) RETURN DISTINCT n.class'
    neuron_birthtime_query = 'MATCH(n:Neuron) WHERE EXISTS(n.birthtime) RETURN DISTINCT n.birthtime'
    neuron_somaSide_query = 'MATCH(n:Neuron) WHERE EXISTS(n.somaSide) RETURN DISTINCT n.somaSide'
    neuron_entryNerve_query = 'MATCH(n:Neuron) WHERE EXISTS(n.entryNerve) RETURN DISTINCT n.entryNerve'
    neuron_exitNerve_query = 'MATCH(n:Neuron) WHERE EXISTS(n.exitNerve) RETURN DISTINCT n.exitNerve'
    neuron_hemilineage_query = 'MATCH(n:Neuron) WHERE EXISTS(n.hemilineage) RETURN DISTINCT n.hemilineage'
    neuron_longTract_query = 'MATCH(n:Neuron) WHERE EXISTS(n.longTract) RETURN DISTINCT n.longTract'
    neuron_modality_query = 'MATCH(n:Neuron) WHERE EXISTS(n.modality) RETURN DISTINCT n.modality'
    neuron_origin_query = 'MATCH(n:Neuron) WHERE EXISTS(n.origin) RETURN DISTINCT n.origin'
    neuron_predictedNt_query = 'MATCH(n:Neuron) WHERE EXISTS(n.predictedNt) RETURN DISTINCT n.predictedNt'
    neuron_serialMotif_query = 'MATCH(n:Neuron) WHERE EXISTS(n.serialMotif) RETURN DISTINCT n.serialMotif'
    neuron_somaNeuromere_query = 'MATCH(n:Neuron) WHERE EXISTS(n.somaNeuromere) RETURN DISTINCT n.somaNeuromere'
    neuron_somaSide_query = 'MATCH(n:Neuron) WHERE EXISTS(n.somaSide) RETURN DISTINCT n.somaSide'
    neuron_subclass_query = 'MATCH(n:Neuron) WHERE EXISTS(n.subclass) RETURN DISTINCT n.subclass'
    neuron_systematicType_query = 'MATCH(n:Neuron) WHERE EXISTS(n.systematicType) RETURN DISTINCT n.systematicType'
    neuron_target_query = 'MATCH(n:Neuron) WHERE EXISTS(n.target) RETURN DISTINCT n.target'
    
    neuron_types = client.fetch_custom(neuron_types_query)['n.type'].values.tolist()
    neuron_types_with_wildcard = get_wildcard(neuron_types)
    neuron_classes = client.fetch_custom(neuron_classes_query)['n.class'].values.tolist()
    neuron_classes_with_wildcard = get_wildcard(neuron_classes)
    neuron_birthtimes = client.fetch_custom(neuron_birthtime_query)['n.birthtime'].values.tolist()
    neuron_somaSides = client.fetch_custom(neuron_somaSide_query)['n.somaSide'].values.tolist()
    neuron_entryNerve = client.fetch_custom(neuron_entryNerve_query)['n.entryNerve'].values.tolist()
    neuron_entryNerve_with_wildcard = get_wildcard(neuron_entryNerve)
    neuron_exitNerve = client.fetch_custom(neuron_exitNerve_query)['n.exitNerve'].values.tolist()
    neuron_exitNerve_with_wildcard = get_wildcard(neuron_exitNerve)
    neuron_hemilineage = client.fetch_custom(neuron_hemilineage_query)['n.hemilineage'].values.tolist()
    neuron_hemilineage_with_wildcard = get_wildcard(neuron_hemilineage)    
    neuron_longTract = client.fetch_custom(neuron_longTract_query)['n.longTract'].values.tolist()
    neuron_modality = client.fetch_custom(neuron_modality_query)['n.modality'].values.tolist()
    neuron_origin = client.fetch_custom(neuron_origin_query)['n.origin'].values.tolist()
    neuron_origin_with_wildcard = get_wildcard(neuron_origin)
    neuron_predictedNt = client.fetch_custom(neuron_predictedNt_query)['n.predictedNt'].values.tolist()    
    neuron_somaSide = client.fetch_custom(neuron_somaSide_query)['n.somaSide'].values.tolist()
    neuron_subclass = client.fetch_custom(neuron_subclass_query)['n.subclass'].values.tolist()
    neuron_subclass_with_wildcard = get_wildcard(neuron_subclass)
    neuron_systematicType = client.fetch_custom(neuron_systematicType_query)['n.systematicType'].values.tolist()
    neuron_systematicType_with_wildcard = get_wildcard(neuron_systematicType)
    neuron_target = client.fetch_custom(neuron_target_query)['n.target'].values.tolist()
    neuron_target_with_wildcard = get_wildcard(neuron_target)
    cell_body_fibers = client.fetch_custom(cell_body_fibers_query)['n.cellBodyFiber'].values.tolist()
    
    
    neuron_attributes = client.fetch_custom(neuron_attributes_query)
    allRois = fetch_all_rois(client=client)

    node_fields = {}
    for property, type in neuron_attributes.itertuples(index=False):
        if property == "type":
            node_fields[property] = parse_node_fields(property, type, neuron_types_with_wildcard)
        elif property == "class":
            node_fields[property] = parse_node_fields(property, type, neuron_classes_with_wildcard)
        elif property == "birthtime":
            node_fields[property] = parse_node_fields(property, type, neuron_birthtimes)
        elif property == "n.somaSide":
            node_fields[property] = parse_node_fields(property, type, neuron_somaSides)
        elif property == "entryNerve":
            node_fields[property] = parse_node_fields(property, type, neuron_entryNerve_with_wildcard)
        elif property == "exitNerve":
            node_fields[property] = parse_node_fields(property, type, neuron_exitNerve_with_wildcard)
        elif property == "hemilineage":
            node_fields[property] = parse_node_fields(property, type, neuron_hemilineage_with_wildcard)
        elif property == "longTract":
            node_fields[property] = parse_node_fields(property, type, neuron_longTract)
        elif property == "modality":
            node_fields[property] = parse_node_fields(property, type, neuron_modality)
        elif property == "modality":
            node_fields[property] = parse_node_fields(property, type, neuron_origin_with_wildcard)
        elif property == "cellBodyFiber":
            node_fields[property] = parse_node_fields(property, type, cell_body_fibers)
        elif property == "predictedNt":
            node_fields[property] = parse_node_fields(property, type, neuron_predictedNt)
        elif property == "somaSide":
            node_fields[property] = parse_node_fields(property, type, neuron_somaSide)
        elif property == "subclass":
            node_fields[property] = parse_node_fields(property, type, neuron_subclass_with_wildcard)
        elif property == "systematicType":
            node_fields[property] = parse_node_fields(property, type, neuron_systematicType_with_wildcard)
        elif property == "target":
            node_fields[property] = parse_node_fields(property, type, neuron_target_with_wildcard)
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
    allRois = fetch_all_rois(client=client)

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
