"""
Module with the Partitional Analysis tools of the Comp_Tools library.
For more information, see:
Pauxy Gentil-Nunes - Análise Particional: Uma Mediação Entre Composição Musical e a Teoria das Partições.
"""

import music21 as m21
from typing import Tuple, Union, List, Sequence, Generator, Dict
from fractions import Fraction
import matplotlib.pyplot as plt
from .basic_tools import markov
from graphviz import Digraph
from collections import defaultdict


def extract_parts(
    filename: str,
) -> List:

    """Extracts the parts from a piece. The filename is a string.
    The file can be a MIDI file or an MusicXml file.
    """

    piece = m21.converter.parse(filename).voicesToParts().stripTies()
    raw_parts = [x for x in piece.getElementsByClass("Part")]
    parts = []
    for part in raw_parts:
        new_part = part.flat.getElementsByClass("GeneralNote")
        filled_part = new_part.makeRests(fillGaps=True, inPlace=False)
        parts.append(filled_part)

    return parts


def partitional_analysis(
    filename: str,
) -> List:

    """Returns the rhythmic partitional analysis of a piece, given its filename.
    """
  
    raw_parts = extract_parts(filename)

    parts = []
    for part in raw_parts:
        for nota in part:
            parts.append(nota)

    parts.sort(key= lambda x: x.offset)

    parts_off = defaultdict(list)

    for nota in parts:
        offset = float(nota.offset)
        dur = float(nota.quarterLength)
        if type(nota) == m21.note.Note:
            if dur != 0:
                parts_off[offset].append(dur)
        elif type(nota) == m21.note.Rest:
            parts_off[offset] = []
        elif type(nota) == m21.chord.Chord:
            for el in nota:
                dur = float(el.quarterLength)
                if dur != 0:
                    parts_off[offset].append(dur)

    parts_final = [[key]+ parts_off[key] for key in sorted(list(parts_off.keys()))]

    for i in range(1,len(parts_final)):
        prev = parts_final[i-1]
        cur = parts_final[i]
        for el in prev[1:]:
            if type(el) != tuple:
                if el + prev[0] > cur[0]:
                    cur.append(tuple([prev[0],el]))
            else:
                goal = el[0] + el[1]
                if goal > cur[0]:
                    cur.append(el)

    analise = dict()
    for parte in parts_final:
        part = parte[1:]
        count_analise = []
        ind = list(set(part))
        for x in ind:
            count_analise.append(part.count(x))
            analise[parte[0]] = tuple(sorted(count_analise))
    return analise


def binary_relations(
    n: int,
) -> int:

    """Returns the number of possible binary relations given a number of parts.
    """

    return (n*(n-1))/2


def agglomeration_index(
    part: tuple,
) -> int:

    """Returns the agglomeration index of the partition of an integer.
    """

    result = 0
    for element in part:
        result += binary_relations(element)
    
    return result


def dispersion_index(
    part: tuple,
) -> int:

    """Returns the dispersion index of the partition of an integer.
    """

    return binary_relations(sum(part)) - agglomeration_index(part)


def make_partitiogram(
    parts: list,
) -> None:

    """Plots the partitiogram of a list of partitions.
    """

    parts = list(set(parts))
    a = [agglomeration_index(x) for x in parts]
    b = [dispersion_index(x) for x in parts]
    fig, ax = plt.subplots()
    ax.scatter(a,b,s=250)
    for i in range(len(a)):
        ax.annotate(parts[i], (a[i],b[i]))
    plt.show()


def accel_asc(
    n: int
) -> Generator:

    """Generator function for the partitions of an integer.
    """

    a = [0 for i in range(n + 1)]
    k = 1
    y = n - 1
    while k != 0:
        x = a[k - 1] + 1
        k -= 1
        while 2 * x <= y:
            a[k] = x
            y -= x
            k += 1
        l = k + 1
        while x <= y:
            a[k] = x
            a[l] = y
            yield a[:k + 2]
            x += 1
            y -= 1
        a[k] = x + y
        y = x + y - 1
        yield a[:k + 1]


def all_partitions(
    n: int,
) -> List:

    """Returns a list of all partitions of an integer.
    """

    return[tuple(x) for x in accel_asc(n)]


def young_ret(
    n: int,
) -> List:

    """Returns the partitions of all integers up to a given integer n.
    """

    result = []
    for i in range(1,n+1):
        result += all_partitions(i)

    return result


def resizing(
    part: Tuple,
) -> List:

    """Applies the resizing operation to a partition.
    """

    result = []
    part = list(part)
    for i, el in enumerate(part):
        new_part = part[0:i] + [el+1] + part[i+1:]
        new_part = tuple(sorted(new_part))
        result.append(new_part)

    result = list(set(result))
    return result


def revariance(
    part: Tuple,
) -> Tuple:

    """Applies the revariance operation on a partition.
    """

    part = list(part)
    new_part = [1] + part

    return tuple(new_part)


def transference(
    part: Tuple,
) -> Union[Tuple, bool]:

    """Applies the transference operation to a partition.
    """

    result = []
    if part == tuple([1]):
        result = None
    elif len(part) == 1:
        new_part = [x for x in part]
        new_part[-1] -= 1
        new_part.insert(0,1)
        new_part = [x for x in new_part if x != 0]
        if new_part != part:
            result.append(tuple(new_part))
    else:
        for i in range(len(part)):
            no_i = [x for x in part]
            no_i[i] -= 1
            no_i.insert(0,1)
            no_i = tuple(sorted([x for x in no_i if x != 0]))
            if no_i != part: result.append(no_i)

            other_index = [j for j in range(len(part)) if j != i]
            for j in other_index:
                new_part = [x for x in part]
                new_part[i] -= 1
                new_part[j] += 1
                new_part = tuple(sorted([x for x in new_part if x != 0]))
                if new_part != part: result.append(new_part)
            result = list(set(result))
    return result
                    


def find_operator(part1, part2):
    parts = sorted([part1, part2], key=len)
    part1 = parts[0]
    part2 = parts[1]
    if part1 == part2: return "Identity"
    else:
        if len(part1) == len(part2):
            if sum(part1) == sum(part2):
                return "Transference"
            elif abs(sum(part1) - sum(part2)) == 1:
                return "Resizing"
            elif abs(len(part1)-len(part2)) == 1:
                if part2[0] == 1 and part1 == tuple([x for x in part2[1:]]):
                    return "Revariance"


def creat_op_graph(upper_int):
    result = []
    parts = young_ret(upper_int-1)
    for part in parts:
        red_edge = [sorted([part, x]) for x in resizing(part)]
        for p in red_edge: p.append('m')

        rev_edge = sorted([part, revariance(part)])
        rev_edge.append('v')

        if transference(part):
            trans_edge = [sorted([part, x]) for x in transference(part)]
            for t in trans_edge:
                t.append('t')
                if t not in result:
                    result.append(t)
        result += red_edge
        result.append(rev_edge)

    for part in all_partitions(upper_int):
        if transference(part):
            trans_edge = [sorted([part, x]) for x in transference(part)]
            for t in trans_edge:
                t.append('t')
                if t not in result:
                    result.append(t)

    return result


### Functions for Linear Partitional Analysis


def linvectors_list(
    pitches: List,
) -> List:

    """Returns the linvectors of a list of MIDI pitches.
    """

    result = []
    first_linvector = [pitches[0]]
    result.append(first_linvector)
    for pitch in pitches[1:]:
        next_linvector = []
        for element in result[-1]:
            if abs(pitch-element) <= 2:
                pass
            else:
                next_linvector.append(element)
        next_linvector.append(pitch)
        result.append(next_linvector)

    return result


def linear_partitions(
    pitches: List,
) -> List:
    
    """Returns the Linear Partitions of a given list of pitches.
    """

    result = ["N"]
    linvectors = linvectors_list(pitches)
    for i in range(1, len(linvectors)):
        if linvectors[i] == linvectors[i-1]:
            result.append("R")
        elif linvectors[i] != linvectors[i-1]:
            if len(linvectors[i]) == len(linvectors[i-1]):
                if linvectors[i][-1] in linvectors[i-1][:-1]:
                    result.append("G")
                elif abs(linvectors[i][-1] - linvectors[i-1][-1]) < 3:
                    result.append("P")
                else:
                    result.append("A")
            elif len(linvectors[i]) > len(linvectors[i-1]):
                result.append("N")
            else:
                if abs(linvectors[i][-1] - linvectors[i-1][-1]) < 3:
                    result.append("C")
                else:
                    result.append("F")

    return result


def part_rep(
    part: Tuple,
) -> str:

    """Function that returns the string representation of a partition,
    so it can act as the node of a graph.
    """

    result = ""
    for x in part: result += str(x) + "."
    return result[:-1]


def partitiograph(
    filename: str,
    new_name: str,
) -> None:

    """Function to create the rhythmic partitiograph of a piece of music.
    """

    analysis = partitional_analysis(filename)
    keys = sorted(list(analysis.keys()))

    partitions = [analysis[key] for key in keys]
    ind_partitions = list(set(partitions))

    markov_an = markov(partitions)

    for part in ind_partitions:
        if part not in markov_an.keys(): markov_an[part] = []
    gra = Digraph(new_name,filename=new_name.lower() + ".gv", engine="circo")
    #gra.attr(rankdir='LR')

    list_edges = []
    for i in range(len(ind_partitions)):
        part1 = ind_partitions[i]
        for j in range(len(ind_partitions)):
            part2 = ind_partitions[j]
            if part2 in markov_an[part1]:
                list_edges.append([part_rep(part1),part_rep(part2), str(markov_an[part1].count(part2))])

    for part in ind_partitions: gra.node(part_rep(part))
    for edge in list_edges: gra.edge(edge[0],edge[1],label=edge[2])

    gra.view()


def partitiograph_linear(
    filename: str,
) -> None:

    """Function to create the partitiograph of the linear partitions of a melody.
    """

    notes = m21.converter.parse(filename).flat.stripTies().getElementsByClass("Note")
    pitches = [note.pitch.midi for note in notes]

    partitions = linear_partitions(pitches)
    ind_partitions = list(set(partitions))

    markov_an = markov(partitions)


    for part in ind_partitions:
        if part not in markov_an.keys(): markov_an[part] = []

        
    gra = Digraph()
    gra.attr(rankdir='LR')

    list_edges = []
    for i in range(len(ind_partitions)):
        part1 = ind_partitions[i]
        for j in range(len(ind_partitions)):
            part2 = ind_partitions[j]
            if part2 in markov_an[part1]:
                list_edges.append([part1, part2, str(markov_an[part1].count(part2))])

    for part in ind_partitions: gra.node(part)
    for edge in list_edges: gra.edge(edge[0],edge[1],label=edge[2])

    gra.view()

def build_graph(
    edges: List,
)->Dict:
    
    """Function that builds an adjacency dictionary to model a graph.
    """
    
    graph = defaultdict(list)
    for edge in edges:
        a, b = edge[0], edge[1]
        graph[a].append(b)
        graph[b].append(a)
    return dict(graph)


def shortest_path(
    graph: Dict,
    start: Tuple,
    goal: Tuple,
) -> List:
    
    """Function that returns the shortest path between two nodes in a graph.
    """
    
    explored = []
    queue = [[start]]
    if start == goal:
        return queue[0]
    while queue:
        path = queue.pop(0)
        node = path[-1]
        if node not in explored:
            neighbours = graph[node]
            for neighbour in neighbours:
                new_path = list(path)
                new_path.append(neighbour)
                queue.append(new_path)
                if neighbour == goal:
                    return new_path
            explored.append(node)
    return []