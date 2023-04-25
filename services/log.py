import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import time

db = None
if firebase_admin._apps:
    db = firestore.client()
else:
    # Initialize a new app if the app does not exist
    cred = credentials.Certificate('vimo-server-firestore-credentials.json')
    default_app = firebase_admin.initialize_app(cred)
    db = firestore.client()

collection = db.collection('sketches')

def anonymize_properties(properties):
    if properties is None:
        return None
    else:
        return {key: 'hidden' for key in properties}

def anonymize_sketch(sketch):
    # print(sketch)
    res = {'nodes': [], 'edges': [], 'dimension': sketch['dimension']}
    # nodes
    for node in sketch['nodes']:
        res['nodes'].append({
            **node,
            'properties': anonymize_properties(node['properties']),
            'tree': None
        })
    # edges
    for edge in sketch['edges']:
        res['edges'].append({
            **edge,
            'properties': anonymize_properties(edge['properties']),
            'tree': None
        })
    # print(res)
    return res
def log_sketch(motif, lim):
    data = {
        "timestamp": time.time(),
        "sketch": anonymize_sketch(motif),
        "numberOfResults": lim,
    }
    try:
        collection.document().set(data)
    except Exception as e:
        print(e)
