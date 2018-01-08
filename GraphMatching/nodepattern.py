import collections
import typing

import itertools
import networkx as nx

# A Graph Pattern is a graph in which some nodes are parametric (i.e. can be replaced).
#
# In such a graph pattern, where there are n holes (i.e. parameters) we can denote the graph as G[p1, p2, ... pn].
#
# Pattern metadata:
# Subgraph
# edge input mapping {nodeid: {edgename: new edge name}}
# edge output mapping {nodeid: {edgename: new edge name}}
# name

PatternData = collections.namedtuple("PatternData", ["graph", "in_edge_mapping", "out_edge_mapping"])

# Replacement structure:
# nodes are nodes that will be subsumed in the pattern

Replacement = collections.namedtuple("Replacement", ["result_node", "nodes", "edges"])

# Edge structure:
# out: output name of source node
# in: input name of destination node



class Pattern:
    def __init__(self, pattern: PatternData, validator: typing.Callable[[nx.MultiDiGraph], bool]):
        self.pattern = pattern

        # node_id marks the location within the graph to be replaced.
        self.sub_patterns = {node_id: node_data for node_id, node_data in pattern.graph.nodes(True) if
                             'pattern' in node_data}
        self.validator = validator

    def is_terminal(self):
        return not self.sub_patterns

    def instantiate(self):
        pass


    def match(self, graph: nx.MultiDiGraph) -> typing.List[Replacement]:
        """
        :param graph: Graph to identify isomorphisms
        :return: list of node isomorphisms after recognizing and replacing patterns.
        """
        matches = {}
        for pattern_id, pattern_data in self.sub_patterns.items():
            pattern_data = pattern_data['pattern']
            matches[pattern_id] = pattern_data.graph.match(graph)

        # verify that there are no pattern overlapping
        # todo: replace with independent set
        for (id1, matches1), (id2, matches2) in itertools.combinations_with_replacement(matches.items(), 2):
            for m1, m2 in itertools.product(matches1, matches2):
                if not m1.isdisjoint(m2):
                    raise Exception(f"Patterns not disjoint: {id1} {id2} overlap with isomorphisms {m1}, {m2}")

        # perform replacement
        for pattern_id in matches:
            isomorphisms = matches[pattern_id]


def replace(node_id, graph: nx.MultiDiGraph, isomorphism: typing.Mapping, pattern_data: PatternData, data):
    graph.add_node(node_id, **data)

    # for each in-edge to the set of nodes, find the replacement and create a new edge
    # given a targeted node and a key, find the source node. Then wire the source node to the replacement node
    # the structure is then {destination: [(key, new_key)]}
    # these serve as a remapping of inputs
    # the isomorphism is given (by networkx) as {graph node: pattern node}.

    for graph_node, pattern_node in isomorphism.items():
        # pattern_data.in_edge_mapping provides the information to turn graph_node's in-edges into the pattern node's
        # edge
        print(pattern_node)
        edge_map = pattern_data.in_edge_mapping[pattern_node]
        for source, dest, edge_data in graph.in_edges(graph_node, data=True):
            if source in isomorphism:
                continue
            edge_data["out"] = edge_map[edge_data["out"]]
            graph.add_edge(source, node_id, **edge_data)

        # for each out-node from the output nodes, we map them all as outputs of the pattern node.
        # to maintain information, we include metadata with these edges.

    # pattern node -> graph node
    reversed_isomorphism = {value: key for key, value in isomorphism.items()}
    print(reversed_isomorphism)
    for pattern_node, mapping in pattern_data.out_edge_mapping.items():
        graph_node = reversed_isomorphism[pattern_node]
        for _, dest, edge_data in graph.out_edges(graph_node, data=True):
            if dest in isomorphism:
                continue
            # at this point there is a graph node that needs to be 'rewired'.
            edge_data["in"] = mapping[edge_data["in"]]
            graph.add_edge(node_id, dest, **edge_data)

    # for each out-edge, we map it to a new out-edge from the pattern node

    graph.remove_nodes_from(isomorphism)

