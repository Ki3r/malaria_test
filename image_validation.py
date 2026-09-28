"""
Contrôles de validation des images pour l'application de détection du paludisme.

Deux niveaux de contrôle sont assurés :

1. valider_format_fichier()
   Vérifie que le fichier uploadé est RÉELLEMENT une image (et pas un fichier
   quelconque simplement renommé avec une extension .jpg/.png) et que son
   format effectif (détecté par PIL, pas seulement l'extension du nom de
   fichier) fait partie des formats acceptés.

2. analyser_contenu_image()
   Applique une heuristique d'analyse de couleurs/texture pour estimer si
   l'image ressemble à une image microscopique de frottis sanguin coloré
   (coloration de type Giemsa/May-Grünwald), par opposition à une photo
   quelconque, un document scanné, une capture d'écran, un logo, etc.

⚠️ IMPORTANT : le contrôle de contenu (point 2) est une heuristique fondée
sur l'analyse des couleurs et de la texture de l'image. Ce n'est PAS un
modèle entraîné de classification d'images et il ne peut donc pas garantir
à 100 % la nature exacte de l'image. Il sert de filtre de bon sens pour
éviter que le modèle de prédiction ne soit sollicité sur des images
manifestement hors contexte (paysage, document, capture d'écran...). Pour
une garantie plus forte, il faudrait entraîner un second modèle de
classification binaire ("frottis sanguin" / "autre") sur un jeu de données
dédié.
"""

from PIL import Image, UnidentifiedImageError
import numpy as np

# Formats réellement acceptés (détectés via PIL, pas via l'extension du nom
# de fichier, qui peut être falsifiée).
FORMATS_AUTORISES = {"JPEG", "PNG", "BMP", "TIFF"}
EXTENSIONS_AUTORISEES = ["jpg", "jpeg", "png", "bmp", "tiff", "tif"]

TAILLE_MIN_PX = 32       # image plus petite = inexploitable par le modèle
TAILLE_MAX_MO = 15       # taille de fichier maximale acceptée

SCORE_SEUIL_ACCEPTABLE = 50  # sur 100


def valider_format_fichier(uploaded_file):
    """
    Vérifie que le fichier uploadé est une image valide d'un format accepté.

    Retourne un tuple (ok, message, image) :
        - ok (bool) : True si le fichier passe le contrôle
        - message (str) : message d'erreur ou "OK"
        - image (PIL.Image ou None) : image chargée en RGB si ok, sinon None
    """
    # --- Taille du fichier ---
    uploaded_file.seek(0, 2)
    taille_octets = uploaded_file.tell()
    uploaded_file.seek(0)

    if taille_octets == 0:
        return False, "Le fichier est vide.", None

    if taille_octets > TAILLE_MAX_MO * 1024 * 1024:
        return False, f"Le fichier dépasse la taille maximale autorisée ({TAILLE_MAX_MO} Mo).", None

    # --- Intégrité : le fichier est-il réellement une image ? ---
    try:
        image_verif = Image.open(uploaded_file)
        image_verif.verify()  # lève une exception si le contenu n'est pas une image valide
        format_reel = (image_verif.format or "").upper()
    except (UnidentifiedImageError, OSError, ValueError, Exception):
        return False, (
            "Le fichier n'est pas une image valide (ou est corrompu). "
            "Seules les images sont acceptées, quel que soit le nom du fichier."
        ), None

    if format_reel not in FORMATS_AUTORISES:
        return False, (
            f"Format de fichier non pris en charge ({format_reel or 'inconnu'}). "
            f"Formats acceptés : PNG, JPG/JPEG, BMP, TIFF."
        ), None

    # verify() invalide l'objet Image : on doit rouvrir le flux pour charger les pixels
    uploaded_file.seek(0)
    try:
        image = Image.open(uploaded_file).convert("RGB")
    except Exception:
        return False, "Impossible de lire le contenu de l'image.", None

    largeur, hauteur = image.size
    if largeur < TAILLE_MIN_PX or hauteur < TAILLE_MIN_PX:
        return False, (
            f"Image trop petite ({largeur}x{hauteur}px). "
            f"Taille minimale requise : {TAILLE_MIN_PX}x{TAILLE_MIN_PX}px."
        ), None

    return True, "OK", image


def analyser_contenu_image(image: Image.Image):
    """
    Heuristique estimant si l'image ressemble à une image microscopique de
    frottis sanguin coloré (et non à une photo, un document, un logo...).

    Retourne un dict :
        {
            "score": int (0-100),
            "acceptable": bool,
            "raisons": list[str]  # explications des points perdus
        }
    """
    img_small = image.resize((128, 128))
    arr = np.array(img_small).astype(np.float32) / 255.0
    r, g, b = arr[..., 0], arr[..., 1], arr[..., 2]

    hsv = np.array(img_small.convert("HSV")).astype(np.float32)
    h, s = hsv[..., 0] / 255.0, hsv[..., 1] / 255.0
    teinte_deg = h * 360

    raisons = []
    score = 0

    # 1) Proportion de teintes violettes/roses/magenta typiques d'une
    #    coloration de Giemsa (35 points)
    masque_coloration = ((teinte_deg >= 250) & (teinte_deg <= 345)) | (teinte_deg <= 10)
    masque_sature = s > 0.15
    prop_coloration = float(np.mean(masque_coloration & masque_sature))
    if prop_coloration > 0.12:
        score += 35
    elif prop_coloration > 0.05:
        score += 18
    else:
        raisons.append("Peu de teintes violettes/roses typiques d'une coloration de frottis sanguin.")

    # 2) Saturation moyenne : une image quasi grise (scan, capture d'écran)
    #    est suspecte (15 points)
    saturation_moyenne = float(np.mean(s))
    if saturation_moyenne > 0.08:
        score += 15
    else:
        raisons.append("Image très peu saturée (proche du noir et blanc), atypique pour un frottis coloré.")

    # 3) Texture/granularité LOCALE : une image microscopique a une texture
    #    fine et irrégulière PARTOUT dans l'image (cellules), contrairement à
    #    une photo composée de larges zones unies (ciel, mur, herbe...) ou à
    #    un document. On calcule l'écart-type sur des petits blocs de
    #    l'image (et non sur l'image entière, qui peut être trompée par deux
    #    grandes zones de couleurs différentes) (25 points).
    gris = np.mean(arr, axis=2)
    taille_bloc = 8
    n = gris.shape[0] // taille_bloc
    blocs = gris[: n * taille_bloc, : n * taille_bloc].reshape(
        n, taille_bloc, n, taille_bloc
    )
    std_par_bloc = blocs.std(axis=(1, 3))
    texture_mediane = float(np.median(std_par_bloc))
    proportion_blocs_texturés = float(np.mean(std_par_bloc > 0.03))
    if texture_mediane > 0.025 and proportion_blocs_texturés > 0.5:
        score += 25
    elif texture_mediane > 0.015 and proportion_blocs_texturés > 0.3:
        score += 12
    else:
        raisons.append("Texture trop uniforme/localement homogène pour une image microscopique de cellules.")

    # 4) Proportion de fond quasi blanc (typique d'un document scanné ou
    #    d'une capture d'écran) (15 points)
    prop_blanc = float(np.mean((r > 0.92) & (g > 0.92) & (b > 0.92)))
    if prop_blanc < 0.5:
        score += 15
    else:
        raisons.append("Trop grande proportion de fond blanc uniforme (aspect document/capture d'écran).")

    # 5) Teintes "nature" (ciel bleu, végétation verte), peu probables sur
    #    un frottis sanguin (10 points)
    masque_nature = ((teinte_deg >= 90) & (teinte_deg <= 200)) & (s > 0.2)
    prop_nature = float(np.mean(masque_nature))
    if prop_nature < 0.35:
        score += 10
    else:
        raisons.append("Dominance de teintes bleues/vertes (ciel, végétation...) inhabituelle pour un frottis sanguin.")

    return {
        "score": score,
        "acceptable": score >= SCORE_SEUIL_ACCEPTABLE,
        "raisons": raisons,
    }
