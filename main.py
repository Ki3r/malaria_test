import streamlit as st


# style
st.markdown("""
    <style>
    body {
        background-color: #b52220;
        color: white;
    }
    .main-title {
        text-align: center;
        font-size: 2.5em;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .sub-title {
        text-align: center;
        font-size: 1.2em;
        color: #bbbbbb;
        margin-bottom: 30px;
    }
    .stButton>button {
        border-radius: 25px;
        padding: 10px 20px;
        font-size: 1em;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# Page d'acceuil
st.markdown("<div class='main-title'>Malaria Detection</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Une solution intelligente pour accélérer et fiabiliser le diagnostic du paludisme</div>", unsafe_allow_html=True)

st.write("### Bienvenue !")
st.write("Cette application utilise un modèle d'intelligence artificielle basé sur **ResNet50** pour détecter automatiquement la présence du parasite du paludisme sur des images microscopiques de frottis sanguins. ")
st.write("➡️ Utilisez la section **Détection** dans le menu pour tester l'application avec vos propres images.")
