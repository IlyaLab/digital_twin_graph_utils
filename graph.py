from scipy import sparse

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

class Graph:

    def __init__(self, nodes, edges, node_types, edge_types,
            edge_matrix=None):
        """
        nodes: list of (_id, _name, _labels_id) where _labels_id corresponds to a key in node_types
        edges: dict of (node1, node2, _type_id) where node1 and node2 index into nodes, and _type_id corresponds to a key in edge_types
        node_types: dict of int: str (_labels)
        edge_types: dict of int: str (_type)
        """
        self.nodes = nodes
        self.edges = edges
        self.node_types = node_types
        self.edge_types = edge_types
        if edge_matrix is not None:
            self.edge_matrix = edge_matrix
        else:
            self.edge_matrix = to_sparse(nodes, edges)
        self.name_to_id = {x[1]: x[0] for x in nodes}
        self.id_to_index = {x[0]: i for i, x in enumerate(nodes)}

    def symmetrize_edge_matrix(self):
        matrix = self.edge_matrix
        lower_triangle = sparse.tril(matrix)
        upper_triangle = sparse.triu(matrix)
        sym = lower_triangle + lower_triangle.T + upper_triangle + upper_triangle.T
        self.symmetric_edge_matrix = sym
        return sym

    def get_subgraph_ids(self, node_ids):
        """
        Returns an instance of Graph that only contains the given ids.
        """
        pass

    def get_subgraph_indices(self, node_indices):
        """
        Returns an instance of Graph that only contains the node indices.
        """
        pass

    def get_nodes_from_names(self, node_names):
        if isinstance(node_names, str):
            pass
        else:
            pass

