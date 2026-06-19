import flet as ft  
from utils import (
    TENANT_ID, TENANT_NAME, ROLE, USER_ID, ACCESS_TOKEN, USER_NAME, EXPIRATION_DATE, PLAN_CHOISI, 
    resource_path, BG_COLOR, convert_date_to_string, CARD_BG, SHADOW_COLOR, BORDER_COLOR, TEXT_PRIMARY, MAIN_COLOR,
    TEXT_SECONDARY,  format_milliers_fr
)
from services.async_function import supabase_request_async
import asyncio, threading
from styles import stat_style
    

class Board(ft.Container):
    def __init__(self, cp: object):
        super().__init__(expand=True,bgcolor=BG_COLOR)
        
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
            controls=[
                ft.Text(f"Bienvenue {self.user_name}", size=20, font_family="PEB")
            ]
        )