import flet as ft
import os
import uuid
from styles import input_style, drop_style, datatable_style, stat_style
from components.components import MyButton
from utils import (
    ACCESS_TOKEN, TENANT_ID, ROLE, MAIN_COLOR, BG_COLOR, resource_path, format_milliers_fr, CARD_BG, BORDER_COLOR, SHADOW_COLOR
)
import asyncio, threading
from services.async_function import supabase_request_async
from services.supabase_client import supabase_client

DEFAULT_IMAGE = "https://hojfmjmrhtsvgfzynelr.supabase.co/storage/v1/object/public/images/19005357.png"


class Products(ft.Container):
    def __init__(self, cp: object):
        super().__init__(expand=True)
        self.cp = cp

        # Récupération des données d'authentification
        self.tenant_id = self.cp.page.client_storage.get(TENANT_ID)
        self.access_token = self.cp.page.client_storage.get(ACCESS_TOKEN)
        self.user_role = self.cp.page.client_storage.get(ROLE)

        # Liste des produits
        self.liste_des_produits: list = []
        self.selected_image_path = None

        # Statistiques
        self.stat_total_produits = ft.Text("0", size=22, font_family="PEB")
        self.stat_valeur_stock = ft.Text("0", size=22, font_family="PEB")
        self.stat_categories = ft.Text("0", size=22, font_family="PEB")

        self.loader = ft.ProgressRing(width=20, height=20, stroke_width=2, color=MAIN_COLOR, visible=False)

        # Recherche
        self.search_field = ft.TextField(
            **input_style,
            width=350,
            label="Rechercher",
            prefix_icon=ft.Icons.SEARCH_ROUNDED,
            on_change=self.filter_products_locally
        )

        # Tableau principal avec une colonne supplémentaire pour le transfert
        self.data_table = ft.DataTable(
            **datatable_style,
            columns=[
                ft.DataColumn(ft.Row(
                    [ft.Image(resource_path('assets/icons/grey/shopping-cart.svg'), width=18, height=18),
                     ft.Text("Désignation")])),
                ft.DataColumn(ft.Row(
                    [ft.Image(resource_path('assets/icons/grey/tag.svg'), width=18, height=18), ft.Text("Catégorie")])),
                ft.DataColumn(ft.Row([ft.Image(resource_path('assets/icons/grey/badge-cent.svg'), width=18, height=18),
                                      ft.Text("Prix")])),
                ft.DataColumn(ft.Row([ft.Image(resource_path('assets/icons/grey/store.svg'), width=18, height=18),
                                      ft.Text("Stock boutique")])),
                ft.DataColumn(ft.Row([ft.Image(resource_path('assets/icons/grey/sigma.svg'), width=18, height=18),
                                      ft.Text("Stock tampon")])),
                ft.DataColumn(ft.Row(
                    [ft.Image(resource_path('assets/icons/grey/circle-dollar-sign.svg'), width=18, height=18),
                     ft.Text("Valeur")])),
                ft.DataColumn(ft.Text("")),  # modification (crayon)
            ],
        )

        self.table_container = ft.ListView(controls=[self.data_table], expand=True, spacing=10)

        # Champs du formulaire produit (inchangés)
        self.p_name = ft.TextField(**input_style, label="Désignation du produit", width=440,
                                   capitalization=ft.TextCapitalization.WORDS)
        self.p_category = ft.Dropdown(**drop_style, label="Catégorie", width=440, options=[])
        self.p_price = ft.TextField(**input_style, label="Prix", width=170, input_filter=ft.NumbersOnlyInputFilter(),
                                    text_align=ft.TextAlign.RIGHT)
        self.p_price_buy = ft.TextField(**input_style, label="Prix achat", width=170,
                                        input_filter=ft.NumbersOnlyInputFilter(), text_align=ft.TextAlign.RIGHT)
        self.p_stock = ft.TextField(**input_style, label="Stock Initial", width=170, value="0",
                                    input_filter=ft.NumbersOnlyInputFilter(), text_align=ft.TextAlign.RIGHT,
                                    disabled=True)
        self.p_image_name = ft.TextField(**input_style, label="Image sélectionnée", width=300, read_only=True,
                                         hint_text="Aucune image choisie (Image par défaut)")

        # File pickers
        self.excel_picker = ft.FilePicker(on_result=self.on_excel_file_picked)
        self.image_picker = ft.FilePicker(on_result=self.on_image_file_picked)
        self.cp.page.overlay.extend([self.excel_picker, self.image_picker])

        has_admin_rights = self.user_role in ["admin", "manager"]

        self.content = ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Column([ft.Text("Gestion du Catalogue Produits", size=26, font_family="PEB")], spacing=4),
                        ft.Row([self.loader], spacing=15, vertical_alignment=ft.CrossAxisAlignment.CENTER)
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                ft.Divider(height=15, color=ft.Colors.TRANSPARENT),
                self.build_stats_row(),
                ft.Divider(height=15, color=ft.Colors.TRANSPARENT),
                ft.Container(
                    **stat_style, expand=True,
                    content=ft.Column(
                        expand=True,
                        controls=[
                            ft.Row(
                                controls=[
                                    self.search_field,
                                    ft.Row(
                                        controls=[
                                            # Suppression du bouton Transférer Stock
                                            MyButton(
                                                "Ajouter un produit", resource_path("assets/icons/white/user-plus.svg"),
                                                     click=self.open_add_product_container
                                            ),
                                            MyButton("Importer via excel", resource_path("assets/icons/white/sheet.svg"),
                                                     click=lambda e: self.excel_picker.pick_files(
                                                         allowed_extensions=["xlsx", "xls"])),
                                        ],
                                        visible=has_admin_rights
                                    )
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            ),
                            ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                            self.table_container
                        ]
                    )
                ),
            ],
            spacing=10
        )
        self.on_mount()

    def build_stats_row(self):
        def create_stat_card(title, text_control, icon):
            return ft.Container(
                **stat_style, width=285,
                content=ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Text(title, size=13, font_family="PPR", color='grey'),
                                ft.Image(resource_path(icon), width=18, height=18),
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                        ),
                        text_control
                    ],
                ),
            )
        return ft.Row([
            create_stat_card("Articles Référencés", self.stat_total_produits, "assets/icons/grey/shopping-cart.svg"),
            create_stat_card("Valeur du Stock", self.stat_valeur_stock, "assets/icons/grey/badge-cent.svg"),
            create_stat_card("Catégories Actives", self.stat_categories, "assets/icons/grey/tag.svg"),
        ], spacing=15, wrap=True)

    @staticmethod
    def run_async_in_thread(coro):
        def runner():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(coro)
            loop.close()
        threading.Thread(target=runner).start()

    def on_mount(self):
        self.run_async_in_thread(self.load_products_data())

    async def load_products_data(self):
        self.loader.visible = True
        self.update()

        try:
            params = {'select': '*', 'tenant_id': f'eq.{self.tenant_id}', 'order': 'designation.asc'}
            response = await supabase_request_async(
                access_token=self.access_token, tenant_id=self.tenant_id,
                table_name="v_produits_avec_tampon", method="GET", params=params
            )
            self.liste_des_produits = response if (response and isinstance(response, list)) else []
        except Exception as ex:
            print(f"Erreur de chargement des produits : {ex}")
            self.liste_des_produits = []

        self.calculate_metrics()
        self.render_products_table(self.liste_des_produits)
        self.loader.visible = False
        self.cp.page.update()

    def calculate_metrics(self):
        total_items = len(self.liste_des_produits)
        valeur_totale = 0
        categories_uniques = set()

        for p in self.liste_des_produits:
            stock = int(p.get("stock_reel", 0))
            prix_vente = float(p.get("price_sell", 0))
            valeur_totale += (stock * prix_vente)
            if p.get("product_type"):
                categories_uniques.add(p.get("product_type"))

        self.p_category.options.clear()
        for category in categories_uniques:
            self.p_category.options.append(ft.dropdown.Option(key=category, text=category))

        self.stat_total_produits.value = str(total_items)
        self.stat_valeur_stock.value = f"{format_milliers_fr(valeur_totale)}"
        self.stat_categories.value = str(len(categories_uniques))

    def render_products_table(self, products_list):
        self.data_table.rows.clear()
        can_edit = self.user_role in ["admin", "manager"]

        for prod in products_list:
            stock_actuel = int(prod.get("stock_reel", 0))
            p_vente = float(prod.get("price_sell", 0))
            valeur = int(stock_actuel * p_vente)
            stock_tampon = int(prod.get("stock_tampon", 0))
            row_color = "red" if stock_actuel <= 0 else "black"

            # Bouton Modifier
            if can_edit:
                edit_btn = ft.Container(
                    content=ft.Image(resource_path("assets/icons/grey/pen.svg"), width=18, height=18),
                    on_click=lambda e, p=prod: self.open_edit_product_container(p),
                    data=prod
                )
                transfer_btn = ft.Container(
                    content=ft.Image(resource_path("assets/icons/grey/folder-sync.svg"), width=18, height=18),
                    on_click=lambda e, p=prod: self.open_transfer_modal(p),
                    data=prod, tooltip="Transférer du stock tampon vers boutique",
                )
            else:
                edit_btn = ft.Text("")
                transfer_btn = ft.Text("")
            # Bouton Transférer (visible pour admin/manager)


            row_item = ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(prod.get("designation", "Sans désignation"))),
                    ft.DataCell(ft.Text(prod.get("product_type", "Général"))),
                    ft.DataCell(ft.Text(f"{format_milliers_fr(p_vente)}")),
                    ft.DataCell(ft.Text(f"{format_milliers_fr(stock_actuel)}", color=row_color)),
                    ft.DataCell(ft.Text(f"{format_milliers_fr(stock_tampon)}", color=row_color)),
                    ft.DataCell(ft.Text(f"{format_milliers_fr(valeur)}", color=row_color)),
                    ft.DataCell(
                        ft.Row(
                            controls=[
                                edit_btn, transfer_btn
                            ]
                        )
                    ),
                ]
            )
            self.data_table.rows.append(row_item)
        self.cp.page.update()

    # --- Transfert individuel ---
    def open_transfer_modal(self, product_data):
        """Ouvre un modal pour transférer une quantité du tampon vers la boutique"""
        product_id = product_data.get("produit_id")
        designation = product_data.get("designation", "")
        stock_boutique = int(product_data.get("stock_reel", 0))
        stock_tampon = int(product_data.get("stock_tampon", 0))

        # Champs du modal
        name_text = ft.Text(f"Produit : {designation}", size=18, font_family="PEB")
        stock_info = ft.Text(f"Stock boutique : {stock_boutique}  |  Stock tampon : {stock_tampon}", size=16, font_family="PPM")
        qty_field = ft.TextField(
            **input_style,
            label="Quantité à transférer",
            width=200,
            value="1",
            input_filter=ft.NumbersOnlyInputFilter(),
            text_align=ft.TextAlign.RIGHT,
        )

        # Bouton Valider
        def on_validate(e):
            try:
                qty = int(qty_field.value)
                if qty <= 0:
                    self.cp.show_alert("La quantité doit être positive.", ft.Icons.WARNING, ft.Colors.ORANGE)
                    return
                if qty > stock_tampon:
                    self.cp.show_alert(f"Quantité demandée ({qty}) dépasse le stock tampon ({stock_tampon}).", ft.Icons.ERROR, ft.Colors.RED)
                    return
                # Fermer le modal
                self.cp.hide_container(self.cp.st_container)
                # Lancer le transfert
                self.run_async_in_thread(self.execute_transfer(product_id, qty))
            except ValueError:
                self.cp.show_alert("Veuillez entrer un nombre valide.", ft.Icons.WARNING, ft.Colors.ORANGE)

        # Construction du modal
        self.cp.st_container.content.height = 320
        self.cp.st_container.content.width = 400
        self.cp.st_form.content = ft.Column(
            controls=[
                ft.Row([
                    ft.Text("Transfert de stock", size=22, font_family="PEB"),
                    ft.Container(
                        content=ft.Image(
                            resource_path('assets/icons/black/x.svg'), width=18, height=18
                        ),
                        on_click=lambda _: self.cp.hide_container(self.cp.st_container)
                    ),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(height=10, thickness=1),
                name_text,
                stock_info,
                ft.Divider(height=10, color="transparent"),
                qty_field,
                ft.Row([
                    MyButton("Valider le transfert", resource_path("assets/icons/white/check.svg"), on_validate)
                ], alignment=ft.MainAxisAlignment.END)
            ],
            spacing=15,
        )
        self.cp.show_container(self.cp.st_container)
        self.cp.page.update()

    async def execute_transfer(self, product_id: str, qty: int):
        """Effectue la mise à jour des stocks en base"""
        if not product_id:
            self.cp.show_alert("Identifiant produit manquant.", ft.Icons.ERROR, ft.Colors.RED)
            return

        self.loader.visible = True
        self.cp.page.update()

        try:
            # Récupérer les stocks actuels via la vue
            params = {'select': '*', 'produit_id': f'eq.{product_id}'}
            result = await supabase_request_async(
                access_token=self.access_token,
                tenant_id=self.tenant_id,
                table_name="v_produits_avec_tampon",
                method="GET",
                params=params
            )
            if not result or len(result) == 0:
                self.cp.show_alert("Produit introuvable.", ft.Icons.ERROR, ft.Colors.RED)
                return

            data = result[0]
            print(data, type(data))
            # Récupération sécurisée des stocks (convertir None en 0)
            stock_boutique = int(data.get("stock_reel") or 0)
            stock_tampon = int(data.get("stock_tampon") or 0)
            print("stock réel", stock_boutique)
            print('st tampon', stock_tampon)

            # Validation
            if qty <= 0:
                self.cp.show_alert("La quantité doit être positive.", ft.Icons.WARNING, ft.Colors.ORANGE)
                return
            if qty > stock_tampon:
                self.cp.show_alert(f"Stock tampon insuffisant. Disponible : {stock_tampon}.", ft.Icons.ERROR, ft.Colors.RED)
                return

            # 3. Calcul des nouveaux stocks
            new_stock_boutique = stock_boutique + qty
            new_stock_tampon = stock_tampon - qty

            # 4. Mise à jour de la table products (stock boutique)
            update_payload = {"stock": new_stock_boutique}

            await supabase_request_async(
                access_token=self.access_token,
                tenant_id=self.tenant_id,
                table_name="products",
                method="PATCH",
                params={"id": f"eq.{int(product_id)}"},  # Uniquement le filtre ici
                data=update_payload                 # Le payload va dans le corps JSON (adapte le nom de l'argument si nécessaire, ex: payload=...)
            )
            
            new_stock_tampon = stock_tampon - qty

            # 5. Mise à jour de la table stock_tampons (stock tampon)
            update_payload_tampon = {"stock": new_stock_tampon}
            await supabase_request_async(
                access_token=self.access_token,
                tenant_id=self.tenant_id,
                table_name="stock_tampons",
                method="PATCH",
                params={"id": f"eq.{int(product_id)}"},  # Uniquement le filtre ici
                data=update_payload_tampon               # Le payload va dans le corps JSON (adapte le nom de l'argument si nécessaire, ex: payload=...)
            )

            # 6. Recharger l'affichage
            await self.load_products_data()
            self.cp.show_alert(
                f"Transfert de {qty} unité(s) effectué avec succès !", 
                ft.Icons.CHECK_CIRCLE, 
                ft.Colors.GREEN
            )

            # Recharger la liste des produits
            await self.load_products_data()
            self.cp.show_alert(f"Transfert de {qty} unité(s) effectué avec succès !", ft.Icons.CHECK_CIRCLE, ft.Colors.GREEN)

        except Exception as ex:
            print(f"Erreur lors du transfert : {ex}")
            self.cp.show_alert("Erreur lors du transfert en base.", ft.Icons.ERROR, ft.Colors.RED)
        finally:
            self.loader.visible = False
            self.cp.page.update()
            
    # --- Filtre de recherche ---
    def filter_products_locally(self, e):
        query = self.search_field.value.lower().strip()
        if not query:
            self.render_products_table(self.liste_des_produits)
            return
        filtered = [
            p for p in self.liste_des_produits
            if query in p.get("designation", "").lower() or query in p.get("product_type", "").lower()
        ]
        self.render_products_table(filtered)

    # --- Gestion des images ---
    def on_image_file_picked(self, e: ft.FilePickerResultEvent):
        if e.files and len(e.files) > 0:
            self.selected_image_path = e.files[0].path
            self.p_image_name.value = os.path.basename(self.selected_image_path)
            self.p_image_name.update()

    # --- Ajout de produit ---
    def open_add_product_container(self, e):
        self.p_name.value = ""
        self.p_name.disabled = False
        self.p_category.value = "Général"
        self.p_price.value = ""
        self.p_stock.value = "0"
        self.p_image_name.value = ""
        self.selected_image_path = None

        self.cp.st_container.content.height = 500
        self.cp.st_container.content.width = 500

        self.cp.st_form.content = ft.Column(
            controls=[
                ft.Row([
                    ft.Text("Nouveau Produit", size=22, font_family="PEB"),
                    ft.Container(
                        content=ft.Image(resource_path('assets/icons/black/x.svg'), width=18, height=18),
                        on_click=lambda e: self.cp.hide_container(self.cp.st_container)
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(height=5, color="grey200"),
                ft.Divider(height=10, color="transparent"),
                ft.Column(
                    spacing=10, scroll=ft.ScrollMode.ADAPTIVE,
                    controls=[
                        self.p_name, self.p_category, self.p_price, self.p_price_buy, self.p_stock,
                        ft.Row([
                            self.p_image_name,
                            ft.IconButton(
                                icon=ft.Icons.IMAGE_SEARCH_ROUNDED, icon_color=MAIN_COLOR, tooltip="Choisir une image",
                                on_click=lambda _: self.image_picker.pick_files(
                                    allowed_extensions=["png", "jpg", "jpeg"])
                            )
                        ], alignment=ft.MainAxisAlignment.START),
                        ft.Divider(height=15, color="transparent"),
                        ft.Row([
                            MyButton("Enregistrer l'article", resource_path("assets/icons/white/user-check.svg"),
                                     click=lambda e: self.run_async_in_thread(self.save_new_product(e)))
                        ], alignment=ft.MainAxisAlignment.END)
                    ]
                )
            ]
        )
        self.cp.show_container(self.cp.st_container)
        self.cp.update()

    async def save_new_product(self, e):
        if not self.p_name.value or not self.p_price.value:
            self.cp.show_alert("Veuillez remplir les champs obligatoires !", ft.Icons.ERROR_OUTLINED, ft.Colors.RED)
            return

        self.loader.visible = True
        self.cp.page.update()
        final_image_url = DEFAULT_IMAGE

        if self.selected_image_path and os.path.exists(self.selected_image_path):
            try:
                file_extension = os.path.splitext(self.selected_image_path)[1]
                unique_filename = f"{self.tenant_id}/{uuid.uuid4()}{file_extension}"
                with open(self.selected_image_path, "rb") as image_file:
                    file_bytes = image_file.read()

                supabase_client.storage.from_("image_produits").upload(path=unique_filename, file=file_bytes,
                                                                       file_options={
                                                                           "content-type": f"image/{file_extension.replace('.', '')}"})
                final_image_url = supabase_client.storage.from_("image_produits").get_public_url(unique_filename)
            except Exception as upload_error:
                print(f"Erreur lors du téléversement de l'image : {upload_error}")
                final_image_url = DEFAULT_IMAGE

        payload = {
            "tenant_id": self.tenant_id,
            "designation": self.p_name.value.strip(),
            "product_type": self.p_category.value,
            "price": float(self.p_price.value),
            "price_buy": float(self.p_price_buy.value) if self.p_price_buy.value else 0.0,
            "stock": int(self.p_stock.value or 0),
            "image": final_image_url
        }

        try:
            await supabase_request_async(
                access_token=self.access_token,
                tenant_id=self.tenant_id,
                table_name="products",
                method="POST",
                data=payload
            )
            await supabase_request_async(
                access_token=self.access_token,
                tenant_id=self.tenant_id,
                table_name="stock_tampons",
                method="POST",
                data=payload
            )
            self.cp.hide_container(self.cp.st_container)
            await self.load_products_data()
            self.cp.show_alert("Produit enregistré avec succès !", ft.Icons.CHECK_CIRCLE, ft.Colors.GREEN)
        except Exception as ex:
            print(f"Erreur d'insertion du produit : {ex}")
            self.cp.show_alert("Erreur lors de l'enregistrement en BDD.", ft.Icons.ERROR, ft.Colors.RED)

        self.loader.visible = False
        self.cp.page.update()

    # --- Modification de produit ---
    def open_edit_product_container(self, product_data):
        self.p_name.value = product_data.get("designation", "")
        self.p_name.disabled = False

        self.cp.st_container.content.height = 300
        self.cp.st_form.content = ft.Column(
            controls=[
                ft.Row([
                    ft.Text("Modifier le Produit", size=22, font_family="PEB"),
                    ft.IconButton(icon=ft.Icons.CLOSE_ROUNDED,
                                  on_click=lambda _: self.cp.hide_container(self.cp.st_container))
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(height=5, color="grey200"),
                ft.Divider(height=10, color="transparent"),
                ft.Text("Seul le nom de l'article est modifiable après création.", size=12, color="grey"),
                self.p_name,
                ft.Divider(height=15, color="transparent"),
                ft.Row([
                    MyButton("Enregistrer les modifications", resource_path("assets/icons/white/user-check.svg"),
                             click=lambda e, p_id=product_data.get("id"): self.run_async_in_thread(
                                 self.save_edited_product(p_id)))
                ], alignment=ft.MainAxisAlignment.END)
            ],
            spacing=10, scroll=ft.ScrollMode.ADAPTIVE
        )
        self.cp.show_container(self.cp.st_container)
        self.cp.update()

    async def save_edited_product(self, product_id):
        if not self.p_name.value:
            self.cp.show_alert("La désignation ne peut pas être vide !", ft.Icons.ERROR_OUTLINED, ft.Colors.RED)
            return

        self.loader.visible = True
        self.cp.page.update()
        update_payload = {"designation": self.p_name.value.strip()}

        try:
            await supabase_request_async(
                access_token=self.access_token,
                tenant_id=self.tenant_id,
                table_name="products", method="PATCH",
                params={"id": f"eq.{product_id}", **update_payload}
            )
            await supabase_request_async(
                access_token=self.access_token,
                tenant_id=self.tenant_id,
                table_name="stock_tampons",
                method="PATCH",
                params={"id": f"eq.{product_id}", **update_payload}
            )

            self.cp.hide_container(self.cp.st_container)
            await self.load_products_data()
            self.cp.show_alert("Produit mis à jour avec succès !", ft.Icons.CHECK_CIRCLE, ft.Colors.GREEN)
        except Exception as ex:
            print(f"Erreur de modification produit : {ex}")
            self.cp.show_alert("Erreur lors de la modification.", ft.Icons.ERROR, ft.Colors.RED)

        self.loader.visible = False
        self.cp.page.update()

    # --- Import Excel ---
    def on_excel_file_picked(self, e: ft.FilePickerResultEvent):
        if not e.files:
            return
        self.run_async_in_thread(self.process_excel_import(e.files[0].path))

    async def process_excel_import(self, filepath):
        self.loader.visible = True
        self.cp.page.update()

        try:
            import openpyxl
            wb = openpyxl.load_workbook(filepath, data_only=True)
            sheet = wb.active
            success_count = 0

            for row in sheet.iter_rows(min_row=2, values_only=True):
                if not row or row[0] is None:
                    continue

                payload = {
                    "tenant_id": self.tenant_id,
                    "designation": str(row[0]).strip(),
                    "product_type": str(row[1]).strip() if row[1] else "Général",
                    "price_buy": float(row[2]) if row[2] is not None else 0.0,
                    "price": float(row[3]) if row[3] is not None else 0.0,
                    "stock": int(row[4]) if row[4] is not None else 0,
                    "image": DEFAULT_IMAGE
                }

                await supabase_request_async(
                    access_token=self.access_token,
                    tenant_id=self.tenant_id,
                    table_name="products",
                    method="POST",
                    data=payload
                )
                await supabase_request_async(
                    access_token=self.access_token,
                    tenant_id=self.tenant_id,
                    table_name="stock_tampons",
                    method="POST",
                    data=payload
                )
                success_count += 1

            await self.load_products_data()
            self.cp.show_alert(f"Importation réussie : {success_count} produits intégrés !", ft.Icons.CHECK_CIRCLE,
                               ft.Colors.GREEN)
        except Exception as ex:
            print(f"Erreur d'importation Excel : {ex}")
            self.cp.show_alert("Fichier Excel invalide ou corrompu.", ft.Icons.ERROR, ft.Colors.RED)

        self.loader.visible = False
        self.cp.page.update()
        