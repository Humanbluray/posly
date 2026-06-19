import flet as ft  
from utils import TENANT_ID, TENANT_NAME, ROLE, USER_ID, ACCESS_TOKEN, USER_NAME, EXPIRATION_DATE, PLAN_CHOISI, \
    resource_path, BG_COLOR, convert_date_to_string


class Entries(ft.Container):
    def __init__(self, cp: object):
        super().__init__(
            expand=True, alignment=ft.alignment.center
        )
        self.cp = cp
        self.access_token = self.cp.page.client_storage.get(ACCESS_TOKEN)
        self.role = self.cp.page.client_storage.get(ROLE)
        self.user_id = self.cp.page.client_storage.get(USER_ID)
        self.tenant_id = self.cp.page.client_storage.get(TENANT_ID)
        self.tenant_name = self.cp.page.client_storage.get(TENANT_NAME)
        self.user_name = self.cp.page.client_storage.get(USER_NAME)
        self.plan_choisi = self.cp.page.client_storage.get(PLAN_CHOISI)
        self.expiration_date = self.cp.page.client_storage.get(EXPIRATION_DATE)
        
        self.content = ft.Column(
            alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text(
                    f"Bienvenue, {self.user_name}", size=18, font_family="PEB"
                ),
                ft.Image(
                    resource_path('assets/icons/grey/loader.svg'), width=36, height=36
                ),
                ft.Text("Section en cours de developpement...")
            ]
        )