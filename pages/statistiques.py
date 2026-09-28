import streamlit as st
import numpy as np

st.title("Performances du modèle")

# Affichage du temps de traitement de l'analyse
import os
st.subheader("Temps de traitement du modèle (dernière analyse)")
if os.path.exists("processing_time.npy"):
	processing_time = np.load("processing_time.npy")[0]
	st.info(f"Temps de traitement pour l'analyse : {processing_time:.3f} secondes")
else:
	st.warning("Aucune analyse n'a encore été effectuée.")
