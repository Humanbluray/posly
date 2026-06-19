import flet as ft
from utils import (
    TENANT_ID, TENANT_NAME, ROLE, USER_ID, ACCESS_TOKEN, USER_NAME, EXPIRATION_DATE, PLAN_CHOISI, 
    resource_path, BG_COLOR, convert_date_to_string, SHADOW_COLOR
)

from styles import input_style, datatable_style, settings_style
from components.components import MyButton
import datetime, asyncio, threading
from services.async_function import supabase_request_async
from services.supabase_client import supabase_client


class Settings(ft.Container):
    def __init__(self, cp: object):
        super().__init__(expand=True, alignment=ft.alignment.center,)
        self.cp = cp

        self.access_token = self.cp.page.client_storage.get(ACCESS_TOKEN)
        self.role = self.cp.page.client_storage.get(ROLE)
        self.user_id = self.cp.page.client_storage.get(USER_ID)
        self.tenant_id = self.cp.page.client_storage.get(TENANT_ID)
        self.tenant_name = self.cp.page.client_storage.get(TENANT_NAME)
        self.user_name = self.cp.page.client_storage.get(USER_NAME)
        self.plan_choisi = self.cp.page.client_storage.get(PLAN_CHOISI)
        self.expiration_date = self.cp.page.client_storage.get(EXPIRATION_DATE)
        
        self.info_tenant_id = ft.TextField(
            **input_style, disabled=True,
            value=f"{self.tenant_id}", width=600
        )
        self.info_name = ft.TextField(
            **input_style,
            value=f"{self.tenant_name}", 
        )
        self.info_slogan = ft.TextField(
            **input_style, width=300, 
            value=f"{self.tenant_name}"
        )
        self.info_contact = ft.TextField(
            **input_style, width=300, 
        )
        self.info_adress = ft.TextField(
            **input_style, width=300, 
        )
        self.info_abo = ft.TextField(
            **input_style, width=300, value=f"{self.plan_choisi}", disabled=True,
        )
        self.info_fin_abo = ft.TextField(
            **input_style, width=300, value=f"{self.expiration_date}", disabled=True,
        )
        self.info_delay_abo = ft.TextField(
            **input_style, width=300, value=f"{self.verifier_abonnement()} jour(s)", disabled=True,
        )

        self.section_home = ft.Column(
            width=800, alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.Row(
                    controls=[
                        ft.Image(resource_path("assets/icons/grey/store.svg"), width=324, height=24),
                        ft.Text("Paramètres établissement", size=26, font_family='PPN', color="#717171"),
                    ]
                ),
                ft.Container(
                    **settings_style, width=800,
                    content=ft.Column(
                        controls=[
                            ft.Container(
                                padding=20, border=ft.border.only(bottom=ft.BorderSide(1, BG_COLOR)),
                                content=ft.Row(
                                    controls=[
                                        ft.Column(
                                            spacing=0, controls=[
                                                ft.Text("ID établissement", size=16, font_family="PPN"),
                                                ft.Text(
                                                    "Uuidde votre compte",
                                                    size=13, font_family="PPM", color="grey"
                                                )
                                            ]
                                        ),
                                        self.info_tenant_id
                                        
                                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                )
                            ),
                            ft.Container(
                                padding=20, border=ft.border.only(bottom=ft.BorderSide(1, BG_COLOR)),
                                content=ft.Row(
                                    controls=[
                                        ft.Column(
                                            spacing=0, controls=[
                                                ft.Text("Nom étabmlissement", size=16, font_family="PPN"),
                                                ft.Text(
                                                    "Sera visible apparaîtra sur les rapports et factures",
                                                    size=13, font_family="PPM", color="grey"
                                                )
                                            ]
                                        ),
                                        self.info_name
                                        
                                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                )
                            ),
                            ft.Container(
                                padding=20, border=ft.border.only(bottom=ft.BorderSide(1, BG_COLOR)),
                                content=ft.Row(
                                    controls=[
                                        ft.Column(
                                            spacing=0, controls=[
                                                ft.Text("Slogan", size=16, font_family="PPN"),
                                                ft.Text(
                                                    "Sera visible sur les factures",
                                                    size=13, font_family="PPM", color="grey"
                                                )
                                            ]
                                        ),
                                        self.info_slogan
                                        
                                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                )
                            ),
                            ft.Container(
                                padding=20, border=ft.border.only(bottom=ft.BorderSide(1, BG_COLOR)),
                                content=ft.Row(
                                    controls=[
                                        ft.Column(
                                            spacing=0, controls=[
                                                ft.Text("Contact", size=16, font_family="PPN"),
                                                ft.Text(
                                                    "Sera visible sur les factures",
                                                    size=13, font_family="PPM", color="grey"
                                                )
                                            ]
                                        ),
                                        self.info_contact
                                        
                                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                )
                            ),
                            ft.Container(
                                padding=20,
                                content=ft.Row(
                                    controls=[
                                        ft.Column(
                                            spacing=0, controls=[
                                                ft.Text("Adresse physique", size=16, font_family="PPN"),
                                                ft.Text(
                                                    "Sera visible sur les factures",
                                                    size=13, font_family="PPM", color="grey"
                                                )
                                            ]
                                        ),
                                        self.info_adress
                                        
                                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                )
                            ),
                            
                        ]
                    )
                ),
                ft.Row(
                    [MyButton(
                        "Sauvegarder changements", resource_path('assets/icons/white/save.svg'),
                        self.update_tenant_infos
                    )], alignment=ft.MainAxisAlignment.END
                ),      
                
            ]
        )
        self.section_abo = ft.Column(
            alignment=ft.MainAxisAlignment.CENTER, width=800,
            controls=[
                ft.Row(
                    controls=[
                        ft.Image(resource_path("assets/icons/grey/calendar-days.svg"), width=324, height=24),
                        ft.Text("Paramètres Abonnement", size=26, font_family='PPN', color="#717171"),
                    ]
                ),
                ft.Container(
                   **settings_style, width=800,
                    content=ft.Column(
                        controls=[
                            ft.Container(
                                padding=20, border=ft.border.only(bottom=ft.BorderSide(1, BG_COLOR)),
                                content=ft.Row(
                                    controls=[
                                        ft.Column(
                                            spacing=0, controls=[
                                                ft.Text("formula d'abonnement", size=16, font_family="PPN"),
                                                ft.Text(
                                                    "Formule d'abonnement en vigueur",
                                                    size=13, font_family="PPM", color="grey"
                                                )
                                            ]
                                        ),
                                        self.info_abo
                                        
                                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                )
                            ),
                            ft.Container(
                                padding=20, border=ft.border.only(bottom=ft.BorderSide(1, BG_COLOR)),
                                content=ft.Row(
                                    controls=[
                                        ft.Column(
                                            spacing=0, controls=[
                                                ft.Text("Date d'expiration", size=16, font_family="PPN"),
                                                ft.Text(
                                                    "Date de fin d'abonnement",
                                                    size=13, font_family="PPM", color="grey"
                                                )
                                            ]
                                        ),
                                        self.info_fin_abo
                                        
                                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                )
                            ),
                            ft.Container(
                                padding=20, border=ft.border.only(bottom=ft.BorderSide(1, BG_COLOR)),
                                content=ft.Row(
                                    controls=[
                                        ft.Column(
                                            spacing=0, controls=[
                                                ft.Text("Expire Dans", size=16, font_family="PPN"),
                                                ft.Text(
                                                    "Nombre de jrs avant la fin de l'abonnement",
                                                    size=13, font_family="PPM", color="grey"
                                                )
                                            ]
                                        ),
                                        self.info_delay_abo
                                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                )
                            ),
                            
                            
                        ]
                    )
                ),
                ft.Row(
                    [MyButton(
                        "Se réabonner", resource_path('assets/icons/white/plus.svg'),
                        self.open_paiement_window
                    )], alignment=ft.MainAxisAlignment.END
                ), 
            ]
        )
        
        self.table_paiements = ft.DataTable(
            **datatable_style,
            columns=[
                ft.DataColumn(ft.Text("Date paiement")),
                ft.DataColumn(ft.Text("Type Abonnement")),
                ft.DataColumn(ft.Text("Début")),
                ft.DataColumn(ft.Text("Fin")),
            ]
        )
        
        self.section_paiement = ft.Column(
            width=800, alignment=ft.MainAxisAlignment.CENTER, expand=True,
            controls=[
                ft.Row(
                    controls=[
                        ft.Image(resource_path("assets/icons/grey/badge-cent.svg"), width=24, height=24),
                        ft.Text("Historique des paiements", size=26, font_family='PPN', color="#717171"),
                    ]
                ),
                ft.Container(
                    **settings_style, width=800,
                    expand=True,
                    content=ft.Column(
                        controls=[
                            ft.Container(
                                padding=20, border=ft.border.only(bottom=ft.BorderSide(1, BG_COLOR)), expand=True,
                                height=300,
                                content=ft.ListView(
                                    controls=[self.table_paiements], expand=True, 
                                )
                            ),
                        ]
                    )
                ),    
            ]
        )
        
        # Contentu principal...
        self.content = ft.Column(
            alignment=ft.alignment.center, width=900, expand=True, scroll=ft.ScrollMode.AUTO,
            controls=[ 
                self.section_home,            
                self.section_abo,
                self.section_paiement
            ]
        )
        self.load_datas()
    
    def verifier_abonnement(self):
        print("vérifier abonnement...")
        print("date expiration :", self.expiration_date)
        
        y, m, d = map(int, self.expiration_date.split('-'))
        delay = (datetime.date(y, m, d) - datetime.date.today()).days
        
        print("délai", delay)
        return delay

    @staticmethod
    def run_async_in_thread(coro):
        """Exécute une coroutine asynchrone dans un thread séparé"""

        def runner():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(coro)
            loop.close()

        thread = threading.Thread(target=runner)
        thread.start()

    # def on_mount(self):
    #     """Appelé au montage du composant"""
    #     self.run_async_in_thread(self.on_init_async())

    async def on_init_async(self):
        """Initialisation asynchrone"""
        await self.load_datas()
    
    def load_datas(self):
        my_request = supabase_client.table('tenants').select("*").eq('id', self.tenant_id).execute()
        infos = my_request.data[0]
        
        adresse = infos['adresse'] if infos['adresse'] else ""
        contact = infos['contact'] if infos['contact'] else ""
        slogan = infos['slogan'] if infos['slogan'] else ""
        
        self.info_adress.value = adresse
        self.info_slogan.value = slogan
        self.info_contact.value = contact
        
        payments = supabase_client.table("paiements").select("*").eq('tenant_id', self.tenant_id).execute()
        
        self.table_paiements.rows.clear()
        
        for pay in payments.data:
            self.table_paiements.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(f"{pay['date_paiement']}")),
                        ft.DataCell(ft.Text(f"{pay['reference_transaction']}")),
                        ft.DataCell(ft.Text(f"{pay['periode_couverte_debut']}")),
                        ft.DataCell(ft.Text(f"{pay['periode_couverte_fin']}")),
                    ]
                )
            )
    
    def update_tenant_infos(self, e):
        if self.info_name.value:
            try:
                supabase_client.table("tenants") \
                    .update(
                        {
                            "slogan": self.info_slogan.value, "adresse": self.info_adress.value, 
                            "contact": self.info_contact.value, "nom_entreprise": self.info_name.value
                        }
                    ) \
                    .eq("id", self.tenant_id) \
                    .execute()
                    
                print("Mise à jour réussie !")
                self.cp.show_alert("Données mises à jour", ft.Icons.CHECK_CIRCLE, ft.Colors.LIGHT_GREEN)
                
            except Exception as ex:
                print(f"Erreur lors de la mise à jour : {ex}")
        else:
            self.cp.show_alert("Nom doit être nom nul", ft.Icons.INFO, ft.Colors.RED)
    
    def open_paiement_window(self, e):     
        self.cp.show_alert("Fonctionnalité à venir", ft.Icons.INFO, ft.Colors.RED)
        