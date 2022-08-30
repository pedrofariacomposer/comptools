"""
Module with tools extending the Abjad library.
"""

import abjad
from abjadext import rmakers
from .basic_tools import flatten_sequence
from .lisparser import LisParser
import random
from typing import Sequence, List, Union

def make_staff_divisions(
    divs: Sequence,
    props: Sequence,
    div_points: Sequence
) -> abjad.Staff:

    """Makes a staff on which each measure is a number from divs,
    each measure's proportion is a number in props, and some pitches
    given by div_points are altered by numbers in props.
    """


    divisions = [(x,4) for x in divs]
    stack = rmakers.stack(
        rmakers.note(),
        rmakers.beam(),
        )
    selections = stack(divisions)
    staff = abjad.Staff(selections, lilypond_type="RhythmicStaff")
    for i, log_tie in enumerate(abjad.select.logical_ties(staff)):
        time_sig = abjad.TimeSignature(divisions[i])
        tup = abjad.mutate.logical_tie_to_tuplet(log_tie, props[i])
        tup.hide = tup.trivial()
        abjad.attach(time_sig, tup[0])

    for i in reversed(range(len(div_points))):
        prop = (1,) * divs[i]
        log_tie = abjad.select.logical_tie(staff,div_points[i])
        indicators = abjad.get.indicators(log_tie[0])
        tup = abjad.mutate.logical_tie_to_tuplet(log_tie, prop)
        tup.hide = tup.trivial()
        if len(indicators) != 0:
            abjad.attach(indicators[0],abjad.select.logical_tie(staff,div_points[i])[0])
            indicators = abjad.get.indicators(log_tie[0])

    for tup in abjad.select.tuplets(staff):
        tup.hide = tup.trivial()
    return staff


def ferneyhough(
    master_divs: Sequence,
) -> abjad.Score:

    """Applies a Brian Ferneyhough process using the make_staff_divisions
    """

    divisions = [(x,8) for x in master_divs]
    staves = []
    for k in range(len(master_divs)):
        divs = master_divs[k:] + master_divs[0:k]
        props = [(1,) * x for x in reversed(divs)]
        div_points = abjad.math.cumulative_sums(divs)[1:-1]
        staff = make_staff_divisions(master_divs,props,div_points)
        staves.append(abjad.mutate.copy((staff)))
    new_score = abjad.Score(staves, simultaneous=True)

    return new_score


def make_rtm(
    old_rtm: str,
    new_data: Sequence,
) -> str:

    """Given a OpenMusic rhythm tree and a sequence of numbers, create a new tree
    with the same shape as the given one.
    """
    new_rtm = "(1 ("
    it = iter(new_data)
    for x in old_rtm[4:]:
        if x.isalnum():
            new_rtm += str(next(it))
        else:
            new_rtm += x
    return new_rtm


def make_tree(
    rtm: str,
    dur: Sequence, 
    time_sig: bool = False,
) -> abjad.Staff:

    """Given an OpenMusic rhythm tree, a total duration, creates the 
    actual tree. If time_sig is True, returns an actual staff. Else, returns
    an abjad object to be placed in a staff.
    """
    ircamparser = abjad.rhythmtrees.RhythmTreeParser()
    tree = ircamparser(rtm)[0](dur)
    if time_sig:
        staff = abjad.Staff(abjad.mutate.copy(tree), lilypond_type="RhythmicStaff")
        abjad.attach(abjad.TimeSignature(dur), abjad.select.leaves(staff)[0])
        return staff
    else:
        return tree


def tree_rotations(
    rtm: str,
    dur: Sequence,
) -> abjad.Score:

    """Given an OpenMusic rhythmm tree and its duration, returns a score
    comprised of all the rotations of the elements of the tree.
    """
    parsed_tree = flatten_sequence(LisParser(rtm).recursive_unpack())[1:]
    rotations = []
    for i in range(len(parsed_tree)):
        new_rot = parsed_tree[i:] + parsed_tree[0:i]
        if new_rot not in rotations:
            rotations.append(new_rot)

    staves = []
    for rot in rotations:
        new_rtm = make_rtm(rtm, rot)
        staff = make_tree(new_rtm, dur, time_sig=True)
        staves.append(staff)
    score = abjad.Score(staves, simultaneous=True)
    return score