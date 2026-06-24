import flet as ft
from utils import (
    MAIN_COLOR, SECOND_COLOR, CARD_BG, TEXT_PRIMARY,
    TEXT_SECONDARY, BORDER_COLOR, SHADOW_COLOR, TEXT_PRIMARY_DARK
)

# --- Style des champs de saisie ---
input_style: dict = dict(
    border_radius=8,
    border_color=BORDER_COLOR,
    focused_border_color=MAIN_COLOR,
    focused_bgcolor=CARD_BG,
    bgcolor=CARD_BG,
    height=42,
    content_padding=14,
    cursor_color=MAIN_COLOR,
    hint_style=ft.TextStyle(size=14, font_family="PPM", color=TEXT_SECONDARY),
    text_style=ft.TextStyle(size=15, font_family="PPM", color=TEXT_PRIMARY),
    label_style=ft.TextStyle(size=14, font_family="PPM", color=TEXT_SECONDARY),
    focused_border_width=1,
    border_width=1,
    selection_color=SECOND_COLOR,
)

# --- Style du bouton principal ---
button_primary_style = ft.ButtonStyle(
    shape=ft.RoundedRectangleBorder(radius=10),
    bgcolor=MAIN_COLOR,
    color=ft.Colors.WHITE,
    elevation=0,
    overlay_color=ft.Colors.with_opacity(0.2, ft.Colors.WHITE),
    animation_duration=200,
)

# --- Style des cartes ---
card_style: dict = dict(
    bgcolor=CARD_BG,
    border_radius=16,
    shadow=ft.BoxShadow(
        spread_radius=1,
        blur_radius=20,
        color=SHADOW_COLOR,
        offset=ft.Offset(0, 6),
    ),
)

# --- Style des conteneurs modaux (overlay) ---
ct_style: dict = dict(
    bgcolor=ft.Colors.with_opacity(0.5, ft.Colors.BLACK),
    blur=ft.Blur(8, 8, ft.BlurTileMode.MIRROR),
    alignment=ft.alignment.center,
    visible=False,
)

intern_ct_style: dict = dict(
    bgcolor=CARD_BG,
    border_radius=20,
    shadow=ft.BoxShadow(
        spread_radius=1,
        blur_radius=24,
        color=SHADOW_COLOR,
        offset=ft.Offset(0, 8),
    ),
    scale=ft.Scale(0),
    animate_scale=ft.Animation(350, ft.AnimationCurve.EASE_OUT_BACK),
)

# --- Style des tabs ---
tabs_style: dict = dict(
    tab_alignment=ft.TabAlignment.START,
    selected_index=0,
    expand=True,
    animation_duration=300,
    unselected_label_color=TEXT_SECONDARY,
    label_color=MAIN_COLOR,
    indicator_border_radius=8,
    indicator_border_side=ft.BorderSide(2, MAIN_COLOR),
    indicator_tab_size=True,
)

# --- Style des dropdown ---
drop_style: dict = dict(
    border_radius=8,
    focused_border_width=2,
    focused_border_color=MAIN_COLOR,
    label_style=ft.TextStyle(size=14, font_family="PPM", color=TEXT_SECONDARY),
    text_style=ft.TextStyle(size=14, font_family="PPM", color=TEXT_PRIMARY),
    hint_style=ft.TextStyle(size=14, font_family="PPM", color=TEXT_SECONDARY),
    border_width=1,
    border_color=BORDER_COLOR,
    content_padding=12,
    bgcolor=CARD_BG,
    editable=True,
    enable_filter=True,
    enable_search=True,
    max_menu_height=200,
    selected_trailing_icon=ft.Icons.KEYBOARD_ARROW_UP_OUTLINED,
    trailing_icon=ft.Icons.KEYBOARD_ARROW_DOWN_OUTLINED,
)

# --- Style des switchs ---
switch_style: dict = dict(
    active_color=MAIN_COLOR,
    inactive_track_color=BORDER_COLOR,
    thumb_color={
        ft.ControlState.SELECTED: MAIN_COLOR,
        ft.ControlState.DEFAULT: ft.Colors.BLACK54,
    },
    track_color={
        ft.ControlState.SELECTED: ft.Colors.with_opacity(0.7, BORDER_COLOR),
        ft.ControlState.DEFAULT: BORDER_COLOR,
    },
)

# --- Style des DataTable ---
datatable_style: dict = dict(
    data_text_style=ft.TextStyle(font_family="PPM", size=14),
    heading_text_style=ft.TextStyle(font_family="PPB", size=15, color=ft.Colors.BLACK45),
    divider_thickness=1,
    column_spacing=20,
    horizontal_lines=ft.BorderSide(1, BORDER_COLOR),
    border=ft.border.all(1, BORDER_COLOR),
    border_radius=8,
    horizontal_margin=10,
    data_row_min_height=50,


)

# --- Style des radios ---
radio_style: dict = dict(
    label_style=ft.TextStyle(font_family="PPM", size=15, color=TEXT_PRIMARY),
    fill_color=MAIN_COLOR,
    hover_color=SECOND_COLOR,
)

# --- Autres styles ---
login_style: dict = dict(
    border_radius=8,
    content_padding=14,
    cursor_height=24,
    text_style=ft.TextStyle(size=15, font_family="PPM", color=TEXT_PRIMARY),
    hint_style=ft.TextStyle(size=14, font_family="PPM", color=TEXT_SECONDARY),
    label_style=ft.TextStyle(size=14, font_family="PPM", color=TEXT_SECONDARY),
    border_color=BORDER_COLOR,
    focused_border_color=MAIN_COLOR,
    focused_bgcolor=CARD_BG,
    bgcolor=CARD_BG,
    cursor_color=MAIN_COLOR,
    selection_color=SECOND_COLOR,
    border_width=1,
    focused_border_width=1,
)

config_tf_style: dict = dict(
    border_radius=0,
    content_padding=12,
    cursor_height=24,
    text_style=ft.TextStyle(size=15, font_family="PPM", color=TEXT_PRIMARY),
    hint_style=ft.TextStyle(size=14, font_family="PPM", color=TEXT_SECONDARY),
    label_style=ft.TextStyle(size=14, font_family="PPM", color=TEXT_SECONDARY),
    focused_border_color=MAIN_COLOR,
    border_color=BORDER_COLOR,
    border=ft.InputBorder.UNDERLINE,
    focused_border_width=1,
    border_width=1,
    cursor_color=MAIN_COLOR,
    selection_color=SECOND_COLOR,
    bgcolor=CARD_BG,
)

info_style: dict = dict(
    border_radius=6,
    border_color=BORDER_COLOR,
    focused_border_color=MAIN_COLOR,
    height=38,
    autofocus=True,
    content_padding=12,
    cursor_color=MAIN_COLOR,
    hint_style=ft.TextStyle(size=13, font_family="PPM", color=TEXT_SECONDARY),
    label_style=ft.TextStyle(size=13, font_family="PPM", color=TEXT_SECONDARY),
    focused_border_width=1,
    border_width=1,
    selection_color=SECOND_COLOR,
    animate_cursor_opacity=True,
    bgcolor=CARD_BG,
)

text_style: dict = dict(
    size=15,
    font_family="PPB",
    color=TEXT_PRIMARY,
)
stat_style: dict = dict(
    bgcolor="white",
    border_radius=12,
    padding=24,
    border=ft.border.all(1, "#E2E8F0"), # Bordure Slate 200 très fine
    shadow=ft.BoxShadow(
        spread_radius=0,
        blur_radius=4,
        color=ft.Colors.with_opacity(0.04, "#000000"),
        offset=ft.Offset(0, 2),
    ),
)
settings_style: dict = dict(
    bgcolor="white",
    border_radius=12,
    padding=0,
    border=ft.border.all(1, "#E2E8F0"), # Bordure Slate 200 très fine
    shadow=ft.BoxShadow(
        spread_radius=0,
        blur_radius=4,
        color=ft.Colors.with_opacity(0.04, "#000000"),
        offset=ft.Offset(0, 2),
    ),
)

card_kpi_style: dict = dict(
    bgcolor="white",
    border_radius=12,
    padding=24,
    # border=ft.border.all(1, "#E2E8F0"), # Bordure Slate 200 très fine
    shadow=ft.BoxShadow(
        spread_radius=0,
        blur_radius=8,
        color=ft.Colors.with_opacity(0.04, "#000000"),
        offset=ft.Offset(0, 2),
    ),
)