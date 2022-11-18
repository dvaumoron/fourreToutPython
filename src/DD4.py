
import functools
from tkinter import ttk
import tkinter

raceList = ["Changelin", "Crystalien", "Demi-elfe", "Demi-orque", "Deva",
            "Drakeide", "Drow", "Eladrin", "Elfe", "Feral Griffe-effilée",
            "Feral Longue-dent", "Forgelier", "Genasi", "Githyanki", "Gnome",
            "Goliath", "Halfeling", "Humain", "Kalashtar", "Minotaure", "Nain",
            "Sylvanien", "Tiefling"]

classeList = ["Barbare", "Barde", "Batailleur", "Chaman", "Druide",
              "Ensorceleur", "Faconneur", "Flamboyant", "Gardien",
              "Guerrier", "Invoqueur", "Limier", "Mage", "Mage d'arme",
              "Maitre de guerre", "Moine", "Paladin", "Pretre",
              "Pretre des runes", "Psion", "Rodeur", "Sorcier",
              "Vengeur", "Voleur"]

class DD4Builder(ttk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("DD4")
        self.pack()

        self.race = tkinter.StringVar(self)
        self.raceCombo = ttk.Combobox(self, textvariable=self.race,
                                        values=raceList,
                                        state="readonly")
        self.raceCombo.pack(side="top")
        self.raceCombo.bind("<<ComboboxSelected>>", self.displayRaceClasse)

        self.classe = tkinter.StringVar(self)
        self.classeCombo = ttk.Combobox(self, textvariable=self.classe,
                                        values=classeList,
                                        state="readonly")
        self.classeCombo.pack(side="top")
        self.classeCombo.bind("<<ComboboxSelected>>", self.displayRaceClasse)

        self.createAttributeFrame("force")
        self.createAttributeFrame("constitution")
        self.createAttributeFrame("dexterite")        
        self.createAttributeFrame("intelligence")
        self.createAttributeFrame("charisme")
        self.createAttributeFrame("sagesse")

        self.createDefense("vigueur")
        self.createDefense("reflexes")
        self.createDefense("volonte")

    def createAttributeFrame(self, name):
        frame = ttk.Frame(self)
        frame.pack(side="top")

        titleName = name[0].upper() + name[1:]
        labelText =  titleName + " : "
        updateName = "update" + titleName

        setattr(self, name + "Frame", frame)

        var = tkinter.IntVar(self, 10)
        setattr(self, name, var)
        mod = tkinter.StringVar(self, "+0")
        setattr(self, name + "Mod", mod)

        label = ttk.Label(frame, text=labelText)
        setattr(self, name + "Label", label)
        label.pack(side="left")

        entry = ttk.Entry(frame, textvariable=var)
        setattr(self, name + "Entry", entry)
        entry.pack(side="left")
        entry.bind("<KeyPress>", getattr(self, updateName))

        modLabel = ttk.Label(frame, textvariable=mod)
        setattr(self, name + "ModLabel", modLabel)
        modLabel.pack(side="left")

    def createDefense(self, name):
        frame = ttk.Frame(self)
        frame.pack(side="top")

        setattr(self, name + "Frame", frame)

        var = tkinter.IntVar(self, 10)
        setattr(self, name, var)

        label = ttk.Label(frame, text=name[0].upper() + name[1:] + " : ")
        setattr(self, name + "Label", label)
        label.pack(side="left")

        value = ttk.Label(frame, textvariable=var)
        setattr(self, name + "Value" , value)
        value.pack(side="left")

    def getMod(self, name):
        return (getattr(self, name).get() - 10) // 2

    def update(self, event, name, defenseName, name2):
        mod = self.getMod(name)
        s = str(mod)
        if mod >= 0:
            s = "+" + s
        getattr(self, name + "Mod").set(s)
        defense = 10 + max(mod, self.getMod(name2))
        getattr(self, defenseName).set(defense)

    updateForce = functools.partialmethod(update, name="force",
                                          defenseName="vigueur",
                                          name2="constitution")
    updateConstitution = functools.partialmethod(update, name="constitution",
                                                 defenseName="vigueur",
                                                 name2="force")
    updateDexterite = functools.partialmethod(update, name="dexterite",
                                              defenseName="reflexes",
                                              name2="intelligence")
    updateIntelligence = functools.partialmethod(update, name="intelligence",
                                                 defenseName="reflexes",
                                                 name2="dexterite")
    updateCharisme = functools.partialmethod(update, name="charisme",
                                             defenseName="volonte",
                                             name2="sagesse")
    updateSagesse = functools.partialmethod(update, name="sagesse",
                                            defenseName="volonte",
                                            name2="charisme")

    def displayRaceClasse(self, event):
        print(self.race.get(), self.classe.get())

if __name__ == "__main__":
    root = tkinter.Tk()
    builder = DD4Builder(root)
    builder.mainloop()
