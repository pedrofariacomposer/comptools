import music21 as m21
import abjad

def parse_notes(listNotes):
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

def lily21(notes):

    '''Given a container of Music21 notes or chords, returns a Lilypond representation
    of that container.
    WARNING: DOES NOT YET HANDLE TUPLETS!'''

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

testcont = [m21.note.Note(quarterLength=0.75),m21.note.Note(),m21.note.Note(),
m21.note.Rest(), m21.chord.Chord([64,67,69])]

filename = "comptools/test_tup.xml"

piece = list(m21.converter.parse(filename).flat.getElementsByClass(["Note","Rest","Chord"]))

f_no = piece[0]

# print(1/f_no.duration.tuplets[0].tupletMultiplier())
# print(f_no.duration.components)
# print(f_no.duration.tuplets[0].type)


    
new_string = lily21(parse_notes(piece))

voice_1 = abjad.Voice(new_string, name="Voice 1")
voice_2 =abjad.Voice(new_string, name="Voice 2")
abjad.mutate.transpose(voice_2, "-m3")
staff_1 = abjad.Staff([voice_1,voice_2], name="Staff 1")
abjad.mutate.scale(staff_1[0][0][0],abjad.Multiplier(2))
abjad.show(staff_1 ,output_directory=r"C:/Users/Pedro/Google Drive/Python_Scripts/test abjad", should_open=False)