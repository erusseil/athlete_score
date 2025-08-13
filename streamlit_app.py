import streamlit as st
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import athlete as atl
import wr_data as wr

# Color definitions
color_record = "#FF8552"
color_debutant = "#297373"
color_entre = "white"
color_inter2 = "#ffc48e"
color_inter = "#FFC289"
marker_color = "black"
color_grid = "#E0E0E0"


def plot_force(age, poids, S, B, D, sexe):
    fig, ax = plt.subplots()
    ax.set_axisbelow(True)
    ax.yaxis.grid(color=color_grid)
    ax.xaxis.grid(color=color_grid)

    SBD = S + B + D
    model = atl.model_params_homme if sexe == "M" else atl.model_params_femme

    mini_poids = 40
    maxi_poids = 300
    X_poids = np.linspace(max(mini_poids, poids - 30), min(maxi_poids, poids + 30), 100)

    fage = atl.facteur_age_sbd(age)
    record = atl.wr_model(X_poids, *model)
    record_age = record * fage
    baseline_plot = atl.baseline_sbd * record_age
    wr_force = fage * atl.wr_model(poids, *model)
    baseline = atl.baseline_sbd * wr_force

    ax.plot(X_poids, record_age, linewidth=3.5, color=color_debutant, label="World record")
    ax.plot(X_poids, baseline_plot, linewidth=3.5, color=color_record, label="Beginner")

    if mini_poids <= poids <= maxi_poids:
        ax.vlines(x=poids, ymin=baseline, ymax=SBD, linestyle="dashed", color=color_record, alpha=0.9, linewidth=2)
        ax.vlines(x=poids, ymin=SBD, ymax=wr_force, linestyle="dashed", color=color_debutant, alpha=0.9, linewidth=2)
        ax.scatter(poids, SBD, color=marker_color, marker="x", s=150, linewidths=2, label="You")

    ax.set_xlabel("Weight (kg)")
    ax.set_title(f"Total S+B+D = {SBD:.0f} kg")
    ax.legend()
    fig.tight_layout()
    return fig


def plot_endu(age, h, m, s, sexe, discipline):
    fig, ax = plt.subplots()
    ax.set_axisbelow(True)
    ax.yaxis.grid(color=color_grid)
    ax.xaxis.grid(color=color_grid)

    temps = 60 * h + m + s / 60
    temps = 99999 if temps == 0 else temps

    mini_age = 16
    maxi_age = 100
    X_age = np.linspace(max(mini_age, age - 15), min(maxi_age, age + 15), 100)

    mdist = 42.195
    axis_age = np.array([atl.facteur_age_marathon(k) for k in X_age])
    facteur_age = atl.facteur_age_marathon(age)

    if sexe == "M":
        wr_base = wr.marathon_age_homme
        wr_semi = wr.semi_age_homme
    else:
        wr_base = wr.marathon_age_femme
        wr_semi = wr.semi_age_femme

    if discipline == "Marathon":
        perso_vitesse = 60 * mdist / temps
        wr_vitesse = 60 * mdist / wr_base[:, 1].min()
    else:
        perso_vitesse = 60 * (mdist / 2) / temps
        wr_vitesse = 60 * (mdist / 2) / wr_semi[:, 1].min()

    baseline_vitesse = wr_vitesse / atl.baseline_endurance

    ax.plot(X_age, axis_age * wr_vitesse, linewidth=3.5, color=color_debutant, label="World record")
    ax.plot(X_age, axis_age * baseline_vitesse, linewidth=3.5, color=color_record, label="Beginner")

    if mini_age <= age <= maxi_age:
        ax.vlines(x=age, ymin=baseline_vitesse * facteur_age, ymax=perso_vitesse, linestyle="dashed", color=color_record, alpha=0.9, linewidth=1.5)
        ax.vlines(x=age, ymin=perso_vitesse, ymax=wr_vitesse * facteur_age, linestyle="dashed", color=color_debutant, alpha=0.9, linewidth=1.5)
        ax.scatter(age, perso_vitesse, color=marker_color, marker="x", s=150, linewidths=2, label="You")

    ax.set_xlabel("Age")
    ax.set_title(f"Average speed = {perso_vitesse:.1f} km/h")
    ax.legend()
    fig.tight_layout()
    return fig


def plot_final(force_score, endu_score):
    fig, ax = plt.subplots()
    cvals = [0, 50, 75, 100]
    colors = [color_debutant, color_entre, color_inter, color_record]
    norm = matplotlib.colors.Normalize(min(cvals), max(cvals))
    tuples = list(zip(norm(cvals), colors))
    cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", tuples)

    axis = np.linspace(0, 1, 100)
    y, x = np.meshgrid(axis, axis)
    renorm_x = atl.score_renorm(x)
    renorm_y = atl.score_renorm(y)
    z = 100 * np.mean([renorm_y, renorm_x], axis=0)
    c = ax.pcolormesh(100 * x, 100 * y, z, cmap=cmap)
    fig.colorbar(c, ax=ax)

    ax.scatter(force_score, endu_score, color=marker_color, marker="x", s=150, linewidths=2)
    ax.vlines(x=force_score, ymin=0, ymax=endu_score, linestyle="dashed", color="black", linewidth=0.7)
    ax.hlines(y=endu_score, xmin=0, xmax=force_score, linestyle="dashed", color="black", linewidth=0.7)

    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.set_xlabel("Force score (%)")
    ax.set_ylabel("Endurance score (%)")
    ax.set_title("Computing hybrid score")
    fig.tight_layout()
    return fig


def main():

    st.markdown("""<style>.stApp {background-color: white;}</style>""", unsafe_allow_html=True)
    st.set_page_config(layout = "wide")

    title_cols = st.columns(3)
    title_cols[0].markdown("""<hr style="border: none; height: 1px; background-color: black;" />""",unsafe_allow_html=True)
    title_cols[1].markdown("<h2 style='text-align: center; color: black; font-size: 53px;'>Athlete Score Calculator</h2>", unsafe_allow_html=True)
    title_cols[2].markdown("""<hr style="border: none; height: 1px; background-color: black;" />""",unsafe_allow_html=True)

    title_cols[0].markdown("<h2 style='text-align: center; color: black; font-size: 48px;'>Endurance</h2>", unsafe_allow_html=True)
    title_cols[1].markdown("<h2 style='text-align: center; color: black;'>User info</h2>", unsafe_allow_html=True)
    title_cols[2].markdown("<h2 style='text-align: center; color: black; font-size: 48px;'>Strength</h2>", unsafe_allow_html=True)

    # Inject custom CSS to make number input labels black
    st.markdown("""
        <style>
        label {
            color: black !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # First row: three input blocks
    cols = st.columns(9)
    with cols[1]:
        h = st.number_input("Hours", min_value=0, max_value=99, value=0)
        m = st.number_input("Minutes", min_value=0, max_value=59, value=0)
        s = st.number_input("Seconds", min_value=0, max_value=59, value=0)
        discipline_endurance = st.selectbox("Discipline", ["Half-Marathon", "Marathon"])

    with cols[4]:
        age = st.number_input("Age", min_value=15, max_value=100, value=25, step=1)
        poids = st.number_input("Weigt (kg)", min_value=0.0, max_value=300.0, value=80.0, step=1.0)
        sexe = st.selectbox("Sex", ["M", "F"])
    
    
    with cols[7]:
        S = st.number_input("Squat (kg)", min_value=0.0, max_value=1000.0, value=0.0, step=1.0)
        B = st.number_input("Bench (kg)", min_value=0.0, max_value=1000.0, value=0.0, step=1.0)
        D = st.number_input("Deadlift (kg)", min_value=0.0, max_value=1000.0, value=0.0, step=1.0)
        discipline_force = st.selectbox("Discipline", ["Total SBD"])

    # Compute scores
    temps = 60 * h + m + s / 60
    temps_semi = temps if discipline_endurance == "Half-Marathon" else None
    temps_marathon = temps if discipline_endurance == "Marathon" else None
    final_score, force_score, endu_score = atl.score_athlete(sexe, poids, age, S, B, D, temps_marathon, temps_semi)
    
    st.markdown("""<hr style="border: none; height: 1px; background-color: black;" />""",unsafe_allow_html=True)


    # Metrics row
    metric_cols = st.columns(3)
    metric_cols[0].markdown(f"<h2 style='text-align: center; color: {color_debutant}; font-size: 45px;'>Endurance Score</h2>", unsafe_allow_html=True)
    metric_cols[1].markdown(f"<h2 style='text-align: center; color: {color_record}; font-size: 45px;'>Hybrid Score</h2>", unsafe_allow_html=True)
    metric_cols[2].markdown(f"<h2 style='text-align: center; color: {color_debutant}; font-size: 45px;'>Strength Score</h2>", unsafe_allow_html=True)

    metric_cols[0].markdown(
        f"""
        <div style="display: flex; justify-content: center; margin-bottom: 30px">
            <div style="
                background-color: {color_debutant};
                color: white;
                padding: 0px 15px;
                border-radius: 8px;
                display: inline-block;
                text-align: center;
            ">
                <span style='font-size: 65px; font-weight: bold;'>{endu_score:.1f}%</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    metric_cols[1].markdown(
        f"""
        <div style="display: flex; justify-content: center; margin-bottom: 30px">
            <div style="
                background-color: {color_record};
                color: white;
                padding: 0px 15px;
                border-radius: 8px;
                display: inline-block;
                text-align: center;
            ">
                <span style='font-size: 65px; font-weight: bold;'>{final_score:.1f}%</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    metric_cols[2].markdown(
        f"""
        <div style="display: flex; justify-content: center; margin-bottom: 30px">
            <div style="
                background-color: {color_debutant};
                color: white;
                padding: 0px 15px;
                border-radius: 8px;
                display: inline-block;
                text-align: center;
            ">
                <span style='font-size: 65px; font-weight: bold;'>{force_score:.1f}%</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Second row: three plots
    pcol1, pcol2, pcol3 = st.columns(3)
    pcol1.pyplot(plot_endu(age, h, m, s, sexe, discipline_endurance), use_container_width=True)
    pcol2.pyplot(plot_final(force_score, endu_score), use_container_width=True)
    pcol3.pyplot(plot_force(age, poids, S, B, D, sexe), use_container_width=True)


if __name__ == "__main__":
    main()

