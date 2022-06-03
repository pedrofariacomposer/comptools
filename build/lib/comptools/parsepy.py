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
from collections import defaultdict, Counter


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


def split_chord(
    chord: m21.chord.Chord,
) -> List:

    """Splits a music21 chord into a list of notes"""

    result = [x for x in chord]
    for i in result:
        i.quarterLength = chord.quarterLength
        i.offset = chord.offset
    return result


def partitional_analysis(
    filename: str,
    no_reps: bool = False,
) -> Dict:

    """Returns the rhythmic partitional analysis of a piece, given its filename.
    """
  
    offset_dict = defaultdict(list)
    parts = extract_parts(filename)
    offsets = []
    for p in parts:
        for el in p:
            if el.offset not in offsets:
                offsets.append(el.offset)
    offsets.sort()
    for p in parts:
        for el in p:
            if isinstance(el, m21.chord.Chord):
                new_el = split_chord(el)
                for element in new_el:
                    offset_dict[el.offset].append(element)
            elif isinstance(el, m21.note.Note):
                offset_dict[el.offset].append(el)
            else:
                pass
    new_values = []
    analise = dict()
    for i, el in enumerate(offsets):
        if i == 0:
            cur_list = [(el,x.quarterLength) for x in offset_dict[el]]
        else:
            cur_list = [(el,x.quarterLength) for x in offset_dict[el]]
            prev_list = new_values[i-1]
            for y in prev_list:
                if round(y[0] + y[1],5) > round(el,5):
                    cur_list.append(y)
        counts = Counter(cur_list)
        final_count = tuple(sorted(list(counts.values())))
        if len(final_count) == 0:
            final_count = tuple([0])
        analise[el] = final_count
        new_values.append(cur_list)
        
    if no_reps == True:
        new_analise = dict()
        for y, el in enumerate(offsets):
            if y == 0:
                new_analise[el] = analise[el]
            else:
                if analise[el] != analise[offsets[y-1]]:
                    new_analise[el] = analise[el]
                else:
                    pass
        return new_analise
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
    no_reps: bool = False,
) -> None:

    """Function to create the rhythmic partitiograph of a piece of music.
    """

    analysis = partitional_analysis(filename,no_reps=no_reps)
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