
import random
from tkinter import ttk
import tkinter

class Dice(ttk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("Dice")
        self.pack()

        self.diceNumber = tkinter.IntVar(self, 1)
        self.diceSize = tkinter.IntVar(self, 20)
        self.bonus = tkinter.IntVar(self, 4)

        self.diceNumberEntry = ttk.Entry(self, textvariable=self.diceNumber)
        self.diceNumberEntry.pack(side="left")

        self.label = ttk.Label(self, text="D")
        self.label.pack(side="left")

        self.diceSizeEntry = ttk.Entry(self, textvariable=self.diceSize)
        self.diceSizeEntry.pack(side="left")

        self.label2 = ttk.Label(self, text="+")
        self.label2.pack(side="left")

        self.bonusEntry = ttk.Entry(self, textvariable=self.bonus)
        self.bonusEntry.pack(side="left")

        self.button = ttk.Button(self, text="Roll", command=self.roll)
        self.button.pack(side="left")

    def roll(self):
        diceNumber = self.diceNumber.get()
        diceSize = self.diceSize.get()
        bonus = self.bonus.get()
        diceSizeP1 = diceSize + 1
        res = bonus
        l = []
        for i in range(diceNumber):
            r = random.randrange(1, diceSizeP1)
            l.append(str(r))
            res += r
        if bonus == 0:
            print(diceNumber, "d", diceSize, " = ", sep="", end="")
            print("+".join(l), "=", res)
        else:
            print(diceNumber, "d", diceSize, "+", bonus, " = ", sep="", end="")
            print("+".join(l), "+", bonus, "=", res)

def roll(diceNumberStr, diceSizeStr, l):
    if "" == diceNumberStr:
        diceNumber = 1
    else:
        diceNumber = int(diceNumberStr)
    diceSizeP1 = int(diceSizeStr) + 1
    res = 0
    for i in range(diceNumber):
        r = random.randrange(1, diceSizeP1)
        res += r
        l.append(str(r))
    return res

def rollString(s):
    res = 0
    l = []
    for e in s.split("+"):
        if "d" in e:
            d = e.split("d")
            res += roll(d[0], d[1], l)
        elif "D" in e:
            d = e.split("D")
            res += roll(d[0], d[1], l)
        else:
            l.append(e)
            res += int(e)
    print(s, "=", "+".join(l), "=", res)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Launch some dice")
    parser.add_argument("-v", "--version", action="version",
                        version="%(prog)s version 0.2")
    parser.add_argument("dice", nargs="*", help="expression like 5d6+9")
    args = parser.parse_args()
    if not args.dice: 
        root = tkinter.Tk()
        dice = Dice(root)
        dice.mainloop()
    else:
        for dice in args.dice:
            rollString(dice)
