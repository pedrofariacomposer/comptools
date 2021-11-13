"""
Module with the tools to create new pieces based on the
Partitional Analysis of an existing piece.
"""


import music21 as m21
from collections import defaultdict
import random
from typing import Dict, Sequence, List


def make_catalog_dict(
    filename: str,
) -> Dict:

    """Given a xml or MIDI file, creates a catalog.
    Each measure of the original file must have complete independence between parts.
    That means that the partitional analysis of each point of a measure must be 1 ** n,
    with n being the number of parts.
    """

    piece = m21.converter.parse(filename)
    num_parts = len(piece.parts)
    measures = [part.getElementsByClass("Measure") for part in piece.parts]
    num_measures = len(measures[0])

    master_list = []
    final_dict = defaultdict(list)

    for j in range(num_measures):
        mm_list = []
        for i in range(num_parts):
            cur_measure = measures[i][j]
            durs = [x.quarterLength for x in cur_measure.getElementsByClass("GeneralNote")]
            mm_list.append(durs)
        master_list.append(mm_list)

    for mm in master_list:
        dur_mm = sum(mm[0])
        final_dict[dur_mm].append(mm)

    return final_dict               
              

def part_frags(
    part: Sequence,
    catalog: Dict,
    dur: float,
) -> List:

    """Creates a random rhythmic fragment that conforms to a
    given partition. The argument 'dur' is the length of the measure.
    """

    num_parts = len(part)
    possible_melodies = random.choice(catalog[dur])
    choices = random.sample(possible_melodies, num_parts)
    result = []
    for i in range(num_parts):
        for k in range(part[i]):
            result.append(choices[i])

    return result


def make_full_scale(
    scale: List,
    rang: List,
) -> List:

    """Given a scale and a range, creates a full scale within the range.
    """

    full_scale = []
    count = 0
    i = 0
    while True:
        if i == len(scale):
            i = 0
            count += 1
        new_nota = rang[0] + (12*count) + scale[i]
        full_scale.append(new_nota)
        i += 1
        if full_scale[-1] >= rang[1]:
            break

    return full_scale


def create_part_melody(
    frag: List,
    scale: List,
    rang: List,
) -> List:

    """Given a rhythmic fragment, a scale and a range, creates a random melody,
    with pitches and durations.
    """

    full_scale = make_full_scale(scale,rang)
    num_notes = len(frag)
    melody = random.choices(full_scale, k=num_notes)
    result = [(melody[i],frag[i]) for i in range(len(melody))]
    
    return result