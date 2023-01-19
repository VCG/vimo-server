
def search_hemibrain_motif(data_server, data_version, auth_token, motif, lim):

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

    executor = NeuPrintExecutor(host=data_server, dataset=data_version, token=auth_token)
    motif_source = nodes_and_edges_to_motif_string(motif)
    motif = Motif(enforce_inequality=True).from_motif(motif_source)
    results = executor.find(motif=motif, limit=lim)
    return results.to_dict('records')
