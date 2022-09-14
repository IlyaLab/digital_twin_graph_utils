# Import spoke matrix from a neo4j csv dump.

import csv

from scipy import sparse, io


def import_csv(csv_filename, edges_to_include=None):
    """
    Args:
        csv_filename: name of csv file
        edges_to_include: set of edge types

    Returns:
        nodes: list of (_id, _name, _labels_id) where _labels_id corresponds to a key in node_types
        edges: dict of (node1, node2, _type_id) where node1 and node2 are ints that index into nodes, and _type_id corresponds to a key in edge_types
        node_types: dict of int: str (_labels)
        edge_types: dict of int: str (_type)
    """
    nodes = []
    n_nodes = 0
    # mapping of _id to index in nodes
    node_index = {}
    # node_types is a map of string (
    node_types = {}
    edges = {}
    # edge_types is a map of string (_type) to node
    edge_types = {}
    with open(csv_filename) as f:
        dr = csv.DictReader(f)
        for i, row in enumerate(dr):
            if i % 10000 == 0:
                print(i, 'nodes: ', len(node_index), 'edges: ', len(edges))
            # if this is a node
            if row['_id']:
                if row['_labels'] in node_types:
                    nodes.append((int(row['_id']), row['name'], node_types[row['_labels']]))
                else:
                    nodes.append((int(row['_id']), row['name'], len(node_types) + 1))
                    node_types[row['_labels']] = len(node_types) + 1
                node_index[int(row['_id'])] = n_nodes 
                n_nodes += 1
            # if this row is an edge
            else:
                edge_type = row['_type']
                if edges_to_include is None or edge_type in edges_to_include:
                    node1 = node_index[int(row['_start'])]
                    node2 = node_index[int(row['_end'])]
                    if edge_type in edge_types:
                        edges[(node1, node2)] = edge_types[edge_type]
                    else:
                        edges[(node1, node2)] = len(edge_types) + 1
                        edge_types[row['_type']] = len(edge_types) + 1
    node_types = {v: k for k, v in node_types.items()}
    edge_types = {v: k for k, v in edge_types.items()}
    return nodes, edges, node_types, edge_types


def to_sparse(nodes, edges):
    """
    Returns a LIL matrix from the edges...
    """
    n_nodes = len(nodes)
    edge_matrix = sparse.dok_array((n_nodes, n_nodes), dtype=int)
    for k, v in sorted(edges.items()):
        n1, n2 = k
        edge_matrix[n1, n2] = v
    return edge_matrix


def load_spoke(filename='spoke.csv'):
    nodes, edges, node_types, edge_types = import_csv(filename)
    edge_matrix = to_sparse(nodes, edges)
    io.mmwrite('spoke.mtx', edge_matrix)
    return nodes, edges, node_types, edge_types, edge_matrix

def symmetrize_matrix(matrix):
    """
    Returns a dok matrix that is symmetric and a copy of matrix.
    Takes the larger of two values if a pair is already symmetric.
    """
    matrix_copy = sparse.dok_array(matrix)
    ind1, ind2 = matrix.nonzero()
    for i, j in zip(ind1, ind2):
        if matrix_copy[j, i]:
            matrix_copy[j, i] = max(matrix[j, i], matrix[i, j])
        else:
            matrix_copy[j, i] = matrix[i, j]
    return matrix_copy
