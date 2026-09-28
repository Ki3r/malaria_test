import streamlit as st
import tensorflow as tf
import numpy as np
import base64
import sys
import os
from PIL import Image

# Permettre l'import de image_validation.py situé à la racine du projet
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from image_validation import (
    valider_format_fichier,
    analyser_contenu_image,
    EXTENSIONS_AUTORISEES,
)

# Fonction pour ajouter un background local
def add_bg_from_local(image_file):
    with open(image_file, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    css = f"""
    <style>
    [data-testid="stAppViewContainer"] {{
        background-image: url("data:image/png;base64,{encoded}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }}
    [data-testid="stHeader"] {{
        background: rgba(0,0,0,0);
    }}
    [data-testid="stSidebar"] {{
        background: rgba(55,47,47,0.85);
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
    
# Ajouter le background
add_bg_from_local("logo.jpg")


# Charger le modèle
@st.cache_resource
def load_model():
    return tf.keras.models.load_model("malaria_model.h5")

model = load_model()

# Prétraitement
def preprocess_image(image):
    img = image.resize((64, 64))
    img_array = np.array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    return img_array

st.title("Détection du paludisme")
st.write("Importez une image microscopique de frottis sanguin ")

uploaded_file = st.file_uploader(
    "Choisissez une image (JPG/JPEG/PNG/BMP/TIFF)",
    type=EXTENSIONS_AUTORISEES,
)

if uploaded_file is not None:
    # --- Contrôle 1 : le fichier est-il réellement une image d'un format accepté ? ---
    format_ok, message_format, image = valider_format_fichier(uploaded_file)

    if not format_ok:
        st.error(f"❌ Fichier rejeté : {message_format}")
    else:
        st.image(image, caption="Image chargée", use_container_width=True)

        # --- Contrôle 2 : l'image ressemble-t-elle à un frottis sanguin ? ---
        analyse = analyser_contenu_image(image)

        with st.expander("Détail du contrôle de contenu de l'image"):
            st.write(f"Score de vraisemblance « frottis sanguin » : **{analyse['score']}/100**")
            if analyse["raisons"]:
                for raison in analyse["raisons"]:
                    st.write(f"- {raison}")
            else:
                st.write("Aucune anomalie détectée.")

        peut_diagnostiquer = analyse["acceptable"]

        if not analyse["acceptable"]:
            st.warning(
                "⚠️ Cette image ne présente pas les caractéristiques attendues "
                "d'une image microscopique de frottis sanguin coloré. Le modèle "
                "n'est fiable que sur ce type d'image et le diagnostic est donc "
                "bloqué par défaut."
            )
            peut_diagnostiquer = st.checkbox(
                "Je confirme qu'il s'agit bien d'une image microscopique de "
                "cellules sanguines et je souhaite analyser quand même."
            )

        if st.button("Diagnostiquer", disabled=not peut_diagnostiquer):
            import time
            start_time = time.time()
            img_array = preprocess_image(image)
            pred = model.predict(img_array)[0][0]
            end_time = time.time()
            processing_time = end_time - start_time
            # Sauvegarder le temps de traitement dans un fichier npy
            np.save("processing_time.npy", np.array([processing_time]))

            if pred > 0.5:
                st.success("Résultat : Cellule **saine**")
            else:
                st.error("Résultat : Cellule **infectée par le paludisme**")
