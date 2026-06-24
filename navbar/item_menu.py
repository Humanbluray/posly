import flet as ft
from utils import MAIN_COLOR, SECOND_COLOR, resource_path


class ItemMenu(ft.Container):
    def __init__(self, title: str, my_icon: str, my_icon_2: str, visible: bool):
        super().__init__(
            shape=ft.BoxShape.RECTANGLE,
            padding=ft.padding.only(left=16, right=10, top=8, bottom=8),
            border_radius=12,
            expand=True,
            animate=200,
            scale=ft.Scale(1),
            animate_scale=ft.Animation(300, ft.AnimationCurve.EASE_IN),
            on_hover=self.hover_ct,
            height=40,
            bgcolor=None,
            visible=visible
        )
        # ... le reste du code inchangé ...
        self.title = title
        self.my_icon = my_icon
        self.my_icon_2 = my_icon_2
        self.is_clicked = False
        self.visuel = ft.Image(src=resource_path(my_icon), width=20, height=20)
        self.visuel_2 = ft.Image(src=resource_path(my_icon_2), width=20, height=20)
        self.name = ft.Text(title.capitalize(), font_family="PPM", size=15, color=ft.Colors.BLACK54)
        self.name_2 = ft.Text(title.capitalize(), font_family="PPB", size=16, color="black")
        self.unselected = ft.Row(controls=[self.visuel, self.name],spacing=10)
        self.selected = ft.Row(controls=[self.visuel_2, self.name_2], spacing=10)

        self.first = ft.Stack(expand=True, alignment=ft.alignment.center, controls=[self.selected, self.unselected])
        self.second = ft.Container(
            border_radius=16, width=5, content=ft.Text(""), bgcolor="#82c9ff", height=20, visible=False
        )
        self.content = ft.Row([self.first, self.second], spacing=0)

    def hover_ct(self, e):
        if e.data == "true":
            self.scale = 1.05
            self.update()
        else:
            self.scale = 1
            self.update()

        e.control.update()

    def set_is_clicked_true(self):
        self.is_clicked = True
        self.unselected.visible = False
        self.selected.visible = True
        self.second.visible = False
        self.padding = ft.padding.only(left=20, right=10, top=7, bottom=7)
        self.bgcolor = SECOND_COLOR

    def set_is_clicked_false(self):
        self.is_clicked = False
        self.unselected.visible = True
        self.selected.visible = False
        self.second.visible = False
        self.padding = ft.padding.only(left=10, right=10, top=7, bottom=7)
        self.bgcolor = None



