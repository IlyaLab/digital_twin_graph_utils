# TODO: get arivale nodes onto spoke?
# create SPOKE entry points for arivale features
# run topic pagerank to get propagated SPOKE entry vectors?

# 1. get all proteins/metabolites that occur in the arivale data
# 2. create PSEVs for all these proteins/metabolites, as in https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7828077/
# 3. Using the arivale data, 
import json

from neo4j import GraphDatabase
import numpy as np

import spoke_loader
import pagerank_sparse
import graph

driver = GraphDatabase.driver(uri='bolt://localhost:7687')

def get_protein_names(tx, uniprot_ids):
    """
    uniprot_ids is a list of uniprot ids
    """
    id_names = []
    for uniprot in uniprot_ids:
        result = tx.run('MATCH (n:Protein) WHERE n.identifier=$id RETURN ID(n), n.name', id=uniprot)
        id_names.append((uniprot, result.single()))
    return id_names

def get_compound_names(tx, pubchem_chembl_ids):
    """
    pubchem_chembl_ids is a dict of pubchem : chembl ID.
    """
    id_names = []
    for pubchem, chembl in pubchem_chembl_ids.items():
        result = tx.run('MATCH (n:Compound) WHERE n.identifier=$id RETURN ID(n), n.name', id=chembl)
        id_names.append((pubchem, result.single()))
    return id_names

def generate_psevs(g, edge_matrix, node_ids):
    psevs = []
    for n in node_ids:
        topics = g.get_indices_from_ids([n])
        pr_probs_topic = pagerank_sparse.topic_pagerank(edge_matrix, topics, modify_matrix=False, resid=0.85, topic_prob=0.15, n_iters=50)
        psevs.append(pr_probs_topic)
    return psevs

if __name__ == '__main__':
    # 1. load arivale variables
    with open('../arivale_utils/pubchem_to_chembl.json') as f:
        pubchem_to_chembl = json.load(f)
    with open('../arivale_utils/arivale_uniprot.txt') as f:
        uniprot_ids = [x.strip() for x in f.readlines()]
    # 2. get graph node IDs...
    with driver.session() as session:
        protein_name_ids = session.execute_read(get_protein_names, uniprot_ids)
        metabolite_name_ids = session.execute_read(get_compound_names, pubchem_to_chembl)
    protein_name_ids = [x for x in protein_name_ids if x[1] is not None]
    metabolite_name_ids = [x for x in metabolite_name_ids if x[1] is not None]
    # save output
    with open('arivale_metabolites.json', 'w') as f:
        json.dump(metabolite_name_ids, f)
    with open('arivale_proteins.json', 'w') as f:
        json.dump(protein_name_ids, f)
    # 3. load KG, map proteins and metabolites to KG nodes
    nodes, edges, node_types, edge_types, edge_matrix = spoke_loader.load_spoke('spoke_2021.jsonl.gz', remove_unused_nodes=True, mtx_filename='spoke_2021.mtx')
    g = graph.Graph(nodes, edges, node_types, edge_types, edge_matrix)
    # 4. generate PSEVs for these node IDs
    metabolite_ids = [int(x[1][0]) for x in metabolite_name_ids]
    protein_ids = [int(x[1][0]) for x in protein_name_ids]
    metabolite_psevs = generate_psevs(g, edge_matrix, metabolite_ids)
    protein_psevs = generate_psevs(g, edge_matrix, protein_ids)
    np.savetxt('arivale_metabolite_psevs.txt', np.vstack(metabolite_psevs))
    np.savetxt('arivale_protein_psevs.txt', np.vstack(protein_psevs))



