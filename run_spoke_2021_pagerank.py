import numpy as np

import spoke_loader
import pagerank_sparse
import graph

if __name__ == '__main__':
    # load graph
    nodes, edges, node_types, edge_types, edge_matrix = spoke_loader.load_spoke('spoke_2021.jsonl.gz', remove_unused_nodes=True, mtx_filename='spoke_2021.mtx')
    # run pagerank
    g = graph.Graph(nodes, edges, node_types, edge_types, edge_matrix)
    pr_probs_all = pagerank_sparse.pagerank(edge_matrix, modify_matrix=False, n_iters=50)
    np.savetxt('pr_spoke_2021.txt', pr_probs_all.flatten())
    pr_sorted = pr_probs_all.flatten().argsort()[::-1]
    top_pr_nodes = [nodes[i] for i in pr_sorted[:50]]
    # find interesting nodes?

    # i got these node ids via a neo4j query
    t2d_name = "type 2 diabetes mellitus"
    # list of topics to use:
    # "metformin"
    # "D-glucose"
    topics = [t2d_name]
    topics = [g.get_indices_from_names(i) for i in topics]
    # run topic pagerank on t2d
    pr_probs_topic = pagerank_sparse.topic_pagerank(edge_matrix, topics, modify_matrix=False, resid=0.85, topic_prob=0.15, n_iters=50)
    np.savetxt('pr_topics_spoke_2021.txt', pr_probs_topic.flatten())
    topics_sorted = pr_probs_topic.flatten().argsort()[::-1]
    top_topic_nodes = [nodes[i] + (pr_probs_topic[i],) for i in topics_sorted[:50]]
    top_topic_genes = [nodes[i] + (pr_probs_topic[i],) for i in topics_sorted[:200] if node_types[nodes[i][2]]=='Gene']
    top_topic_compounds = [nodes[i] + (pr_probs_topic[i],) for i in topics_sorted[:1000] if node_types[nodes[i][2]]=='Compound']
    top_topic_diseases = [nodes[i] + (pr_probs_topic[i],) for i in topics_sorted[:1000] if node_types[nodes[i][2]]=='Disease']

    # try it with a symmetric adjacency matrix? are the results more reasonable?
    edge_matrix_symmetric = spoke_loader.symmetrize_matrix(edge_matrix)
    pr_probs_topic_symmetric = pagerank_sparse.topic_pagerank(edge_matrix_symmetric, topics, modify_matrix=False, resid=0.85, topic_prob=0.15, n_iters=50)
    np.savetxt('pr_topics_spoke_2021.txt', pr_probs_topic_symmetric.flatten())
    topics_sorted = pr_probs_topic_symmetric.flatten().argsort()[::-1]
    top_topic_nodes_pr = [nodes[i] + (pr_probs_topic_symmetric[i][0],) for i in topics_sorted[:50]]
    top_topic_genes = [nodes[i] + (pr_probs_topic_symmetric[i][0],) for i in topics_sorted[:400] if node_types[nodes[i][2]]=='Gene']
    top_topic_anatomy = [nodes[i] + (pr_probs_topic_symmetric[i][0],) for i in topics_sorted[:400] if node_types[nodes[i][2]]=='Anatomy']
    top_topic_protein = [nodes[i] + (pr_probs_topic_symmetric[i][0],) for i in topics_sorted[:400] if node_types[nodes[i][2]]=='Protein']
    top_topic_compounds = [nodes[i] + (pr_probs_topic_symmetric[i][0],) for i in topics_sorted[:2000] if node_types[nodes[i][2]]=='Compound']
    top_topic_diseases = [nodes[i] + (pr_probs_topic_symmetric[i][0],) for i in topics_sorted[:200] if node_types[nodes[i][2]]=='Disease']
    top_topic_foods = [nodes[i] + (pr_probs_topic_symmetric[i][0],) for i in topics_sorted[:2000] if node_types[nodes[i][2]]=='Food']

    import json
    json.dump(top_topic_nodes_pr, open('top_topic_nodes_pr.json', 'w'), indent=2)
    json.dump(top_topic_genes, open('top_topic_genes.json', 'w'), indent=2)
    json.dump(top_topic_compounds, open('top_topic_compounds.json', 'w'), indent=2)
    json.dump(top_topic_diseases, open('top_topic_diseases.json', 'w'), indent=2)
    top_genes = [d[1] for d in top_topic_genes]
    top_diseases = [d[1] for d in top_topic_diseases]
    top_compounds = [d[1] for d in top_topic_compounds]
    top_anatomy = [d[1] for d in top_topic_anatomy]
    np.savetxt('top_t2d_genes.txt', top_genes, fmt='%s')
    np.savetxt('top_t2d_diseases.txt', top_diseases, fmt='%s')
    np.savetxt('top_t2d_compounds.txt', top_compounds, fmt='%s')
    np.savetxt('top_t2d_anatomy.txt', top_anatomy, fmt='%s')
