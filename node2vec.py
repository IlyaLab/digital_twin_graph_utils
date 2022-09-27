# TODO: use an existing library for node2vec?
# which library?
import functools

#from numba import jit
import numpy as np
from scipy import sparse


def random_walks(adj_list, r, l, p=1, q=1, verbose=False):
    """
    Biased random walk starting from node i.
    r = number of walks per node
    l = length of walk
    p and q are probs
    """
    @functools.lru_cache(10000)
    def tr_probs(prev, node):
        """
        node2vec transition probabilities
        returns array of transition probs indexed to neighbors
        """
        neighbors = adj_list[node]
        transition_probs = np.ones(len(neighbors))
        if p == 1 and q == 1:
            return transition_probs/transition_probs.sum()
        prev_neighbors = adj_list[prev]
        # bias
        for i, t in enumerate(neighbors):
            if t == prev:
                transition_probs[i] = 1./p
            elif t not in prev_neighbors:
                transition_probs[i] = 1./q
        transition_probs /= transition_probs.sum()
        return transition_probs
    walks = []
    for start in range(len(adj_list)):
        if verbose and start % 1000 == 0:
            print('Node: ', start)
        for _ in range(r):
            n_walk = 0
            prev_node = None
            node = start
            walk = []
            while n_walk < l:
                n_walk += 1
                walk.append(node)
                neighbors = adj_list[node]
                if prev_node is not None:
                    tr = tr_probs(prev_node, node)
                else:
                    tr = np.ones(len(neighbors))/len(neighbors)
                prev_node = node
                node = np.random.choice(neighbors, p=tr)
            walks.append(walk)
    return walks



if __name__ == '__main__':
    # TODO: try this with a smaller graph?
    import spoke_loader
    # load graph
    nodes, edges, node_types, edge_types, edge_matrix = spoke_loader.load_spoke('spoke.csv', remove_unused_nodes=True)
    edge_matrix = spoke_loader.symmetrize_matrix(edge_matrix)
    edge_matrix = sparse.lil_matrix(edge_matrix)
    adj_sets = [set(row) for row in edge_matrix.rows]
    print('calculating random walks...')
    walks = random_walks(edge_matrix.rows, 1, 10, verbose=True)
