
import collections
import random

def checkValue(value):
    if not isinstance(value, int) or value < 1 or value > 9:
        raise ValueError("case must contains int between 1 and 9")

class Case:
    __slots__ = ("first", "possibility")
    def __init__(self, arg=None):
        self.first = True
        if arg is None:
            self.reset()
        else:
            if isinstance(arg, int):
                checkValue(arg)
                self.possibility = {arg}
            elif isinstance(arg, Case):
                self.possibility = arg.possibility.copy()            
    def reset(self):
        self.possibility = {1,2,3,4,5,6,7,8,9}
    def found(self):
        return len(self.possibility) == 1
    def foundFirst(self):
        if self.first and self.found():
            self.first = False
            return True
        else:
            return False
    @property
    def value(self):
        return next(iter(self.possibility))
    def __contains__(self, value):
        return value in self.possibility
    def impossible(self, value):
        try:
            self.possibility.remove(value)
            return True
        except KeyError:
            return False
    def set(self, value):
        checkValue(value)
        if self.found():
            return False
        else:
            self.possibility = {value}
            return True
    def randomValue(self):
        if len(self.possibility) > 1:
            value = random.choice(list(self.possibility))
            self.possibility = {value}
            return True
        else:
            return False
    def __str__(self):
        return str(self.possibility)
    def display(self):
        if self.found():
            return str(self.value)
        else:
            return " "

def subSquareIndex(n):
    if n < 3:
        return 0, 3
    elif n < 6:
        return 3, 6
    else:
        return 6, 9

Position = collections.namedtuple("Position", ["line", "column"])

class Grille:
    __slots__ = ("innerGrille",)
    def __init__(self, arg=None):
        if arg is None:
            self.innerGrille = [[Case() for j in range(9)] for i in range(9)]
        elif isinstance(arg, Grille):
            innerGrille = arg.innerGrille
            self.innerGrille = [[Case(innerGrille[i][j]) for j in range(9)]
                                for i in range(9)]
        else:
            self.innerGrille = []
            with open(arg) as f:
                for i in range(9):
                    line = []
                    values = f.readline().split(",")
                    for j in range(9):
                        value = values[j][0]
                        if " " == value:
                            line.append(Case())
                        else:
                            line.append(Case(int(value)))
                    self.innerGrille.append(line)
    def isNotComplete(self):
        for i in range(9):
            for j in range(9):
                if not self.innerGrille[i][j].found():
                    return True
        return False
    def __ne__(self, other):
        for i in range(9):
            for j in range(9):
                caseValue1 = self.innerGrille[i][j]
                caseValue2 = other.innerGrille[i][j]
                if not (caseValue1.found() and caseValue2.found() and \
                        caseValue1.value == caseValue2.value):
                    return True
        return False
    def solve(self):
        nbBoucle = -1
        change = True
        while change:
            change = False
            nbBoucle += 1
            for i in range(9):
                for j in range(9):
                    caseValue = self.innerGrille[i][j]
                    if caseValue.foundFirst():
                        value = caseValue.value
                        for k in range(9):
                            if k != j and \
                               self.innerGrille[i][k].impossible(value):
                                change = True
                            if k != i and \
                               self.innerGrille[k][j].impossible(value):
                                change = True

                        for i2 in range(*subSquareIndex(i)):
                            for j2 in range(*subSquareIndex(j)):
                                if not(i2 == i and j2 == j) and \
                                   self.innerGrille[i2][j2].impossible(value):
                                    change = True
            for value in range(1,10):
                for i in range(9):
                    listColumn = []
                    listLine = []
                    for j in range(9):
                        if value in self.innerGrille[i][j]:
                            listColumn.append(j)
                        if value in self.innerGrille[j][i]:
                            listLine.append(j)

                    if len(listColumn) == 1 and \
                       self.innerGrille[i][listColumn[0]].set(value):
                        change = True
                    if len(listLine) == 1 and \
                       self.innerGrille[listLine[0]][i].set(value):
                        change = True
                change = self.computeSquare(change, value, 0, 3, 0, 3)
                change = self.computeSquare(change, value, 0, 3, 3, 6)
                change = self.computeSquare(change, value, 0, 3, 6, 9)
                change = self.computeSquare(change, value, 3, 6, 0, 3)
                change = self.computeSquare(change, value, 3, 6, 3, 6)
                change = self.computeSquare(change, value, 3, 6, 6, 9)
                change = self.computeSquare(change, value, 6, 9, 0, 3)
                change = self.computeSquare(change, value, 6, 9, 3, 6)
                change = self.computeSquare(change, value, 6, 9, 6, 9)
        return nbBoucle
    def computeSquare(self, change, value, iStart, iEnd, jStart, jEnd):
        listPosition = [Position(i,j) for i in range(iStart, iEnd) for j in
                        range(jStart, jEnd) if value in self.innerGrille[i][j]]

        size = len(listPosition)
        if size == 1:
            position = listPosition[0]
            if self.innerGrille[position.line][position.column].set(value):
                change = True
        elif size == 2:
            position1 = listPosition[0]
            position2 = listPosition[1]
            line = position1.line
            if line == position2.line:
                change = self.impossibleLine(change, value, line, jStart, jEnd)
            else:
                column = position1.column
                if column == position2.column:
                     change = self.impossibleColumn(change, value, column,
                                                    iStart, iEnd)
        elif size == 3:
            position1 = listPosition[0]
            position2 = listPosition[1]
            position3 = listPosition[2]
            line = position1.line
            if line == position2.line and line == position3.line:
                change = self.impossibleLine(change, value, line, jStart, jEnd)
            else:
                column = position1.column
                if column == position2.column and column == position3.column:
                     change = self.impossibleColumn(change, value, column,
                                                    iStart, iEnd)
        return change
    def impossibleLine(self, change, value, line, jStart, jEnd):
        for j in range(9):
            if (j < jStart or j >= jEnd) and \
                self.innerGrille[line][j].impossible(value):
                change = True
        return change
    def impossibleColumn(self, change, value, column, iStart, iEnd):
        for i in range(9):
            if (i < iStart or i >= iEnd) and \
                self.innerGrille[i][column].impossible(value):
                change = True
        return change
    def __str__(self):
        buffer = []
        ba = buffer.append
        for i in range(9):
            for j in range(9):
                ba(self.innerGrille[i][j].display())
                if j != 8:
                    ba(",")
            ba("\n")
        return "".join(buffer)
    def display(self):
        buffer = []
        ba = buffer.append
        lineSep = "+-----+-----+-----+\n"
        ba(lineSep)
        for i in range(9):
            ba("|")
            for j in range(9):
                ba(self.innerGrille[i][j].display())
                if j == 2 or j == 5 or j == 8:
                    ba("|")
                else:
                    ba(",")
            ba("\n")
            if i == 2 or i == 5:
                ba(lineSep)
        ba(lineSep)
        return "".join(buffer)

def generateGrille():
    nb = 0
    run = True
    grille = None
    while run:
        grille = Grille()
        innerGrille = grille.innerGrille

        for i in range(9):
            for j in range(9):
                if innerGrille[i][j].randomValue():
                    nb += grille.solve()

        run = grille.isNotComplete()

    print("Nombre de boucle pour generer :", nb)
    print()

    return grille

def obfuscateGrille(grille):
    grille2 = Grille(grille)
    innerGrille2 = grille2.innerGrille

    positions = [Position(i,j) for i in range(9) for j in range(9)]
    random.shuffle(positions)

    nbObfuscate = 0
    for position in positions:
        caseValue = innerGrille2[position.line][position.column]
        if not caseValue.found():
            raise Exception
        value = caseValue.value
        caseValue.reset()
        workingGrille = Grille(grille2)
        nbObfuscate += workingGrille.solve()

        if workingGrille.isNotComplete():
            caseValue.set(value)

    workingGrille = Grille(grille2)
    nbSolve = workingGrille.solve()
    if grille != workingGrille:
        raise Exception

    print("Nombre de boucle pour obfusquer :", nbObfuscate)
    print("Nombre de boucle pour resoudre :", nbSolve)
    print()

    return grille2


if __name__ == "__main__":
    import datetime

    now = datetime.datetime.now

    start = now()

    g = Grille(r"..\javaWorkspace\sudoku\grilles\generatedGrille1.txt")
    print(g.display())

    nb = g.solve()

    print("Nombre de boucle pour resoudre :", nb)
    print()
    print(g.display())

    end = now()

    print("temps de calcul :", end - start)
    print()

    start = now()

    g = generateGrille()
    print(g.display())

    print(obfuscateGrille(g).display())

    end = now()

    print("temps de calcul :", end - start)
