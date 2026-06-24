from calendar import month
import flet as ft
import datetime, os, sys
from typing import List


# --- Pallette orange (origine) ---
MAIN_COLOR = "#ff7f00"
SECOND_COLOR = "#ff952b"
# MAIN_COLOR = "#0E21A0"
# SECOND_COLOR = "#4D2FB2"
THIRD_COLOR = ft.Colors.DEEP_PURPLE_50
RED_COLOR = "#e1040a"
GREEN_COLOR = "#308f62"

# --- Couleurs light mode ---
BG_COLOR_LIGHT = "#F8FAFC"
CARD_BG_LIGHT = "#FFFFFF"
SURFACE_COLOR_LIGHT = "#FFFFFF"   # Pour tous les containers "blancs"
TEXT_PRIMARY_LIGHT = "#212529"
TEXT_SECONDARY_LIGHT = "#6C757D"
BORDER_COLOR_LIGHT = "#E9ECEF"

# --- Couleurs dark mode ---
BG_COLOR_DARK = "#1A1A2E"
CARD_BG_DARK = "#2D2D44"
SURFACE_COLOR_DARK = "#1E1E2E"    # Fond sombre pour les containers
TEXT_PRIMARY_DARK = "#F1F5F9"
TEXT_SECONDARY_DARK = "#94A3B8"
BORDER_COLOR_DARK = "#3E3E5E"

# --- Variables globales ---
BG_COLOR = BG_COLOR_LIGHT
CARD_BG = CARD_BG_LIGHT
SURFACE_COLOR = SURFACE_COLOR_LIGHT   # Nouvelle variable
TEXT_PRIMARY = TEXT_PRIMARY_LIGHT
TEXT_SECONDARY = TEXT_SECONDARY_LIGHT
BORDER_COLOR = BORDER_COLOR_LIGHT
SHADOW_COLOR = ft.Colors.with_opacity(0.08, ft.Colors.BLACK)

def apply_theme(theme_mode):
    """Applique le thème et met à jour les constantes globales"""
    global BG_COLOR, CARD_BG, SURFACE_COLOR, TEXT_PRIMARY, TEXT_SECONDARY, BORDER_COLOR, SHADOW_COLOR
    
    if theme_mode == ft.ThemeMode.DARK:
        BG_COLOR = BG_COLOR_DARK
        CARD_BG = CARD_BG_DARK
        SURFACE_COLOR = SURFACE_COLOR_DARK
        TEXT_PRIMARY = TEXT_PRIMARY_DARK
        TEXT_SECONDARY = TEXT_SECONDARY_DARK
        BORDER_COLOR = BORDER_COLOR_DARK
        SHADOW_COLOR = ft.Colors.with_opacity(0.3, ft.Colors.BLACK)
    else:
        BG_COLOR = BG_COLOR_LIGHT
        CARD_BG = CARD_BG_LIGHT
        SURFACE_COLOR = SURFACE_COLOR_LIGHT
        TEXT_PRIMARY = TEXT_PRIMARY_LIGHT
        TEXT_SECONDARY = TEXT_SECONDARY_LIGHT
        BORDER_COLOR = BORDER_COLOR_LIGHT
        SHADOW_COLOR = ft.Colors.with_opacity(0.08, ft.Colors.BLACK)

# Initialisation par défaut (light)
apply_theme(ft.ThemeMode.LIGHT)

# ... (tes autres fonctions)

# ... (toutes tes autres fonctions : format_milliers_fr, resource_path, etc.)



ACCESS_TOKEN = "access_token"
USER_ID = "user_id"
TENANT_ID = "tenant_id"
USER_NAME = "user_name"
ROLE = "role"
TENANT_NAME = "tenant_name"
PLAN_CHOISI = "plan_choisi"
EXPIRATION_DATE = "expiration_date"
USER_EMAIL = "user_email"
IS_FIRST_LOGIN = "is_first_login"


# _______________dictionnaire des couleurs pour graphique__________________________
graphic_colors = {
    "OM": {"color": ft.Colors.DEEP_ORANGE, "bg_color": ft.Colors.DEEP_ORANGE_50},
    "MOMO": {"color": ft.Colors.DEEP_ORANGE, "bg_color": ft.Colors.DEEP_ORANGE_50},
    "Cash": {"color": ft.Colors.DEEP_ORANGE, "bg_color": ft.Colors.DEEP_ORANGE_50},
}

icones_datas = {
    "Dépenses": ft.Icons.KEYBOARD_ARROW_UP_OUTLINED,
    "Recettes": ft.Icons.KEYBOARD_ARROW_DOWN_OUTLINED,
    "Résultat": ft.Icons.CURRENCY_BITCOIN_OUTLINED
}

stats_colors = {
    "Dépenses": {"color": ft.Colors.DEEP_ORANGE, "bgcolor": ft.Colors.DEEP_ORANGE_50},
    "Recettes": {"color": ft.Colors.DEEP_ORANGE, "bgcolor": ft.Colors.DEEP_ORANGE_50},
    "Résultat": {"color": ft.Colors.DEEP_ORANGE, "bgcolor": ft.Colors.DEEP_ORANGE_50},
}

def format_milliers_fr(value):
    try:
        # conversion en float ou int automatiquement
        num = float(value)
        # test si nombre entier
        if num.is_integer():
            return format(int(num), ",")
        return format(num, ",")
    except ValueError:
        return value  # si ce n’est pas un nombre


def format_time(time_number: int) -> str:
    """
    renvoie une chaîne de caractère à la place d'un nombre
    :param time_number:
    :return:
    """
    if time_number <= 9:
        return f"0{time_number}"
    else:
        return str(time_number)


def write_time():
    """
    renvoie la date du jour sous le format date heure
    :return: str
    """
    now = datetime.datetime.now()
    return f"{format_time(now.hour)}:{format_time(now.minute)}:{format_time(now.second)}"


def convert_date_to_string(date: datetime.date) -> str:
    my_day = str(date.day) if date.day >= 10  else f"0{date.day}"
    my_month = str(date.month) if date.month >= 10 else f"0{date.month}"
    my_year = date.year
    return f"{my_day}/{my_month}/{my_year}"


def create_objet_date(my_date: str):
    day = my_date[0:2]
    mois = my_date[3:5]
    year = my_date[6::]
    objet_date = datetime.date(int(year), int(mois), int(day))
    return objet_date


def max_pour_graphique(key: str, liste_de_dico: List[dict]) -> int:
    """
    retourne le maximum d'une valeur parmi les dictionnaires de la liste
    :param key:
    :param liste_de_dico:
    :return:
    """
    ma_liste = []
    for item in liste_de_dico:
        ma_liste.append(item[key])

    return max(ma_liste)


def diviseur_unites(nombre: int):
    """
    retourne une écriture contractée des nombres > 1000
    :param nombre:
    :return:
    """
    if nombre / 1000000 >= 1:
        coupe = nombre // 1000
        return f"{coupe} M"
    elif nombre / 1000 >= 1:
        coupe = nombre // 1000
        return f"{coupe} K"
    else:
        return format_milliers_fr(nombre)


def get_next_period(month: int, year: int):
    """
    retourne la prochaine période comptable
    :param month:
    :param year:
    :return: dict
    """
    if month == 12:
        next_month = 1
        next_year = year + 1
    else:
        next_month = month + 1
        next_year = year

    return {
        "next_month": next_month,
        "next_year": next_year
    }


def get_previous_period(month: int, year: int):
    """
    retourne la dernière période comptable
    :param month:
    :param year:
    :return:
    """
    if month == 1:
        previous_month = 12
        previous_year = year - 1
    else:
        previous_month = month - 1
        previous_year = year

    return {
        "previous_month": previous_month,
        "previous_year": previous_year
    }


def separateur_milliers(value):
    try:
        # conversion en float ou int automatiquement
        num = float(value)
        # test si nombre entier
        if num.is_integer():
            return format(int(num), ",")
        return format(num, ",")
    except ValueError:
        return value  # si ce n’est pas un nombre


def resource_path(relative_path):
    # Si on est sur Railway (environnement Cloud), Flet gère les assets via le serveur Web.
    # On transforme juste 'assets/icons/file.svg' en '/icons/file.svg'
    if os.getenv("PORT"):
        if relative_path.startswith("assets/"):
            return relative_path.replace("assets", "")
        if not relative_path.startswith("/"):
            return "/" + relative_path
        return relative_path

    # --- Ton code d'origine pour PyInstaller (Laisse-le pour ton mode local/EXE) ---
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def find_facture_number():
    month = datetime.date.today().month
    year = datetime
