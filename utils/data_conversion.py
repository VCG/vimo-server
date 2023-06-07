from utils.trie import Trie
def nodes_and_edges_to_networkx(motif):
    import json
    import networkx as nx
    '''
    Converts node and edge string to networkx graph
    @param motif: node and edge string
    @return: directed networkx graph
    '''
    graph = nx.DiGraph()
    motif = json.loads(motif)
    for edge in motif['edges']:
        graph.add_edge(edge['indices'][0], edge['indices'][1])
    return graph


def nodes_and_edges_to_motif_string(motif, dataset, token):
    from neuprint import fetch_all_rois, Client
    """
    Converts Query Builder Mongo-esque parameters to dotmotif query format
    """

    client = Client(server, dataset=dataset, token=token)
    # print(motif)
    edges = motif['edges']
    nodes = motif['nodes']
    output = "\n "

    rois = fetch_all_rois(client=client)
    # First list every edge like A -> B [weight > x]
    for edge in edges:
        edge_str = edge['label']
        if 'properties' in edge and edge['properties'] is not None:
            edge_str += ' ['
            for i, prop in enumerate(list(edge['properties'].items())):
                if i != 0:
                    edge_str += ', '
                array = []
                if prop[0] in rois:
                    array = ["\"" + prop[0] + '.pre"']
                else:
                    array = [prop[0]]
                for i, el in enumerate(array):
                    if i != 0:
                        edge_str += ', '
                    edge_str += el
                    if type(prop[1]) == int or type(prop[1]) == float:
                        edge_str += ' == ' + str(prop[1])
                    elif '$lt' in prop[1]:
                        edge_str += ' < ' + str(prop[1]['$lt'])
                    elif '$gt' in prop[1]:
                        edge_str += ' > ' + str(prop[1]['$gt'])

            edge_str += ']'
        edge_str += ' \n'
        output += edge_str
    # Now list every node property like A['prop'] == True
    for node in nodes:
        node_str = str(node['label']) + '.status = "Traced" \n'
        if 'properties' in node and node['properties'] is not None:
            for prop in list(node['properties'].items()):
                # Special Handling for Wildcard Type Fields
                if prop[0] == 'type' and type(prop[1]) == str and prop[1].endswith('*'):
                    node_str += str(node['label']) + '["' + str(prop[0]) + '"] contains ' + str(prop[1])[:-1] + '\n'
                elif prop[0] == 'type' and '$ne' in prop[1] and prop[1]['$ne'].endswith('*'):
                    node_str += str(node['label']) + '["' + str(prop[0]) + '"] !contains ' + '"' + str(
                        prop[1]['$ne'])[:-1] + '"' + '\n'
                elif type(prop[1]) == bool or type(prop[1]) == int or type(prop[1]) == float:
                    node_str += str(node['label']) + '["' + str(prop[0]) + '"] = ' + str(prop[1]) + '\n'
                elif type(prop[1]) == str:
                    node_str += str(node['label']) + '["' + str(prop[0]) + '"] = ' + '"' + str(prop[1]) + '"' + '\n'
                elif '$lt' in prop[1]:
                    node_str += str(node['label']) + '["' + str(prop[0]) + '"] < ' + str(prop[1]['$lt']) + '\n'
                elif '$gt' in prop[1]:
                    node_str += str(node['label']) + '["' + str(prop[0]) + '"] > ' + str(prop[1]['$gt']) + '\n'
                elif '$ne' in prop[1]:
                    node_str += str(node['label']) + '["' + str(prop[0]) + '"] != ' + '"' + str(
                        prop[1]['$ne']) + '"' + '\n'
        output += node_str.replace("'", "\'")
    return output

def parse_roi_fields(property):
    return {
        "label": property,
        "type": "boolean",
        "operators": ["equal"],
        "valueSources": ["value"],
        "defaultValue": True
    }
def parse_node_fields(property, type, values=None):
    if type in ["FLOAT", "INTEGER"]:
        attrs = {
            "label": property,
            "type": "number",
            "valueSources": ["value"],
            "defaultValue": True
        }
        if property in ['size', 'somaRadius']:
            return {
                **attrs,
                "operators": ["equal", "less", "greater"]
            }
        else:
            return {
                **attrs,
                "fieldSettings": {
                    "valuePlaceholder": "Enter ID",
                },
                "operators": ["equal"]
            }
    else:
        if property in ["type", "birthtime", "class", "someSide", "entryNerve", "exitNerve", "hemilineage", "longTract", "modality", "origin", "predictedNt", "serialMotif", "somaNeuromere", "somaSide", "subclass", "systematicType", "target"]:
            return {
                "label": property,
                "type": "select",
                "fieldSettings": {
                    "showSearch": True,
                    "listValues": values,
                },
                "operators": ["select_equals", "select_not_equals"],
                "valueSources": ["value"],
            }
        elif property == "statusLabel":
            return {
                "label": property,
                "type": "select",
                "fieldSettings": {
                    "listValues": [
                        { "value": "Leaves",
                          "title": "Leaves"
                        },
                        {
                          "value": "Roughly traced",
                          "title": "Roughly traced",
                        },
                        { "value": "Traced",
                          "title": "Traced"
                        },
                    ],
                },
                "operators": ["select_equals"],
                "valueSources": ["value"],
                "defaultValue": "Traced",
            }
        elif property == "cellBodyFiber":
            return {
                "label": property,
                "type": "select",
                "fieldSettings": {
                    "showSearch": True,
                    "listValues": values,
                },
                "operators": ["select_equals"],
                "valueSources": ["value"],
                # "defaultValue": True,
            }
        elif property == "instance":
            return {
                "label": property,
                "fieldSettings": {
                  "valuePlaceholder": "Enter Instance",
                },
                "type": "text",
                "operators": ["equal"],
                "valueSources": ["value"],
                "defaultValue": True,
            }
        elif property in ["hemibrain", "notes", "roiInfo", "status"]:
            return None
        else:
            return None
def parse_edge_fields(property):
    return {
        "label": property,
        "type": "number",
        "operators": ["greater", "less", "equal"],
        "valueSources": ["value"],
    }

def get_wildcard(words):
    trie = Trie()
    for word in words:
        trie.insert(word)

    multi_child_nodes = trie.find_multi_child_nodes()

    result = []
    for multi_child_node in multi_child_nodes:
        if multi_child_node is not None:
            node = multi_child_node
            res = ''
            while node.parent is not None:
                res += node.get_char_in_context()
                node = node.parent
            result.append(res[len(res)::-1])
        else:
            print("No multi-child node found in the Trie.")

    import re
    output = []
    # pattern = '(\d+$)|(_[a-zA-Z]$)|(\d+[a-zA-Z]*\d?[_]?[a-zA-Z]*\d*$)|([a-zA-Z]_[a-zA-Z]$)|([a-zA-Z]$)'
    pattern = '(\d+$)|(_[a-zA-Z]$)|(\d+[a-zA-Z]*\d?[_]?[a-zA-Z]*\d*$)|([a-zA-Z]_[a-zA-Z]$)|([-]$)'
    for r in result:
        match = re.split(pattern, r)
        if len(match[0]) > 1 and match[0] + "*" not in output:
            output.append(match[0] + '*')
    return sorted(words + output)
