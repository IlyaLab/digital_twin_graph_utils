# Using a sparse matrix imported from...

import numpy as np
from scipy import sparse, io


def pagerank(adjacency, probs=None, n_iters=20, resid=0.85, modify_matrix=True):
    """
    Args:
        adjacency - sparse matrix
        probs - array of initial random jump probabilities.
    """
    n_nodes, _ = adjacency.shape
    adjacency = sparse.csr_array(adjacency.astype(bool)).astype(float)
    # set 'sinks' to have random transitions
    out_degrees = adjacency.sum(1)
    # TODO: is there a better way of dealing with sinks than modifying the matrix? probs[zero_indices] = (1/n_nodes)*probs[zero_indices]
    if modify_matrix:
        adjacency[out_degrees == 0, :] = np.ones(n_nodes)
        adjacency.setdiag(0)
        out_degrees = adjacency.sum(1)
    transitions = adjacency*(1/out_degrees[:, np.newaxis])
    transitions = transitions.T
    transitions = sparse.csc_array(transitions)
    # initial rank: all equal
    # adjacency[i, j] indicates an edge from i to j 
    if probs is None:
        probs = np.ones(n_nodes)/n_nodes
        probs = probs[:, np.newaxis]
    # run power iterations
    for _ in range(n_iters):
        probs = resid*transitions.dot(probs) + (1 - resid)*(1/n_nodes)
        probs /= probs.sum()
    return probs


def topic_pagerank(adjacency, topics, probs=None, n_iters=20, resid=0.85, topic_prob=0.15, modify_matrix=True):
    """
    Args:
        adjacency - sparse matrix
        topics - a list of node indices representing the priority nodes.
        probs - array of initial random jump probabilities.
        resid - probability of using the transition matrix.
        topic_prob - probability of jumping to the selected topics. By default, 1 - resid - topic_prob = 0; if this is less than 0, then there is a probability of a random jump.
    """
    n_nodes, _ = adjacency.shape
    adjacency = sparse.csr_array(adjacency.astype(bool)).astype(float)
    # set 'sinks' to have random transitions
    out_degrees = adjacency.sum(1)
    if modify_matrix:
        adjacency[out_degrees == 0, :] = np.ones(n_nodes)
        adjacency.setdiag(0)
        out_degrees = adjacency.sum(1)
    transitions = adjacency*(1/out_degrees[:, np.newaxis])
    transitions = transitions.T
    transitions = sparse.csc_array(transitions)
    # initial rank: all equal
    # adjacency[i, j] indicates an edge from i to j 
    if probs is None:
        probs = np.ones(n_nodes)/n_nodes
        probs = probs[:, np.newaxis]
    # create a topic vector
    topic_vector = np.zeros((n_nodes, 1))
    topic_vector[topics, :] = 1/len(topics)
    # run power iterations
    random_prob = 1 - resid - topic_prob
    for _ in range(n_iters):
        probs = resid*transitions.dot(probs) + topic_prob*topic_vector
        if random_prob > 0:
            probs += random_prob * (1/n_nodes)
        probs /= probs.sum()
    return probs



def run_spoke(matrix_filename='spoke.mtx'):
    matrix = io.mmread(matrix_filename)
    probs = pagerank(matrix, modify_matrix=False)
    return probs

if __name__ == '__main__':
    adjacency = sparse.csc_array([[0,0,0,0], [1,0,1,0], [1,0,0,0],[1,1,1,0]])
    probs = pagerank(adjacency, modify_matrix=False)
    print(probs)
    # try out some more test graphs...
    # https://www.ccs.neu.edu/home/vip/teach/IRcourse/4_webgraph/notes/Pagerank%20Explained%20Correctly%20with%20Examples.html
    adjacency = sparse.csc_array([[0,1,1,0], [0,0,1,0], [1,0,0,0],[0,0,1,0]])
    probs = pagerank(adjacency, modify_matrix=False)
    print(probs)
    probs = probs.flatten()
    assert(probs[2] > probs[0] and probs[0] > probs[1] and probs[1] > probs[3])
    adjacency = sparse.csc_array([[0,1,1,1,0,0,0,0], [1,0,0,0,0,0,0,0], [1,0,0,0,0,0,0,0],[1,0,0,0,1,1,1,1],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0]])
    probs = pagerank(adjacency, modify_matrix=False)
    print(probs)
    assert(probs[0] > probs[1] and probs[1] > probs[4] and probs[1] == probs[2] and probs[2] == probs[3] and probs[4]==probs[5] and probs[5] == probs[6] and probs[6] == probs[7])
