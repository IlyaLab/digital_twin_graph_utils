# TODO: get arivale nodes onto spoke?
# create SPOKE entry points for arivale features
# run topic pagerank to get propagated SPOKE entry vectors?

# 1. get all proteins/metabolites that occur in the arivale data
# 2. create PSEVs for all these proteins/metabolites, as in https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7828077/
# 3. Using the arivale data, 

from neo4j import GraphDatabase

import spoke_loader
import pagerank_sparse
import graph

driver = GraphDatabase.driver(uri='bolt://localhost:7687')

def get_protein_names(tx, uniprot_ids):
    id_names = {}
    for uniprot in uniprot_ids:
        result = tx.run('MATCH (n:Protein) WHERE n.identifer=$id RETURN ID(n), n.name', id=uniprot)
        id_names[uniprot] = result.single()
    return id_names

def generate_psevs(node_ids):
    nodes, edges, node_types, edge_types, edge_matrix = spoke_loader.load_spoke('spoke_2021.jsonl.gz', remove_unused_nodes=True, mtx_filename='spoke_2021.mtx')
    g = graph.Graph(nodes, edges, node_types, edge_types, edge_matrix)
    psevs = []
    for n in node_ids:
        topics = g.get_indices_from_ids([n])
        pr_probs_topic = pagerank_sparse.topic_pagerank(edge_matrix, topics, modify_matrix=False, resid=0.85, topic_prob=0.15, n_iters=50)
        psevs.append(pr_probs_topic)
    return psevs

if __name__ == '__main__':
    pass



