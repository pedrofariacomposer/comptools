from scamp import *
import random
from itertools import cycle

def text_to_music(text, instrument1, instrument2, off1=-20, vol1=0.5, dur1=0.5, off2=0, vol2=0.8, dur2=0.5, wait1=0.2, wait2=0.2, wait3=0.2):
    for char in text:
        if char == " ":
            wait(wait1)
        elif char.isalnum():
            instrument1.play_note(ord(char) + off1, vol1, dur1)
        else:
            wait(wait2)
            instrument2.play_note(ord(char) + off2, vol2, dur2)
            wait(wait3)


def build_chord(interval_options, num_notes, pitch_center, round_transposition=True):
    chord = [0]
    while len(chord) < num_notes:
        chord.append(chord[-1] + random.choice(interval_options))
    transposition = pitch_center - sum(chord) / len(chord)
    if round_transposition:
        transposition = round(transposition)
    return [p + transposition for p in chord]


def do_isorhythm(instrument, color, talea, voluminor=(1.0,)):
    for pitch, volume, dur in zip(cycle(color),cycle(voluminor),cycle(talea)):
        instrument.play_note(pitch, volume, dur)


def is_consonant(p1, p2, intervals=[0,3,4,7,8,9]):
    if abs(p1-p2) in intervals:
        return True
    else:
        return False


def make_counterpoint(cantus_firmus, counterpoint, intervals=[0,3,4,7,8,9], motion_option=[1,2,-1,2,3,-3,4,-4]):
    i = 0
    while i < len(cantus_firmus):
        if i+1 >= len(cantus_firmus):
            break
        else:
            for option in motion_option:
                if cantus_firmus[i+1] > cantus_firmus[i]:
                    option *= -1
                if is_consonant(cantus_firmus[i+1], counterpoint[i] + option, intervals=intervals):
                    counterpoint.append(counterpoint[i] + option)
                    break
            else:
                break
            i += 1
    return counterpoint


    def fib_cycle(instrument, modulo, starting_pitch, dur=0.25, vol=0.7, length=0, a=1, b=1):
        if length == 0:
            while True:
                instrument.play_note(starting_pitch + a, vol, dur)
                a, b = b, (a + b) % modulo
        else:
            count = 0
            while count < length:
                instrument.play_note(starting_pitch + a, vol, dur)
                a, b = b, (a + b) % modulo
                count += 1