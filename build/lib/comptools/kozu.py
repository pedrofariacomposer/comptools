"""
Module that implements Fernando Kozu's description
of a Brian Ferneyhough process.
"""

from .basic_tools import flatten_sequence
import pycse.lisp
from typing import List, Sequence, Union


def make_beat_cycle(
    beat_cycle: Sequence,
    num_bars: int,
) -> List:

    """Given a beat cycle, extends it for the given number of bars.
    """

    result = []
    i = 0
    while i < num_bars:
        bar = []
        for j in range(beat_cycle[i % len(beat_cycle)]): bar.append(1)
        result.append(bar)
        i += 1

    return result

def make_bar_cycle(
    bar_cycle: Sequence,
    num_bars: Sequence,
) -> List:

    """Given a bar cycle, extends it for the given number of bars.
    """

    result = []
    i = 0
    while i < num_bars:
        result.append(bar_cycle[i % len(bar_cycle)])
        i += 1
    return result


def kozu(
    bars_cycle: Sequence,
    beat_cycle: Sequence,
    num_bars_cycles: Sequence,
    sub_pos: Sequence,
    sub_nature: Sequence,
    high_cycle: Sequence,
    high_mid_cycle: Sequence,
    low_mid_cycle: Sequence,
    low_cycle: Sequence,
    ranges: Sequence,
) -> Union[str,str]:

    """Implements Fernando Kozu's description of a Brian Ferneyhough process.
    """

    beat_cycles = make_beat_cycle(beat_cycle,num_bars_cycles)
    bar_cycles = make_bar_cycle(bars_cycle,num_bars_cycles)
    flat_cycles = flatten_sequence(beat_cycles)

    sub_inds = [[-1,0]]
    k = 0
    while sub_inds[-1][0] < len(flat_cycles):
        pos = sub_pos[k % len(sub_pos)] + sub_inds[k][0]
        nat = sub_nature[k % len(sub_nature)]
        pair = [pos,nat]
        sub_inds.append(pair)
        k += 1
    sub_inds.pop(0)
    if sub_inds[-1][0] > len(flat_cycles): sub_inds.pop()
    sub_ind_dict = dict()
    for pair in sub_inds: sub_ind_dict[pair[0]] = pair[1]

    sub_i = [x[0] for x in sub_inds]
    sub_value = [x[1] for x in sub_inds]
    heads = [sub_i[0]]
    for i in range(1,len(sub_i)):
        backlist = sub_value[0:i]
        heads.append(sub_i[i] + sum(backlist))
    sub_ind_dict = dict()
    for i in range(len(heads)):
        sub_ind_dict[heads[i]] = sub_value[i]
    full_flat = [x for x in flat_cycles]
    for key in sub_ind_dict.keys(): full_flat += [1] * (sub_ind_dict[key])
    high_inds = [high_cycle[0] - 1]
    h = 1
    while high_inds[-1] < len(full_flat):
        value = high_inds[-1] + high_cycle[h % len(high_cycle)]
        high_inds.append(value)
        h += 1
    for i, x in enumerate(high_inds):
        low_heads = [y for y in heads if y <= x]
        soma = high_inds[i] + len(low_heads)
        soma_low = [x for x in heads if x <= soma and x not in low_heads]
        soma += len(soma_low)
        high_inds[i] = soma
    if high_inds[-1] > len(full_flat):
        while high_inds[-1] > len(full_flat): high_inds.pop()
    high_mid_inds = [high_mid_cycle[0] - 1]
    h = 1
    while high_mid_inds[-1] < len(full_flat):
        value = high_mid_inds[-1] + high_mid_cycle[h % len(high_mid_cycle)]
        high_mid_inds.append(value)
        h += 1
    for i, x in enumerate(high_mid_inds):
        low_heads = [y for y in heads if y <= x]
        soma = high_mid_inds[i] + len(low_heads)
        soma_low = [x for x in heads if x <= soma and x not in low_heads]
        soma += len(soma_low)
        high_mid_inds[i] = soma
    if high_mid_inds[-1] > len(full_flat):
        while high_mid_inds[-1] > len(full_flat): high_mid_inds.pop()
    low_mid_inds = [low_mid_cycle[0] - 1]
    h = 1
    while low_mid_inds[-1] < len(full_flat):
        value = low_mid_inds[-1] + low_mid_cycle[h % len(low_mid_cycle)]
        low_mid_inds.append(value)
        h += 1
    for i, x in enumerate(low_mid_inds):
        low_heads = [y for y in heads if y <= x]
        soma = low_mid_inds[i] + len(low_heads)
        soma_low = [x for x in heads if x <= soma and x not in low_heads]
        soma += len(soma_low)
        low_mid_inds[i] = soma
    if low_mid_inds[-1] > len(full_flat):
        while low_mid_inds[-1] > len(full_flat): low_mid_inds.pop()
    low_inds = [low_cycle[0] - 1]
    h = 1
    while low_inds[-1] < len(full_flat):
        value = low_inds[-1] + low_cycle[h % len(low_cycle)]
        low_inds.append(value)
        h += 1
    for i, x in enumerate(low_inds):
        low_heads = [y for y in heads if y <= x]
        soma = low_inds[i] + len(low_heads)
        soma_low = [x for x in heads if x <= soma and x not in low_heads]
        soma += len(soma_low)
        low_inds[i] = soma
    if low_inds[-1] > len(full_flat):
        while low_inds[-1] > len(full_flat): low_inds.pop()
    full_high = []
    h = 0
    full_mid_high = []
    mh = 0
    full_mid_low = []
    ml = 0
    full_low = []
    l = 0
    k = 0
    while k < len(full_flat):
        if k in high_inds:
            full_high.append(high_cycle[h % len(high_cycle)] + ranges[3])
            h += 1
        else:
            full_high.append(0)
        if k in high_mid_inds:
            full_mid_high.append(high_mid_cycle[h % len(high_mid_cycle)] + ranges[2])
            mh += 1
        else:
            full_mid_high.append(0)
        if k in low_mid_inds:
            full_mid_low.append(low_mid_cycle[h % len(low_mid_cycle)] + ranges[1])
            ml += 1
        else:
            full_mid_low.append(0)
        if k in low_inds:
            full_low.append(low_cycle[h % len(low_cycle)] + ranges[0])
            l += 1
        else:
            full_low.append(0)
        k += 1
    pitch_groups = [[full_high[i],full_mid_high[i],full_mid_low[i],full_low[i]] for i in range(len(full_flat))]
    final_pitches = []
    for i in range(len(full_flat)):
        group = pitch_groups[i]
        if group.count(0) == 4: pass
        else:
            available = [x for x in group if x != 0]
            final_pitches.append(max(available) * 100) 
    rests_raw = [i for i in range(len(pitch_groups)) if pitch_groups[i].count(0) == 4]
    rests = [x for x in rests_raw if x not in heads]
    for i in range(len(full_flat)):
        if i in rests: full_flat[i] = -1
    new_flat = []
    k = 0
    while k < len(full_flat):
        if k in heads:
            cur = full_flat[k]
            size_group = sub_ind_dict[k]
            group = full_flat[k+1: size_group+k+1]
            #full_flat[k] = [cur,group]
            new_flat.append([cur,group])
            k += len(group)+1
        else:
            new_flat.append(full_flat[k])
            k += 1
    final_proportions = []
    k = 0
    for bar in beat_cycles:
        group = new_flat[k:k+len(bar)]
        final_proportions.append(group)
        k += len(group)
    final_piece = [[bar_cycles[i],final_proportions[i]] for i in range(len(bar_cycles))]
    final_piece_om = ["?"]
    final_piece_om.append(final_piece)
    final_piece_om = final_piece_om.lisp.replace('"',"")

    return final_piece_om, final_pitches.lisp