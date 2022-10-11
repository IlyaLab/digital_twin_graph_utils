import numpy as np

import spoke_loader
import pagerank_sparse

if __name__ == '__main__':
    # load graph
    nodes, edges, node_types, edge_types, edge_matrix = spoke_loader.load_spoke('spoke_2021.csv.gz', remove_unused_nodes=True)
    # run pagerank
    pr_probs_all = pagerank_sparse.pagerank(edge_matrix, modify_matrix=False, n_iters=50)
    np.savetxt('pr_spoke_2021.txt', pr_probs_all.flatten())
    pr_sorted = pr_probs_all.flatten().argsort()[::-1]
    top_pr_nodes = [nodes[i] for i in pr_sorted[:50]]
    # find interesting nodes?
    node_id_index = {n[0]: i for i, n in enumerate(nodes)}

    # i got these node ids via a neo4j query
    t2d_id = 38409
    diabetes_id = 1787474
    # list of topics to use:
    # "metformin"
    # "D-glucose"
    topics = [t2d_id]
    topics = [node_id_index[i] for i in topics]
    # run topic pagerank on t2d
    pr_probs_topic = pagerank_sparse.topic_pagerank(edge_matrix, topics, modify_matrix=False, resid=0.85, topic_prob=0.15, n_iters=50)
    np.savetxt('pr_topics_spoke_2021.txt', pr_probs_topic.flatten())
    topics_sorted = pr_probs_topic.flatten().argsort()[::-1]
    top_topic_nodes = [nodes[i] + (pr_probs_topic[i],) for i in topics_sorted[:50]]
    top_topic_genes = [nodes[i] + (pr_probs_topic[i],) for i in topics_sorted[:200] if nodes[i][2]==1]
    top_topic_compounds = [nodes[i] + (pr_probs_topic[i],) for i in topics_sorted[:1000] if nodes[i][2]==5]
    top_topic_diseases = [nodes[i] + (pr_probs_topic[i],) for i in topics_sorted[:1000] if nodes[i][2]==9]

    # try it with a symmetric adjacency matrix? are the results more reasonable?
    edge_matrix_symmetric = spoke_loader.symmetrize_matrix(edge_matrix)
    pr_probs_topic_symmetric = pagerank_sparse.topic_pagerank(edge_matrix_symmetric, topics, modify_matrix=False, resid=0.85, topic_prob=0.15, n_iters=50)
    np.savetxt('pr_topics_spoke_2021.txt', pr_probs_topic_symmetric.flatten())
    topics_sorted = pr_probs_topic_symmetric.flatten().argsort()[::-1]
    top_topic_nodes_pr = [nodes[i] + (pr_probs_topic_symmetric[i][0],) for i in topics_sorted[:50]]
    top_topic_genes = [nodes[i] + (pr_probs_topic_symmetric[i][0],) for i in topics_sorted[:400] if nodes[i][2]==1]
    top_topic_anatomy = [nodes[i] + (pr_probs_topic_symmetric[i][0],) for i in topics_sorted[:400] if nodes[i][2]==11]
    top_topic_protein = [nodes[i] + (pr_probs_topic_symmetric[i][0],) for i in topics_sorted[:400] if nodes[i][2]==12]
    top_topic_compounds = [nodes[i] + (pr_probs_topic_symmetric[i][0],) for i in topics_sorted[:2000] if nodes[i][2]==5]
    top_topic_diseases = [nodes[i] + (pr_probs_topic_symmetric[i][0],) for i in topics_sorted[:200] if nodes[i][2]==9]
    top_topic_foods = [nodes[i] + (pr_probs_topic_symmetric[i][0],) for i in topics_sorted[:2000] if nodes[i][2]==13]

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
