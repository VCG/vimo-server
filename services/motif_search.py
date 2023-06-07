from services import log
def search_motif(data_server, data_version, auth_token, motif, lim):
    from dotmotif import Motif
    from dotmotif.executors.NeuPrintExecutor import NeuPrintExecutor
    from utils.data_conversion import nodes_and_edges_to_motif_string

    """ Searches for a motif in the hemibrain dataset.
    @param data_server: URL of the server where data is downloaded from, , e.g. 'https://neuprint.janelia.org/'
    @param data_version: Version of the dataset, e.g. 'hemibrain:v1.2.1'
    @param auth_token: NeuPrint authentication token for the data server
    @param motif_specs: dictionary containing the motif specifications
    @param lim: limit of the number of results
    """

    _LOOKUP = {
        "INHIBITS": "ConnectsTo",
        "EXCITES": "ConnectsTo",
        "SYNAPSES": "ConnectsTo",
        "INH": "ConnectsTo",
        "EXC": "ConnectsTo",
        "SYN": "ConnectsTo",
        "DEFAULT": "ConnectsTo",
    }

    _DEFAULT_ENTITY_LABELS = {
        "node": "Neuron",
        "edge": _LOOKUP,
    }

    log.log_sketch(motif, lim)

    executor = NeuPrintExecutor(host=data_server, dataset=data_version, token=auth_token)
    motif_source = nodes_and_edges_to_motif_string(motif, data_server, dataset=data_version, token=auth_token)
    motif = Motif(enforce_inequality=True).from_motif(motif_source)

    cypher = executor.motif_to_cypher(motif=motif,
                                      count_only=False,
                                      static_entity_labels=_DEFAULT_ENTITY_LABELS,
                                      json_attributes=executor.rois)

    # add limit
    if lim:
        cypher += f" LIMIT {lim}"

    return cypher
