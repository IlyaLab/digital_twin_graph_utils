from scipy import sparse

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

class Graph:

    # TODO: multiedges?
    def __init__(self, nodes, edges, node_types, edge_types,
            edge_matrix=None, multi_edges=False):
        """
        nodes: list of (_id, _name, _labels_id) where _labels_id corresponds to a key in node_types
        edges: dict of (node1, node2) : _type_id where node1 and node2 index into nodes, and _type_id corresponds to a key in edge_types
        node_types: dict of int: str (_labels)
        edge_types: dict of int: str (_type or list of types for multi-edge graphs)
        edge_matrix: sparse array
        multi_edge: boolean
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
        # adjacency list - map of node index to list of node indices
        self._outgoing_edges = {}
        self.multi_edges = multi_edges

    @property
    def outgoing_edges(self):
        if self._outgoing_edges:
            return self._outgoing_edges
        else:
            self._outgoing_edges = {}
            for k in self.edges.keys():
                start_node, end_node = k
                if k in self._outgoing_edges:
                    self._outgoing_edges[start_node].append(end_node)
                else:
                    self._outgoing_edges[start_node] = [end_node]
            return self._outgoing_edges

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
        visited_indices = set()
        # maps from old indices to new indices
        index_map = {}
        new_nodes = []
        new_edges = {}
        for ni in node_ids:
            index = self.id_to_index[ni]
            if index not in visited_indices:
                new_nodes.append(self.nodes[index])
                index_map[index] = len(new_nodes) - 1
            visited_indices.add(index)
        for index in visited_indices:
            edges = self.outgoing_edges[index]
            for e in edges:
                if e in visited_indices:
                    new_edges[index_map[index], index_map[e]] = self.edges[index, e]
        return Graph(new_nodes, new_edges, self.node_types, self.edge_types)


    def get_subgraph_indices(self, node_indices):
        """
        Returns an instance of Graph that only contains the node indices.
        """
        pass
        visited_indices = set()
        # maps from old indices to new indices
        index_map = {}
        new_nodes = []
        new_edges = {}
        for index in node_indices:
            if index not in visited_indices:
                new_nodes.append(self.nodes[index])
                index_map[index] = len(new_nodes) - 1
            visited_indices.add(index)
        for index in visited_indices:
            edges = self.outgoing_edges[index]
            for e in edges:
                if e in visited_indices:
                    new_edges[index_map[index], index_map[e]] = self.edges[index, e]
        return Graph(new_nodes, new_edges, self.node_types, self.edge_types)

    def get_indices_from_names(self, node_names):
        """
        Returns an index or a list of indices.
        """
        if isinstance(node_names, str):
            node_id = self.name_to_id[node_names]
            return self.id_to_index[node_id]
        else:
            indices = [self.id_to_index[self.name_to_id[n]] for n in node_names]
            return indices

    def get_indices_from_ids(self, node_ids):
        """
        Returns an index or a list of indices, given ids.
        """
        if isinstance(node_ids, int):
            return self.id_to_index[node_ids]
        else:
            return [self.id_to_index[i] for i in node_ids]

    def get_nodes_from_names(self, node_names):
        """
        Returns a node or a list of nodes. A node is a tuple of (id, name, type).
        """
        if isinstance(node_names, str):
            node_id = self.name_to_id[node_names]
            node_index = self.id_to_index[node_id]
            return self.nodes[node_index]
        else:
            indices = [self.id_to_index[self.name_to_id[n]] for n in node_names]
            nodes = [self.nodes[n] for n in indices]
            return nodes

    def get_nodes_from_ids(self, node_ids):
        """
        Returns a node or a list of nodes, given ids.
        """
        if isinstance(node_ids, int):
            return self.nodes[self.id_to_index[node_ids]]
        else:
            return [self.nodes[self.id_to_index[i]] for i in node_ids]
