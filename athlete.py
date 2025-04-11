import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit
import warnings
import wr_data as wr
import pwlf
warnings.simplefilter("ignore", category=RuntimeWarning)

#import tkinter as tk

def wr_model(poids, slope, offset_X, amplitude):
    X = poids - offset_X
    return amplitude/(1 + np.exp(-slope * X))


def score_SBD(sexe, poids, age, SBD):

    facteur_age = facteur_age_sbd(age)

    if sexe == 'H':
        wr = facteur_age * wr_model(poids, *model_params_homme)

    elif sexe == 'F':
        wr = facteur_age * wr_model(poids, *model_params_femme)

    else:
        raise Exception("ERREUR: Sexe doit être H ou F")

    baseline = 0.15 * wr

    return max((SBD-baseline)/(wr-baseline), 0)

def facteur_age_marathon(age):

    # On fit une 4 lignes pour décrire l'évolution records du monde selon l'age des hommes (moins biaisé par le manque de perf).
    # On normalise entre 0 et 1 pour avoir le facteur à appliquer

    vitesse_homme = 60 * 42/wr.marathon_age_homme[:, 1]
    normed_vitesse = vitesse_homme/max(vitesse_homme)

    x0 = np.array([0, 23, 40, 80, 110])
    marathon_age_model = pwlf.PiecewiseLinFit(wr.marathon_age_homme[:, 0], normed_vitesse)
    marathon_age_model.fit_with_breaks(x0)
    facteur = marathon_age_model.predict(age)[0]

    #plt.scatter(wr.marathon_age_homme[:, 0], vitesse_homme/max(vitesse_homme), color='blue')
    #age_range = np.linspace(15, 100, 100)
    #plt.plot(age_range, yHat, color='blue', alpha=0.4, linewidth=4)

    return facteur

def facteur_age_sbd(age):

    # On fit une 2 lignes pour décrire l'évolution records du monde selon l'age des hommes (moins biaisé par le manque de perf).
    # On normalise entre 0 et 1 pour avoir le facteur à appliquer

    normed_sbd_wr = wr.sbd_age_homme74[:, 1]/wr.sbd_age_homme74[:, 1].max()

    x0 = np.array([16, 26, 80])
    sbd_age_model = pwlf.PiecewiseLinFit(wr.sbd_age_homme74[:, 0], normed_sbd_wr)
    sbd_age_model.fit_with_breaks(x0)
    facteur = sbd_age_model.predict(age)[0]

    #plt.scatter(wr.sbd_age_homme74[:, 0], normed_sbd_wr, color='blue')
    #age_range = np.linspace(15, 100, 100)
    #plt.plot(age_range, sbd_age_model(age_range, *model_sbd_age_homme_params),color='blue', alpha=0.4, linewidth=4)

    return facteur

def score_endurance(sexe, age, temps_marathon=None, temps_semi=None):

    mdist = 42.195
    facteur_age = facteur_age_marathon(age)
    if sexe == 'H':
        wr_marathon = facteur_age * mdist / wr.marathon_age_homme[0, 1]
        wr_semi = facteur_age * (mdist/2) / wr.semi_age_homme[0, 1]

    elif sexe == 'F':
        wr_marathon = facteur_age * mdist / wr.marathon_age_femme[0, 1]
        wr_semi = facteur_age * (mdist/2) / wr.semi_age_femme[0, 1]

    else:
        raise Exception("ERREUR: Sexe doit être H ou F")

    baseline_ratio = 4

    baseline_marathon = wr_marathon / baseline_ratio
    baseline_semi = wr_semi / baseline_ratio

    scores = [np.nan, np.nan]

    if temps_marathon is not None:
        vitesse_marathon = mdist/temps_marathon
        scores[0] = (vitesse_marathon - baseline_marathon) / (wr_marathon - baseline_marathon)

    if temps_semi is not None:
        vitesse_semi = (mdist/2)/temps_semi
        scores[1] = (vitesse_semi - baseline_semi) / (wr_semi - baseline_semi)

    return max(np.nanmean(scores), 0)


def score_athlete(sexe, poids, age, SBD, temps_marathon=None, temps_semi=None):

    if (temps_marathon==None) & (temps_semi==None):
        raise Exception("ERREUR: Veuillez renseigner au moins un temps de course")

    score_SBD_value = score_SBD(sexe, poids, age, SBD)
    score_endurance_value = score_endurance(sexe, age, temps_marathon=temps_marathon, temps_semi=temps_semi)

    tout = np.array([score_SBD_value, score_endurance_value])
    renormed_tout = score_renorm(tout)
    final = np.nanmean(renormed_tout)

    print(f"Votre score d'athlète est de {final:.1f}%")
    return final, renormed_tout

def score_renorm(x, n=1.5):

    for i in range(2):
        if x[i] >= 1:
            x[i] = 1
        elif x[i] <= 0:
            x[i] = 0

    x = x/2 + 0.5
    return 100 * ((x ** n) / ((x ** n) + ((1 - x) ** n)) -0.5) * 2


model_params_homme, _ = curve_fit(wr_model, wr.sbd_poids_homme[:, 0],  wr.sbd_poids_homme[:, 1], p0=[0.05, 50, 800])
model_params_femme, _ = curve_fit(wr_model,  wr.sbd_poids_femme[:, 0],  wr.sbd_poids_femme[:, 1], p0=[0.05, 50, 800])

'''
plt.figure(figsize=(10, 7))
poids_range = np.linspace(40, 150, 100)
plt.scatter(wr_sbd_homme[:, 0],  wr.sbd_poids_homme[:, 1], color='blue', label='WR hommes')
plt.plot(poids_range, wr_model(poids_range, *model_params_homme),
         color='blue', label='WR hommes théorique', alpha=0.4, linewidth=4)
plt.scatter(wr_sbd_femme[:, 0],  wr.sbd_poids_femme[:, 1], color='red', label='WR femmes')
plt.plot(poids_range, wr_model(poids_range, *model_params_femme),
         color='red', label='WR femmes théorique', alpha=0.4, linewidth=4)

plt.xlabel("Poids (kg)", fontsize=16)
plt.ylabel("S+B+D", fontsize=16)
plt.xlim(40, 145)
plt.legend()
plt.savefig("model_WR_SBD.png")
'''


if __name__=="__main__":
    sexe = 'H'
    poids = 81
    age = 22
    SBD = 273 + 253 + 140

    temps_marathon = None #238
    temps_semi = 80

    final, tout = score_athlete(sexe, poids, age, SBD, temps_marathon, temps_semi)
    print(final, tout)


    from tkinter import *

    root = Tk()
    root.geometry("300x300")
    root.title(" Q&A ")

    def Take_input():
        INPUT = inputtxt.get("1.0", "end-1c")
        print(INPUT)
        if(INPUT == "120"):
            Output.replace(END, 'Correct')
        else:
            Output.replace(END, "Wrong answer")

    lsbd = Label(text = "SBD ? ")
    input_sbd = Text(root, height = 3,
                    width = 10,
                    bg = "light yellow")

    lsbd.pack()
    input_sbd.pack()

    lsemi = Label(text = "semi ? ")
    input_semi = Text(root, height = 3,
                width = 10,
                bg = "light cyan")

    lsemi.pack()
    input_semi.pack()

    mainloop()
