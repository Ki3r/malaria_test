import streamlit as st
import base64

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
        background: rgba(255,255,255,0.85);
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
    
# Ajouter le background
add_bg_from_local("logo.jpg")

st.title("À propos du projet")

st.write("""
Ce projet de mémoire vise à démontrer l'apport de l'intelligence artificielle dans la lutte contre le **paludisme**.
L'application présentée ici s'appuie sur un modèle de deep learning permettant de détecter automatiquement 
la présence du parasite à partir d'images microscopiques de frottis sanguins.

### Objectifs
- Accélérer le processus de diagnostic
- Réduire le risque d'erreurs humaines
- Proposer un outil accessible et simple d'utilisation pour les professionnels de santé
""")
