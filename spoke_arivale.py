# TODO: get arivale nodes onto spoke?
# create SPOKE entry points for arivale features
# run topic pagerank to get propagated SPOKE entry vectors?

# 1. get all proteins/metabolites that occur in the arivale data
# 2. create PSEVs for all these proteins/metabolites, as in https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7828077/
# 3. Using the arivale data, 
import json

from neo4j import GraphDatabase
import numpy as np
import pandas as pd

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
        if ',' in uniprot:
            uniprot = uniprot.split(',')[0]
        result = tx.run('MATCH (n:Protein) WHERE n.identifier=$id RETURN ID(n), n.name', id=uniprot.strip())
        id_names.append((uniprot, result.single()))
    return id_names

def get_compound_names(tx, pubchem_chembl_ids):
    """
    pubchem_chembl_ids is a dict of pubchem : chembl ID.
    """
    id_names = []
    for pubchem, chembl in pubchem_chembl_ids.items():
        result = tx.run('MATCH (n:Compound) WHERE n.identifier=$id RETURN ID(n), n.pref_name', id=chembl.strip())
        id_names.append((pubchem, result.single()))
        print(id_names[-1])
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
    pubchem_to_spoke = {x[0]: x[1] for x in metabolite_name_ids}
    uniprot_to_spoke = {x[0]: x[1] for x in protein_name_ids}

    # save protein and metabolite refs
    with open('arivale_metabolites.json', 'w') as f:
        json.dump(metabolite_name_ids, f, indent=1)
    with open('arivale_proteins.json', 'w') as f:
        json.dump(protein_name_ids, f, indent=1)

    # update arivale_mets.xlsx, arivale_prots.xlsx
    arivale_mets = pd.read_excel('../arivale_utils/arivale_mets.xlsx')
    arivale_prots = pd.read_excel('../arivale_utils/arivale_prots.xlsx')
    new_mets = []
    for row in arivale_mets.iterrows():
        row = row[1].copy()
        if np.isnan(row['PUBCHEM']):
            row['CHEMBL'] = ''
            row['IN_SPOKE'] = 0
            row['SPOKE_ID'] = -1
            new_mets.append(row)
            continue
        pubchem_id = str(int(row['PUBCHEM']))
        if row['PUBCHEM'] and pubchem_id in pubchem_to_chembl:
            row['CHEMBL'] = pubchem_to_chembl[pubchem_id].strip()
            if pubchem_id in pubchem_to_spoke:
                row['IN_SPOKE'] = 1
                row['SPOKE_ID'] = pubchem_to_spoke[pubchem_id][0]
            else:
                row['IN_SPOKE'] = 0
                row['SPOKE_ID'] = -1
        else:
            row['CHEMBL'] = ''
            row['IN_SPOKE'] = 0
            row['SPOKE_ID'] = -1
        new_mets.append(row)
    new_mets = pd.DataFrame(new_mets)
    new_mets.to_csv('../arivale_utils/arivale_mets.tsv', index=None, sep='\t')
    new_prots = []
    for row in arivale_prots.iterrows():
        row = row[1].copy()
        uniprot_id = str(row['uniprot'])
        if uniprot_id and uniprot_id in uniprot_to_spoke:
            row['IN_SPOKE'] = 1
            row['SPOKE_ID'] = uniprot_to_spoke[uniprot_id][0]
        else:
            row['IN_SPOKE'] = 0
            row['SPOKE_ID'] = -1
        new_prots.append(row)
    new_prots = pd.DataFrame(new_prots)
    new_prots.to_csv('../arivale_utils/arivale_prots.tsv', index=None, sep='\t')

    # 3. load KG, map proteins and metabolites to KG nodes
    nodes, edges, node_types, edge_types, edge_matrix = spoke_loader.load_spoke('spoke_2021.jsonl.gz', remove_unused_nodes=True, mtx_filename='spoke_2021.mtx.gz')
    g = graph.Graph(nodes, edges, node_types, edge_types, edge_matrix)

    # 4. generate PSEVs for these node IDs
    metabolite_psevs = []
    metabolite_node_ids = []
    metabolite_name_ids_filtered = []
    for x in metabolite_name_ids:
        n = int(x[1][0])
        try:
            topics = g.get_indices_from_ids([n])
            pr_probs_topic = pagerank_sparse.topic_pagerank(edge_matrix, topics, modify_matrix=False, resid=0.85, topic_prob=0.15, n_iters=50)
            np.savetxt('arivale_met_psevs/{0}.txt'.format(x[0]), pr_probs_topic)
            metabolite_psevs.append(pr_probs_topic)
            metabolite_node_ids.append(n)
            metabolite_name_ids_filtered.append(x[0])
        except:
            pass
    #np.savetxt('arivale_metabolite_psev_ids.txt', np.array(metabolite_name_ids_filtered), fmt='%s')

    protein_psevs = []
    protein_node_ids = []
    protein_name_ids_filtered = []
    for x in protein_name_ids:
        n = int(x[1][0])
        try:
            topics = g.get_indices_from_ids([n])
            pr_probs_topic = pagerank_sparse.topic_pagerank(edge_matrix, topics, modify_matrix=False, resid=0.85, topic_prob=0.15, n_iters=50)
            np.savetxt('arivale_prot_psevs/{0}.txt'.format(x[0]), pr_probs_topic)
            protein_psevs.append(pr_probs_topic)
            protein_node_ids.append(n)
            protein_name_ids_filtered.append(x[0])
        except:
            pass
    #np.savetxt('arivale_protein_psev_ids.txt', np.array(protein_name_ids_filtered), fmt='%s')
