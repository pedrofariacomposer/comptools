"""
Module with tools for creating and analyzing graphs.
"""


from collections import defaultdict
from typing import Dict, List, Sequence


def build_graph(
    edges: List,
) -> Dict:

    """
    Function to build a graph, given a list of edges.
    """

    graph = defaultdict(list)
    for edge in edges:
        a, b = edge[0], edge[1]
        if b not in graph[a]:
            graph[a].append(b)
    graph = dict(graph)
    
    return graph
