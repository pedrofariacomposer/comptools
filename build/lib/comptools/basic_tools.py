"""
Module with the basic tools of the Comp_Tools library.
"""


from typing import Dict, Sequence, List
from itertools import chain, combinations
#from collections import Iterable, defaultdict
from collections import defaultdict
from numpy import array, reshape
from random import choice


def interval_class(
    pitch1: int,
    pitch2: int,
) -> int:
    """Finds the interval class between two pitches or pitch-classes.
    """

    diff_mod_12 = abs(pitch1 - pitch2) % 12
    if diff_mod_12 > 6:
        diff_mod_12 = 12 - diff_mod_12

    return diff_mod_12


def interval_vector(
    pitches: Sequence,
) -> List:
    """Finds the interval vector of a sequence of pitches or pitch-classes.
    """

    interval_class_vector = [0] * 6
    for i in range(len(pitches)):
        for k in range(i + 1, len(pitches)):
            interval_class_result = interval_class(pitches[i], pitches[k])
            interval_class_vector[interval_class_result - 1] += 1
    return interval_class_vector


def index_vector(
    pcset: Sequence,
) -> List:

    """Returns the index vector of a pitch class set.
    """

    all_sums = [[x, y] for x in pcset for y in pcset if x <= y]
    vector = [0] * 12
    for i in all_sums:
        soma = sum(i) % 12
        if len(set(i)) == 1:
            vector[soma] += 1
        else:
            vector[soma] += 2
    return vector


def retrograde(
    sequence: Sequence,
) -> List:

    """Finds the retrograde of any sequence.
    """

    return list(reversed(sequence))


def transposition(
    pitches: Sequence,
    transposing_factor: int,
) -> List:

    """Transposes a sequence of MIDI pitches or pitch classes.
    """
    result = []
    for p in pitches:
        result.append(p + transposing_factor)
    if max(pitches) <= 11:
        result = [x % 12 for x in result]
    return result



def intervals(
    pitches: Sequence,
    icclass: bool = False,
) -> List:

    """Finds the interval sequence of a sequence of MIDI pitches or pitch classes.
    """

    if max(pitches) <= 11:
        if icclass == True:
            return[interval_class(pitches[i+1],pitches[i]) for i in range(len(pitches)-1)]
        else:
            return [(pitches[i+1]-pitches[i]) % 12 for i in range(len(pitches)-1)]
    else:
        return [pitches[i+1]-pitches[i] for i in range(len(pitches)-1)]


def start_sequence_pitches(
    first_pitch: int,
    interval_sequence: List,
) -> List:

    """"Given a first pitch and an interval sequence, creates a pitch sequence.
    """

    new_sequence = [first_pitch]
    for interval in interval_sequence:
        new_pitch = new_sequence[-1] + interval
        new_sequence.append(new_pitch)
    
    return new_sequence


def inversion(
    pitches: Sequence,
    factor: int = 0
) -> List:

    """Inverts a sequence of pitch classes or a sequence of MIDI pitches.
    """

    if max(pitches) <= 11:
        return transposition([(12-pitch_class) % 12 for pitch_class in pitches],factor)
    else:
        intervals_pitches = [-x for x in intervals(pitches)]
        return start_sequence_pitches(pitches[0],intervals_pitches)


def multiplication(
    pitch_class_sequence: Sequence,
    multiplying_factor: int,
) -> List:

    """Multiplies each pitch class in a sequence by a integer.
    """

    return [(pitch_class * multiplying_factor) % 12 for pitch_class in pitch_class_sequence]


def rotate_sequence(
    sequence: Sequence,
    new_first_element_index: int,
) -> List:

    """Rotates any sequence, making it start on the new given index
    """

    sequence_copy_list = [element for element in sequence]
    return sequence_copy_list[new_first_element_index:] + sequence_copy_list[:new_first_element_index]


def all_rotations(
    sequence: Sequence,
)-> List:

    """Returns all the rotations of a given sequence, including the original sequence.
    """

    all_rotations_list = []
    for i in range(len(sequence)):
        all_rotations_list.append(rotate_sequence(sequence,i))
    
    return all_rotations_list


### Functions for Normal Form and Prime Form ###


def most_compact(
    a: Sequence,
    b: Sequence,
) -> Sequence:

    """ Compares two lists and returns the one that is more compact, as defined by Forte and Straus.
    Function written by Raphael Santos.
    """

    for i in range(len(a) - 1, 0, -1):
        a_diff = (a[i] - a[0]) % 12
        b_diff = (b[i] - b[0]) % 12
        if a_diff < b_diff:
            return a
        elif a_diff > b_diff:
            return b
    if a[0] < b[0]:
        return a
    else:
        return b


def normal_form(
    pcset: Sequence,
) -> Sequence:

    """Returns the Normal Form of a sequence of pitch classes.
    Function written by Raphael Santos.
    """

    uniques = list(set(pcset))
    uniques.sort()
    best = uniques
    for i in range(1, len(uniques)):
        best = most_compact(best, rotate_sequence(uniques, i))
    return best


def prime_form(
    pitch_classes: Sequence,
) -> List:

    """Returns the Prime Form of a sequence of pitch classes.
    Function written by Raphael Santos.
    """
    normal = normal_form(pitch_classes)
    normal_inv = normal_form(inversion(pitch_classes))
    norm = transposition(normal, -normal[0])
    inv = transposition(normal_inv, -normal_inv[0])
    prime = norm
    if inv < norm:
        prime = inv
    return prime


def contour_profile(
        seq: Sequence,
) -> List:
    
    """Given a list of pitches or pitch classes, return the contour
    profile of that list"""
    
    return [sorted(seq).index(x) for x in seq]


def contour_matrix(
        contour: Sequence,
) -> List:
    
    """Given a contour list, returns its matrix.
    """    
    result = []
    for i in contour:
        sub = []
        for j in contour:
            val = j - i
            if val != 0:
                val = int(val/abs(val))
            sub.append(val)
        result.append(sub)
    return result


def all_subsets(
        iterable: Sequence,
    ) -> List:

    """Given a set, returns all of the subsets of length 3 or higher from it.
    """
    
    s = list(iterable)
    new = []
    a = list(chain.from_iterable(combinations(s, r) for r in range(len(s) + 1)))
    for i in a:
        if len(i) >= 3 and len(i) != len(s):
            b = prime_form(list(i))
            if b not in new:
                new.append(b)
    return new


def flatten_sequence(
    sequence: Sequence,
) -> List:

    """Given a sequence, returns a flat version of it. For instance,
    flatten_sequence([0,1,2,[3,[4,5]]]) = [0,1,2,3,4,5].
    """
    #if isinstance(sequence,Iterable):
    if isinstance(sequence, list) or isinstance(sequence, tuple) :
        return [a for i in sequence for a in flatten_sequence(i)]
    else:
        return [sequence]


def group_tuplets(
    linha: Sequence,
    min_constant: int = 4,
) -> List:

    """Given a sequence of quarterLengths, group the tuplets into sublists.
    If min_constant == 8, the least value considered is a 32nd note.
    """
    
    result = []
    it = linha.__iter__()
    while len(flatten_sequence(result)) < len(linha):
        el = next(it)
        control = el * min_constant
        if control == round(control):
            result.append(el)
        else:
            group = [el]   
            valor = sum(group) * min_constant
            if valor == round(valor):
                result.append(group)
                group = []
            else:
                valor = sum(group) * min_constant
                while valor != round(valor):
                    group.append(next(it))
                    valor = sum(group) * min_constant
                result.append(group)
    return result


def simple_multiplication(
    multiplicand: Sequence,
    multiplier: Sequence,
) -> List:

    """Applies simple pitch class set multiplication onto two pitch class sets.
       See: Heinemann - Pitch Class Set Multiplication in Theory and Practice.
    """
    ois = transposition(multiplicand, -multiplicand[0])

    multiplication_result = []
    for i in multiplier:
        multiplier_ois = normal_form(transposition(ois, i-ois[0]))
        for element in multiplier_ois:
            if element not in multiplication_result:
                multiplication_result.append(element)

    return normal_form(multiplication_result)


def complex_multiplication(
    multiplicand: Sequence,
    multiplier: Sequence,
    multiplication_factor: int,
) -> List:

    """Applies complex pitch class set multiplication onto two pitch class sets.
       See: Heinemann - Pitch Class Set Multiplication in Theory and Practice.
    """

    simple_multication_result = simple_multiplication(multiplicand, multiplier)
    transposition_factor = (multiplicand[0] - multiplication_factor) % 12

    return normal_form(transposition(simple_multication_result, transposition_factor))


def stravinsky_rotation(
    pcset: Sequence,
) -> array:

    """Returns a numpy array with the Stravinsky rotations of a given pitch class set.
    """
    
    a = [transposition(x, pcset[0]-x[0]) for x in all_rotations(pcset)]
    m = reshape(a, (len(pcset), len(pcset)))

    return m


def remove_reps(
    seq: Sequence,
) -> Sequence:

    """Remove consecutive equal elements from a given sequence"""
    
    result = [seq[0]]
    for el in seq[1:]:
        if el == result[-1]:
            pass
        else:
            result.append(el)
    return result

    
def markov(
    seq: Sequence,
    no_reps: bool = False,
) -> Dict:

    """Given a sequence of elements, returns a Markov Chain.
    """
    if no_reps:
        seq = remove_reps(seq)
    result = defaultdict(list)
    for cur, nex in zip(seq[0:-1],seq[1:]): result[cur].append(nex)
    result_dict = dict(result)
    
    return result_dict


def build_from_markov(
    chain: Dict,
    first,
    n: int,
) -> List:

    """Given a Markov Chain, returns a new sequence of length 'n' starting with 'first'.
    """

    result = [first]
    i = 0
    while i < n-1:
        candidates = chain.get(first)
        if candidates != None:
            result.append(choice(candidates))
            first = result[-1]
            i += 1
        else:
            i = n
    return result



def make_golden(
    sequence: Sequence,
)-> List:

    """Given a sequence of elements, separates it into two new sequences,
    on the index that is equivalent to the golden ratio of the sequence length.
    """
    
    golden_index = round(len(sequence) * 0.618)

    return [sequence[0:golden_index], sequence[golden_index:]]
