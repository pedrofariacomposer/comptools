"""
Module with the advanced tools of the Comp_Tools library.
"""


from .basic_tools import flatten_sequence, rotate_sequence
from .lisparser import LisParser
from typing import Sequence, List
import music21 as m21

def rot_measure(
    measure: Sequence,
    rot_num: int,
) -> List:

    """Rotates the positions of the OpenMusic representation of a measure.
    """

    measure_lisp = measure.lisp
    flat_lisp = flatten_sequence(measure)
    flat_rot = rotate_sequence(flat_lisp,rot_num)
    for x in ["0", ".", "-"]: measure_lisp = measure_lisp.replace(x,"")
    indexes = []
    for ind,x in enumerate(measure_lisp):
        if x not in ["(",")"," "]: indexes.append(ind)
    str_lisp = list(measure_lisp)
    for i in range(len(indexes)): str_lisp[indexes[i]] = str(flat_rot[i])
    new_lisp = "".join(str_lisp)
    new_first = LisParser(new_lisp).recursive_unpack()

    return new_first


def parse_notes(
    listNotes: List,
) -> List:

    """Given a list of music21 notes, rests and/or chordsd,
    group the tuplets as a single list, using the tuplets.type attribute.
    """

    result = []
    i = 0

    while i < len(listNotes):
        el = listNotes[i]
        tups = el.duration.tuplets
        if len(tups) == 0:
            result.append(el)
            i += 1
        else:
            t_group = [el]
            j = 1
            while el.duration.tuplets[0].type != "stop":
                el = listNotes[i + j]
                t_group.append(el)
                j += 1
            result.append(t_group)
            i += len(t_group)
    return result


def lily21(
    notes: List,
) -> List:

    '''Given a container of Music21 notes or chords, returns a Lilypond representation
    of that container!'''

    pcdict = {0:"c", 1: "cs", 2: 'd', 3: 'ef',
            4: 'e', 5: 'f', 6:'fs', 7:'g', 8:'af',
            9:'a', 10: 'bf', 11:'b'}

    def lilyOctaveMark(pitch):
        if 60 <= pitch < 72:
            return "'"
        elif 72 <= pitch < 84:
            return "''"
        elif 84 <= pitch < 96:
            return "'''"
        elif 96 <= pitch < 108:
            return "''''"
        elif 108 <= pitch < 120:
            return "'''''"
        elif 48 <= pitch < 60:
            return ""
        elif 36 <= pitch < 48:
            return ","
        elif 24 <= pitch < 36:
            return ",,"
        elif 12 <= pitch < 24:
            return ",,,"
        else:
            return     

    result = ''

    for nota in notes:
        if isinstance(nota, m21.note.Note):
            comps = nota.duration.components[0]
            durString = str(int(4 / comps[2])) + (int(comps[1]) * '.')
            pitchNumber = nota.pitch.midi
            pitchString = pcdict[pitchNumber % 12] + lilyOctaveMark(pitchNumber)
            result += pitchString + durString + " "
        elif isinstance(nota, m21.note.Rest):
            comps = nota.duration.components[0]
            durString = str(int(4 / comps[2])) + (int(comps[1]) * '.')
            pitchString = "r"
            result += pitchString + durString + " "
        elif isinstance(nota, m21.chord.Chord):
            comps = nota.duration.components[0]
            durString = str(int(4 / comps[2])) + (int(comps[1]) * '.')
            chordString = "<"
            for i, el in enumerate(nota):
                pitchNumber = el.pitch.midi
                pitchString = pcdict[pitchNumber % 12] + lilyOctaveMark(pitchNumber)
                if i != len(nota) - 1:
                    chordString += pitchString + " "
                else:
                    chordString += pitchString + ">" + durString
            result += chordString
        elif isinstance(nota, list):
            prov_result = lily21(nota)
            mult = str(1/nota[0].duration.tuplets[0].tupletMultiplier())
            new_result = '\\tuplet ' + mult + " {" + prov_result + "} "
            result += new_result
    return result


