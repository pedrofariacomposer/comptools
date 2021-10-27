"""
Module with the advanced tools of the Comp_Tools library.
"""


from .basic_tools import flatten_sequence, rotate_sequence
from .lisparser import LisParser
from typing import Sequence, List

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




