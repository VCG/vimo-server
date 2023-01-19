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


def nodes_and_edges_to_motif_string(motif):
    from neuprint import fetch_all_rois
    """
    Converts Query Builder Mongo-esque parameters to dotmotif query format
    """

    print(motif)
    edges = motif['edges']
    nodes = motif['nodes']
    output = "\n "

    rois = fetch_all_rois()
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
