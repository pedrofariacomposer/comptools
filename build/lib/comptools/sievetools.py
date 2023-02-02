import copy
from math import lcm, ceil
import string


def _operationsSieves(firstBin, secondBin, opType):
    mmc = int(lcm(len(firstBin), len(secondBin)))
    sx = firstBin * int((mmc / len(firstBin)))
    sy = secondBin * int((mmc / len(secondBin)))
    onesFirst = [k for k in range(len(sx)) if sx[k] == 1]
    onesSecond = [k for k in range(len(sy)) if sy[k] == 1]

    orOnes = sorted(onesFirst + onesSecond)
    andOnes = [k for k in onesFirst if k in onesSecond]
    xorOnes = sorted([k for k in onesFirst if k not in onesSecond] + [k for k in onesSecond if k not in onesFirst])

    result = [0] * int(mmc)
    dictOps = {"|": orOnes, "&": andOnes, "+": xorOnes}

    for k in dictOps[opType]:
        result[k] = 1    
    return result


### ---------------------------------------------------###

class Residual():
    def __init__(self, m, shift=0):
        if isinstance(m, int):
            self.module = m
            self.shift = shift
        elif isinstance(m, str):
            parts = m.split("@")
            self.module = int(parts[0])
            self.shift = int(parts[1])
        self.bin = self._binary_repr()
        self.stringrepr = str(m) + "@" + str(shift)
        self.period = len(self.bin)


    def _binary_repr(self):
        result = [0] * self.module
        result[self.shift % self.module] = 1
        return result 
    
    def segment(self, minVal, maxVal, shift=0):
        result = []
        for x in range(minVal, maxVal+1):
            if self.bin[x % len(self.bin)] == 1:
                result.append(x)
        return [x + shift for x in result]

    def __repr__(self) -> str:
        return self.stringrepr


    def intersection(self, other):
        return _operationsSieves(self.bin, other.bin, "&")


    def union(self, other):
      return _operationsSieves(self.bin, other.bin, "|")

### ---------------------------------------------------###


class Compress():
    def __init__(self, src):
        self.src = list(copy.deepcopy(src))
        self.src.sort()
        self.match = []
        for num in self.src: #
            if num not in self.match:
                self.match.append(num)
        if len(self.match) <= 1:
            raise ValueError('segment must have more than one element')
        self.z = list(range(self.match[0], (self.match[-1] + 1))) 
        self.MAXMOD = len(self.z)
        self._process()
        self._compressedrepr()

    def _subset(self, sub, set):
        common = 0
        for x in sub:
            if x in set:
                common = common + 1
        if common == len(sub):
            return 1
        else: return 0

    def _find(self, n, part, whole):
        """given a point, and seiveSegment, find a modulus and shift that
        match"""
        m = 1
        while 1:
            obj = Residual(m, n)
            seg = obj.segment(self.z[0], self.z[-1])
            if self._subset(seg, part):
                return obj, seg
            elif self._subset(seg, whole):
                return obj, seg
            m = m + 1
            assert m <= self.MAXMOD

    def _process(self):
        self.residuals = []
        match = copy.copy(self.match)
        while 1:
            n = match[0]
            obj, seg = self._find(n, match, self.match)
            assert obj != None
            if obj not in self.residuals:
                self.residuals.append(obj)
                for x in seg:
                    if x in match:
                        match.remove(x)
            if len(match) == 0:
                break
    
    def _compressedrepr(self):
        self.stringrepr = self.residuals[0].stringrepr
        for EL in self.residuals[1:]:
            self.stringrepr = self.stringrepr + "|" + EL.stringrepr
            

### ---------------------------------------------------###

class Sieve(Residual):
    
    def __init__(self, initializer):
        self.module = None
        self.shift = None
        if isinstance(initializer, list):
            if sorted(list(set(initializer))) == [0,1]:
                self.bin = initializer
                self.initSeg = self.segment(0, len(initializer))
                CONDITION = 0
            else:
                self.initSeg = initializer
                CONDITION = 1
            compressedSeg = Compress(self.initSeg)
            self.stringrepr = compressedSeg.stringrepr
            if CONDITION == 1:
                residsForBin = [x.bin for x in compressedSeg.residuals]
                self.bin = residsForBin[0]
                for EL in residsForBin[1:]:
                    self.bin = _operationsSieves(self.bin, EL, "|")
        elif isinstance(initializer, str):
            self.stringrepr = initializer
            self.bin = self._parsestring()
        self.canonic_intervals = self._canonic_intervals()
        self.canonic_unitsegment = self._canonic_unitsegment()
        self.period = len(self.bin)
        self.canonic_segment = self._canonic_segment()
        self.compressed = self._compressed()
        

    def _parsestring(self):
        groups = self.stringrepr.split("|")
        unionGroups = []
        for group in groups:
            indRes = [x.strip("()") for x in group.split("&")]
            resd = Residual(indRes[0])
            firstRed = resd.bin
            for res in indRes[1:]:
                firstRed = _operationsSieves(firstRed, Residual(res).bin,"&")

            unionGroups.append(firstRed)
        firstU = unionGroups[0]
        for otherU in unionGroups[1:]:
            firstU = _operationsSieves(firstU, otherU, "|")
        return firstU

    def intervals(self, minVal, maxVal):
        seg = self.segment(minVal, maxVal)
        if len(seg) == 1:
            return seg
        else:
            return [seg[i+1] - seg[i] for i in range(len(seg)-1)]

    def _canonic_intervals(self):
        return self.intervals(0, len(self.bin))


    def unitsegment(self, minVal, maxVal):
        seg = self.segment(minVal, maxVal)
        min, max = seg[0], seg[-1]
        span = max - min
        unit = []
        if len(seg) > 1:
            for val in seg:
                dif = val - min
                if isinstance(dif, int):
                    dif = float(dif)         
                if span != 0:
                    unit.append(dif / span)
                else: # fill value if span is zero
                    unit.append(0)
        else: # if one element, return 0 (could be 1, or .5)
            unit.append(0)
        return unit

    def _canonic_unitsegment(self):
        return self.unitsegment(0, len(self.bin))

    def _canonic_segment(self):
        return self.segment(0, self.period)


    def __repr__(self) -> str:
        return self.stringrepr

    
    def _compressed(self):
        compSieve = Compress(self.canonic_segment)
        return compSieve.stringrepr



### ---------------------------------------------------###
if __name__ == "__main__":
    strB = "5@4|6@1|(3@2&13@7)"
    sieve = Sieve(strB)
    print(sieve.compressed)
    string_A = "3@2|5@3"
    binary_A = [0, 0, 1, 1, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 1]
    segment_A = [2, 3, 5, 8, 11, 13, 14]

    examples = [string_A, binary_A, segment_A]
    names = ["string", "binary", "segment"]

'''    for i,example in enumerate(examples):
        print("Sieve made with: " + names[i])
        sieve = Sieve(example)
        print("String repr", sieve.stringrepr)
        print("Binary repr", sieve.bin)
        print("Segment repr", sieve.segment(0, sieve.period))
        print("Canonic unit repr", sieve.canonic_unitsegment)
        print("Canonic intervals", sieve.canonic_intervals)
        print("Period", sieve.period)
        print("*******************")'''
