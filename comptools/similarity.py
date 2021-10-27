"""
Module with the similarity tools of the Comp_Tools library.
For more information, see:
Isaacson - Similarity of Interval-Class Content Between Pitch-Class Sets: The IcVSIM Relation
"""


from .basic_tools import interval_vector, prime_form
from ._all_classes import allClasses
from numpy import sqrt, reshape, array
from typing import Sequence, List
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd

def forte(
    pcset1: Sequence,
    pcset2: Sequence,
) -> str:

    """Returns the Forte similarity relation between two pitch class sets.
       If the sets don't have the same cardinality, the function returns None.
    """
    if len(pcset1) != len(pcset2):
        forte_relation = None
    else:
        v1 = interval_vector(pcset1)
        v2 = interval_vector(pcset2)
        common_entries = [i for i in range(6) if v1[i] == v2[i]]
        if len(common_entries) == 0:
            forte_relation = "R0"
        elif len(common_entries) == 4:
            diff_entries = [i for i in range(6) if i not in common_entries]
            pair1 = [v1[x] for x in diff_entries]
            pair2 = [v2[x] for x in diff_entries]
            if sorted(pair1) == sorted(pair2):
                forte_relation = "R1"
            else:
                forte_relation = "R2"
    
    return forte_relation
            
            
def morris(
    pcset1: Sequence,
    pcset2: Sequence,
) -> int:

    """Returns the Morris similarity relation between two pitch class sets.
    """

    vector1 = interval_vector(pcset1)
    vector2 = interval_vector(pcset2)
    result = 0
    for i in range(len(vector1)):
        result += abs(vector1[i]-vector2[i])
    return result


def lord(
    pcset1: Sequence,
    pcset2: Sequence,
) -> float:

    
    """Returns the Lord similarity relation between two pitch class sets.
    """

    return morris(pcset1,pcset2) / 2


def rahn(
    pcset1: Sequence,
    pcset2: Sequence,
) -> int:

    
    """Returns the Rahn similarity relation between two pitch class sets.
    """

    vector1 = interval_vector(pcset1)
    vector2 = interval_vector(pcset2)
    result = 0
    for i in range(6):
        if (vector1[i] == 0 or vector2[i] == 0):
            pass
        else:
            result += vector1[i] + vector2[i]
    return result
            

def rahn_mod(
    pcset1: Sequence,
    pcset2: Sequence,
) -> float:

    
    """Returns the modified Rahn similarity relation between two pitch class sets.
    """
    
    original_rahn = rahn(pcset1, pcset2)

    return (1/2) * original_rahn / ((len(pcset1) * (len(pcset1) - 1)) +(len(pcset2) * (len(pcset2) - 1)))


def lewin(
    pcset1: Sequence,
    pcset2: Sequence,
) -> float:

    """Returns the Lewin similarity relation between two pitch class sets.
    """

    vector1 = interval_vector(pcset1)
    vector2 = interval_vector(pcset2)    
    factor1 = 0
    for i in range(6):
        factor1 += sqrt(vector1[i] * vector2[i])
    factor2 = ((len(pcset1) * (len(pcset1) - 1)) *(len(pcset2) * (len(pcset2) - 1)))

    return (2 * factor1) / sqrt(factor2)
    
    
def teitelbaum(
    pcset1: Sequence,
    pcset2: Sequence,
) -> float:

    """Returns the Teitelbaum similarity relation between two pitch class sets.
    """

    vector1 = interval_vector(pcset1)
    vector2 = interval_vector(pcset2)
    factor1 = 0
    for i in range(6):
        factor1 += (vector1[i]-vector2[i]) ** 2

    return sqrt(factor1)


def isaacson(
    pcset1: Sequence,
    pcset2: Sequence,
) -> float:

    """Returns the Isaacson similarity relation between two pitch class sets.
    """

    vector1 = interval_vector(pcset1)
    vector2 = interval_vector(pcset2)
    idv = [vector2[i]-vector1[i] for i in range(6)]
    idv_mean = sum(idv) / 6
    factor1 = 0
    for i in range(6):
        factor1 += (idv[i] - idv_mean) ** 2
    
    return sqrt(factor1/6)
    

def text_set_class(
    set_class: Sequence,
) -> str:

    """Converts a set class into a string representing its interval vector.
    """
    
    id_dict = {0: "one",
             1: "two",
             2: "three",
             3: "four",
             4: "five",
             5: "six"}
    result = ""

    for i, el in enumerate(interval_vector(set_class)):
        for _ in range(el):
            result += id_dict[i] + " "

    return result.rstrip()


def text_sim(
    sc1: Sequence,
    sc2: Sequence,
) -> float:

    """Returns the Text_Sim similarity measure between two pitch class sets.
    """
    sc1 = prime_form(sc1)
    sc2 = prime_form(sc2)
    
    corpus = [text_set_class(x) for x in sorted(allClasses)]
    vectorizer = TfidfVectorizer()
    trsfm = vectorizer.fit_transform(corpus)
    text_similarity = cosine_similarity(trsfm)
    names = [str(x) for x in sorted(allClasses)]
    df = pd.DataFrame(text_similarity.round(3), columns=names, index=names)
    return df[str(sc1)][str(sc2)]





def simile_table(
    pitch_class_sets1: Sequence,
    pitch_class_sets2: Sequence,
    simile_function,
) -> array :

    """Creates a numpy array with the similarities between two sets of pitch-class sets.
    """

    mod = ['X'] + pitch_class_sets2
    new = [mod]
    for i in pitch_class_sets1:
        new2 = [i]
        for j in pitch_class_sets2:
            a = simile_function(i, j)
            new2.append(a)
        new.append(new2)
    k = len(pitch_class_sets1) + 1
    n = len(pitch_class_sets2) + 1
    m = reshape(new, (k, n))
    
    return m