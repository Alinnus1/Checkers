import time
import copy
import pygame
import sys

sarit = False
ADANCIME_MAX = 4

class Joc:
    """
    Clasa care defineste jocul. Se va schimba de la un joc la altul.
    """
    JMIN = None
    JMAX = None
    GOL = "#"
    NR_LINII = None
    NR_COLOANE = None
    scor_maxim = 0

    # aceasta functie este apelata o singura data si bam gata. si e apelata la inceputul jocului iar e ne face configuratie de joc
    @classmethod
    def initializeaza(cls, display, NR_LINII=8, NR_COLOANE=8, dim_celula=50):
        cls.NR_LINII = NR_LINII
        cls.NR_COLOANE = NR_COLOANE

        ######## calculare scor maxim ###########
        # TODO: calculeaza estimarea maxima posibila pentru un nod
        cls.scor_maxim = 2*4*3 # aceasta estimare reprezinta numarul maxim de piese regi pe care le poate avea un jucator. 2-iul este de dat de faptul ca un rege valoreaza de doua ori mai mult decat 

        cls.display = display
        cls.dim_celula = dim_celula
        cls.a_img = pygame.image.load("palb.png")
        cls.a_img = pygame.transform.scale(cls.a_img, (dim_celula, dim_celula))
        cls.n_img = pygame.image.load("pnegru.png")
        cls.n_img = pygame.transform.scale(cls.n_img, (dim_celula, dim_celula))
        cls.ra_img = pygame.image.load("ralb.png")
        cls.ra_img = pygame.transform.scale(cls.ra_img,(dim_celula,dim_celula))
        cls.rn_img = pygame.image.load("rnegru.png")
        cls.rn_img = pygame.transform.scale(cls.rn_img,(dim_celula,dim_celula))

        cls.celuleGrid = []  # este lista cu patratelele din grid
        for linie in range(NR_LINII):
            for coloana in range(NR_COLOANE):
                patr = pygame.Rect(
                    coloana * (dim_celula + 1),
                    linie * (dim_celula + 1),
                    dim_celula,
                    dim_celula,
                )
                cls.celuleGrid.append(patr)
    
    # e bun pentru problema mea
    def __init__(self, matr=None):
        # creez proprietatea ultima_mutare # (l,c)
        self.ultima_mutare = None

        if matr:
            # e data tabla, deci suntem in timpul jocului
            self.matr = matr
        else:
            # nu e data tabla deci suntem la initializare
            # tabla e mereu aceeasi deci o putem hard coda
            self.matr = [[self.__class__.GOL,"a",self.__class__.GOL,"a",self.__class__.GOL,"a",self.__class__.GOL,"a"],["a",self.__class__.GOL,"a",self.__class__.GOL,"a",self.__class__.GOL,"a",self.__class__.GOL],[self.__class__.GOL,"a",self.__class__.GOL,"a",self.__class__.GOL,"a",self.__class__.GOL,"a"],[self.__class__.GOL,self.__class__.GOL,self.__class__.GOL,self.__class__.GOL,self.__class__.GOL,self.__class__.GOL,self.__class__.GOL,self.__class__.GOL],
            [self.__class__.GOL,self.__class__.GOL,self.__class__.GOL,self.__class__.GOL,self.__class__.GOL,self.__class__.GOL,self.__class__.GOL,self.__class__.GOL],["n",self.__class__.GOL,"n",self.__class__.GOL,"n",self.__class__.GOL,"n",self.__class__.GOL],[self.__class__.GOL,"n",self.__class__.GOL,"n",self.__class__.GOL,"n",self.__class__.GOL,"n"],["n",self.__class__.GOL,"n",self.__class__.GOL,"n",self.__class__.GOL,"n",self.__class__.GOL]
            ]

    def deseneaza_grid(self, marcaj=None):

        for linie in range(self.__class__.NR_LINII):
            for coloana in range(self.__class__.NR_COLOANE):
                # desenarea tabla 
                if (coloana+linie) % 2 == 1:
                    
                    culoare = (84, 137, 28)
                else:
                    
                    culoare = (255, 239, 188)
                # desenare patratica marcata
                if(marcaj):
                    if(marcaj[0] == linie and marcaj[1] == coloana):
                        culoare = (198,167,33)
                pygame.draw.rect(
                    self.__class__.display,
                    culoare,
                    self.__class__.celuleGrid[
                        linie * self.__class__.NR_COLOANE + coloana
                    ],
                )  # alb = (255,255,255)
                if self.matr[linie][coloana] == "a":
                    self.__class__.display.blit(
                        self.__class__.a_img,
                        (
                            coloana * (self.__class__.dim_celula + 1),
                            linie * (self.__class__.dim_celula + 1),
                        ),
                    )
                elif self.matr[linie][coloana] == "n":
                    self.__class__.display.blit(
                        self.__class__.n_img,
                        (
                            coloana * (self.__class__.dim_celula + 1),
                            linie * (self.__class__.dim_celula + 1),
                        ),
                    )
                elif self.matr[linie][coloana] == "A":
                    self.__class__.display.blit(
                        self.__class__.ra_img, 
                        (
                            coloana *(self.__class__.dim_celula+1),
                            linie * (self.__class__.dim_celula +1),
                        ),
                    )
                elif self.matr[linie][coloana] == "N":
                    self.__class__.display.blit(
                        self.__class__.rn_img, 
                        (
                            coloana *(self.__class__.dim_celula+1),
                            linie * (self.__class__.dim_celula +1),
                        ),
                    )
        pygame.display.update()

    @classmethod
    def jucator_opus(cls, jucator):
        return cls.JMAX if jucator == cls.JMIN else cls.JMIN


    def parcurgerea(self,culoare):
        if culoare == "n" or culoare == "N":
            culoareopus ="a"
        else:
            culoareopus ="n"
        if(self.check_possibilities(culoareopus)== 0):
            return True
        else:
            return False 
        # ei bine se pare ca check posi e buna si pentru cazul i ncare nu mai are piese. pt ca atunci cand o culoare nu mai are piese implicit nu are mutari deci va ramane zero
    
    def check_possibilities(self,culoare):
        """Functie care verifica pentru un jucator daca mai are mutari posibile
        """
        nr_mutari = 0
        if (ord(culoare) == 65 or ord(culoare) == 78):
            culoareM = culoare
            culoarem = chr(ord(culoare)+32)
        else:
            culoareM = chr(ord(culoare)-32)
            culoarem = culoare
        for i in range(self.__class__.NR_LINII):
            for j in range(self.__class__.NR_COLOANE):
                if self.matr[i][j] == culoarem:
                    # inseamna ca acum suntem pe o piesa buna deci putem testa mutari in diagonala.
                    if (culoarem == "n"):
                        #adica pot sa ma duc doar in sus
                        perechi_directii = [(-1, -1),(-1, 1)]
                    else:
                        #adica pot sa ma duc doar in jos
                        perechi_directii = [(1,1),(1,-1)]
                    # primul caz este daca in vreo diagonala am liber inseamna ca pot sa fac o mutaare
                    # al doileacaz este daca in vreo diagonala am simbol opus iar dupa am gol
                    # sa nu uitam totusi ca daca avem negru inseamna ca verificam doar in diagonalele sus iar daca avem alb doar in diagonalele in jos . dar sa nu uitam ca daca avem litear mare inseamna ca putem sa verificam toate diagonalele
                    for directie in perechi_directii:
                        mutaretemp = (i+directie[0],j+directie[1])
                        if (
                            not 0 <= mutaretemp[0] < self.__class__.NR_LINII
                            or not 0 <= mutaretemp[1] < self.__class__.NR_COLOANE
                        ):
                            continue
                        if(self.matr[mutaretemp[0]][mutaretemp[1]] != self.__class__.GOL and self.matr[mutaretemp[0]][mutaretemp[1]] != culoarem and self.matr[mutaretemp[0]][mutaretemp[1]] != culoareM):
                            #adica daca in diagonala e piesa opusa
                            mutaretemp1 = (mutaretemp[0]+directie[0],mutaretemp[1]+directie[1])
                            if (
                            not 0 <= mutaretemp1[0] < self.__class__.NR_LINII
                            or not 0 <= mutaretemp1[1] < self.__class__.NR_COLOANE
                            ):
                                continue
                            if(self.matr[mutaretemp1[0]][mutaretemp1[1]] == self.__class__.GOL):
                                #inseamna ca se poate face salt
                                nr_mutari +=1
                                
                        if (self.matr[mutaretemp[0]][mutaretemp[1]] == self.__class__.GOL):
                            # inseamna ca se poate face mutarea aici
                            nr_mutari +=1

                elif self.matr[i][j] == culoareM:
                    perechi_directii = [
                        [(1, 1), (-1, -1)],
                        [(1, -1), (-1, 1)],
                    ]
                    for pereche_dir in perechi_directii:
                        for directie in pereche_dir:
                            mutaretemp = (i+directie[0],j+directie[1])
                            if (
                                not 0 <= mutaretemp[0] < self.__class__.NR_LINII
                                or not 0 <= mutaretemp[1] < self.__class__.NR_COLOANE
                            ):
                                continue
                            if(self.matr[mutaretemp[0]][mutaretemp[1]] != self.__class__.GOL and self.matr[mutaretemp[0]][mutaretemp[1]] != culoarem and self.matr[mutaretemp[0]][mutaretemp[1]] != culoareM):
                                #adica daca in diagonala e piesa opusa
                                mutaretemp1 = (mutaretemp[0]+directie[0],mutaretemp[1]+directie[1])
                                if (
                                not 0 <= mutaretemp1[0] < self.__class__.NR_LINII
                                or not 0 <= mutaretemp1[1] < self.__class__.NR_COLOANE
                                ):
                                    continue
                                if(self.matr[mutaretemp1[0]][mutaretemp1[1]] == self.__class__.GOL):
                                    #inseamna ca se poate face salt
                                    nr_mutari +=1

                            if (self.matr[mutaretemp[0]][mutaretemp[1]] == self.__class__.GOL):
                                # inseamna ca se poate face mutarea aici
                                nr_mutari +=1
        return nr_mutari

    def final(self):
        """Returneaza castigatorul sau "remiza" daca jocul s-a incheiat,
        altfel returneaza False.
        """
        # in ultima mutare practic am tot ce imi trebuie cand vine vorba de jucator and shit
        if not self.ultima_mutare:
            return False
        um = self.ultima_mutare
        culoare = self.matr[um[0]][um[1]]
        if (self.parcurgerea(culoare)):
            #inseamna ca adversarul nu mai are mutari dar trb verificat si daca eu am mutari
            if culoare == "n" or culoare == "N":
                culoareopus ="a"
            else:
                culoareopus ="n"
            if(self.parcurgerea(culoareopus)):
                return "remiza"
            else:
                return culoare
        else:
            return False


        # ideea e aici ca trebuie sa introudc urmatoarele conditii:
        # daca ultima mutare face ca celalalt jucator sa nu mai aiba piese win ultima mutare
        # daca ultima mutare face ca celalalt jucator sa nu mai aiba nicio mutare legala win ulitma mutare
        # daca niciunul dintre jucatori nu mai poate face o mutare leagala atunci este remiza
        # deci practic o sa am nevoie de o functie care sa mi daca mai exista mutari legale pentru jucator si in acelasi timp as putea face ca acea functie sa mi si indice pentru jucatori mutarile.
        # sa nu uitam regula ca daca se poate sari trebuie sa sa sara neaparat ceea ce face ca o lista sa fie inlocuita la un moment dat cu mutarea de sarit.

    
    def mutari(self, jucator):
        """Functia asta este pentru calculator pentru a genera toate mutarile posibile returneaza o lista de jocuri care se pot obtine din o mutare.
        
        Bun aici e interesant pentru ca mai intai trebuie sa cautam daca putem efectua sarituri. daca se pot efectua sarituri in l_mutari punem doar sarituri. daca nu se pot efectua parcurgem din nou si punem toate posibile
        """
        if (ord(jucator) == 65 or ord(jucator) == 78):
            culoareM = jucator
            culoarem = chr(ord(jucator)+32)
        else:
            culoareM = chr(ord(jucator)-32)
            culoarem = jucator
        l_mutari = []
        global sarit
        sarit = False
        for i in range(self.__class__.NR_LINII):
            for j in range(self.__class__.NR_COLOANE):
                #mai intai trebuie sa mi gasesc piesa
                if self.matr[i][j] == culoarem :
                    if (culoarem == "n"):
                        #adica pot sa ma duc doar in sus
                        perechi_directii = [(-1, -1),(-1, 1)]
                        linie_rege = 0
                    else:
                        #adica pot sa ma duc doar in jos
                        perechi_directii = [(1,1),(1,-1)]
                        linie_rege = 7
                    for directie in perechi_directii:
                        mutaretemp = (i+directie[0],j+directie[1])
                        if (
                            not 0 <= mutaretemp[0] < self.__class__.NR_LINII
                            or not 0 <= mutaretemp[1] < self.__class__.NR_COLOANE
                        ):
                            continue
                        if(self.matr[mutaretemp[0]][mutaretemp[1]] != self.__class__.GOL and self.matr[mutaretemp[0]][mutaretemp[1]] != culoarem and self.matr[mutaretemp[0]][mutaretemp[1]] != culoareM): 
                            #adica daca in diagonala e piesa opusa
                           
                            mutaretemp1 = (mutaretemp[0]+directie[0],mutaretemp[1]+directie[1])
                            if (
                            not 0 <= mutaretemp1[0] < self.__class__.NR_LINII
                            or not 0 <= mutaretemp1[1] < self.__class__.NR_COLOANE
                            ):
                                continue
                            if(self.matr[mutaretemp1[0]][mutaretemp1[1]] == self.__class__.GOL):
                                #inseamna ca se poate face salt
                                sarit = True
                                matr_tabla_noua = copy.deepcopy(self.matr)
                                matr_tabla_noua[mutaretemp[0]][mutaretemp[1]] = self.__class__.GOL
                                if(linie_rege == mutaretemp1[0]):
                                    matr_tabla_noua[mutaretemp1[0]][mutaretemp1[1]] = culoareM
                                else:
                                    matr_tabla_noua[mutaretemp1[0]][mutaretemp1[1]] = matr_tabla_noua[i][j] 
                                matr_tabla_noua[i][j] = self.__class__.GOL
                                joc_nou = Joc(matr_tabla_noua)
                                joc_nou.ultima_mutare = (mutaretemp1[0],mutaretemp1[1])
                                l_mutari.append(joc_nou)
                elif self.matr[i][j] == culoareM :
                    perechi_directii = [
                        [(1, 1), (-1, -1)],
                        [(1, -1), (-1, 1)],
                    ]
                    for pereche_dir in perechi_directii:
                        for directie in pereche_dir:
                            mutaretemp = (i+directie[0],j+directie[1])
                            if (
                                not 0 <= mutaretemp[0] < self.__class__.NR_LINII
                                or not 0 <= mutaretemp[1] < self.__class__.NR_COLOANE
                            ):
                                continue
                            if(self.matr[mutaretemp[0]][mutaretemp[1]] != self.__class__.GOL and self.matr[mutaretemp[0]][mutaretemp[1]] != culoarem and self.matr[mutaretemp[0]][mutaretemp[1]] != culoareM):
                                #adica daca in diagonala e piesa opusa
                                mutaretemp1 = (mutaretemp[0]+directie[0],mutaretemp[1]+directie[1])
                                if (
                                not 0 <= mutaretemp1[0] < self.__class__.NR_LINII
                                or not 0 <= mutaretemp1[1] < self.__class__.NR_COLOANE
                                ):
                                    continue
                                if(self.matr[mutaretemp1[0]][mutaretemp1[1]] == self.__class__.GOL):
                                    #inseamna ca se poate face salt
                                    sarit = True
                                    matr_tabla_noua = copy.deepcopy(self.matr)
                                    matr_tabla_noua[i][j] = self.__class__.GOL
                                    matr_tabla_noua[mutaretemp[0]][mutaretemp[1]] = self.__class__.GOL
                                    matr_tabla_noua[mutaretemp1[0]][mutaretemp1[1]] = culoareM
                                    joc_nou = Joc(matr_tabla_noua)
                                    joc_nou.ultima_mutare = (mutaretemp1[0],mutaretemp1[1])
                                    l_mutari.append(joc_nou)
        if (not sarit):
            for i in range(self.__class__.NR_LINII):
                for j in range(self.__class__.NR_COLOANE):
                    #mai intai trebuie sa mi gasesc piesa
                    if self.matr[i][j] == culoarem :
                        #mai intai trebuie sa mi gasesc piesa
                        if (culoarem == "n"):
                            #adica pot sa ma duc doar in sus
                            perechi_directii = [(-1, -1),(-1, 1)]
                            linie_rege = 0
                        else:
                            #adica pot sa ma duc doar in jos
                            perechi_directii = [(1,1),(1,-1)]
                            linie_rege = 7
                        for directie in perechi_directii:
                            mutaretemp = (i+directie[0],j+directie[1])
                            if (
                                not 0 <= mutaretemp[0] < self.__class__.NR_LINII
                                or not 0 <= mutaretemp[1] < self.__class__.NR_COLOANE
                            ):
                                continue
                            if (self.matr[mutaretemp[0]][mutaretemp[1]] == self.__class__.GOL):
                                matr_tabla_noua = copy.deepcopy(self.matr)
                                
                                if(linie_rege == mutaretemp[0]):
                                    matr_tabla_noua[mutaretemp[0]][mutaretemp[1]] = culoareM
                                else:
                                    matr_tabla_noua[mutaretemp[0]][mutaretemp[1]] = matr_tabla_noua[i][j]
                                matr_tabla_noua[i][j] = self.__class__.GOL
                                joc_nou = Joc(matr_tabla_noua)
                                joc_nou.ultima_mutare = (mutaretemp[0],mutaretemp[1])
                                l_mutari.append(joc_nou)

                    elif self.matr[i][j] == culoareM :
                        perechi_directii = [
                        [(1, 1), (-1, -1)],
                        [(1, -1), (-1, 1)],
                        ]
                        for pereche_dir in perechi_directii:
                            for directie in pereche_dir:
                                mutaretemp = (i+directie[0],j+directie[1])
                                if (
                                    not 0 <= mutaretemp[0] < self.__class__.NR_LINII
                                    or not 0 <= mutaretemp[1] < self.__class__.NR_COLOANE
                                ):
                                    continue
                                if (self.matr[mutaretemp[0]][mutaretemp[1]] == self.__class__.GOL):
                                    matr_tabla_noua = copy.deepcopy(self.matr)
                                    matr_tabla_noua[i][j] = self.__class__.GOL
                                    matr_tabla_noua[mutaretemp[0]][mutaretemp[1]] = culoareM
                                    joc_nou = Joc(matr_tabla_noua)
                                    joc_nou.ultima_mutare = (mutaretemp[0],mutaretemp[1])
                                    l_mutari.append(joc_nou)

        return l_mutari

    def val_piese(self,jucator):
        """Functie folosita pentru estimarea scorului unei stari.
        """
        if (ord(jucator) == 65 or ord(jucator) == 78):
            culoareM = jucator
            culoarem = chr(ord(jucator)+32)
        else:
            culoareM = chr(ord(jucator)-32)
            culoarem = jucator
        # primul mod de estimare scor
        val = 0
        for i in range(self.__class__.NR_LINII):
            for j in range(self.__class__.NR_COLOANE):
                # daca e piesa normala are valoare 1 iar daca e rege are valoare 2
                if(self.matr[i][j]==culoarem):
                    val+=1
                elif(self.matr[i][j]==culoareM):
                    val+=2

        # al doilea mod de estimare scor
        # if (culoarem == "n"):
        #     val = 0
        #     for i in range(self.__class__.NR_LINII):
        #         for j in range(self.__class__.NR_COLOANE):
        #             if(self.matr[i][j]==culoarem):
        #                 # daca piesa se afla in jumatatea adversarului are valoare mai mare decat daca se afla in jumatatea proprie
        #                 if(i<4):
        #                     val+=7
        #                 else:
        #                     val+5
        #             elif(self.matr[i][j]==culoareM):
        #                 val+=10
        # elif(culoarem =="a"):
        #     val = 0
        #     for i in range(self.__class__.NR_LINII):
        #         for j in range(self.__class__.NR_COLOANE):
        #             if(self.matr[i][j]==culoarem):
        #                 # daca piesa se afla in jumatatea adversarului are valoare mai mare decat daca se afla in jumatatea proprie
        #                 if(i>=4):
        #                     val+=7
        #                 else:
        #                     val+5
        #             elif(self.matr[i][j]==culoareM):
        #                 val+=10
            
        return val

    def estimeaza_scor(self, adancime):
        t_final = self.final()
        # if (adancime==0):
        if t_final == self.__class__.JMAX:
            return self.__class__.scor_maxim + adancime
        elif t_final == self.__class__.JMIN:
            return -self.__class__.scor_maxim - adancime
        elif t_final == "remiza":
            return 0
        else:
            # returnam diferenta de valori de piese pentru jucatori
            return self.val_piese(self.__class__.JMAX) - self.val_piese(self.__class__.JMIN)

    def sirAfisare(self):
        sir = "  |"
        sir += " ".join([chr(i) for i in range(97,105)]) + "\n"
        sir += "-" * (self.NR_COLOANE + 1) * 2 + "\n"
        sir += "\n".join(
            [
                str(i) + " |" + " ".join([str(x) for x in self.matr[i]])
                for i in range(len(self.matr))
            ]
        )
        return sir

    def __str__(self):
        return self.sirAfisare()

    def __repr__(self):
        return self.sirAfisare()

def min_max(stare):

    if stare.adancime == 0 or stare.tabla_joc.final():
        stare.scor = stare.tabla_joc.estimeaza_scor(stare.adancime)
        return stare

    # calculez toate mutarile posibile din starea curenta
    stare.mutari_posibile = stare.mutari()

    # aplic algoritmul minimax pe toate mutarile posibile (calculand astfel subarborii lor)
    mutari_scor = [min_max(mutare) for mutare in stare.mutari_posibile]

    if stare.j_curent == Joc.JMAX:
        # daca jucatorul e JMAX aleg starea-fiica cu scorul maxim
        stare.stare_aleasa = max(mutari_scor, key=lambda x: x.scor)
    else:
        # daca jucatorul e JMIN aleg starea-fiica cu scorul minim
        stare.stare_aleasa = min(mutari_scor, key=lambda x: x.scor)
    stare.scor = stare.stare_aleasa.scor
    return stare

def alpha_beta(alpha, beta, stare):
    if stare.adancime == 0 or stare.tabla_joc.final():
        stare.scor = stare.tabla_joc.estimeaza_scor(stare.adancime)
        return stare

    if alpha > beta:
        return stare  # este intr-un interval invalid deci nu o mai procesez

    stare.mutari_posibile = stare.mutari()

    if stare.j_curent == Joc.JMAX:
        scor_curent = float("-inf")

        for mutare in stare.mutari_posibile:
            # calculeaza scorul
            stare_noua = alpha_beta(alpha, beta, mutare)

            if scor_curent < stare_noua.scor:
                stare.stare_aleasa = stare_noua
                scor_curent = stare_noua.scor
            if alpha < stare_noua.scor:
                alpha = stare_noua.scor
                if alpha >= beta:
                    break

    elif stare.j_curent == Joc.JMIN:
        scor_curent = float("inf")

        for mutare in stare.mutari_posibile:

            stare_noua = alpha_beta(alpha, beta, mutare)

            if scor_curent > stare_noua.scor:
                stare.stare_aleasa = stare_noua
                scor_curent = stare_noua.scor

            if beta > stare_noua.scor:
                beta = stare_noua.scor
                if alpha >= beta:
                    break
    stare.scor = stare.stare_aleasa.scor

    return stare

def afis_daca_final(stare_curenta):
    final = stare_curenta.tabla_joc.final()
    if final:
        if final == "remiza":
            print("Remiza!")
        else:
            print("A castigat " + final)

        return True

    return False

class Buton:
    def __init__(
        self,
        display=None,
        left=0,
        top=0,
        w=0,
        h=0,
        culoareFundal=(53, 80, 115),
        culoareFundalSel=(89, 134, 194),
        text="",
        font="consolas",
        fontDimensiune=16,
        culoareText=(255, 255, 255),
        valoare="",
    ):
        self.display = display
        self.culoareFundal = culoareFundal
        self.culoareFundalSel = culoareFundalSel
        self.text = text
        self.font = font
        self.w = w
        self.h = h
        self.selectat = False
        self.fontDimensiune = fontDimensiune
        self.culoareText = culoareText
        fontObj = pygame.font.SysFont(self.font, self.fontDimensiune)
        self.textRandat = fontObj.render(self.text, True, self.culoareText)
        self.dreptunghi = pygame.Rect(left, top, w, h)
        self.dreptunghiText = self.textRandat.get_rect(center=self.dreptunghi.center)
        self.valoare = valoare

    def selecteaza(self, sel):
        self.selectat = sel
        self.deseneaza()

    def selecteazaDupacoord(self, coord):
        if self.dreptunghi.collidepoint(coord):
            self.selecteaza(True)
            return True
        return False

    def updateDreptunghi(self):
        self.dreptunghi.left = self.left
        self.dreptunghi.top = self.top
        self.dreptunghiText = self.textRandat.get_rect(center=self.dreptunghi.center)

    def deseneaza(self):
        culoareF = self.culoareFundalSel if self.selectat else self.culoareFundal
        pygame.draw.rect(self.display, culoareF, self.dreptunghi)
        self.display.blit(self.textRandat, self.dreptunghiText)

class Stare:
    """
    Clasa folosita de algoritmii minimax si alpha-beta
    Are ca proprietate tabla de joc
    Functioneaza cu conditia ca in cadrul clasei Joc sa fie definiti JMIN si JMAX (cei doi jucatori posibili)
    De asemenea cere ca in clasa Joc sa fie definita si o metoda numita mutari() care ofera lista cu configuratiile posibile in urma mutarii unui jucator
    """

    def __init__(self, tabla_joc, j_curent, adancime, parinte=None, scor=None):
        self.tabla_joc = tabla_joc
        self.j_curent = j_curent

        # adancimea in arborele de stari
        self.adancime = adancime

        # scorul starii (daca e finala) sau al celei mai bune stari-fiice (pentru jucatorul curent)
        self.scor = scor

        # lista de mutari posibile din starea curenta
        self.mutari_posibile = []

        # cea mai buna mutare din lista de mutari posibile pentru jucatorul curent
        self.stare_aleasa = None

    def mutari(self):
        l_mutari = self.tabla_joc.mutari(self.j_curent)
        juc_opus = Joc.jucator_opus(self.j_curent)
        l_stari_mutari = [
            Stare(mutare, juc_opus, self.adancime - 1, parinte=self)
            for mutare in l_mutari
        ]

        return l_stari_mutari

    def options(self,poz):
        lista =[]
        
        # mai intai trebuie sa identificam daca suntem alb sau negru
        # apoi trebuie verificat daca conform chestiilor unde poate merge
        culoarem = self.j_curent
        culoareM = chr(ord(culoarem)-32)
        sarit = False
        if(culoarem == "n"):
            if(self.tabla_joc.matr[poz[0]][poz[1]] == culoarem ):
                perechi_directii = [(-1, -1),(-1, 1)]
                for directie in perechi_directii:
                        mutaretemp = (poz[0]+directie[0],poz[1]+directie[1])
                        if (
                            not 0 <= mutaretemp[0] < Joc.NR_LINII
                            or not 0 <= mutaretemp[1] < Joc.NR_COLOANE
                        ):
                            continue
                        if(self.tabla_joc.matr[mutaretemp[0]][mutaretemp[1]] != Joc.GOL and self.tabla_joc.matr[mutaretemp[0]][mutaretemp[1]] != culoarem and self.tabla_joc.matr[mutaretemp[0]][mutaretemp[1]] != culoareM):
                            #adica daca in diagonala e piesa opusa
                            mutaretemp1 = (mutaretemp[0]+directie[0],mutaretemp[1]+directie[1])
                            if (
                            not 0 <= mutaretemp1[0] < Joc.NR_LINII
                            or not 0 <= mutaretemp1[1] < Joc.NR_COLOANE
                            ):
                                continue
                            if(self.tabla_joc.matr[mutaretemp1[0]][mutaretemp1[1]] == Joc.GOL):
                                sarit = True
                                lista.append(mutaretemp1)
            elif (self.tabla_joc.matr[poz[0]][poz[1]] == culoareM):
                perechi_directii = [
                        [(1, 1), (-1, -1)],
                        [(1, -1), (-1, 1)],
                    ]
                for pereche_directie in perechi_directii:
                    for directie in pereche_directie:
                        mutaretemp = (poz[0]+directie[0],poz[1]+directie[1])
                        if (
                            not 0 <= mutaretemp[0] < Joc.NR_LINII
                            or not 0 <= mutaretemp[1] < Joc.NR_COLOANE
                        ):
                            continue
                        if(self.tabla_joc.matr[mutaretemp[0]][mutaretemp[1]] != Joc.GOL and self.tabla_joc.matr[mutaretemp[0]][mutaretemp[1]] != culoarem and self.tabla_joc.matr[mutaretemp[0]][mutaretemp[1]] != culoareM):
                            #adica daca in diagonala e piesa opusa
                            mutaretemp1 = (mutaretemp[0]+directie[0],mutaretemp[1]+directie[1])
                            if (
                            not 0 <= mutaretemp1[0] < Joc.NR_LINII
                            or not 0 <= mutaretemp1[1] < Joc.NR_COLOANE
                            ):
                                continue
                            if(self.tabla_joc.matr[mutaretemp1[0]][mutaretemp1[1]] == Joc.GOL):
                                sarit = True
                                lista.append(mutaretemp1)         
            if(not sarit):
                if(self.tabla_joc.matr[poz[0]][poz[1]] == culoarem ):
                    perechi_directii = [(-1, -1),(-1, 1)]
                    for directie in perechi_directii:
                            mutaretemp = (poz[0]+directie[0],poz[1]+directie[1])
                            if (
                                not 0 <= mutaretemp[0] < Joc.NR_LINII
                                or not 0 <= mutaretemp[1] < Joc.NR_COLOANE
                            ):
                                continue
                            if(self.tabla_joc.matr[mutaretemp[0]][mutaretemp[1]] == Joc.GOL):
                                lista.append(mutaretemp)
                elif(self.tabla_joc.matr[poz[0]][poz[1]] == culoareM):
                    perechi_directii = [
                        [(1, 1), (-1, -1)],
                        [(1, -1), (-1, 1)],
                    ]
                    for pereche_directie in perechi_directii:
                        for directie in pereche_directie:
                            mutaretemp = (poz[0]+directie[0],poz[1]+directie[1])
                            if (
                                not 0 <= mutaretemp[0] < Joc.NR_LINII
                                or not 0 <= mutaretemp[1] < Joc.NR_COLOANE
                            ):
                                continue
                            if(self.tabla_joc.matr[mutaretemp[0]][mutaretemp[1]] == Joc.GOL):
                                lista.append(mutaretemp)
                        
        elif(culoarem == "a"):
            if(self.tabla_joc.matr[poz[0]][poz[1]] == culoarem):
                perechi_directii = [(1,1),(1,-1)]
                for directie in perechi_directii:
                        mutaretemp = (poz[0]+directie[0],poz[1]+directie[1])
                        if (
                            not 0 <= mutaretemp[0] < Joc.NR_LINII
                            or not 0 <= mutaretemp[1] < Joc.NR_COLOANE
                        ):
                            continue
                        if(self.tabla_joc.matr[mutaretemp[0]][mutaretemp[1]] != Joc.GOL and self.tabla_joc.matr[mutaretemp[0]][mutaretemp[1]] != culoarem and self.tabla_joc.matr[mutaretemp[0]][mutaretemp[1]] != culoareM):
                            #adica daca in diagonala e piesa opusa
                            mutaretemp1 = (mutaretemp[0]+directie[0],mutaretemp[1]+directie[1])
                            if (
                            not 0 <= mutaretemp1[0] < Joc.NR_LINII
                            or not 0 <= mutaretemp1[1] < Joc.NR_COLOANE
                            ):
                                continue
                            if(self.tabla_joc.matr[mutaretemp1[0]][mutaretemp1[1]] == Joc.GOL):
                                sarit = True
                                lista.append(mutaretemp1)

            elif (self.tabla_joc.matr[poz[0]][poz[1]] == culoareM):
                perechi_directii = [
                        [(1, 1), (-1, -1)],
                        [(1, -1), (-1, 1)],
                    ]
                for pereche_directie in perechi_directii:
                    for directie in pereche_directie:
                        mutaretemp = (poz[0]+directie[0],poz[1]+directie[1])
                        if (
                            not 0 <= mutaretemp[0] < Joc.NR_LINII
                            or not 0 <= mutaretemp[1] < Joc.NR_COLOANE
                        ):
                            continue
                        if(self.tabla_joc.matr[mutaretemp[0]][mutaretemp[1]] != Joc.GOL and self.tabla_joc.matr[mutaretemp[0]][mutaretemp[1]] != culoarem and self.tabla_joc.matr[mutaretemp[0]][mutaretemp[1]] != culoareM):
                            #adica daca in diagonala e piesa opusa
                            mutaretemp1 = (mutaretemp[0]+directie[0],mutaretemp[1]+directie[1])
                            if (
                            not 0 <= mutaretemp1[0] < Joc.NR_LINII
                            or not 0 <= mutaretemp1[1] < Joc.NR_COLOANE
                            ):
                                continue
                            if(self.tabla_joc.matr[mutaretemp1[0]][mutaretemp1[1]] == Joc.GOL):
                                sarit = True
                                lista.append(mutaretemp1)
            if(not sarit):
                if(self.tabla_joc.matr[poz[0]][poz[1]] == culoarem ):
                    perechi_directii = [(1,1),(1,-1)]
                    for directie in perechi_directii:
                            mutaretemp = (poz[0]+directie[0],poz[1]+directie[1])
                            if (
                                not 0 <= mutaretemp[0] < Joc.NR_LINII
                                or not 0 <= mutaretemp[1] < Joc.NR_COLOANE
                            ):
                                continue
                            if(self.tabla_joc.matr[mutaretemp[0]][mutaretemp[1]] == Joc.GOL):
                                lista.append(mutaretemp)
                elif(self.tabla_joc.matr[poz[0]][poz[1]] == culoareM):
                    perechi_directii = [
                        [(1, 1), (-1, -1)],
                        [(1, -1), (-1, 1)],
                    ]
                    for pereche_directie in perechi_directii:
                        for directie in pereche_directie:
                            mutaretemp = (poz[0]+directie[0],poz[1]+directie[1])
                            if (
                                not 0 <= mutaretemp[0] < Joc.NR_LINII
                                or not 0 <= mutaretemp[1] < Joc.NR_COLOANE
                            ):
                                continue
                            if(self.tabla_joc.matr[mutaretemp[0]][mutaretemp[1]] == Joc.GOL):
                                lista.append(mutaretemp)
  
        return lista

    def sarituri(self):
        listaf = []
        listai = []
        culoarem = self.j_curent
        culoareM = chr(ord(culoarem)-32)
        if(culoarem == "n"):
            for i in range(Joc.NR_LINII):
                for j in range(Joc.NR_COLOANE):
                    poz = (i,j)
                    if(self.tabla_joc.matr[poz[0]][poz[1]] == culoarem ):
                        perechi_directii = [(-1, -1),(-1, 1)]
                        for directie in perechi_directii:
                                mutaretemp = (poz[0]+directie[0],poz[1]+directie[1])
                                if (
                                    not 0 <= mutaretemp[0] < Joc.NR_LINII
                                    or not 0 <= mutaretemp[1] < Joc.NR_COLOANE
                                ):
                                    continue
                                if(self.tabla_joc.matr[mutaretemp[0]][mutaretemp[1]] != Joc.GOL and self.tabla_joc.matr[mutaretemp[0]][mutaretemp[1]] != culoarem and self.tabla_joc.matr[mutaretemp[0]][mutaretemp[1]] != culoareM):
                                    #adica daca in diagonala e piesa opusa
                                    mutaretemp1 = (mutaretemp[0]+directie[0],mutaretemp[1]+directie[1])
                                    if (
                                    not 0 <= mutaretemp1[0] < Joc.NR_LINII
                                    or not 0 <= mutaretemp1[1] < Joc.NR_COLOANE
                                    ):
                                        continue
                                    if(self.tabla_joc.matr[mutaretemp1[0]][mutaretemp1[1]] == Joc.GOL):
                                        listai.append(poz)
                                        listaf.append(mutaretemp1)
                    elif (self.tabla_joc.matr[poz[0]][poz[1]] == culoareM):
                        perechi_directii = [
                                [(1, 1), (-1, -1)],
                                [(1, -1), (-1, 1)],
                            ]
                        for pereche_directie in perechi_directii:
                            for directie in pereche_directie:
                                mutaretemp = (poz[0]+directie[0],poz[1]+directie[1])
                                if (
                                    not 0 <= mutaretemp[0] < Joc.NR_LINII
                                    or not 0 <= mutaretemp[1] < Joc.NR_COLOANE
                                ):
                                    continue
                                if(self.tabla_joc.matr[mutaretemp[0]][mutaretemp[1]] != Joc.GOL and self.tabla_joc.matr[mutaretemp[0]][mutaretemp[1]] != culoarem and self.tabla_joc.matr[mutaretemp[0]][mutaretemp[1]] != culoareM):
                                    #adica daca in diagonala e piesa opusa
                                    mutaretemp1 = (mutaretemp[0]+directie[0],mutaretemp[1]+directie[1])
                                    if (
                                    not 0 <= mutaretemp1[0] < Joc.NR_LINII
                                    or not 0 <= mutaretemp1[1] < Joc.NR_COLOANE
                                    ):
                                        continue
                                    if(self.tabla_joc.matr[mutaretemp1[0]][mutaretemp1[1]] == Joc.GOL):
                                        sarit = True
                                        listai.append(poz)
                                        listaf.append(mutaretemp1)
        elif(culoarem == "a"):
            for i in range(Joc.NR_LINII):
                for j in range(Joc.NR_COLOANE):
                    poz = (i,j)
                    if(self.tabla_joc.matr[poz[0]][poz[1]] == culoarem):
                        perechi_directii = [(1,1),(1,-1)]
                        for directie in perechi_directii:
                                mutaretemp = (poz[0]+directie[0],poz[1]+directie[1])
                                if (
                                    not 0 <= mutaretemp[0] < Joc.NR_LINII
                                    or not 0 <= mutaretemp[1] < Joc.NR_COLOANE
                                ):
                                    continue
                                if(self.tabla_joc.matr[mutaretemp[0]][mutaretemp[1]] != Joc.GOL and self.tabla_joc.matr[mutaretemp[0]][mutaretemp[1]] != culoarem and self.tabla_joc.matr[mutaretemp[0]][mutaretemp[1]] != culoareM):
                                    #adica daca in diagonala e piesa opusa
                                    mutaretemp1 = (mutaretemp[0]+directie[0],mutaretemp[1]+directie[1])
                                    if (
                                    not 0 <= mutaretemp1[0] < Joc.NR_LINII
                                    or not 0 <= mutaretemp1[1] < Joc.NR_COLOANE
                                    ):
                                        continue
                                    if(self.tabla_joc.matr[mutaretemp1[0]][mutaretemp1[1]] == Joc.GOL):
                                        listai.append(poz)
                                        listaf.append(mutaretemp1)
                    elif (self.tabla_joc.matr[poz[0]][poz[1]] == culoareM):
                        perechi_directii = [
                                [(1, 1), (-1, -1)],
                                [(1, -1), (-1, 1)],
                            ]
                        for pereche_directie in perechi_directii:
                            for directie in pereche_directie:
                                mutaretemp = (poz[0]+directie[0],poz[1]+directie[1])
                                if (
                                    not 0 <= mutaretemp[0] < Joc.NR_LINII
                                    or not 0 <= mutaretemp[1] < Joc.NR_COLOANE
                                ):
                                    continue
                                if(self.tabla_joc.matr[mutaretemp[0]][mutaretemp[1]] != Joc.GOL and self.tabla_joc.matr[mutaretemp[0]][mutaretemp[1]] != culoarem and self.tabla_joc.matr[mutaretemp[0]][mutaretemp[1]] != culoareM):
                                    #adica daca in diagonala e piesa opusa
                                    mutaretemp1 = (mutaretemp[0]+directie[0],mutaretemp[1]+directie[1])
                                    if (
                                    not 0 <= mutaretemp1[0] < Joc.NR_LINII
                                    or not 0 <= mutaretemp1[1] < Joc.NR_COLOANE
                                    ):
                                        continue
                                    if(self.tabla_joc.matr[mutaretemp1[0]][mutaretemp1[1]] == Joc.GOL):
                                        sarit = True
                                        listai.append(poz)
                                        listaf.append(mutaretemp1)   
        return (listai,listaf)

    def __str__(self):
        sir = str(self.tabla_joc) + "(Juc curent:" + self.j_curent + ")\n"
        return sir

    def __repr__(self):
        sir = str(self.tabla_joc) + "(Juc curent:" + self.j_curent + ")\n"
        return sir

class GrupButoane:
    def __init__(
        self, listaButoane=[], indiceSelectat=0, spatiuButoane=10, left=0, top=0
    ):
        self.listaButoane = listaButoane
        self.indiceSelectat = indiceSelectat
        self.listaButoane[self.indiceSelectat].selectat = True
        self.top = top
        self.left = left
        leftCurent = self.left
        for b in self.listaButoane:
            b.top = self.top
            b.left = leftCurent
            b.updateDreptunghi()
            leftCurent += spatiuButoane + b.w

    def selecteazaDupacoord(self, coord):
        for ib, b in enumerate(self.listaButoane):
            if b.selecteazaDupacoord(coord):
                self.listaButoane[self.indiceSelectat].selecteaza(False)
                self.indiceSelectat = ib
                return True
        return False

    def deseneaza(self):
        # atentie, nu face wrap
        for b in self.listaButoane:
            b.deseneaza()

    def getValoare(self):
        return self.listaButoane[self.indiceSelectat].valoare

def deseneaza_alegeri(display, tabla_curenta):
    btn_alg = GrupButoane(
        top=30,
        left=30,
        listaButoane=[
            Buton(display=display, w=80, h=30, text="minimax", valoare="minimax"),
            Buton(display=display, w=80, h=30, text="alphabeta", valoare="alphabeta"),
        ],
        indiceSelectat=1,
    )
    btn_juc = GrupButoane(
        top=100,
        left=30,
        listaButoane=[
            Buton(display=display, w=50, h=30, text="alb", valoare="a"),
            Buton(display=display, w=50, h=30, text="negru", valoare="n"),
        ],
        indiceSelectat=0,
    )
    btn_choice = GrupButoane(
        top = 170,
        left = 30,
        listaButoane=[
            Buton(display = display, w= 35, h=30, text="PvC", valoare ="pvc"),
            Buton(display=display, w= 35, h=30, text="PvP", valoare ="pvp"),
            Buton(display=display, w= 35, h=30, text="CvC", valoare ="cvc"),
        ],
        indiceSelectat=0,
    )
    btn_difilcutate = GrupButoane(
        top = 240,
        left = 30,
        listaButoane=[
            Buton(display = display, w= 60,h=30,text ="easy",valoare ="easy"),
            Buton(display = display, w= 60,h=30,text ="medium",valoare ="medium"),
            Buton(display = display, w= 60,h=30,text ="hard",valoare ="hard"),
        ],
        indiceSelectat=0
    )
    ok = Buton(
        display=display,
        top=310,
        left=30,
        w=40,
        h=30,
        text="ok",
        culoareFundal=(155, 0, 55),
    )
    btn_alg.deseneaza()
    btn_juc.deseneaza()
    btn_choice.deseneaza()
    btn_difilcutate.deseneaza()
    ok.deseneaza()
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif ev.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if not btn_alg.selecteazaDupacoord(pos):
                    if not btn_juc.selecteazaDupacoord(pos):
                        if not btn_choice.selecteazaDupacoord(pos):
                            if not btn_difilcutate.selecteazaDupacoord(pos):
                                if ok.selecteazaDupacoord(pos):
                                    tabla_curenta.deseneaza_grid()
                                    return btn_juc.getValoare(), btn_alg.getValoare(),btn_choice.getValoare(),btn_difilcutate.getValoare()
        pygame.display.update()


def main():
    #setam interfata grafica
    pygame.init()
    pygame.display.set_caption("Anghel Alin-Cosmin - Dame")
    nl = 8
    nc = 8
    w = 75

    ecran = pygame.display.set_mode(
        size=(nc * (w + 1) - 1, nl * (w + 1) - 1)
    )  # N *100+ N-1= N*(100+1)-1
    Joc.initializeaza(ecran, NR_LINII=nl, NR_COLOANE=nc, dim_celula=w)

    # initializare tabla
    tabla_curenta = Joc()
    Joc.JMIN, tip_algoritm, mod,dificultate = deseneaza_alegeri(ecran, tabla_curenta)
    
    if(dificultate=="easy"):
        ADANCIME_MAX = 2
    elif(dificultate=="medium"):
        ADANCIME_MAX = 5
    else:
        ADANCIME_MAX = 8
        
    print(Joc.JMIN, tip_algoritm)

    if(mod == "pvc"):
        print(ADANCIME_MAX)
        # JMAx = calculator jMIN = player
        Joc.JMAX = "a" if Joc.JMIN == "n" else "n"

        print("Tabla initiala")
        print(str(tabla_curenta))

        # creare stare initiala
        # jucatorul cu piese negre incepe
        stare_curenta = Stare(tabla_curenta, "n", ADANCIME_MAX)

        de_mutat = False
        tabla_curenta.deseneaza_grid()
        while True:
            if stare_curenta.j_curent == Joc.JMIN:
                if(Joc.JMIN == "n"):
                    linie_rege = 0
                else:
                    linie_rege = 7

                obligat = stare_curenta.sarituri() # o sa fac o lista cu doua liste in prima lista avem piesa care face saritura si a doua o sa aiba pozitia pe care ajunge
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        pos = pygame.mouse.get_pos()  # coordonatele cursorului

                        for np in range(len(Joc.celuleGrid)):
                            if Joc.celuleGrid[np].collidepoint(pos):
                                linie = np // Joc.NR_LINII
                                coloana = np % Joc.NR_COLOANE
                                if stare_curenta.tabla_joc.matr[linie][coloana] == Joc.JMIN or stare_curenta.tabla_joc.matr[linie][coloana] == chr(ord(Joc.JMIN)-32):
                                    if(de_mutat and linie == de_mutat[0] and coloana == de_mutat[1]):
                                        de_mutat= False
                                        stare_curenta.tabla_joc.deseneaza_grid()
                                    else:
                                        de_mutat = (linie,coloana)
                                        #desenez gridul cu patratelul marcat
                                        stare_curenta.tabla_joc.deseneaza_grid(de_mutat)
                                if stare_curenta.tabla_joc.matr[linie][coloana] == Joc.GOL:
                                    if de_mutat:
                                        ### teste legate de mutarea simbolului
                                        ## bun deci aici vom avea o functie care ne va return tupluri de mutari(pozitii) pe care le poate face piesa marcata
                                        optiuni = stare_curenta.options(de_mutat)
                                        if(obligat != ([],[])):
                                            try:
                                                index = obligat[1].index((linie,coloana))
                                            except:
                                                index = 0
                                        
                                            if((linie,coloana) == obligat[1][index] and (linie,coloana) in optiuni and de_mutat == obligat[0][index]):
                                                salt = False
                                                if(de_mutat[0]+2 == linie and de_mutat[1]+2 == coloana):
                                                    stare_curenta.tabla_joc.matr[de_mutat[0]+1][de_mutat[1]+1] = Joc.GOL
                                                    salt = True
                                                elif(de_mutat[0]+2 == linie and de_mutat[1]-2 == coloana):
                                                    stare_curenta.tabla_joc.matr[de_mutat[0]+1][de_mutat[1]-1] = Joc.GOL
                                                    salt = True
                                                elif(de_mutat[0]-2 == linie and de_mutat[1]-2 == coloana):
                                                    stare_curenta.tabla_joc.matr[de_mutat[0]-1][de_mutat[1]-1] = Joc.GOL
                                                    salt = True
                                                elif(de_mutat[0]-2 == linie and de_mutat[1]+2 == coloana):
                                                    stare_curenta.tabla_joc.matr[de_mutat[0]-1][de_mutat[1]+1] = Joc.GOL
                                                    salt = True
                                                if(linie_rege == linie):
                                                    stare_curenta.tabla_joc.matr[linie][coloana] = chr(ord(Joc.JMIN)-32)
                                                    devenit = True
                                                else:
                                                    stare_curenta.tabla_joc.matr[linie][coloana] = stare_curenta.tabla_joc.matr[de_mutat[0]][de_mutat[1]]
                                                    devenit = False
                                                stare_curenta.tabla_joc.matr[de_mutat[0]][de_mutat[1]] = Joc.GOL
                                                stare_curenta.tabla_joc.ultima_mutare = (linie,coloana)
                                                de_mutat=False
                                                # afisarea starii jocului in urma mutarii utilizatorului
                                                print("\nTabla dupa mutarea jucatorului")
                                                print(str(stare_curenta))

                                                stare_curenta.tabla_joc.deseneaza_grid()
                                                # testez daca jocul a ajuns intr-o stare finala
                                                # si afisez un mesaj corespunzator in caz ca da
                                                if afis_daca_final(stare_curenta):
                                                    break

                                                # S-a realizat o mutare. Schimb jucatorul cu cel opus
                                                # aici o sa apara modificare pentru salt
                                                if(stare_curenta.sarituri() == ([],[]) or devenit ):
                                                    stare_curenta.j_curent = Joc.jucator_opus(
                                                    stare_curenta.j_curent
                                                    )
                                        elif((linie,coloana) in optiuni):
                                            if(linie_rege == linie):
                                                stare_curenta.tabla_joc.matr[linie][coloana] = chr(ord(Joc.JMIN)-32)

                                            else:
                                                stare_curenta.tabla_joc.matr[linie][coloana] = stare_curenta.tabla_joc.matr[de_mutat[0]][de_mutat[1]]

                                            stare_curenta.tabla_joc.matr[de_mutat[0]][de_mutat[1]] = Joc.GOL
                                            stare_curenta.tabla_joc.ultima_mutare = (linie,coloana)
                                            de_mutat=False
                                            # afisarea starii jocului in urma mutarii utilizatorului
                                            print("\nTabla dupa mutarea jucatorului")
                                            print(str(stare_curenta))

                                            stare_curenta.tabla_joc.deseneaza_grid()
                                            # testez daca jocul a ajuns intr-o stare finala
                                            # si afisez un mesaj corespunzator in caz ca da
                                            if afis_daca_final(stare_curenta):
                                                break

                                            # S-a realizat o mutare. Schimb jucatorul cu cel opus
                                            # aici o sa apara modificare pentru salt
                                            stare_curenta.j_curent = Joc.jucator_opus(
                                            stare_curenta.j_curent
                                            )

            # --------------------------------
            else:  # jucatorul e JMAX (calculatorul)
                # Mutare calculator

                # preiau timpul in milisecunde de dinainte de mutare
                t_inainte = int(round(time.time() * 1000))
                if tip_algoritm == "minimax":
                    stare_actualizata = min_max(stare_curenta)
                else:  # tip_algoritm=="alphabeta"
                    stare_actualizata = alpha_beta(-500, 500, stare_curenta)
                k = 1
                #daca inainte de urmatoarea stare nu eram obligat sa sar trb sa pasez tura
                if(stare_curenta.sarituri() == ([],[])):
                    k = 0
                stare_curenta.tabla_joc = stare_actualizata.stare_aleasa.tabla_joc

                print("Tabla dupa mutarea calculatorului\n" + str(stare_curenta))

                # preiau timpul in milisecunde de dupa mutare
                t_dupa = int(round(time.time() * 1000))
                print(
                    'Calculatorul a "gandit" timp de '
                    + str(t_dupa - t_inainte)
                    + " milisecunde."
                )

                stare_curenta.tabla_joc.deseneaza_grid()
                if afis_daca_final(stare_curenta):
                    break
                rege = False
                temp = stare_curenta.tabla_joc.ultima_mutare
                if (stare_curenta.j_curent == "n" and temp[0] == 0):
                    rege = True
                elif(stare_curenta.j_curent == "a" and temp[0] == 1):
                    rege = True

                # S-a realizat o mutare. Schimb jucatorul cu cel opus
                if(stare_curenta.sarituri() == ([],[]) or k ==0 or rege):
                    stare_curenta.j_curent = Joc.jucator_opus(stare_curenta.j_curent)
    elif(mod == "cvc"):
        Joc.JMAX = "a" if Joc.JMIN == "n" else "n"
        tip_algoritm1 = "alphabeta" if tip_algoritm =="minimax" else "minimax"

        print("Tabla initiala")
        print(str(tabla_curenta))

        stare_curenta = Stare(tabla_curenta, "n", ADANCIME_MAX)

        tabla_curenta.deseneaza_grid()
        while True:
            # preiau timpul in milisecunde de dinainte de mutare
                t_inainte = int(round(time.time() * 1000))
                if tip_algoritm == "minimax":
                    stare_actualizata = min_max(stare_curenta)
                else:  # tip_algoritm=="alphabeta"
                    stare_actualizata = alpha_beta(-500, 500, stare_curenta)
                k = 1
                #daca inainte de urmatoarea stare nu eram obligat sa sar trb sa pasez tura
                if(stare_curenta.sarituri() == ([],[])):
                    k = 0
                stare_curenta.tabla_joc = stare_actualizata.stare_aleasa.tabla_joc

                print("Tabla dupa mutarea calculatorului\n" + str(stare_curenta))

                # preiau timpul in milisecunde de dupa mutare
                t_dupa = int(round(time.time() * 1000))
                print(
                    'Calculatorul a "gandit" timp de '
                    + str(t_dupa - t_inainte)
                    + " milisecunde."
                )

                stare_curenta.tabla_joc.deseneaza_grid()
                if afis_daca_final(stare_curenta):
                    break
                rege = False
                temp = stare_curenta.tabla_joc.ultima_mutare
                if (stare_curenta.j_curent == "n" and temp[0] == 0):
                    rege = True
                elif(stare_curenta.j_curent == "a" and temp[0] == 1):
                    rege = True

                # S-a realizat o mutare. Schimb jucatorul cu cel opus
                if(stare_curenta.sarituri() == ([],[]) or k ==0 or rege):
                    stare_curenta.j_curent = Joc.jucator_opus(stare_curenta.j_curent)
                    temp = tip_algoritm
                    tip_algoritm = tip_algoritm1
                    tip_algoritm1 = temp
    elif(mod == "pvp"):
        print(mod)
        Joc.JMAX = "a" if Joc.JMIN == "n" else "n"

        print("Tabla initiala")
        print(str(tabla_curenta))

        # creare stare initiala
        # jucatorul cu piese negre incepe
        stare_curenta = Stare(tabla_curenta, "n", ADANCIME_MAX)

        de_mutat = False
        while True:
            if stare_curenta.j_curent == Joc.JMIN:
                if(Joc.JMIN == "n"):
                    linie_rege = 0
                else:
                    linie_rege = 7
                obligat = stare_curenta.sarituri() # o sa fac o lista cu doua liste in prima lista avem piesa care face saritura si a doua o sa aiba pozitia pe care ajunge
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        pos = pygame.mouse.get_pos()  # coordonatele cursorului

                        for np in range(len(Joc.celuleGrid)):
                            if Joc.celuleGrid[np].collidepoint(pos):
                                linie = np // Joc.NR_LINII
                                coloana = np % Joc.NR_COLOANE
                                if stare_curenta.tabla_joc.matr[linie][coloana] == Joc.JMIN or stare_curenta.tabla_joc.matr[linie][coloana] == chr(ord(Joc.JMIN)-32):
                                    if(de_mutat and linie == de_mutat[0] and coloana == de_mutat[1]):
                                        de_mutat= False
                                        stare_curenta.tabla_joc.deseneaza_grid()
                                    else:
                                        de_mutat = (linie,coloana)
                                        #desenez gridul cu patratelul marcat
                                        stare_curenta.tabla_joc.deseneaza_grid(de_mutat)
                                if stare_curenta.tabla_joc.matr[linie][coloana] == Joc.GOL:
                                    if de_mutat:
                                        ### teste legate de mutarea simbolului
                                        ## bun deci aici vom avea o functie care ne va return tupluri de mutari(pozitii) pe care le poate face piesa marcata
                                        optiuni = stare_curenta.options(de_mutat)
                                        if(obligat != ([],[])):
                                            try:
                                                index = obligat[1].index((linie,coloana))
                                            except:
                                                index = 0
                                        
                                            if((linie,coloana) == obligat[1][index] and (linie,coloana) in optiuni and de_mutat == obligat[0][index]):
                                                salt = False
                                                if(de_mutat[0]+2 == linie and de_mutat[1]+2 == coloana):
                                                    stare_curenta.tabla_joc.matr[de_mutat[0]+1][de_mutat[1]+1] = Joc.GOL
                                                    salt = True
                                                elif(de_mutat[0]+2 == linie and de_mutat[1]-2 == coloana):
                                                    stare_curenta.tabla_joc.matr[de_mutat[0]+1][de_mutat[1]-1] = Joc.GOL
                                                    salt = True
                                                elif(de_mutat[0]-2 == linie and de_mutat[1]-2 == coloana):
                                                    stare_curenta.tabla_joc.matr[de_mutat[0]-1][de_mutat[1]-1] = Joc.GOL
                                                    salt = True
                                                elif(de_mutat[0]-2 == linie and de_mutat[1]+2 == coloana):
                                                    stare_curenta.tabla_joc.matr[de_mutat[0]-1][de_mutat[1]+1] = Joc.GOL
                                                    salt = True
                                                if(linie_rege == linie):
                                                    stare_curenta.tabla_joc.matr[linie][coloana] = chr(ord(Joc.JMIN)-32)
                                                    devenit = True
                                                else:
                                                    stare_curenta.tabla_joc.matr[linie][coloana] = stare_curenta.tabla_joc.matr[de_mutat[0]][de_mutat[1]]
                                                    devenit = False
                                                stare_curenta.tabla_joc.matr[de_mutat[0]][de_mutat[1]] = Joc.GOL
                                                stare_curenta.tabla_joc.ultima_mutare = (linie,coloana)
                                                de_mutat=False
                                                # afisarea starii jocului in urma mutarii utilizatorului
                                                print("\nTabla dupa mutarea jucatorului")
                                                print(str(stare_curenta))

                                                stare_curenta.tabla_joc.deseneaza_grid()
                                                # testez daca jocul a ajuns intr-o stare finala
                                                # si afisez un mesaj corespunzator in caz ca da
                                                if afis_daca_final(stare_curenta):
                                                    break

                                                # S-a realizat o mutare. Schimb jucatorul cu cel opus
                                                # aici o sa apara modificare pentru salt
                                                if(stare_curenta.sarituri() == ([],[]) or devenit ):
                                                    stare_curenta.j_curent = Joc.jucator_opus(
                                                    stare_curenta.j_curent
                                                    )
                                        elif((linie,coloana) in optiuni):
                                            if(linie_rege == linie):
                                                stare_curenta.tabla_joc.matr[linie][coloana] = chr(ord(Joc.JMIN)-32)

                                            else:
                                                stare_curenta.tabla_joc.matr[linie][coloana] = stare_curenta.tabla_joc.matr[de_mutat[0]][de_mutat[1]]

                                            stare_curenta.tabla_joc.matr[de_mutat[0]][de_mutat[1]] = Joc.GOL
                                            stare_curenta.tabla_joc.ultima_mutare = (linie,coloana)
                                            de_mutat=False
                                            # afisarea starii jocului in urma mutarii utilizatorului
                                            print("\nTabla dupa mutarea jucatorului")
                                            print(str(stare_curenta))

                                            stare_curenta.tabla_joc.deseneaza_grid()
                                            # testez daca jocul a ajuns intr-o stare finala
                                            # si afisez un mesaj corespunzator in caz ca da
                                            if afis_daca_final(stare_curenta):
                                                break

                                            # S-a realizat o mutare. Schimb jucatorul cu cel opus
                                            # aici o sa apara modificare pentru salt
                                            stare_curenta.j_curent = Joc.jucator_opus(
                                            stare_curenta.j_curent
                                            )
            elif stare_curenta.j_curent == Joc.JMAX:
                if(Joc.JMAX == "n"):
                    linie_rege = 0
                else:
                    linie_rege = 7

                obligat = stare_curenta.sarituri() # o sa fac o lista cu doua liste in prima lista avem piesa care face saritura si a doua o sa aiba pozitia pe care ajunge
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        pos = pygame.mouse.get_pos()  # coordonatele cursorului

                        for np in range(len(Joc.celuleGrid)):
                            if Joc.celuleGrid[np].collidepoint(pos):
                                linie = np // Joc.NR_LINII
                                coloana = np % Joc.NR_COLOANE
                                if stare_curenta.tabla_joc.matr[linie][coloana] == Joc.JMAX or stare_curenta.tabla_joc.matr[linie][coloana] == chr(ord(Joc.JMAX)-32):
                                    if(de_mutat and linie == de_mutat[0] and coloana == de_mutat[1]):
                                        de_mutat= False
                                        stare_curenta.tabla_joc.deseneaza_grid()
                                    else:
                                        de_mutat = (linie,coloana)
                                        #desenez gridul cu patratelul marcat
                                        stare_curenta.tabla_joc.deseneaza_grid(de_mutat)
                                if stare_curenta.tabla_joc.matr[linie][coloana] == Joc.GOL:
                                    if de_mutat:
                                        ### teste legate de mutarea simbolului
                                        ## bun deci aici vom avea o functie care ne va return tupluri de mutari(pozitii) pe care le poate face piesa marcata
                                        optiuni = stare_curenta.options(de_mutat)
                                        if(obligat != ([],[])):
                                            try:
                                                index = obligat[1].index((linie,coloana))
                                            except:
                                                index = 0
                                        
                                            if((linie,coloana) == obligat[1][index] and (linie,coloana) in optiuni and de_mutat == obligat[0][index]):
                                                salt = False
                                                if(de_mutat[0]+2 == linie and de_mutat[1]+2 == coloana):
                                                    stare_curenta.tabla_joc.matr[de_mutat[0]+1][de_mutat[1]+1] = Joc.GOL
                                                    salt = True
                                                elif(de_mutat[0]+2 == linie and de_mutat[1]-2 == coloana):
                                                    stare_curenta.tabla_joc.matr[de_mutat[0]+1][de_mutat[1]-1] = Joc.GOL
                                                    salt = True
                                                elif(de_mutat[0]-2 == linie and de_mutat[1]-2 == coloana):
                                                    stare_curenta.tabla_joc.matr[de_mutat[0]-1][de_mutat[1]-1] = Joc.GOL
                                                    salt = True
                                                elif(de_mutat[0]-2 == linie and de_mutat[1]+2 == coloana):
                                                    stare_curenta.tabla_joc.matr[de_mutat[0]-1][de_mutat[1]+1] = Joc.GOL
                                                    salt = True
                                                if(linie_rege == linie):
                                                    stare_curenta.tabla_joc.matr[linie][coloana] = chr(ord(Joc.JMAX)-32)
                                                    devenit = True
                                                else:
                                                    stare_curenta.tabla_joc.matr[linie][coloana] = stare_curenta.tabla_joc.matr[de_mutat[0]][de_mutat[1]]
                                                    devenit = False
                                                stare_curenta.tabla_joc.matr[de_mutat[0]][de_mutat[1]] = Joc.GOL
                                                stare_curenta.tabla_joc.ultima_mutare = (linie,coloana)
                                                de_mutat=False
                                                # afisarea starii jocului in urma mutarii utilizatorului
                                                print("\nTabla dupa mutarea jucatorului")
                                                print(str(stare_curenta))

                                                stare_curenta.tabla_joc.deseneaza_grid()
                                                # testez daca jocul a ajuns intr-o stare finala
                                                # si afisez un mesaj corespunzator in caz ca da
                                                if afis_daca_final(stare_curenta):
                                                    break

                                                # S-a realizat o mutare. Schimb jucatorul cu cel opus
                                                # aici o sa apara modificare pentru salt
                                                if(stare_curenta.sarituri() == ([],[]) or devenit ):
                                                    stare_curenta.j_curent = Joc.jucator_opus(
                                                    stare_curenta.j_curent
                                                    )
                                        elif((linie,coloana) in optiuni):
                                            if(linie_rege == linie):
                                                stare_curenta.tabla_joc.matr[linie][coloana] = chr(ord(Joc.JMAX)-32)

                                            else:
                                                stare_curenta.tabla_joc.matr[linie][coloana] = stare_curenta.tabla_joc.matr[de_mutat[0]][de_mutat[1]]

                                            stare_curenta.tabla_joc.matr[de_mutat[0]][de_mutat[1]] = Joc.GOL
                                            stare_curenta.tabla_joc.ultima_mutare = (linie,coloana)
                                            de_mutat=False
                                            # afisarea starii jocului in urma mutarii utilizatorului
                                            print("\nTabla dupa mutarea jucatorului")
                                            print(str(stare_curenta))

                                            stare_curenta.tabla_joc.deseneaza_grid()
                                            # testez daca jocul a ajuns intr-o stare finala
                                            # si afisez un mesaj corespunzator in caz ca da
                                            if afis_daca_final(stare_curenta):
                                                break

                                            # S-a realizat o mutare. Schimb jucatorul cu cel opus
                                            # aici o sa apara modificare pentru salt
                                            stare_curenta.j_curent = Joc.jucator_opus(
                                            stare_curenta.j_curent
                                            )

if __name__ == "__main__":
    main()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()