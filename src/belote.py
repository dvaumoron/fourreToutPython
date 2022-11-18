
import collections
import enum
import itertools
import operator
import random

class Carte(collections.namedtuple("Carte", ["valeur", "couleur"])):
    __slots__ = ()
    def __repr__(self):
        return f"{self.valeur!s} de {self.couleur!s}"

@enum.unique
class Couleur(enum.Enum):
    COEUR = 0
    PIQUE = 1
    CARREAU = 2
    TREFLE = 3
    def __init__(self, value):
        self._nameLower = self.name[0] + self.name[1:].lower()
    def __str__(self):
        return self._nameLower

ValeurTuple = collections.namedtuple("ValeurTuple",
                                     ["texte", "point", "ordre",
                                      "pointAtout", "ordreAtout"])

@enum.unique
class Valeur(ValeurTuple, enum.Enum):
    SEPT = ("7", 0, 0, 0, 0)
    HUIT = ("8", 0, 1, 0, 1)
    NEUF = ("9", 0, 2, 14, 6)
    VALET = ("Valet", 2, 3, 20, 7)
    DAME = ("Dame", 3, 4, 3, 2)
    ROI = ("Roi", 4, 5, 4, 3)
    DIX = ("10", 10, 6, 10, 4)
    AS = ("As", 11, 7, 11, 5)
    def __str__(self):
        return self.texte

jeu32 = [Carte(v, c) for c in Couleur for v in Valeur]

keyCarte = operator.attrgetter('couleur.value', 'valeur.ordre')

def intInput(prompt, validate, validateMsg):
    while True:
        try:
            i = int(input(prompt))
            if validate(i):
                break
            else:
                print(validateMsg)
        except ValueError:
            print("attend un entier")
    return i

def memeEquipe(joueur1, joueur2):
    if joueur1 == joueur2:
        return True
    elif joueur1 == 1 and joueur2 == 3:
        return True
    elif joueur1 == 2 and joueur2 == 4:
        return True
    elif joueur1 == 3 and joueur2 == 1:
        return True
    elif joueur1 == 4 and joueur2 == 2:
        return True
    else:
        return False

def getOrdreJoueur(joueurCommence):
    if joueurCommence == 1:
        return [1,2,3,4]
    elif joueurCommence == 2:
        return [2,3,4,1]
    elif joueurCommence == 3:
        return [3,4,1,2]
    else:
        return [4,1,2,3]

class Belote:
    def __init__(self, joueurCommence):
        jeuShuffle = self.jeuShuffle()
        self.cartesJoueur1 = jeuShuffle[0:5]
        self.cartesJoueur2 = jeuShuffle[5:10]
        self.cartesJoueur3 = jeuShuffle[10:15]
        self.cartesJoueur4 = jeuShuffle[15:20]

        self.carteChoix = jeuShuffle[20]

        self.cartesRestantes = jeuShuffle[21:32]

        self.triCarte()
        self.initValue(joueurCommence)

    def jeuShuffle(self):
        jeuShuffle = jeu32.copy()
        random.shuffle(jeuShuffle)
        return jeuShuffle

    def triCarte(self):
        self.cartesJoueur1.sort(key=keyCarte)
        self.cartesJoueur2.sort(key=keyCarte)
        self.cartesJoueur3.sort(key=keyCarte)
        self.cartesJoueur4.sort(key=keyCarte)

    def initValue(self, joueurCommence):
        self.joueurPris = 0
        self.joueurCommence = joueurCommence
        self.scoreEquipe1 = 0
        self.scoreEquipe2 = 0
        self.equipePremierPli = None
        self.capot = True
        self.belote = None
        self.beloteJoueur = None

    def getCartesJoueur(self, joueur):
        return getattr(self, f"cartesJoueur{joueur}")

    def choixAtout(self):
        ordreJoueur = getOrdreJoueur(self.joueurCommence)
        for joueur in ordreJoueur:
            print("carte proposé :", self.carteChoix)
            print("Joueur", joueur)
            print(self.getCartesJoueur(joueur))

            print("0: prend")
            print("1: passe")
            choix = intInput("choix: ", lambda x: x == 0 or x == 1,
                             "choix invalide")
            if choix == 0:
                self.joueurPris = joueur
                self.atout = self.carteChoix.couleur
                break

        if self.joueurPris == 0:
            couleurList = []
            for couleur in Couleur:
                if couleur != self.carteChoix.couleur:
                    couleurList.append(couleur)

            for joueur in ordreJoueur:
                print("carte proposé :", self.carteChoix)
                print("Joueur", joueur)
                print(self.getCartesJoueur(joueur))

                for i, couleur in enumerate(couleurList):
                    print(i, ": ", couleur, sep="")
                print("3: passe")
                couleurIndex = intInput("couleur de l'annonce : ",
                                        lambda x: 0 <= x <=3, "choix invalide")

                if couleurIndex != 3:
                    self.joueurPris = joueur
                    self.atout = couleurList[couleurIndex]
                    break

        if self.joueurPris == 0:
            print("personne n'a pris")
        else:
            print("joueur" , self.joueurPris, "a pris à", self.atout)

            i = 0
            for joueur in range(1,5):
                cartesJoueur = self.getCartesJoueur(joueur)
                if joueur == self.joueurPris:
                    cartesJoueur.append(self.carteChoix)
                    cartesJoueur.append(self.cartesRestantes[i])
                    i += 1
                    cartesJoueur.append(self.cartesRestantes[i])
                    i += 1
                else:
                    cartesJoueur.append(self.cartesRestantes[i])
                    i += 1
                    cartesJoueur.append(self.cartesRestantes[i])
                    i += 1
                    cartesJoueur.append(self.cartesRestantes[i])
                    i += 1

            self.triAtout()
            self.compteBelote()

    def triAtout(self):
        def keyCarteAtout(c):
            return c.couleur.value, c.valeur.ordreAtout if c.couleur == \
                self.atout else c.valeur.ordre

        self.cartesJoueur1.sort(key=keyCarteAtout)
        self.cartesJoueur2.sort(key=keyCarteAtout)
        self.cartesJoueur3.sort(key=keyCarteAtout)
        self.cartesJoueur4.sort(key=keyCarteAtout)

    def compteBelote(self):
        for joueur in range(1, 5):
            dameAtout = False
            roiAtout = False
            for carte in self.getCartesJoueur(joueur):
                if carte.couleur == self.atout:
                    if carte.valeur == Valeur.ROI:
                        roiAtout = True
                    elif carte.valeur == Valeur.DAME:
                        dameAtout = True
            if dameAtout and roiAtout:
                self.belote = 0
                self.beloteJoueur = joueur
                if joueur == 1 or joueur == 3:
                    self.scoreEquipe1 += 20
                else:
                    self.scoreEquipe2 += 20
                break

    def tour(self, last):
        pli = {}

        cartesJoueur = self.getCartesJoueur(self.joueurCommence)
        if last:
            carteIndex = 0
        else:
            print("atout :", self.atout)
            print("Joueur", self.joueurCommence)
            for i, carte in enumerate(cartesJoueur):
                print(i, ": ", carte, sep="")
            carteIndex = intInput("carte joué : ",
                                  lambda x: 0 <= x < len(cartesJoueur),
                                  "choix invalide")
        carte = cartesJoueur[carteIndex]
        del cartesJoueur[carteIndex]
        pli[self.joueurCommence] = carte
        self.annonceBelote(carte)
        valeur, couleurDemande = carte
        atoutDemande = couleurDemande == self.atout
        if atoutDemande:
            scorePli = valeur.pointAtout
            maxOrdre = valeur.ordreAtout
        else:
            scorePli = valeur.point
            maxOrdre = valeur.ordre
        if last:
            scorePli += 10

        if self.joueurCommence == 1:
            ordreJoueur = [2,3,4]
        elif self.joueurCommence == 2:
            ordreJoueur = [3,4,1]
        elif self.joueurCommence == 3:
            ordreJoueur = [4,1,2]
        else:
            ordreJoueur = [1,2,3]

        coupe = False
        for joueur in ordreJoueur:
            cartesJoueur = self.getCartesJoueur(joueur)
            if last:
                jouable = cartesJoueur
                carteIndex = 0
            else:
                print("pli :", pli)
                print("atout :", self.atout)
                print("Joueur", joueur)
                print(cartesJoueur)
                if atoutDemande:
                    jouable = [c for c in cartesJoueur if c.couleur == \
                               couleurDemande and c.valeur.ordreAtout > maxOrdre]
                    if len(jouable) == 0:
                        jouable = [c for c in cartesJoueur if c.couleur == \
                                   couleurDemande]
                else:
                    jouable = [c for c in cartesJoueur if c.couleur == \
                               couleurDemande]
                    if len(jouable) == 0 and not memeEquipe(joueur,
                                                            self.joueurCommence):
                        if coupe:
                            jouable = [c for c in cartesJoueur if c.couleur == \
                                       self.atout and c.valeur.ordreAtout > \
                                       maxOrdre]
                            if len(jouable) == 0:
                                jouable = [c for c in cartesJoueur if c.couleur == \
                                           self.atout]
                        else:
                            jouable = [c for c in cartesJoueur if c.couleur == \
                                       self.atout]
                if len(jouable) == 0:
                    jouable = cartesJoueur
                if len(jouable) == 1:
                    carteIndex = 0
                else:
                    for i, carte in enumerate(jouable):
                        print(i, ": ", carte, sep="")
                    carteIndex = intInput("carte joué : ",
                                          lambda x: 0 <= x < len(jouable),
                                          "choix invalide")
            carte = jouable[carteIndex]
            cartesJoueur.remove(carte)
            pli[joueur] = carte
            self.annonceBelote(carte)
            valeur, couleur = carte
            isAtout = couleur == self.atout
            if isAtout:
                scorePli += valeur.pointAtout
                ordreCarte = valeur.ordreAtout
            else:
                scorePli += valeur.point
                ordreCarte = valeur.ordre
            if couleur == couleurDemande:
                if isAtout:
                    if ordreCarte > maxOrdre:
                        maxOrdre = ordreCarte
                        self.joueurCommence = joueur
                elif not coupe and ordreCarte > maxOrdre:
                    maxOrdre = ordreCarte
                    self.joueurCommence = joueur
            elif isAtout:
                if coupe:
                    if ordreCarte > maxOrdre:
                        maxOrdre = ordreCarte
                        self.joueurCommence = joueur
                else:
                    coupe = True
                    maxOrdre = ordreCarte
                    self.joueurCommence = joueur

        print("pli :", pli)
        print("atout :", self.atout)
        print("joueur", self.joueurCommence, "remporte le pli de", scorePli,
              "points")

        if self.joueurCommence == 1 or self.joueurCommence == 3:
            if self.equipePremierPli is None:
                self.equipePremierPli = 1
            elif self.equipePremierPli != 1:
                self.capot = False
            self.scoreEquipe1 += scorePli
            if last and self.capot:
                self.scoreEquipe1 += 90
        else:
            if self.equipePremierPli is None:
                self.equipePremierPli = 2
            elif self.equipePremierPli != 2:
                self.capot = False
            self.scoreEquipe2 += scorePli
            if last and self.capot:
                self.scoreEquipe2 += 90

    def annonceBelote(self, carte):
        valeur, couleur = carte
        if self.belote is not None and \
            (valeur == Valeur.ROI or valeur == Valeur.DAME) and \
            couleur == self.atout:
            if  self.belote == 0:
                self.belote = 1
                print("belote")
            else:
                print("rebelote")

    def main(self):
        self.choixAtout()

        if self.joueurPris != 0:
            for i in range(7):
                self.tour(False)
            self.tour(True)

            self.resultat()
        else :
            self.scorePartieEquipe1 = 0
            self.scorePartieEquipe2 = 0
        print("l'equipe 1 marque", self.scorePartieEquipe1, "points")
        print("l'equipe 2 marque", self.scorePartieEquipe2, "points")

    def resultat(self):
        if self.joueurPris == 1 or self.joueurPris == 3:
            if self.scoreEquipe1 >= self.scoreEquipe2:
                print("l'equipe 1 remporte le tour avec", self.scoreEquipe1,
                      "points contre", self.scoreEquipe2)
                self.scorePartieEquipe1 = self.scoreEquipe1
                self.scorePartieEquipe2 = self.scoreEquipe2
            else:
                print("l'equipe 1 perd le tour avec", self.scoreEquipe1,
                      "points contre", self.scoreEquipe2)
                self.scorePartieEquipe1 = 0
                self.scorePartieEquipe2 = 162
                self.compteBelotePartie()
        else:
            if self.scoreEquipe2 >= self.scoreEquipe1:
                print("l'equipe 2 remporte le tour avec", self.scoreEquipe2,
                      "points contre", self.scoreEquipe1)
                self.scorePartieEquipe1 = self.scoreEquipe1
                self.scorePartieEquipe2 = self.scoreEquipe2
            else:
                print("l'equipe 2 perd le tour avec", self.scoreEquipe2,
                      "points contre", self.scoreEquipe1)
                self.scorePartieEquipe1 = 162
                self.scorePartieEquipe2 = 0
                self.compteBelotePartie()

    def compteBelotePartie(self):
        if self.beloteJoueur is not None:
            if self.beloteJoueur == 1 or self.beloteJoueur == 3:
                self.scorePartieEquipe1 += 20
            else:
                self.scorePartieEquipe2 += 20

class Coinch(Belote):
    def __init__(self, joueurCommence):
        jeuShuffle = self.jeuShuffle()
        self.cartesJoueur1 = jeuShuffle[0:8]
        self.cartesJoueur2 = jeuShuffle[8:16]
        self.cartesJoueur3 = jeuShuffle[16:24]
        self.cartesJoueur4 = jeuShuffle[24:32]

        self.triCarte()
        self.initValue(joueurCommence)

    def initValue(self, joueurCommence):
        super().initValue(joueurCommence)
        self.coinch = None
        self.surCoinch = None

    def choixAtout(self):
        passe = 0
        self.scoreCible = 70
        cycleJoueur = itertools.cycle(getOrdreJoueur(self.joueurCommence))
        for joueur in cycleJoueur:
            print("Joueur", joueur)
            print(self.getCartesJoueur(joueur))

            for couleur in Couleur:
                print(couleur.value, ": ", couleur, sep="")
            print("4: passe")
            if self.joueurPris != 0 and not memeEquipe(joueur, self.joueurPris):
                print("5: coinch")
                couleurIndex = intInput("couleur de l'annonce : ",
                                        lambda x: 0 <= x <=5, "choix invalide")
            else:
                couleurIndex = intInput("couleur de l'annonce : ",
                                        lambda x: 0 <= x <=4, "choix invalide")

            if couleurIndex == 4:
                passe += 1
                if passe == 4:
                    break
            elif couleurIndex == 5:
                self.coinch = joueur
                break
            else:
                passe = 0
                self.joueurPris = joueur
                self.atout = Couleur(couleurIndex)

                def validateScore(i):
                    return i % 10 == 0 and (self.scoreCible < i and (i <= \
                            170 or i == 250 or i == 270))

                self.scoreCible = intInput("score de l'annonce : ",
                                            validateScore,
                                            "le score doit être un multple "
                                            "de 10 entre 80 et 170 ou 250 "
                                            "ou 270 et plus grand que les "
                                            "annonces précédentes")

                if self.scoreCible == 270:
                    passe = 0
                    for joueur in cycleJoueur:
                        if not memeEquipe(joueur, self.joueurPris):
                            print("Joueur", joueur)
                            print(self.getCartesJoueur(joueur))
                            print("0: passe")
                            print("1: coinch")
                            choix = intInput("choix: ", lambda x: x == 0 or x == 1,
                                "choix invalide")

                            if choix == 0:
                                passe += 1
                                if passe == 2:
                                    break
                            else:
                                self.coinch = joueur
                                break
                    break

                print("joueur" , self.joueurPris, "a annoncé",
                        self.scoreCible, "à", self.atout)

        if self.joueurPris == 0:
            print("personne n'a pris")
        else:
            if self.coinch is not None:
                print("joueur" , self.joueurPris, "a annoncé",
                        self.scoreCible, "à", self.atout)
                print("joueur", self.coinch, "a coinché")
                passe = 0
                for joueur in cycleJoueur:
                    if memeEquipe(joueur, self.joueurPris):
                        print("Joueur", joueur)
                        print(self.getCartesJoueur(joueur))
                        print("0: passe")
                        print("1: sur coinch")
                        choix = intInput("choix: ", lambda x: x == 0 or x == 1,
                             "choix invalide")

                        if choix == 0:
                            passe += 1
                            if passe == 2:
                                break
                        else:
                            self.surCoinch = joueur
                            break
            print("joueur", self.joueurPris, "a annoncé", self.scoreCible,
                  "à", self.atout)
            if self.coinch is not None:
                print("joueur", self.coinch, "a coinché")
                if self.surCoinch is not None:
                    print("joueur", self.surCoinch, "a sur coinché")

            self.triAtout()
            self.compteBelote()

    def resultat(self):
        if self.coinch is not None:
            print("joueur", self.coinch, "a coinché")
            if self.surCoinch is not None:
                print("joueur", self.surCoinch, "a sur coinché")
        if self.joueurPris == 1 or self.joueurPris == 3:
            if self.scoreEquipe1 >= self.scoreCible:
                print("l'equipe 1 remporte le tour avec", self.scoreEquipe1,
                      "points pour", self.scoreCible, "annoncé")
                self.scorePartieEquipe1 = self.scoreEquipe1 + self.scoreCible
                if self.coinch is not None:
                    self.scorePartieEquipe2 = 0
                    if self.surCoinch is not None:
                        self.scorePartieEquipe1 *= 4
                    else:
                        self.scorePartieEquipe1 *= 2
                else:
                    self.scorePartieEquipe2 = self.scoreEquipe2
            else:
                print("l'equipe 1 perd le tour avec", self.scoreEquipe1,
                      "points pour", self.scoreCible, "annoncé")
                self.scorePartieEquipe1 = 0
                self.scorePartieEquipe2 = self.scoreCible + 162
                self.compteBelotePartie()
                if self.coinch is not None:
                    self.scorePartieEquipe1 = 0
                    if self.surCoinch is not None:
                        self.scorePartieEquipe2 *= 4
                    else:
                        self.scorePartieEquipe2 *= 2
            print("l'equipe 2 fait", self.scoreEquipe2, "points")
        else:
            if self.scoreEquipe2 >= self.scoreCible:
                print("l'equipe 2 remporte le tour avec", self.scoreEquipe2,
                      "points pour", self.scoreCible, "annoncé")
                self.scorePartieEquipe2 = self.scoreEquipe2 + self.scoreCible
                if self.coinch is not None:
                    self.scorePartieEquipe1 = 0
                    if self.surCoinch is not None:
                        self.scorePartieEquipe2 *= 4
                    else:
                        self.scorePartieEquipe2 *= 2
                else:
                    self.scorePartieEquipe1 = self.scoreEquipe1
            else:
                print("l'equipe 2 perd le tour avec", self.scoreEquipe2,
                      "points pour", self.scoreCible, "annoncé")
                self.scorePartieEquipe2 = 0
                self.scorePartieEquipe1 = self.scoreCible + 162
                self.compteBelotePartie()
                if self.coinch is not None:
                    self.scorePartieEquipe2 = 0
                    if self.surCoinch is not None:
                        self.scorePartieEquipe1 *= 4
                    else:
                        self.scorePartieEquipe1 *= 2
            print("l'equipe 1 fait", self.scoreEquipe1, "points")

class Partie:
    def __init__(self, game, joueur, score):
        self.game = game
        self.joueurCommence = joueur
        self.scoreCible = score
        self.scoreEquipe1 = 0
        self.scoreEquipe2 = 0

    def main(self):
        print("partie en", self.scoreCible, "points")
        cycleJoueur = itertools.cycle(getOrdreJoueur(self.joueurCommence))
        while self.scoreEquipe1 <= self.scoreCible and \
                self.scoreEquipe2 <= self.scoreCible:
            g = self.game(next(cycleJoueur))
            g.main()
            self.scoreEquipe1 += g.scorePartieEquipe1
            self.scoreEquipe2 += g.scorePartieEquipe2
            print("l'equipe 1 a", self.scoreEquipe1, "points")
            print("l'equipe 2 a", self.scoreEquipe2, "points")
        print("partie en", self.scoreCible, "points")
        if self.scoreEquipe1 > self.scoreEquipe2:
            print("l'equipe 1 a gagné")
        elif self.scoreEquipe2 > self.scoreEquipe1:
            print("l'equipe 2 a gagné")
        else:
            print("match nul")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Play belote game")
    parser.add_argument("-v", "--version", action="version",
                        version="%(prog)s version 0.5")
    parser.add_argument("-c", "--coinch", dest="game", action="store_const",
                        const=Coinch, default=Belote, help="coinch variant")
    parser.add_argument("-p", "--party", dest="score", metavar="score",
                        type=int, help="continue until one team reach score")
    parser.add_argument("-s", "--start", dest="joueur", default=1,
                        choices=[1,2,3,4], type=int,
                        help="starting player (default: 1)")

    args = parser.parse_args()

    if args.score is None:
        game = args.game(args.joueur)
    else:
        game = Partie(args.game, args.joueur, args.score)
    game.main()
