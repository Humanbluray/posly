import flet as ft
from utils import MAIN_COLOR, SECOND_COLOR, THIRD_COLOR, THUMB_COLOR, BG_COLOR

tabs_style: dict = dict(
    tab_alignment=ft.TabAlignment.START, selected_index=0, expand=True,
    animation_duration=300,
    unselected_label_color=ft.Colors.GREY, label_color=SECOND_COLOR,
    indicator_border_radius=6, indicator_border_side=ft.BorderSide(3, MAIN_COLOR),
    indicator_tab_size=True,
)
login_style: dict = dict(
    border_radius=6, content_padding=12, cursor_height=24,
    text_style=ft.TextStyle(size=16, font_family="PPM"),
    hint_style=ft.TextStyle(size=15, font_family="PPM"),
    label_style=ft.TextStyle(size=15, font_family="PPM", color="black"),
    border_color=BG_COLOR, focused_border_color=BG_COLOR,
    focused_bgcolor=BG_COLOR, bgcolor=BG_COLOR,
    cursor_color=MAIN_COLOR
)
config_tf_style: dict = dict(
    border_radius=0, content_padding=12, cursor_height=24,
    text_style=ft.TextStyle(size=16, font_family="PPM"),
    hint_style=ft.TextStyle(size=15, font_family="PPM"),
    label_style=ft.TextStyle(size=15, font_family="PPM", color="black"),
    focused_border_color=MAIN_COLOR, border_color="grey",
    border=ft.InputBorder.UNDERLINE, focused_border_width=2, border_width=1,
    cursor_color=MAIN_COLOR
)
drop_style: dict = dict(
    border_radius=6,
    focused_border_width=1,
    focused_border_color=MAIN_COLOR,
    label_style=ft.TextStyle(size=15, font_family="PPM", color='black'),
    text_style=ft.TextStyle(size=15, font_family="PPM", color="black"),
    hint_style=ft.TextStyle(size=15, font_family="PPM", color="black"),
    border_width=1,
    content_padding=12,
    editable=True,
    enable_filter=True,
    enable_search=True,
    max_menu_height=200,
    selected_trailing_icon=ft.Icons.KEYBOARD_ARROW_UP_OUTLINED,
    trailing_icon=ft.Icons.KEYBOARD_ARROW_DOWN_OUTLINED,

)
switch_style: dict = dict(
    active_color=MAIN_COLOR,
    inactive_track_color=ft.Colors.GREY_100,
    thumb_color={
        ft.ControlState.SELECTED: MAIN_COLOR,
        ft.ControlState.DEFAULT: ft.Colors.BLACK87,
    },
    track_color={
        ft.ControlState.SELECTED: BG_COLOR,
        ft.ControlState.DEFAULT: ft.Colors.GREY_100,
    },
)
input_style: dict = dict(
    border_radius=6,
    border_color=ft.Colors.with_opacity(0.3, ft.Colors.BLACK),
    focused_border_color=MAIN_COLOR,
    height=50,
    autofocus=True,
    content_padding=12,
    cursor_color=MAIN_COLOR,
    hint_style=ft.TextStyle(size=15, font_family='PPM', color="black"),
    text_style=ft.TextStyle(size=15, font_family='PPM', color='black'),
    label_style=ft.TextStyle(size=15, font_family="PPM", color='black'),
    focused_border_width=1,
    border_width=1,
)
datatable_style: dict = dict(
    data_text_style=ft.TextStyle(font_family="PPM", size=15, color=ft.Colors.BLACK),
    heading_text_style=ft.TextStyle(font_family="PPR", size=14, color="grey"),
    divider_thickness=1,
)
ct_style: dict = dict(
    # expand=True,
    bgcolor=ft.Colors.with_opacity(0.2, "#464646"), # Fond sombre transparent
    blur=ft.Blur(10, 10, ft.BlurTileMode.MIRROR), # L'effet de flou (Glassmorphism)
    alignment=ft.alignment.center, # C'est ce qui centre ta fenêtre !
    visible=False, # Caché par défaut
)
# _____style pour les containers internes_____
intern_ct_style: dict = dict(
    bgcolor="white",
    border_radius=16,
    # padding=30,
    shadow=ft.BoxShadow(
        spread_radius=1,
        blur_radius=15,
        color=ft.Colors.with_opacity(0.2, "black"),
    ),
    scale=ft.Scale(0), # On garde l'animation de zoom sur la carte
    animate_scale=ft.Animation(300, ft.AnimationCurve.ELASTIC_OUT),
)
radio_style: dict = dict(
    label_style=ft.TextStyle(font_family="PPM", size=16),
    fill_color=MAIN_COLOR, hover_color=SECOND_COLOR
)
text_style: dict = dict(
    size=15, font_family="PPB", color="black",
)
