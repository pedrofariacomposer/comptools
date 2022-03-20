"""
Module with the twelve-tone tools of the Comp_Tools library.
"""


from .basic_tools import *
from .parsepy import accel_asc
from pandas import DataFrame
from numpy import reshape
from typing import Sequence, List, Dict, Tuple
from itertools import permutations
from .master_perms import *


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

def morris_rot_trichord(row):
    chunk_1 = row[0:3]
    chunk_2 = row[3:6]
    chunk_3 = row[6:9]
    chunk_4 = row[9:12]

    return chunk_4 + chunk_3 + chunk_2 + chunk_1


def twelve_tone_pallette(
    row: Sequence,
    extended: bool = False,
    really_extended: bool = False,
) -> Dict:

    """Returns all the classic row forms of a given row.
    If extended = True, returns all 96 forms from Starr and Morris.
    If really_extended = True, also returns the trichord retrogrades of all row forms
    """

    r_form = retrograde(row)

    
    if extended == False and really_extended == False:
        result = dict()

        for ind in range(len(row)):
            t = transposition(row,ind)
            i = inversion(row,ind)
            rs = transposition(r_form,ind)
            ris = inversion(r_form,ind)
            if t not in result.values():
                label = "T" + str(ind)
                result[label] = t
            if i not in result.values():
                label = "I" + str(ind)
                result[label] = i
            if rs not in result.values():
                label = "R" + str(ind)
                result[label] = rs
            if ris not in result.values():
                label = "RI" + str(ind)
                result[label] = ris
            
    if extended == True:
        result = dict()
        prov_result = twelve_tone_pallette(row)
        for key, x in prov_result.items():
            result[key] = x
            mult_5 = multiplication(x,5)
            if mult_5 not in prov_result.values():
                label = "M" + key
                result[label] = mult_5
        
    if really_extended == True:
        result = dict()
        prov_result = twelve_tone_pallette(row, extended)
        for key, x in prov_result.items():
            result[key] = x
            mrt = morris_rot_trichord(x)
            if mrt not in prov_result.values():
                label = "Rot" + key
                result[label] = mrt
    return result


def find_combs(
        rows: Sequence,
        part: Sequence
) -> Sequence:
    
    """Given a list of rows and a partition of 12,
    returns how the partition can break the list of rows, if it can
    in any way. Else, returns False.
    """
    
    size = len(rows)
    
    if size < len(part):
        return False,"Rows and part have different lengths"
    
    else:
        for i in range(len(part)):
            if part[i] > len(rows[i]):
                return False, "There's a part that's bigger than a row"
    
    pieces = [rows[i][0:part[i]] for i in range(len(part))]
    rests = [rows[i][part[i]:] for i in range(len(part))]
    piece_sum = []
    for p in pieces:
        piece_sum += p
    if sorted(piece_sum) == list(range(12)):
        if len(pieces) < size:
            for i in range(len(pieces),size):
                rests.append(rows[i])
        return True,pieces,rests
    else:
        return False,rests


def all_partitions(
        ps: Sequence
) -> Sequence:
    
    """Given a list of rows, returns all the ways this list
    can be partitioned.
    """
    
    size = len(ps)
    result = [[] for _ in range(size)]
    if size <= 6:
        all_perms = up_to_six
    elif 6 < size <= 9:
        all_perms = up_to_six + six_to_nine
    elif 9 < size <= 12:
        all_perms = up_to_six + six_to_nine + ten_to_twelve
    for i in range(0,size):
        if i == 0:
            for p in all_perms:
                a = find_combs(ps,p)
                if a[0] == True:
                    result[0].append([ps,p,a[1],a[2]])
        else:
            for r in result[i-1]:
                g = [y for y in r[3] if len(y) != 0]
                for p in all_perms:
                    a = find_combs(g,p)
                    if a[0] == True:
                        result[i].append([r,p,a[1],a[2]])
    return result[size-1]


def find_partitions_from_result(
    sequence: Sequence,
) -> List:

    """Given the output from all_partitions, finds the partition
    in one of the elements from said output.
    """
    
    if isinstance(sequence, List):
        return [a for i in sequence for a in find_partitions_from_result(i)]
    else:
        return [tuple(sorted(x)) for x in [sequence] if isinstance(x,Tuple)]

    
def imbricated(
        row: Sequence,
        size: int = 3,
) -> List:
    
    """Returns a list of the imbricated trichords (or some other sized set) 
    in a given row.
    """   
    
    if size > len(row):
        print("invalid size of imbricated set")
        return
    else:
        result = []
        for i in range(len(row)-size+1):
            result.append(row[i:i+size])
            return result



def rotate_subset(
    row: Sequence,
    size: int = 3,
    pattern: Sequence = [3,2,1,0],
) -> List:
    
    """Rotates the trichords (or some other division of a row),
    by the specified pattern.
    """    
    
    if len(row) % size != 0:
        print("invalid size of subset")
        return
    elif size * len(pattern) != len(row):
        print("invalid size of pattern of arrangement")
        return
    else:
        chunks = [row[i:i+size] for i in range(0,len(row),size)]
        result = []
        for j in pattern:
            result += chunks[j]
            return result


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