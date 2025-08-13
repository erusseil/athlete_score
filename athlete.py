import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit
import warnings
import wr_data as wr
import pwlf
warnings.simplefilter("ignore", category=RuntimeWarning)


def wr_model(poids, slope, offset_X, amplitude):
    X = poids - offset_X
    return amplitude/(1 + np.exp(-slope * X))

def score_SBD(sexe, poids, age, S, B, D):
    
    SBD = 0
    if (type(S) is float) or (type(S) is int):
        SBD += S

    if (type(B) is float) or (type(B) is int):
        SBD += B

    if (type(D) is float) or (type(D) is int):
        SBD += D

    facteur_age = facteur_age_sbd(age)
    
    if (sexe == 'H') or (sexe == 'M'):
        wr_value = facteur_age * wr_model(poids, *model_params_homme)

    elif sexe == 'F':
        wr_value = facteur_age * wr_model(poids, *model_params_femme)


    else:
        raise Exception("ERREUR: Sex must be M or F")

    wr_percentages = wr.SBD_percentages * wr_value
    baseline_percentages = baseline_sbd * wr_percentages

    # Attempt to separate S, B, D scores. Isn't good because it depends on morphology
    '''
    if (type(S) is float) or (type(S) is int):
        final_s = min(1,max((S-baseline_percentages[0])/(wr_percentages[0]-baseline_percentages[0]), 0))
    else: 
        final_s = 0

    if (type(B) is float) or (type(B) is int):
        final_b = min(1,max((B-baseline_percentages[1])/(wr_percentages[1]-baseline_percentages[1]), 0))
    else:
        final_b = 0

    if (type(D) is float) or (type(D) is int):
        final_d = min(1,max((D-baseline_percentages[2])/(wr_percentages[2]-baseline_percentages[2]), 0))
    else:
        final_d = 0

    final_scores = np.array([final_s, final_b, final_d])
    '''

    return min(1,max((SBD-baseline_sbd)/(wr_value-baseline_sbd), 0))


def facteur_age_marathon(age):

    # On fit une 4 lignes pour décrire l'évolution records du monde selon l'age des hommes (moins biaisé par le manque de perf).
    # On normalise entre 0 et 1 pour avoir le facteur à appliquer

    vitesse_homme = 60 * 42/wr.marathon_age_homme[:, 1]
    normed_vitesse = vitesse_homme/max(vitesse_homme)

    x0 = np.array([0, 23, 40, 80, 110])
    marathon_age_model = pwlf.PiecewiseLinFit(wr.marathon_age_homme[:, 0], normed_vitesse)
    marathon_age_model.fit_with_breaks(x0)
    facteur = marathon_age_model.predict(age)[0]

    return facteur

def facteur_age_sbd(age):

    # On fit une 2 lignes pour décrire l'évolution records du monde selon l'age des hommes (moins biaisé par le manque de perf).
    # On normalise entre 0 et 1 pour avoir le facteur à appliquer

    normed_sbd_wr = wr.sbd_age_homme74[:, 1]/wr.sbd_age_homme74[:, 1].max()

    x0 = np.array([16, 26, 80])
    sbd_age_model = pwlf.PiecewiseLinFit(wr.sbd_age_homme74[:, 0], normed_sbd_wr)
    sbd_age_model.fit_with_breaks(x0)
    facteur = sbd_age_model.predict(age)[0]

    return facteur

def score_endurance(sexe, age, temps_marathon=None, temps_semi=None):

    mdist = 42.195
    facteur_age = facteur_age_marathon(age)

    if (sexe == 'H') or (sexe == 'M'):
        wr_marathon = facteur_age * mdist / wr.marathon_age_homme[:, 1].min()
        wr_semi = facteur_age * (mdist/2) / wr.semi_age_homme[:, 1].min()

    elif sexe == 'F':
        wr_marathon = facteur_age * mdist / wr.marathon_age_femme[:, 1].min()
        wr_semi = facteur_age * (mdist/2) / wr.semi_age_femme[:, 1].min()

    else:
        raise Exception("ERREUR: Sexe doit être H ou F")

    baseline_marathon = wr_marathon / baseline_endurance
    baseline_semi = wr_semi / baseline_endurance

    # Return the score based on marathon in priority, and semi else if it is the only available
    if (temps_marathon is None) and (temps_semi is None):
        return 0

    if temps_marathon is not None:
        if temps_marathon == 0:
            return 0
        vitesse_marathon = mdist/temps_marathon
        return min(1, max(0, (vitesse_marathon - baseline_marathon) / (wr_marathon - baseline_marathon)))

    if temps_semi is not None:
        if temps_semi == 0:
            return 0
        vitesse_semi = (mdist/2)/temps_semi
        return min(1, max(0, (vitesse_semi - baseline_semi) / (wr_semi - baseline_semi)))


def score_athlete(sexe, poids, age, S, B, D, temps_marathon=None, temps_semi=None):

    if (temps_marathon==None) & (temps_semi==None):
        score_endurance_value = 0

    else: 
        score_endurance_value = score_endurance(sexe, age, temps_marathon=temps_marathon, temps_semi=temps_semi)

    score_SBD_value = score_SBD(sexe, poids, age, S, B, D)
    renormed_force = score_renorm(score_SBD_value)
    renormed_endurance = score_renorm(score_endurance_value)
    
    final = np.nanmean([renormed_force, renormed_endurance])

    # We multiply by a small value to enable a theoritical 100% hybrid score.
    # Otherwise a perfect hybrid athlete would need to reach 100% strength and endurance
    bonus = 1.05
    final = np.where(bonus*final<1, bonus*final, 1)
    
    return 100*final, 100*score_SBD_value, 100*score_endurance_value

def score_renorm(x, n=1.5):
    
    if type(x)==float:
        x = min(1, x)
        x = max(0, x)         
        x = x/2 + 0.5
        score = ((x ** n) / ((x ** n) + ((1 - x) ** n)) -0.5) * 2
        return score

    else:
        x = np.where(x<=1, x, 1)
        x = np.where(x>=0, x, 0)
        x = x/2 + 0.5
        score = ((x ** n) / ((x ** n) + ((1 - x) ** n)) -0.5) * 2
        return score


model_params_homme, _ = curve_fit(wr_model, wr.sbd_poids_homme[:, 0],  wr.sbd_poids_homme[:, 1], p0=[0.05, 50, 800])
model_params_femme, _ = curve_fit(wr_model,  wr.sbd_poids_femme[:, 0],  wr.sbd_poids_femme[:, 1], p0=[0.05, 50, 800])
baseline_sbd = 0.15
baseline_endurance = 4
