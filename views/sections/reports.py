import flet as ft
from components.components import MyButton
from utils import (
    ACCESS_TOKEN, ROLE, USER_ID, TENANT_ID, USER_NAME, PLAN_CHOISI, EXPIRATION_DATE, EXPIRATION_DATE, TENANT_NAME,
    TENANT_ID, USER_EMAIL, format_milliers_fr, BG_COLOR,
    resource_path, MAIN_COLOR, convert_date_to_string, create_objet_date,
    TEXT_PRIMARY, TEXT_SECONDARY, SHADOW_COLOR, BORDER_COLOR, CARD_BG
)
import datetime, asyncio, threading
from services.async_function import supabase_request_async
import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from datetime import datetime, date, timedelta
from styles import config_tf_style, drop_style, datatable_style, stat_style


class Reports(ft.Container):
    def __init__(self, cp: object):
        super().__init__(
            expand=True,
        )
        self.cp = cp
        #paramètres généraux
        self.plan_choisi = self.cp.page.client_storage.get(PLAN_CHOISI)
        self.expiration_date = self.cp.page.client_storage.get(EXPIRATION_DATE)
        self.tenant_name = self.cp.page.client_storage.get(TENANT_NAME)
        self.tenant_id = self.cp.page.client_storage.get(TENANT_ID)
        self.user_id = self.cp.page.client_storage.get(USER_ID)
        self.user_name = self.cp.page.client_storage.get(USER_NAME)
        self.access_token = self.cp.page.client_storage.get(ACCESS_TOKEN)
        self.role = self.cp.page.client_storage.get(ROLE)
        self.user_email = self.cp.page.client_storage.get(USER_EMAIL)

        # statistiques
        self.remove_button = ft.Container(
            height=20, width=30, alignment=ft.alignment.center,
            border_radius=ft.border_radius.only(bottom_right=4, bottom_left=4),
            bgcolor="white", border=ft.border.all(1, '#f0f0f6'),
            content=ft.Text("-", size=14, font_family="PPM"),
            on_click=self.remove
        )
        self.add_button = ft.Container(
            height=20, width=30, alignment=ft.alignment.center,
            border_radius=ft.border_radius.only(top_right=4, top_left=4),
            bgcolor="white", border=ft.border.all(1, '#f0f0f6'),
            content=ft.Text("+", size=14, font_family="PPM"),
            on_click=self.add,
        )
        self.changing_day = ft.Text(str(convert_date_to_string(date.today())), size=14, font_family="PPM")
        self.periode_chip = ft.Container(
            height=40, border_radius=2, padding=5, alignment=ft.alignment.center,
            bgcolor="white", border=ft.border.all(1, '#f0f0f6'),width=100,
            content=ft.Row(
                controls=[self.changing_day],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=5
            )
        )
        self.first_title = ft.Text("", size=14, font_family="PPM", color="grey")
        self.first_amount = ft.Text("0", size=18, font_family="PEB")
        self.first_container = ft.Container(
            **stat_style, width=285,
            content=ft.Column(
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            self.first_title,
                            ft.Image(resource_path("assets/icons/grey/badge-cent.svg"), width=18, height=18)
                        ]
                    ),
                    ft.Divider(height=1, color=ft.Colors.TRANSPARENT),
                    ft.Row(
                        controls=[
                            self.first_amount,
                            ft.Text("XAF", size=14, font_family="PPM", color=TEXT_SECONDARY)
                        ]
                    ),
                ]
            )
        )
        
        self.second_title = ft.Text("", size=14, font_family="PPM", color="grey")
        self.second_amount = ft.Text("0", size=18, font_family="PEB")
        self.second_container = ft.Container(
            **stat_style, width=285,
            content=ft.Column(
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            self.second_title,
                            ft.Image(resource_path("assets/icons/grey/badge-cent.svg"), width=18, height=18)
                        ]
                    ),
                    ft.Divider(height=1, color=ft.Colors.TRANSPARENT),
                    ft.Row(
                        controls=[
                            self.second_amount,
                            ft.Text("XAF", size=14, font_family="PPM", color=TEXT_SECONDARY)
                        ]
                    ),
                ]
            )
        )
        
        
        self.prog_title = ft.Text("", size=14, font_family="PPM", color="grey")
        self.prog_amount = ft.Text("0", size=18, font_family="PEB")
        self.prog_icon = ft.Image(
            resource_path("assets/icons/grey/minus.svg"),
            width=16, height=16
        )
        self.prog_percent = ft.Text(size=12, font_family="PPM")
        
        self.prog_container = ft.Container(
            **stat_style, width=285,
            content=ft.Column(
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            self.prog_title,
                            ft.Image(resource_path("assets/icons/grey/chart-spline.svg"), width=18, height=18)
                        ]
                    ),
                    ft.Divider(height=1, color=ft.Colors.TRANSPARENT),
                    ft.Row(
                        controls=[
                            ft.Row([self.prog_amount, ft.Text("XAF", size=14, font_family="PPM", color="grey")]),
                            ft.Row([self.prog_percent, self.prog_icon])
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                ]
            )
        )

        # Main layout
        self.day = ft.TextField(
            **config_tf_style, width=60, text_align=ft.TextAlign.RIGHT,
            input_filter=ft.NumbersOnlyInputFilter(), hint_text="JJ", keyboard_type=ft.KeyboardType.NUMBER,
            value=str(date.today().day), label="Jour"
        )
        self.month = ft.TextField(
            **config_tf_style, width=60, text_align=ft.TextAlign.RIGHT,
            input_filter=ft.NumbersOnlyInputFilter(), hint_text="MM", keyboard_type=ft.KeyboardType.NUMBER,
            value=str(date.today().month), label="Mois"
        )
        self.year = ft.TextField(
            **config_tf_style, width=100, text_align=ft.TextAlign.RIGHT,
            input_filter=ft.NumbersOnlyInputFilter(), keyboard_type=ft.KeyboardType.NUMBER,
            value=str(date.today().year), label="Année"
        )
        self.base_search = ft.Dropdown(
            **drop_style, width=100, dense=True, label="Type", value="=",
            options=[ft.dropdown.Option(item) for item in ['<=', '<', '>=', ">", "="]]
        )
        self.table = ft.DataTable(
            **datatable_style, columns=[
                ft.DataColumn(
                    ft.Row(
                        controls=[
                            ft.Image(src=resource_path("assets/icons/grey/calendar-days.svg"), width=20, height=20),
                            ft.Text("Date")
                        ], alignment=ft.MainAxisAlignment.CENTER
                    )
                ),
                ft.DataColumn(
                    ft.Row(
                        controls=[
                            ft.Image(src=resource_path("assets/icons/grey/sigma.svg"), width=20, height=20),
                            ft.Text("Total ventes")
                        ], alignment=ft.MainAxisAlignment.CENTER
                    )
                ),
                ft.DataColumn(
                    ft.Row(
                        controls=[
                            ft.Image(src=resource_path("assets/icons/grey/badge-cent.svg"), width=20, height=20),
                            ft.Text("Montant ventes")
                        ], alignment=ft.MainAxisAlignment.CENTER
                    )
                ),
                ft.DataColumn(
                    ft.Row(
                        controls=[
                            ft.Image(src=resource_path("assets/icons/grey/smartphone.svg"), width=20, height=20),
                            ft.Text("Orange Moeny")
                        ], alignment=ft.MainAxisAlignment.CENTER
                    )
                ),
                ft.DataColumn(
                    ft.Row(
                        controls=[
                            ft.Image(src=resource_path("assets/icons/grey/smartphone.svg"), width=20, height=20),
                            ft.Text("Mobile Money")
                        ], alignment=ft.MainAxisAlignment.CENTER
                    )
                ),
                ft.DataColumn(
                    ft.Row(
                        controls=[
                            ft.Image(src=resource_path("assets/icons/grey/hand-coins.svg"), width=20, height=20),
                            ft.Text("Cash")
                        ], alignment=ft.MainAxisAlignment.CENTER
                    )
                ),
                ft.DataColumn(
                    ft.Row(
                        controls=[
                            ft.Image(src=resource_path("assets/icons/grey/paperclip.svg"), width=20, height=20),
                            ft.Text("Lien rapport")
                        ], alignment=ft.MainAxisAlignment.CENTER
                    )
                ),
                ft.DataColumn(
                    ft.Row(
                        controls=[
                            ft.Image(src=resource_path("assets/icons/grey/table-of-contents.svg"), width=20, height=20),
                            ft.Text("")
                        ], alignment=ft.MainAxisAlignment.CENTER
                    )
                ),
                
            ]
        )
               
        self.main_layout = ft.Container(
            **stat_style,
            content=ft.Column(
                expand=True,
                controls=[
                    # ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                    ft.Column(
                        expand=True,
                        controls=[
                            ft.Container(
                                expand=True,
                                padding=20, content=ft.Column(
                                    expand=True,
                                    controls=[
                                        ft.Row(
                                            controls=[
                                                ft.Text("Rapports journaliers", size=16, font_family="PEB"),
                                                MyButton(
                                                    "Clôture",
                                                    resource_path("assets/icons/white/wallet.svg"),
                                                    lambda e: self.run_async_in_thread(self.open_cloture_window(e))
                                                )
                                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                        ),
                                        ft.Row(
                                            controls=[
                                                self.base_search, self.day, self.month, self.year,
                                                ft.Container(
                                                    border_radius=6, padding=8, alignment=ft.alignment.center, border=ft.border.all(1, "grey"),
                                                    bgcolor=BG_COLOR,
                                                    content=ft.Image(
                                                        src=resource_path("assets/icons/grey/funnel.svg"), width=16, height=18
                                                    ),
                                                    on_click=self.filter_history
                                                ),
                                                ft.Container(
                                                    border_radius=6, padding=8, alignment=ft.alignment.center,
                                                    border=ft.border.all(1, "grey"),
                                                    bgcolor=BG_COLOR,
                                                    content=ft.Image(
                                                        src=resource_path("assets/icons/grey/funnel-x.svg"), width=16, height=18
                                                    ),
                                                    on_click=lambda e: self.run_async_in_thread(self.load_datas())
                                                ),
                                            ]
                                        ),
                                        ft.Divider(height=2, color=ft.Colors.TRANSPARENT),
                                        ft.ListView(expand=True, controls=[self.table]),
                                    ]
                                )
                            ),
                        ]
                    )
                ]
            )
        )

        # fenêtre des details de vente...
        self.selected_date = ft.Text("", size=24, font_family="PEB")
        self.nb_details = ft.Text("", size=16, font_family="PPM")
        self.total_vendu = ft.Text("", size=18, font_family="PEB")
        self.nb_produits_vendus = ft.Text("", size=16, font_family="PPM")
        self.dt_table = ft.DataTable(
            **datatable_style,
            columns=[
                ft.DataColumn(ft.Text("Désignation")),
                ft.DataColumn(ft.Text("qté")),
                ft.DataColumn(ft.Text("Prix")),
                ft.DataColumn(ft.Text("Total")),
            ]
        )
        
        self.details_vente_form = ft.Column(
            controls=[
                ft.Container(
                    padding=20, bgcolor="white",
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            self.selected_date,
                            ft.Container(
                                content=ft.Image(
                                    resource_path("assets/icons/black/x.svg"), width=20, height=20
                                ),
                                on_click=lambda e: self.cp.hide_container(self.cp.details_vente_container)
                            )
                        ]
                    ),
                ),
                ft.Divider(height=5, thickness=1),
                ft.Container(
                    **stat_style, expand=True,
                    content=ft.Column(
                        controls=[
                                ft.ListView(expand=True, controls=[self.dt_table]),
                                ft.Divider(height=5, thickness=1),
                                ft.Container(
                                    **stat_style,
                                    content=ft.Row(
                                    controls=[
                                        ft.Column(
                                            controls=[
                                                ft.Row(
                                                    controls=[
                                                        ft.Image(
                                                            src=resource_path("assets/icons/grey/sigma.svg"), width=20, height=20
                                                        ),
                                                        ft.Text("Nombre de ventes", size=14, font_family="PPM", color="grey"),
                                                        self.nb_details,
                                                    ]
                                                ),
                                                ft.Row(
                                                    controls=[
                                                        ft.Image(
                                                            src=resource_path("assets/icons/grey/tag.svg"), width=20,
                                                            height=20
                                                        ),
                                                        ft.Text("Nombre Produits vendus", size=14, font_family="PPM",
                                                                color="grey"),
                                                        self.nb_produits_vendus,
                                                    ]
                                                ),
                                                ft.Row(
                                                    controls=[
                                                        ft.Image(
                                                            src=resource_path("assets/icons/grey/badge-cent.svg"), width=20,
                                                            height=20
                                                        ),
                                                        ft.Text("Montant des ventes", size=14, font_family="PPM",
                                                                color="grey"),
                                                        self.total_vendu,
                                                    ]
                                                ),
                                            ]
                                        )
                                    ], alignment=ft.MainAxisAlignment.END,
                                )
                            )
                        ]
                    )
                )
            ], spacing=0, expand=True
        )
        self.progress_container = ft.Container(
            expand=True, alignment=ft.alignment.center, bgcolor="white",
            content=ft.ProgressRing(width=50, height=50, color=MAIN_COLOR)
        )
        self.content = ft.Stack(
            expand=True, alignment=ft.alignment.center,
            controls=[
                ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Text("Historique des ventes", size=24, font_family="PEB"),
                                ft.Row(
                                    controls=[
                                        self.periode_chip,
                                        ft.Column(
                                            controls=[self.add_button, self.remove_button],
                                            spacing=0,
                                            horizontal_alignment=ft.CrossAxisAlignment.CENTER
                                        )
                                    ], spacing=1,
                                ),
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                        ),
                        ft.Row(
                            controls=[self.first_container, self.second_container, self.prog_container],
                        ),
                        ft.Divider(height=5, color=ft.Colors.TRANSPARENT),
                        self.main_layout
                    ]
                ),
                self.progress_container
            ]
        )

        self.r_initial = 0
        self.r_cash = 0
        self.r_om = 0
        self.r_momo = 0
        self.r_total = 0
        self.r_awaited = 0
        
        self.report_date = ft.Text(size=16, font_family="PPM")
        self.report_user = ft.Text(size=16, font_family="PPM")
        self.report_total_vente = ft.Text("-", size=18, font_family="PEB")
        self.report_initial_amount = ft.Text("-", size=18, font_family="PEB")
        self.report_solde_awaited = ft.Text("-", size=18, font_family="PEB", color="red")
        self.report_cash = ft.Text("", size=18, font_family="PEB", color="brown")
        self.report_solde_reel = ft.TextField(
            **config_tf_style, width=150, input_filter=ft.NumbersOnlyInputFilter(), label="Solde réel",
            text_align=ft.TextAlign.RIGHT
        )
        self.report_versement = ft.TextField(
            **config_tf_style, width=170, input_filter=ft.NumbersOnlyInputFilter(), text_align=ft.TextAlign.RIGHT,
            label="Montant versement", value="0"
        )
        self.table_des_ventes: list = []
        self.report_table = ft.DataTable(
            **datatable_style,
            columns=[
                ft.DataColumn(ft.Text("Mode")),
                ft.DataColumn(ft.Text("Montant"))
            ]
        )

        self.on_mount()

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

    def on_mount(self):
        """Appelé au montage du composant"""
        self.run_async_in_thread(self.on_init_async())

    async def on_init_async(self):
        """Initialisation asynchrone"""
        await self.load_datas()
        await self.get_total_sales()

    async def load_datas(self):
        """Charge les catégories de produits"""
        params = {
            'select': "*",
            'order': 'creation_date.desc'
        }

        ventes = await supabase_request_async(
            access_token=self.access_token,
            tenant_id=self.tenant_id,
            table_name="view_rapport_journalier",
            method="GET",
            params=params
        )
        
        self.table_des_ventes = ventes

        # print("DEBUG")
        # print(len(ventes), type(ventes))
        # print(ventes[0])

        self.progress_container.visible = False
        # 3. Chargement par lots
        self.table.rows.clear()
        
        if ventes:
            for item in ventes:
                if item['rapport_url']:
                    my_content = ft.Image(
                        resource_path("assets/icons/grey/paperclip.svg"),
                        width=18, height=18,
                    )
                else:
                    my_content = ft.Text("")
                    
                total_om = format_milliers_fr(item['total_om']) if item['total_om'] else 0
                total_momo = format_milliers_fr(item['total_momo']) if item['total_momo'] else 0
                total_cash = format_milliers_fr(item['total_cash']) if item['total_cash'] else 0
                # Création de la ligne avec les clés du dictionnaire
                row = ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(item['creation_date'])),
                        ft.DataCell(ft.Text(f"{format_milliers_fr(item['nombre_ventes'])}")),
                        ft.DataCell(ft.Text(format_milliers_fr(item['total_ventes']))),
                        ft.DataCell(ft.Text(total_om)),
                        ft.DataCell(ft.Text(total_momo)),
                        ft.DataCell(ft.Text(total_cash)),
                        ft.DataCell(
                            ft.Container(
                                content=my_content,
                                url=item['rapport_url'], data=item,
                            )
                        ),
                        ft.DataCell(
                            ft.Container(
                                content=ft.Image(
                                    resource_path("assets/icons/grey/eye.svg"),
                                    width=18, height=18,
                                ),
                                on_click=self.display_details, data=item
                            )
                        ),
                    ]
                )
                self.table.rows.append(row)

        # On met à jour l'affichage tous les 20 produits pour que l'utilisateur
        # puisse voir les premiers produits arriver instantanément
        self.cp.page.update()

    def display_details(self, e):
        self.run_async_in_thread(self._display_details(e))

    async def _display_details(self, e):
        selected_date = e.control.data['creation_date']
        params = {
            'select': '*',  # On veut tous les champs
            'creation_date': f'eq.{selected_date}'  # 'eq' signifie 'equal' (égal)
        }
        details = await supabase_request_async(
            access_token=self.access_token,
            tenant_id=self.tenant_id,
            table_name="view_historique_ventes",
            method="GET",
            params=params
        )

        print("détails:", len(details))
        self.dt_table.rows.clear()

        nb_produits = 0
        for i, item in enumerate(details):
            nb_produits += item['qte']
            self.dt_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(item['produit_nom'].upper()))),
                        ft.DataCell(ft.Text(item['qte'])),
                        ft.DataCell(ft.Text(f"{format_milliers_fr(item['prix_unitaire'])}")),
                        ft.DataCell(ft.Text(f"{format_milliers_fr(item['prix_unitaire']*item['qte'])}")),
                    ],
                )
            )

        self.selected_date.value = f"Détails du {selected_date}"
        self.nb_details.value = f"{e.control.data['nombre_ventes']} vente(s)"
        self.total_vendu.value = f"{format_milliers_fr(e.control.data['total_ventes'])}"
        self.nb_produits_vendus.value =f"{nb_produits} produit(s)"
        self.cp.details_vente_container.content.content = self.details_vente_form
        self.cp.show_container(self.cp.details_vente_container)
        self.cp.page.update()

    def filter_history(self, e):
        self.run_async_in_thread(self._filter_history(e))

    async def _filter_history(self, e):
        # 1. Construction de la date recherchée
        d = self.day.value.zfill(2)
        m = self.month.value.zfill(2)
        y = self.year.value
        date_recherchee = f"{d}/{m}/{y}"

        # 2. Préparation du paramètre de filtre
        # On utilise le mapping du dropdown pour construire la commande Supabase
        # Ex: si dropdown est "<=", on envoie "lte.DD/MM/YYYY"
        op_map = {"=": "eq", "<": "lt", "<=": "lte", ">": "gt", ">=": "gte"}
        operateur = op_map.get(self.base_search.value, "eq")

        params = {
            'select': "*",
            'creation_date': f"{operateur}.{date_recherchee}",
            'order': 'tenant_id.desc'
        }
        ventes = await supabase_request_async(
            access_token=self.access_token,
            tenant_id=self.tenant_id,
            table_name="view_rapport_journalier",
            method="GET",
            params=params
        )
        print("ventes", len(ventes))
        if isinstance(ventes, list):
            print(ventes[0])

        # 4. Mise à jour de la table
        self.table.rows.clear()

        self.progress_container.visible = True
        # 3. Chargement par lots
        for item in ventes:
            total_om = format_milliers_fr(item['total_om']) if item['total_om'] else 0
            total_momo = format_milliers_fr(item['total_momo']) if item['total_momo'] else 0
            total_cash = format_milliers_fr(item['total_cash']) if item['total_cash'] else 0
            # Création de la ligne avec les clés du dictionnaire
            row = ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(item['creation_date'])),
                    ft.DataCell(ft.Text(f"{format_milliers_fr(item['nombre_ventes'])}")),
                    ft.DataCell(ft.Text(format_milliers_fr(item['total_ventes']))),
                    ft.DataCell(ft.Text(total_om)),
                    ft.DataCell(ft.Text(total_momo)),
                    ft.DataCell(ft.Text(total_cash)),
                    ft.DataCell(
                        ft.Container(
                            content=ft.Image(
                                resource_path("assets/icons/grey/paperclip.svg"),
                                width=18, height=18,
                            ),
                            url=item['rapport_url'], data=item
                        )
                    ),
                    ft.DataCell(
                        ft.Container(
                            content=ft.Image(
                                resource_path("assets/icons/grey/eye.svg"),
                                width=18, height=18,
                            ),
                            on_click=self.display_details, data=item
                        )
                    ),
                ]
            )
            self.table.rows.append(row)

        # On met à jour l'affichage tous les 20 produits pour que l'utilisateur
        # puisse voir les premiers produits arriver instantanément
        self.progress_container.visible = False
        self.cp.page.update()

    async def get_total_sales(self):
        """
        date_choisie doit être une chaîne au format 'DD/MM/YYYY'
        """
        first_date = self.changing_day.value
        date_object = create_objet_date(first_date)
        new_date_object = date_object - timedelta(days=1)
        new_date_string = convert_date_to_string(new_date_object)

        # Appel RPC
        first_montant = await supabase_request_async(
            access_token=self.access_token,
            tenant_id=self.tenant_id,
            table_name="get_total_sales_by_date",  # Nom de la fonction
            method="POST",  # Les RPC se font généralement en POST
            data={"target_date": first_date}
        )

        # Le résultat est souvent retourné sous forme de liste si le RPC est complexe,
        # ou directement la valeur.
        if first_montant:
            first_total = first_montant[0] if isinstance(first_montant, list) else first_montant
        else:
            first_total = 0

        second_montant = await supabase_request_async(
            access_token=self.access_token,
            tenant_id=self.tenant_id,
            table_name="get_total_sales_by_date",  # Nom de la fonction
            method="POST",  # Les RPC se font généralement en POST
            data={"target_date": new_date_string}
        )

        # Le résultat est souvent retourné sous forme de liste si le RPC est complexe,
        # ou directement la valeur.
        if second_montant:  
            second_total = second_montant[0] if isinstance(second_montant, list) else second_montant
        else:
            second_total = 0

        progression = first_total - second_total
        
        if second_total == 0:
            progression_percent = 0
        else:
            progression_percent  = progression * 100 / second_total

        self.first_title.value = f"{first_date}"
        self.second_title.value = f"{new_date_string}"
        self.prog_title.value = "Progression"
        self.first_amount.value = f"{format_milliers_fr(first_total)}"
        self.second_amount.value = f"{format_milliers_fr(second_total)}"
        self.prog_amount.value = f"{format_milliers_fr(progression)}"
        self.prog_percent.value = f"{progression_percent:.2f}%"

        if progression > 0:
            self.prog_percent.color = ft.Colors.TEAL_300
            self.prog_icon.src = resource_path("assets/icons/others/trending-up.svg")
        else:
            self.prog_percent.color = ft.Colors.RED_300
            self.prog_icon.src = resource_path("assets/icons/others/trending-down.svg")

        self.cp.page.update()

    async def _get_total_sales(self, e):
        """
        date_choisie doit être une chaîne au format 'DD/MM/YYYY'
        """
        first_date = self.changing_day.value
        date_object = create_objet_date(first_date)
        new_date_object = date_object - timedelta(days=1)
        new_date_string = convert_date_to_string(new_date_object)

        # Appel RPC
        first_montant = await supabase_request_async(
            access_token=self.access_token,
            tenant_id=self.tenant_id,
            table_name="get_total_sales_by_date",  # Nom de la fonction
            method="POST",  # Les RPC se font généralement en POST
            data={"target_date": first_date}
        )

        # Le résultat est souvent retourné sous forme de liste si le RPC est complexe,
        # ou directement la valeur.
        
        if first_montant:
            first_total = first_montant[0] if isinstance(first_montant, list) else first_montant
        else:
            first_total = 0

        second_montant = await supabase_request_async(
            access_token=self.access_token,
            tenant_id=self.tenant_id,
            table_name="get_total_sales_by_date",  # Nom de la fonction
            method="POST",  # Les RPC se font généralement en POST
            data={"target_date": new_date_string}
        )

        # Le résultat est souvent retourné sous forme de liste si le RPC est complexe,
        # ou directement la valeur.
        if second_montant:
            second_total = second_montant[0] if isinstance(second_montant, list) else second_montant
        else:
            second_total = 0

        progression = first_total - second_total
        
        if second_total == 0:
            progression_percent = 0
        else:
            progression_percent  = progression * 100 / second_total

        self.first_title.value = f"{first_date}"
        self.second_title.value = f"{new_date_string}"
        self.prog_title.value = "Progression"
        self.first_amount.value = f"{format_milliers_fr(first_total)}"
        self.second_amount.value = f"{format_milliers_fr(second_total)}"
        self.prog_amount.value = f"{format_milliers_fr(progression)}"
        self.prog_percent.value = f"{progression_percent:.2f}%"

        if progression > 0:
            self.prog_percent.color = ft.Colors.TEAL_300
            self.prog_icon.src = resource_path("assets/icons/others/trending-up.svg")
        else:
            self.prog_percent.color = ft.Colors.RED_300
            self.prog_icon.src = resource_path("assets/icons/others/trending-down.svg")

        self.cp.page.update()

    def update_total_sales(self, e):
        self.run_async_in_thread(self._get_total_sales(e))

    def add(self, e):
        date_object = create_objet_date(self.changing_day.value)
        new_date_object = date_object + timedelta(days=1)
        new_date_string = convert_date_to_string(new_date_object)
        self.changing_day.value = new_date_string
        self.update_total_sales(e)

    def remove(self, e):
        date_object = create_objet_date(self.changing_day.value)
        new_date_object = date_object - timedelta(days=1)
        new_date_string = convert_date_to_string(new_date_object)
        self.changing_day.value = new_date_string
        self.update_total_sales(e)

    async def handle_cloture(self, e):
        if not self.report_solde_reel.value or not self.report_versement.value:
            self.cp.show_alert("Veuillez remplir tous les champs", ft.Icons.WARNING_ROUNDED, ft.Colors.ORANGE)
            return

        montant_physique = int(self.report_solde_reel.value)
        montant_versement = int(self.report_versement.value)

        self.cp.show_alert("Traitement du rapport PDF et des stocks...", ft.Icons.HOURGLASS_TOP_ROUNDED, ft.Colors.BLUE)

        # 1. On lance ta fonction : elle crée le PDF local + l'upload et donne l'URL
        url_du_rapport = self.generer_pdf_cloture(
            solde_initial=int(self.r_initial),
            val_cash=int(self.r_cash),
            val_momo=int(self.r_momo),
            val_om=int(self.r_om),
            val_total=int(self.r_total),
            montant_physique=montant_physique,
            solde_awaited=self.r_awaited
        )

        if not url_du_rapport:
            self.cp.show_alert("Échec de création du rapport. Processus interrompu.", ft.Icons.ERROR_OUTLINE_ROUNDED, ft.Colors.RED)
            return

        # 2. On envoie la vraie URL à la RPC définitive
        try:
            result = await supabase_request_async(
                access_token=self.access_token,
                tenant_id=self.tenant_id,
                table_name="cloturer_journee_rpc",
                method="POST",
                data={
                    "p_tenant_id": self.tenant_id,
                    "p_montant_fin": float(montant_physique),
                    "p_versement": float(montant_versement),
                    "p_rapport_url": url_du_rapport  # Enregistre l'URL https://...
                }
            )

            if isinstance(result, dict) and "error" in result:
                self.cp.show_alert(f"Erreur BDD : {result.get('error')}", ft.Icons.ERROR_OUTLINE_ROUNDED, ft.Colors.RED)
                return

            self.cp.show_alert("Journée clôturée avec succès !", ft.Icons.CHECK_CIRCLE, ft.Colors.LIGHT_GREEN)
            self.cp.hide_container(self.cp.cloture_container)
            
            await self.load_datas()
            self.cp.page.update()

        except Exception as ex:
            self.cp.show_alert(f"Erreur système : {ex}", ft.Icons.INFO_OUTLINE, ft.Colors.RED)
    
    def generer_pdf_cloture(self, solde_initial, val_cash, val_momo, val_om, val_total, montant_physique, solde_awaited):
        """Génère le rapport PDF de clôture (Z-Report) détaillé après succès et l'envoie sur Supabase"""
        try:
            # Configuration du fichier de sortie
            date_str = datetime.now().strftime("%Y-%m-%d_%H-%M")
            nom_fichier = f"Z_Report_{date_str}.pdf"
            
            # Chemin d'enregistrement par défaut (Dossier Téléchargements)
            chemin_sauvegarde = os.path.join(os.path.expanduser("~"), "Downloads", nom_fichier)

            # Marges et structure de la page
            doc = SimpleDocTemplate(
                chemin_sauvegarde, 
                pagesize=letter, 
                rightMargin=40, 
                leftMargin=40, 
                topMargin=40, 
                bottomMargin=40
            )
            story = []
            styles = getSampleStyleSheet()

            # Styles personnalisés
            title_style = ParagraphStyle(
                'Title', 
                parent=styles['Heading1'], 
                fontSize=22, 
                leading=26, 
                textColor=colors.HexColor("#1A237E"), 
                alignment=1
            )
            section_style = ParagraphStyle(
                'Section', 
                parent=styles['Heading2'], 
                fontSize=14, 
                leading=18, 
                textColor=colors.HexColor("#1A237E"), 
                spaceBefore=15, 
                spaceAfter=5
            )
            normal_style = styles['Normal']
            bold_style = ParagraphStyle('Bold', parent=normal_style, fontName='Helvetica-Bold')
            bold_white_style = ParagraphStyle('BoldWhite', parent=normal_style, fontName='Helvetica-Bold', textColor=colors.white)

            # 1. ENTÊTE DU PDF
            story.append(Paragraph("Postly - RAPPORT DE CLÔTURE JOURNALIER", title_style))
            story.append(Spacer(1, 15))
            
            # Informations générales (Date, Établissement, Caissier)
            story.append(Paragraph(f"<b>Date de traitement :</b> {datetime.now().strftime('%d/%m/%Y à %H:%M')}", normal_style))
            story.append(Paragraph(f"<b>Établissement :</b> {self.tenant_name}", normal_style))
            story.append(Paragraph(f"<b>Caissier(e) :</b> {self.user_name.upper()}", normal_style))
            story.append(Spacer(1, 15))

            # 2. SECTION : FLUX COMPTABLES & REVENUS (Ventes & Mode de paiement)
            story.append(Paragraph("1. Résumé des Ventes et Flux Electroniques", section_style))
            
            # Calcul des entrées mobiles globales pour le rapport
            total_mobile = val_momo + val_om

            data_flux = [
                [Paragraph("<b>Indicateur de Flux</b>", normal_style), Paragraph("<b>Montant enregistré</b>", bold_white_style)],
                [Paragraph("Entrées Ventes en Cash (Espèces)", normal_style), f"{format_milliers_fr(val_cash)} XAF"],
                [Paragraph("Entrées Paiements Mobiles (Orange Money / MoMo)", normal_style), f"{format_milliers_fr(total_mobile)} XAF"],
                [Paragraph("<b>TOTAL DES VENTES DU JOUR (Tout mode)</b>", bold_style), Paragraph(f"<b>{format_milliers_fr(val_total)} XAF</b>", bold_style)]
            ]

            t_flux = Table(data_flux, colWidths=[320, 180])
            t_flux.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (1,0), colors.HexColor("#1A237E")),
                ('TEXTCOLOR', (0,0), (1,0), colors.whitesmoke),
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                ('TOPPADDING', (0,0), (-1,-1), 6),
                ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F9F9F9")]),
                ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
            ]))
            story.append(t_flux)
            story.append(Spacer(1, 15))

            # 3. SECTION : ÉTAT DE LA CAISSE PHYSIQUE (CASH) & ÉCART
            story.append(Paragraph("2. Contrôle de la Caisse Physique (Cash)", section_style))
            
            # Calcul de l'écart (Réel - Attendu)
            ecart = montant_physique - solde_awaited
            if ecart == 0:
                txt_ecart = "0 XAF (Parfait)"
                couleur_ecart = colors.HexColor("#2E7D32") # Vert
            elif ecart > 0:
                txt_ecart = f"+{format_milliers_fr(ecart)} XAF (Excédent)"
                couleur_ecart = colors.HexColor("#1565C0") # Bleu
            else:
                txt_ecart = f"{format_milliers_fr(ecart)} XAF (Déficit)"
                couleur_ecart = colors.HexColor("#C62828") # Rouge

            # Structure des données avec correction couleur (Gris de fond, texte Blanc) et intégration des ventes Cash perçues
            data_caisse = [
                [Paragraph("<b>Élément de contrôle</b>", normal_style), Paragraph("<b>Valeur Comptable / Réelle</b>", bold_white_style)],
                [Paragraph("Solde de départ (Fond de roulement)", normal_style), f"{format_milliers_fr(solde_initial)} XAF"],
                [Paragraph("Ventes Cash perçues dans la journée", normal_style), f"{format_milliers_fr(val_cash)} XAF"],
                [Paragraph("Montant Cash Attendu (Départ + Ventes Cash)", normal_style), f"{format_milliers_fr(solde_awaited)} XAF"],
                [Paragraph("<b>Montant Cash Réel (Déclaré physique)</b>", bold_style), Paragraph(f"<b>{format_milliers_fr(montant_physique)} XAF</b>", bold_style)],
                [Paragraph("<b>ÉCART DE CAISSE</b>", bold_style), Paragraph(f"<b>{txt_ecart}</b>", ParagraphStyle('Ec', parent=normal_style, fontName='Helvetica-Bold', textColor=couleur_ecart))]
            ]

            t_caisse = Table(data_caisse, colWidths=[320, 180])
            t_caisse.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (1,0), colors.HexColor("#424242")), # Menu Fond Gris Foncé
                ('TEXTCOLOR', (0,0), (1,0), colors.white),                # Menu Texte Blanc
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                ('TOPPADDING', (0,0), (-1,-1), 6),
                ('ROWBACKGROUNDS', (0,1), (-1,-2), [colors.white, colors.HexColor("#F5F5F5")]), # Alternance Fond Gris Clair / Blanc
                ('BACKGROUND', (0,-1), (1,-1), colors.HexColor("#E0E0E0")), # Ligne Écart sur fond gris plus prononcé
                ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
            ]))
            story.append(t_caisse)
            
            story.append(Spacer(1, 35))
            story.append(Paragraph("<i>Note : Ce document fait foi de clôture définitive pour la journée indiquée. Toute anomalie ou écart négatif important doit être justifié auprès de la direction.</i>", normal_style))

            # Signatures
            story.append(Spacer(1, 20))
            data_signatures = [
                [Paragraph("<b>Signature du Caissier</b>", normal_style), Paragraph("<b>Signature du Manager / Visa</b>", normal_style)]
            ]
            t_signatures = Table(data_signatures, colWidths=[250, 250])
            t_signatures.setStyle(TableStyle([
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('BOTTOMPADDING', (0,0), (-1,-1), 50), 
            ]))
            story.append(t_signatures)

            # Construction effective du document PDF local
            doc.build(story)
            print(f"Rapport PDF complet généré avec succès dans : {chemin_sauvegarde}")
            
            # ================= ENVOI SUR SUPABASE STORAGE =================
            from services.supabase_client import supabase_admin
            
            with open(chemin_sauvegarde, 'rb') as f:
                supabase_admin.storage.from_("rapports").upload(
                    path=nom_fichier,
                    file=f,
                    file_options={"content-type": "application/pdf"}
                )
            
            url_publique = supabase_admin.storage.from_("rapports").get_public_url(nom_fichier)
            
            self.cp.show_alert(f"Rapport enregistré localement et archivé sur le Cloud", ft.Icons.FILE_DOWNLOAD_DONE_ROUNDED, ft.Colors.BLUE)
            
            return str(url_publique)

        except Exception as pdf_ex:
            print(f"Erreur lors de l'extraction ou de l'upload du PDF de clôture : {pdf_ex}")  
            return None
            
    async def open_cloture_window(self, e):
        # 1. Format ISO STRICT pour Supabase (évite l'erreur 22008)
        date_iso_supabase = date.today().strftime("%Y-%m-%d") # Génère "2026-06-14"

        # 2. Format d'affichage pour l'interface Flet
        date_affichage_fr = convert_date_to_string(date.today()) # Génère "14/06/2026"

        # Vérifier si la ligne de caisse existe déjà pour aujourd'hui
        check_params = {
            'select': 'id',
            'tenant_id': f'eq.{self.tenant_id}',
            'date_cloture': f'eq.{date_iso_supabase}'  # <-- ON UTILISE LE FORMAT ISO ICI
        }
        
        deja_cloture = await supabase_request_async(
            access_token=self.access_token, tenant_id=self.tenant_id,
            table_name="caisse", method="GET", params=check_params
        )

        if deja_cloture and isinstance(deja_cloture, list) and len(deja_cloture) > 0:
            self.cp.show_alert("La journée d'aujourd'hui est déjà clôturée et verrouillée !", ft.Icons.LOCK_CLOCK_OUTLINED, ft.Colors.ORANGE)
        
        else:
            # Récupérer le dernier solde enregistré (le solde fin de la dernière clôture)
            params = {
                'select': 'montant_fin, versement',
                'tenant_id': f'eq.{self.tenant_id}',
                'order': 'date_cloture.desc',
                'limit': 1
            }

            dernier_solde = await supabase_request_async(
                access_token=self.access_token,
                tenant_id=self.tenant_id,
                table_name="caisse",
                method="GET",
                params=params
            )
            
            # Déterminer le montant initial
            solde_initial = 0
            if dernier_solde and isinstance(dernier_solde, list) and len(dernier_solde) > 0:
                solde_initial = (dernier_solde[0].get('montant_fin', 0) or 0) - (dernier_solde[0].get('versement', 0) or 0) 
            
            self.report_initial_amount.value = f"{format_milliers_fr(solde_initial)}"
            self.report_user.value = self.user_name or "Utilisateur"

            # <-- ON ASSIGNE LE FORMAT FRANÇAIS POUR L'AFFICHAGE ÉCRAN DE L'UTILISATEUR
            self.report_date.value = date_affichage_fr

            # Filtrer les données de la journée localement (dépend du format de 'creation_date')
            # Si 'creation_date' dans ton dictionnaire de ventes est en format FR, utilise date_affichage_fr
            # Si c'est au format ISO, utilise date_iso_supabase
            val_cash = 0
            val_om = 0
            val_momo = 0
            val_total = 0

            if hasattr(self, 'table_des_ventes') and self.table_des_ventes:
                # Modifie ici selon le format stocké dans 'table_des_ventes'
                filtered_date_datas = list(filter(lambda x: date_iso_supabase == x.get('creation_date')[:10] if x.get('creation_date') else False, self.table_des_ventes))

                if filtered_date_datas and len(filtered_date_datas) > 0:
                    val_cash = filtered_date_datas[0].get('total_cash', 0) or 0
                    val_om = filtered_date_datas[0].get('total_om', 0) or 0
                    val_momo = filtered_date_datas[0].get('total_momo', 0) or 0
                    val_total = filtered_date_datas[0].get('total_ventes', 0) or 0

            # ... Reste du code de ton fichier inchangé ...

            self.report_table.rows.clear()
            rows = [
                ft.DataRow(cells=[ft.DataCell(ft.Text("Momo")), ft.DataCell(ft.Text(format_milliers_fr(val_momo)))], color=BG_COLOR),
                ft.DataRow(cells=[ft.DataCell(ft.Text("OM")), ft.DataCell(ft.Text(format_milliers_fr(val_om)))]),
                ft.DataRow(cells=[ft.DataCell(ft.Text("Cash")), ft.DataCell(ft.Text(format_milliers_fr(val_cash)))], color=BG_COLOR)
            ]
            for row in rows:
                self.report_table.rows.append(row)
            
            # Remplissage des totaux à l'écran
            self.report_total_vente.value = format_milliers_fr(val_total)
            self.report_cash.value = format_milliers_fr(val_cash)

            # Calcul comptable du solde attendu
            solde_awaited = int(solde_initial) + int(val_cash)
            self.report_solde_awaited.value = format_milliers_fr(solde_awaited)

            # Pré-remplir le champ de saisie du solde réel
            self.report_solde_reel.value = str(solde_awaited)
            self.report_versement.value = "0"

            # Reconstruction de la structure de ton formulaire Flet
            self.cp.cloture_form.controls.clear()
            self.cp.cloture_form.controls = [
                ft.Row(
                    controls=[
                        ft.Text("Clôture journée", size=20, font_family='PEB'),
                        ft.Container(
                            content=ft.Image(resource_path("assets/icons/black/x.svg"), width=18, height=18),
                            on_click=lambda e: self.cp.hide_container(self.cp.cloture_container)
                        )
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                ft.Divider(height=1, thickness=1),
                ft.Row(
                    [
                        ft.Row(controls=[ft.Image(resource_path("assets/icons/grey/user.svg"), width=16, height=16),
                                         ft.Text("Utilisateur", size=14, font_family='PPI', color="grey")]),
                        self.report_user
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                ft.Row(
                    [
                        ft.Row(
                            controls=[ft.Image(resource_path("assets/icons/grey/calendar-days.svg"), width=16, height=16),
                                      ft.Text("Date du jour", size=14, font_family='PPI', color="grey")]),
                        self.report_date
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                ft.Row(
                    [
                        ft.Row(controls=[ft.Image(resource_path("assets/icons/grey/badge-cent.svg"), width=16, height=16),
                                         ft.Text("Montant départ", size=14, font_family='PPI', color="grey")]),
                        self.report_initial_amount
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                ft.Text("Détails par mode", size=14, font_family='PPI', color="grey"),
                ft.Container(
                    padding=0, border=ft.border.all(1, BG_COLOR), border_radius=10, expand=True,
                    content=ft.ListView(expand=True, controls=[self.report_table]),
                ),
                ft.Row(
                    [
                        ft.Row(controls=[ft.Image(resource_path("assets/icons/grey/badge-cent.svg"), width=16, height=16),
                                         ft.Text("Total ventes du jour", size=14, font_family='PPI', color="grey")]),
                        self.report_total_vente
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                ft.Row(
                    [
                        ft.Row(controls=[ft.Image(resource_path("assets/icons/grey/badge-cent.svg"), width=16, height=16),
                                         ft.Text("Total ventes cash du jour", size=14, font_family='PPI', color="grey")]),
                        self.report_cash
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                ft.Row(
                    [
                        ft.Row(controls=[ft.Image(resource_path("assets/icons/grey/badge-cent.svg"), width=16, height=16),
                                         ft.Text("Montant final attendu", size=14, font_family='PPI', color="grey")]),
                        self.report_solde_awaited
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                ft.Row(
                    [
                        ft.Row(controls=[ft.Image(resource_path("assets/icons/grey/badge-cent.svg"), width=16, height=16),
                                         ft.Text("Solde final réel", size=14, font_family='PPI', color="grey")]),
                        self.report_solde_reel
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                ft.Row(
                    [
                        ft.Row(controls=[ft.Image(resource_path("assets/icons/grey/badge-cent.svg"), width=16, height=16),
                                         ft.Text("Versement", size=14, font_family='PPI', color="grey")]),
                        self.report_versement
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                MyButton(
                    "Clôturer journée", resource_path("assets/icons/white/wallet.svg"),
                    lambda e: self.run_async_in_thread(self.handle_cloture(e))
                )
            ]

            self.cp.show_container(self.cp.cloture_container)
            self.cp.page.update()
            
            # pour pdf
            self.r_initial = solde_initial
            self.r_awaited = solde_awaited
            self.r_cash = val_cash
            self.r_momo = val_momo
            self.r_om = val_om
            self.r_total = val_total       
    
