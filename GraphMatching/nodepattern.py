import typing

import itertools
import networkx as nx

from networkx.algorithms import isomorphism

from . import type_base

# A Graph Pattern is a graph in which some nodes are parametric (i.e. can be replaced).
#
# In such a graph pattern, where there are n holes (i.e. parameters) we can denote the graph as G[p1, p2, ... pn].


def _node_match(g1_node, g2_node):
    g1_data = g1_node["data"]
    g2_data = g2_node["data"]
    return issubclass(g1_data.type, g2_data.type)


def _edge_match(g1_edge, g2_edge):
    print(g1_edge, g2_edge)
    return any(
        edgedata1["out"] == edgedata2["out"] and edgedata1["in"] == edgedata2["in"]
        for edgedata1, edgedata2 in itertools.product(g1_edge.values(), g2_edge.values()))


def match(pattern: type_base.SubgraphData, graph: nx.MultiDiGraph) -> typing.Iterable[typing.Mapping]:
    """
    :param graph: Graph to identify and replace isomorphisms (in place)
    :return bool indicating whether or not match was successful
    """

    mapping = isomorphism.MultiDiGraphMatcher(graph, pattern.graph,
                                              node_match=_node_match,
                                              edge_match=_edge_match)
    return mapping.subgraph_isomorphisms_iter()


def replace(node_id, graph: nx.MultiDiGraph, isomorphism: typing.Mapping,
            pattern_data: type_base.SubgraphData, data: type_base.NodeData):
    graph.add_node(node_id, data=data)

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

