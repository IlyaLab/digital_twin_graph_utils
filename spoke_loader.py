# Import spoke matrix from a neo4j csv dump.

import csv
import gzip
import os
import sys

from scipy import sparse, io


def import_csv(csv_filename, edges_to_include=None, remove_unused_nodes=False):
    """
    Args:
        csv_filename: name of csv file
        edges_to_include: set of edge types
        remove_unused_nodes: True if nodes with no in- or out-edges are to be removed.

    Returns:
        nodes: list of (_id, _name, _labels_id) where _labels_id corresponds to a key in node_types
        edges: dict of (node1, node2): _type_id where node1 and node2 index into nodes, and _type_id corresponds to a key in edge_types
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
    # sets of nodes that have in-edges or out-edges (to use when deciding whether to remove nodes)
    node_has_edge = set()
    csv.field_size_limit(sys.maxsize)
    if csv_filename.endswith('.gz'):
        # TODO: handle gzip
        f = gzip.open(csv_filename, 'rt')
    else:
        f = open(csv_filename)
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
                node1 = int(row['_start'])
                node2 = int(row['_end'])
                node_has_edge.add(node1)
                node_has_edge.add(node2)
                if edge_type in edge_types:
                    edges[(node1, node2)] = edge_types[edge_type]
                else:
                    edges[(node1, node2)] = len(edge_types) + 1
                    edge_types[row['_type']] = len(edge_types) + 1
    if remove_unused_nodes:
        # remove all nodes that don't have edges
        to_remove = set(node_index.keys()).difference(node_has_edge)
        nodes = [n for n in nodes if n[0] not in to_remove]
        # rebuild node_index
        node_index = {n[0]: i for i, n in enumerate(nodes)}
    # convert edge indices
    new_edges = {}
    for k, e in edges.items():
        node1, node2 = k
        node1 = node_index[node1]
        node2 = node_index[node2]
        new_edges[(node1, node2)] = e
    edges = new_edges
    node_types = {v: k for k, v in node_types.items()}
    edge_types = {v: k for k, v in edge_types.items()}
    return nodes, edges, node_types, edge_types


def to_sparse(nodes, edges):
    """
    Returns a DOK matrix from the edges...
    """
    n_nodes = len(nodes)
    edge_matrix = sparse.dok_array((n_nodes, n_nodes), dtype=int)
    for k, v in sorted(edges.items()):
        n1, n2 = k
        edge_matrix[n1, n2] = v
    return edge_matrix


def load_spoke(filename='spoke.csv', edges_to_include=None, remove_unused_nodes=False, mtx_filename='spoke.mtx'):
    nodes, edges, node_types, edge_types = import_csv(filename, edges_to_include, remove_unused_nodes)
    if not os.path.exists(mtx_filename):
        edge_matrix = to_sparse(nodes, edges)
        io.mmwrite(mtx_filename, edge_matrix)
    else:
        edge_matrix = io.mmread(mtx_filename)
    return nodes, edges, node_types, edge_types, edge_matrix

def symmetrize_matrix(matrix):
    """
    Symmetrizes an adjacency matrix.

    Warning: this completely destroys any meaning applied to node values. Nonzero = edge exists, zero = edge doesn't exist.
    """
    lower_triangle = sparse.tril(matrix)
    upper_triangle = sparse.triu(matrix)
    return lower_triangle + lower_triangle.T + upper_triangle + upper_triangle.T

if __name__ == '__main__':
    nodes, edges, node_types, edge_types, edge_matrix = load_spoke('spoke_2021.csv.gz', remove_unused_nodes=True, mtx_filename='spoke_2021.mtx')
