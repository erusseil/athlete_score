import streamlit as st
from athlete import Athlete

st.title("Athlete Score Calculator")
bench = st.number_input("Bench press (kg)", min_value=0.0)
squat = st.number_input("Squat (kg)", min_value=0.0)
run_time = st.number_input("5K time (min)", min_value=0.0)

if st.button("Compute"):
    ath = Athlete(bench=bench, squat=squat, run_time=run_time)
    st.success(f"Your score: {ath.total_score():.1f}")

