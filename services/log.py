from google.cloud import firestore
import time
import os

db = None
colletion = None
credentials_file = 'vimo-server-firestore-credentials.json'
os.environ['GOOGLE_APPLICATION_CREDENTIALS']=credentials_file

if os.environ.get('VIMO_LOGGING') == 'on':
    db = firestore.Client()
    collection = db.collection('sketches')
    # print(collection)

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
    if os.environ.get('VIMO_LOGGING') == 'on':
        data = {
            "timestamp": time.time(),
            "sketch": anonymize_sketch(motif),
            "numberOfResults": lim,
        }
        try:
            collection.document().set(data)
        except Exception as e:
            print(e)
