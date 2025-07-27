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

def score_SBD(sexe, poids, age, SBD, do_plot=False):
    
    facteur_age = facteur_age_sbd(age)

    X_poids = np.linspace(50, 200, 100)
    
    if sexe == 'H':
        wr = facteur_age * wr_model(poids, *model_params_homme)
        wr_plot = facteur_age * wr_model(X_poids, *model_params_homme)

    elif sexe == 'F':
        wr = facteur_age * wr_model(poids, *model_params_femme)
        wr_plot = facteur_age * wr_model(X_poids, *model_params_femme)


    else:
        raise Exception("ERREUR: Sexe doit être H ou F")

    baseline = baseline_sbd * wr
    baseline_plot = baseline_sbd * wr_plot
    final_score = max((SBD-baseline)/(wr-baseline), 0)

    if do_plot:
        plt.plot(X_poids, wr_plot, linewidth=4, color="#AABD8C", label="Record du monde")
        plt.plot(X_poids, baseline_plot, color="#F39B6D", linewidth=4, label="Débutant")
        plt.vlines(x=poids, ymin=baseline, ymax=SBD, linestyle='dashed', color="#F39B6D", alpha=0.8)
        plt.vlines(x=poids, ymin=SBD, ymax=wr, linestyle='dashed', color="#AABD8C", alpha=0.8)
        plt.scatter(poids, SBD, color="#381D2A", marker='x', s=50, label="Toi")
        plt.xlabel("Poids (kg)", fontsize=15)
        plt.ylabel("Total S+B+D (kg)", fontsize=15)
        plt.title(f"Sexe : {sexe}, Age : {age}, Score force: {100*final_score:.1f} %", fontsize=16)
        plt.gca().set_yscale("function", functions=lambda x: x * score_renorm(x))
        plt.legend()
        plt.show()

    return min(1, max((SBD-baseline)/(wr-baseline), 0))


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

    if sexe == 'H':
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


def score_athlete(sexe, poids, age, SBD, temps_marathon=None, temps_semi=None):

    if (temps_marathon==None) & (temps_semi==None):
        score_endurance_value = 0

    else: 
        score_endurance_value = score_endurance(sexe, age, temps_marathon=temps_marathon, temps_semi=temps_semi)
        
    score_SBD_value = score_SBD(sexe, poids, age, SBD)
    renormed_force = score_renorm(score_SBD_value)
    renormed_endurance = score_renorm(score_endurance_value)
    
    final = np.nanmean([renormed_force, renormed_endurance])

    # We multiply by a small value to enable a theoritical 100% hybrid score.
    # Otherwise a perfect hybrid athlete would need to reach 100% strength and endurance
    bonus = 1.05
    final = min(bonus*final<1, bonus*final, 1)
    
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

    

    



def plot_force():

    # Fetch input values
    age = int(age_entry.get())
    sexe = str(sex_entry.get().upper())
    poids = float(weight_entry.get())

    S = score_s_entry.get()
    B = score_b_entry.get()
    D = score_d_entry.get()

    if (S!='') & (B!='') & (D!=''):
        SBD = float(S) + float(B) + float(D)
    else:
        return None

    score_SBD(sexe, poids, age, SBD, do_plot=True)

    
def compute_result():

    # Fetch input values
    age = int(age_entry.get())
    sexe = str(sex_entry.get().upper())
    poids = float(weight_entry.get())

    S = score_s_entry.get()
    B = score_b_entry.get()
    D = score_d_entry.get()

    if (S!='') & (B!='') & (D!=''):
        SBD = float(S) + float(B) + float(D)
    else:
        SBD = 0
    
    temps_semi = score_semi_entry.get()
    temps_marathon = score_marathon_entry.get()

    if temps_semi=='':
        temps_semi = None
    else:
        temps_semi = float(temps_semi)
        
    if temps_marathon=='':
        temps_marathon = None
    else:
        temps_marathon = float(temps_marathon)

    if (temps_marathon is None) and (temps_semi is None):
        temps_marathon = 999
        temps_semi = 999
    

    # A simple computation example
    result, both = score_athlete(sexe, poids, age, SBD, temps_marathon, temps_semi)
    score_force, score_endu = both

model_params_homme, _ = curve_fit(wr_model, wr.sbd_poids_homme[:, 0],  wr.sbd_poids_homme[:, 1], p0=[0.05, 50, 800])
model_params_femme, _ = curve_fit(wr_model,  wr.sbd_poids_femme[:, 0],  wr.sbd_poids_femme[:, 1], p0=[0.05, 50, 800])
baseline_sbd = 0.15
baseline_endurance = 4
