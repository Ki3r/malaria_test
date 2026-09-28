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
        background: rgba(55,47,47,0.85);
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
    
# Ajouter le background
add_bg_from_local("logo.jpg")


# CSS custom (issu de main.py)
st.markdown(
    """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    .main-title {
        font-size: 60px;
        font-weight: bold;
        line-height: 1.2;
        margin-bottom: 10px;
    }
    .highlight { color: purple; }

    .description {
        font-size: 18px;
        margin-top: 20px;
        margin-bottom: 30px;
        color: white;
    }

    .custom-button {
        background-color: red;
        color: white;
        padding: 15px 30px;
        border: none;
        border-radius: 8px;
        font-size: 18px;
        font-weight: bold;
        cursor: pointer;
        text-decoration: none;
    }

    .custom-button:hover { 
    background-color: black;
    }

    </style>
    """,
    unsafe_allow_html=True
)

st.markdown ('''<div class="main-title">
            ENSEMBLE <span class="highlight">LUTTONS CONTRE LE PALUDISME.</span>
        </div>
        <p class="description">
            Nous aidons les spécialistes de la santé en fournissant des analyses précises d'images de frottis sanguins, 
            afin de faciliter la prise en charge rapide et efficace des patients atteints de paludisme. 
        </p>
        ''', 
        unsafe_allow_html=True)
    
    # Bouton Analyse
st.markdown(
        f'<a href="/detection" target="_self"><button class="custom-button">Lancer un diagnostic</button></a>',
        unsafe_allow_html=True
    )

