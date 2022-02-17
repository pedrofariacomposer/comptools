"""
Module with the twelve-tone tools of the Comp_Tools library.
"""

from difflib import SequenceMatcher
from pandas.core.indexes.interval import interval_range
from .basic_tools import *
from pandas import DataFrame
from numpy import reshape
from typing import Sequence, List

def twelve_tone_matrix(
    row: Sequence,
) -> DataFrame:

    """ Returns a twelve-tone matrix in the form of a Pandas DataFrame.
    """

    inverted_row = inversion(row)
    inv_mat = transposition(inverted_row, row[0]-inverted_row[0])
    new = [row]
    for i in range(1, 12):
        k = transposition(row, (inv_mat[i] - row[0]) % 12)
        new.append(k)
    m = reshape(new, (12, 12))
    df = DataFrame(m)

    return df


def order_rep(
    pcset: Sequence
) -> List:

    """ Given a tone row, returns a list of pairs [i,ai],
    on which i is the order number and ai is the pitch class
    at that order number. Inspired by Milton Babbitt.
    """

    return [tuple([i,el]) for i, el in enumerate(pcset)]


def transposition_order_rep(
    ttset: Sequence,
    n: int
) -> List:

    """ Applies the transposition operation on a tone row with its order numbers
    """
    result = [0] * len(ttset)
    for i, pair in enumerate(ttset):
        new_pc = (pair[1] + n) % 12
        for scpair in ttset:
            if scpair[1] == new_pc:
                result[i] = scpair
    return result   


def inversion_order_rep(
    ttset: Sequence,
    n: int
) -> List:

    """ Applies the inversion (plus transposition) operation on a tone row with its order numbers
    """
    result = [0] * len(ttset)
    for i, pair in enumerate(ttset):
        new_pc = ((12 - pair[1]) + n) % 12
        for scpair in ttset:
            if scpair[1] == new_pc:
                result[i] = scpair
    return result  


def order_inversions(
    ttset: Sequence
) -> int:

    """ Given a transformed version of a series with order numbers,
    returns the number of order inversions that ocurred because of the transformation.
    """

    orders = [x[0] for x in ttset]
    inv_count = 0
    for i in range(len(ttset)):
        for j in range(i+1, len(ttset)):
            if (orders[i] > orders[j]):
                inv_count += 1
            else:
                pass
    return inv_count


def permutation_cycles(
    ttset: Sequence
) -> List:

    """ Given a transformed version of the series with order numbers,
    returns the sequence of permutations cycles"""

    result = []
    for i, el in enumerate(ttset):
        if el[0] == i:
            result.append(tuple([i]))
        else:
            pair = tuple(sorted([i,el[0]]))
            if pair not in result:
                result.append(pair)
    return result


def dyad_interval_pairs(
    ttset: Sequence,
) -> List:

    """ Given a tone row (in usual form, NOT with order numbers),
    returns the intervals between consecutive dyads
    """

    return [(ttset[i]-ttset[i-1]) % 12 for i in range(1,12,2)]


def compare_dyads(
    row1: Sequence,
    row2: Sequence
) -> Sequence:
    """ Given two tone rows, compare to see if
    they have the same dyads as permutations of one another.
    """

    dyads1 = [tuple(sorted([row1[i],row1[i+1]])) for i in range(0,12,2)]
    dyads2 = [tuple(sorted([row2[i],row2[i+1]])) for i in range(0,12,2)]
    if sorted(dyads1) != sorted(dyads2):
        print("FAIL")
        return False
    else:
        result = []
        for i,x in enumerate(dyads1):
            for j,y in enumerate(dyads2):
                if x == y:
                    if sorted(tuple([i+1,j+1])) not in result and i != j:
                        result.append(sorted(tuple([i+1,j+1])))
    return result


def row_partition(
    row: Sequence,
    part: Sequence,
) -> List:

    """ Given a twelve-tone row and a list of integer which is a partition of 12,
    returns the row partitioned in chunks equal to each member of the partition.
    """

    new = []
    for i in part:
        a = row[:i]
        new.append(a)
        row = row[i:]

    return new


def boulez_matrix_multiplication(
    row: Sequence,
    part: Sequence,
) -> dict:

    """Given a twelve-tone row and a partition of the number 12,
    applies Pierre Boulez's multiplication.
    """

    row_part = row_partition(row,part)
    first = row_part[0]
    if len(first) <= 3:
        k = first[-1]
    else:
        k = first[2]
    result = dict()
    for m in row_part:
        for i in row_part:
            raw_key = [tuple(m),tuple(i)]
            key = tuple(raw_key)
            mult = complex_multiplication(m,i,k)
            result[key] = mult

    return result


def boulez_matrix_multiplication_palette(
    row: Sequence,
    part: Sequence,
) -> dict:


    """Applies Boulez's multiplication to all rotations of a partitioned twelve-tone row.
    """

    result = dict()
    rotations_part = all_rotations(part)
    for rot in rotations_part:
        result[tuple(rot)] = boulez_matrix_multiplication(row,rot)

    return result
    
    
def pedro_chords(
    row: Sequence,
    chord_len: int = 3,
    interval_range: list = [3,6]
) -> List:

    """Returns the 'Pedro Chords' of a twelve-tone row.
    These chords are created by stacking adjacent parts of the row which are
    separated by the interval range described.
    """

    pairs = dict()
    for i, pitch_class in enumerate(row):
        rotated_row = rotate_sequence(row, i)
        candidates = [element for element in rotated_row if interval_range[0] <= 
        (element-rotated_row[0]) % 12 <= interval_range[1]]
        pairs[pitch_class] = candidates[0]
    chords = []
    for pitch_class in row:
        chord = [pitch_class]
        count = 0
        while count < chord_len - 1:
            chord.append(pairs[chord[-1]])
            count += 1
        chords.append(chord)

    return chords



def pedro_chords_palette(
    row: Sequence,
    chord_len: int = 3,
    interval_range: List = [3,6],
) -> dict:

    """Returns the pedro chords for all of the basic forms of the given row.
    """
    final = dict()
    matriz = twelve_tone_matrix(row)
    
    inverse = list(matriz[0])
    retrograde = row[::-1]
    ri = inverse[::-1]
    
    prime_chords = pedro_chords(row, chord_len, interval_range)
    inv_chords = pedro_chords(inverse, chord_len, interval_range)
    retrograde_chords = pedro_chords(retrograde, chord_len, interval_range)
    ri_chords = pedro_chords(ri, chord_len, interval_range)

    all_chords = [prime_chords, inv_chords, retrograde_chords, ri_chords]
    forms = ["P", "I", "R", "RI"]
    for i in range(4):
        final[forms[i]] = all_chords[i]

    return final