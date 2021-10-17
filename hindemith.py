"""
Module with the tools for Paul Hindemith's chord analysis.
"""


from typing import Dict, List, Sequence, Union
from itertools import combinations


def root_interval(
    ord_interval_1: Sequence,
) -> int:


    """Given two pitches or pitch classes, returns the root of the interval,
    based on Paul Hindemith's theory.
    """

    ord_interval = [x % 12 for x in ord_interval_1]
    interval = ord_interval[1] - ord_interval[0]
    mod_interval = interval % 12
    result = 0
    if interval > 0:
        if interval in [3,4,7,8,9]:
            result = ord_interval_1[0]
        elif interval in [1,2,5,10,11]:
            result = ord_interval_1[1]
        else:
            result = 0
    else:
        if mod_interval in [3,4,5,8,9]:
            result = ord_interval_1[1]
        elif mod_interval in [1,2,7,10,11]:
            result = ord_interval_1[0]
        else:
            result = 0

    return result


def no_root(
    chord_1: Sequence,
) -> bool:


    """Returns True if the chord has a root, False if it doesn't.
    """

    result = 0
    chord = [x % 12 for x in chord_1]
    pair_combinations = list(combinations(chord, 2))
    intervals = [(abs(x[1]-x[0]))%12 for x in pair_combinations]
    strong_intervals = [intervals.count(4),intervals.count(8),intervals.count(5),intervals.count(7)]
    if intervals.count(6) > 0:
        if max(strong_intervals) == 0:
            result = True
        else:
            result = False
    else:
        if len(chord) > 3:
            result = False
        else:
            aug = [chord[0], (chord[0] + 4) % 12, (chord[0] + 8) % 12]
            quart = [chord[0], (chord[0] + 5) % 12, (chord[0] + 10) % 12]
            if sorted(chord) in [aug, quart]:
                result = True
            else:
                result = False

    return result


def interval_strength(
    pair: Sequence,
) -> int:

    """Returns the strength of the interval.
    """

    result = 0
    interval = (pair[1] - pair[0]) % 12
    if interval > 6: 
        interval = 12 - interval
    if interval == 6:
        result = 0
    else:
        result = interval
    
    return result


def find_root(
    chord: Sequence,
) -> Union[int, None]:

    """Returns the root of a given chord, if it exists.
    If it doesn't, returns None.
    """

    result = 0
    if no_root(chord) == True:
        result = None
    else:
        all_intervals = list(combinations(chord, 2))
        strengths = [interval_strength(interval) for interval in all_intervals]
        high_indices = []
        for i in range(len(strengths)):
            clean_strengths = [x for x in strengths if x]
            if strengths[i] == max(clean_strengths):
                high_indices.append(i)
    result = root_interval(all_intervals[high_indices[0]])

    return result


def interval_root_force(
    chord: Sequence,
) -> List:

    """Given a chord, return a list of pairs of the type [root,strength] for
    all of the intervals presente.
    """

    result = []
    pair = list(combinations(chord,2))
    for interval in pair:
        result.append([root_interval(interval),interval_strength(interval)])

    return result


def hindemith_classification(
    chord: Sequence,
) -> str:

    """Returns Hindemith's chord classification for a given chord.
    """

    pair = list(combinations(chord, 2))
    intervals = [(abs(x[1]-x[0]))%12 for x in pair]
    root_force_values = interval_root_force(chord)
    forces = [x[1] for x in root_force_values]
    tritones = intervals.count(6)
    root = root_force_values[forces.index(max([x[1] for x in root_force_values]))][0]
    if no_root(chord):
      if 6 in intervals:
          chord_type = "VI"
      else:
          chord_type = "V"
    else:
        if 6 in intervals:
            if 1 in intervals or 11 in intervals:
                if root == chord[0]:
                    chord_type = 'IV.1'
                else:
                    chord_type = 'IV.2'
            else:
                if (10 in intervals and 2 not in intervals) and tritones == 1:
                    if root == chord[0]:
                        chord_type = 'IIa'
                    else:
                        chord_type = 'IIb.2'
                elif (10 in intervals or 2 in intervals) and tritones == 1:    
                    if root == chord[0]:
                        chord_type = 'IIb.1'
                    else:
                        chord_type = 'IIb.2'
                elif tritones >= 2:
                    chord_type = 'IIb.3' 
        else:
            if 1 in intervals or 2 in intervals or 10 in intervals or 11 in intervals:
                if root == chord[0]:
                    chord_type = 'III.1'
                else:
                    chord_type = 'III.2'
            else:
                if root == chord[0]:
                    chord_type = 'I.1'
                else:
                    chord_type = 'I.2'
                    
    return chord_type