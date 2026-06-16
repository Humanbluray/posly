import flet as ft
from utils import TENANT_ID, TENANT_NAME, ROLE, USER_ID, ACCESS_TOKEN, USER_NAME, EXPIRATION_DATE, PLAN_CHOISI, \
    resource_path, BG_COLOR


class Settings(ft.Container):
    def __init__(self, cp: object):
        super().__init__(expand=True, alignment=ft.alignment.center, padding=40)
        self.cp = cp

        self.access_token = self.cp.page.client_storage.get(ACCESS_TOKEN)
        self.role = self.cp.page.client_storage.get(ROLE)
        self.user_id = self.cp.page.client_storage.get(USER_ID)
        self.tenant_id = self.cp.page.client_storage.get(TENANT_ID)
        self.tenant_name = self.cp.page.client_storage.get(TENANT_NAME)
        self.user_name = self.cp.page.client_storage.get(USER_NAME)
        self.plan_choisi = self.cp.page.client_storage.get(PLAN_CHOISI)
        self.expiration_date = self.cp.page.client_storage.get(EXPIRATION_DATE)

        self.section_home = ft.Container(
            border_radius=6, border=ft.border.all(1, BG_COLOR), bgcolor="white", padding=20, width=700,
            shadow=ft.BoxShadow(blur_radius=1, spread_radius=10, color=BG_COLOR),
            content=ft.Column(
                controls=[
                    ft.Text("Infos établissement", size=24, font_family="PEB"),
                    ft.Row(
                        controls=[
                            ft.Image(
                                resource_path('assets/icons/grey/store.svg'), width=24, height=24
                            ),
                            ft.Column(
                                controls=[
                                    ft.Text("Nom établissement", size=13, font_family="PPI", color='grey'),
                                    ft.Text(f"{self.tenant_name}", size=16, font_family="PPB"),
                                ], spacing=0
                            )
                        ]
                    )
                ]
            )
        )

        self.content = ft.Column(
            controls=[
                self.section_home,
            ]
        )