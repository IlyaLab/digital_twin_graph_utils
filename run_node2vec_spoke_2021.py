# TODO: try this with a smaller graph?
from node2vec import random_walks, run_word2vec
import spoke_loader

import numpy as np
from scipy import sparse
import scipy.io
import umap

# load graph
if __name__ == '__main__':
    nodes, edges, node_types, edge_types, edge_matrix = spoke_loader.load_spoke('spoke_2021.jsonl.gz', remove_unused_nodes=True)
    edge_matrix = scipy.io.mmread('spoke_2021.mtx.gz')
    print('matrix loaded')
    edge_matrix = spoke_loader.symmetrize_matrix(edge_matrix)
    edge_matrix = sparse.lil_matrix(edge_matrix)
    print('calculating random walks...')
    walks = random_walks(edge_matrix.rows, r=10, l=50, verbose=True)
    n2v_model = run_word2vec(walks, 8, 50)
    n2v_model.save('spoke_2021_node2vec_gensim_50')
    um = umap.UMAP()
    um.fit_transform(n2v_model.wv.vectors)
    np.savetxt('spoke_umap.txt', um.embedding_)
    # make a 2d plot of spoke nodes, colored by type
    nodes_types = [n[2] for n in nodes]
    # plot using plotly?
    import plotly.express as px
    fig = px.scatter(x=um.embedding_[:, 0], y=um.embedding_[:,1], hover_data=[[(n[1], node_types[n[2]]) for n in nodes]], color=[node_types[n[2]] for n in nodes])
    fig.update_traces(marker=dict(size=1))
    html = fig.to_html()
    with open('spoke.html', 'w') as f:
        f.write(html)
    np.savetxt('spoke_small_nodes.txt', np.array([[str(x) for x in n] for n in nodes]), fmt='%s', delimiter='\t')

