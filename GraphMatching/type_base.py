import typing
import networkx as nx

import abc
# Pattern metadata:
# Subgraph
# edge input mapping {nodeid: {edgename: new edge name}}
# edge output mapping {nodeid: {edgename: new edge name}}
# name

SubgraphData = typing.NamedTuple("SubgraphData",
                                [("graph", nx.MultiDiGraph),
                                 ("in_edge_mapping", typing.Mapping), ("out_edge_mapping", typing.Mapping)])


class Pattern:
    implementations: typing.Collection[typing.Type['Implementation']]
    generalizations: typing.Collection[typing.Type['Pattern']]

    @classmethod
    def is_generalization(cls, other: typing.Type['Pattern']) -> bool:
        return False  # todo: implement this with a search

    def __init_subclass__(cls, generalizations: typing.Collection[typing.Type['Pattern']] = (), **kwargs):
        super().__init_subclass__(**kwargs)
        cls.generalizations = generalizations

    def __init__(self, parameters):
        self.parameters = parameters


class Implementation(abc.ABC):
    pattern: typing.Type[Pattern]
    skeleton: SubgraphData

    def __init_subclass__(cls, pattern: typing.Type[Pattern], skeleton: SubgraphData, **kwargs):
        cls.pattern = pattern
        cls.skeleton = skeleton

    @abc.abstractmethod
    def to_graph(self) -> nx.MultiDiGraph:
        pass

    @classmethod
    @abc.abstractmethod
    def extract(cls, graph: nx.MultiDiGraph):
        pass

# Edge structure:
# out: output name of source node
# in: input name of destination node

NodeData = typing.NamedTuple("NodeData", [("type", typing.Type[Pattern]), ("parameters", typing.List)])


# define a lifting function on types of PatternType that go graph -> parameter space
