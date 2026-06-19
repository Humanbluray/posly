import flet as ft
from styles import drop_style, config_tf_style, login_style, switch_style, stat_style
from components.components import CardItem, StyledButton, FilterItem, MyButton
from utils import ACCESS_TOKEN, USER_ID, TENANT_ID, USER_NAME, ROLE, MAIN_COLOR, format_milliers_fr, resource_path, \
    BG_COLOR
import asyncio, threading, time, datetime, os, webbrowser
from services.async_function import supabase_request_async
from services.supabase_client import supabase_client, supabase_admin
from io import BytesIO
from reportlab.lib.pagesizes import mm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import requests


class Sales(ft.Container):
    def __init__(self, cp: object):
        super().__init__(expand=True)
        self.cp = cp

        # paramètres généraux
        self.access_token = self.cp.page.client_storage.get(ACCESS_TOKEN)
        self.role = self.cp.page.client_storage.get(ROLE)
        self.user_id = self.cp.page.client_storage.get(USER_ID)
        self.tenant_id = self.cp.page.client_storage.get(TENANT_ID)
        self.user_name = self.cp.page.client_storage.get(USER_NAME)

        self.filtered_list: list = []
        self.valeur_du_filtre: str = ""
        self.search_field = ft.TextField(
            **login_style, width=250, prefix_icon=ft.Icons.SEARCH, label="Chercher",
            on_change=self.filter_data_by_typing
        )
        # ___________________Main window____________________________________________
        self.grid = ft.GridView(
            expand=True,
            child_aspect_ratio=0.78,  # Ajusté de 1.0 à 0.78 pour donner de la hauteur à la carte
            spacing=15,
            run_spacing=15,
            max_extent=220,
        )
        self.nb_products = ft.Text("", size=14, font_family="PPM", color="white")
        self.row_filter_categories = ft.Row(
            controls=[], alignment=ft.MainAxisAlignment.START, spacing=10,
            scroll=ft.ScrollMode.AUTO, height=40
        )
        self.row_filter_categories.controls.append(
            FilterItem(self, "Tous", True, self.row_filter_categories.controls)
        )
        self.progress_container = ft.Container(
            expand=True, alignment=ft.alignment.center,
            content=ft.ProgressRing(color=MAIN_COLOR, width=50, height=50),
        )
        # À insérer dans ton __init__ avant la définition de self.left_container :
        self.empty_message = ft.Container(
            visible=False,
            alignment=ft.alignment.center,
            content=ft.Column(
                controls=[
                    ft.Icon(ft.Icons.SHOPPING_BAG_OUTLINED, size=48, color="grey"),
                    ft.Text("Aucun produit pour le moment", size=16, font_family="PPM", color="grey"),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER
            )
        )
        self.left_container = ft.Container(
            bgcolor=BG_COLOR, border_radius=16, padding=10,
            expand=True,
            content=ft.Column(
                expand=True,
                controls=[
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Row(
                                    controls=[
                                        ft.Row(
                                            controls=[
                                                ft.Text("Produits", size=22, font_family="PEB"),
                                                ft.Container(
                                                    padding=3, border_radius=6, width=50,
                                                    bgcolor="black", alignment=ft.alignment.center,
                                                    content=self.nb_products
                                                ),
                                            ]
                                        ),
                                        self.search_field
                                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                ),
                                self.row_filter_categories,
                            ]
                        ),
                        **stat_style
                    ),
                    ft.Divider(height=1, color=ft.Colors.TRANSPARENT),
                    ft.Stack(
                        alignment=ft.alignment.center, expand=True,
                        controls=[self.grid, self.progress_container, self.empty_message]
                    )
                ]
            )
        )

        self.basket = ft.ListView(expand=True, divider_thickness=1, spacing=15)
        self.basket_copy = ft.ListView(expand=True, divider_thickness=1, spacing=15)
        self.amount = ft.Text("0", size=16, font_family="PEB")
        self.amount_copy = ft.Text("0", size=16, font_family="PEB")
        self.payment_mode = ft.RadioGroup(
            on_change=self.changing_payment, value="Cash",
            content=ft.Row(
                controls=[
                    ft.Radio(
                        label=item['label'], value=item['value'],
                        label_style=ft.TextStyle(size=14, font_family="PPM"),
                        active_color=MAIN_COLOR
                    )
                    for item in [
                        {"value": "OM", "label": "OM"},
                        {"value": "MOMO", "label": "MOMO"},
                        {"value": "Cash", "label": "CASH"},
                    ]
                ]
            )
        )
        self.due = ft.Text("0", size=16, font_family="PEB")
        self.espece = ft.TextField(
            value='0',
            width=150, border_radius=10, bgcolor="#f0f0f6", focused_bgcolor="#f0f0f6",
            border_color="#f0f0f6", content_padding=12, cursor_height=24, dense=True,
            border=ft.InputBorder.UNDERLINE, text_align=ft.TextAlign.RIGHT,
            text_style=ft.TextStyle(size=16, font_family="PPM"), input_filter=ft.NumbersOnlyInputFilter(),
            focused_border_width=2, focused_border_color=MAIN_COLOR,
            on_blur=self.on_blur_espece
        )
        self.switch_table = ft.Switch(
            **switch_style, scale=0.8, on_change=self.on_switch_change
        )
        self.table_number = ft.TextField(
            **config_tf_style, width=50, input_filter=ft.NumbersOnlyInputFilter(),
            text_align=ft.TextAlign.RIGHT, disabled=True, value="1"
        )
        self.right_container = ft.Container(
            **stat_style, width=300,
            content=ft.Column(
                controls=[
                    ft.Column(
                        expand=True,
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Row(
                                        controls=[
                                            ft.Image(src="assets/icons/grey/shopping-cart.svg", width=24, height=24),
                                            ft.Text("Panier", size=22, font_family="PEB"),
                                        ]
                                    ),
                                    ft.Text(
                                        str(datetime.date.today()), size=14, font_family='PPM',
                                        color="grey",
                                    )
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            ),
                            ft.Divider(height=1, thickness=1),
                            self.basket,
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER
                    ),
                    ft.Column(
                        controls=[
                            # ft.Divider(height=1, thickness=1),
                            ft.Row(
                                controls=[
                                    ft.Text("Total", size=16, font_family="PPM", color="grey"),
                                    ft.Row(
                                        controls=[
                                            self.amount, ft.Text("FCFA", size=16, font_family="PEB")
                                        ], spacing=10
                                    )
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            ),
                            # ft.Divider(height=1, thickness=1),
                            # ft.Row(
                            #     controls=[
                            #         ft.Text("Mode", size=16, font_family="PPM", color="grey"),
                            #         self.payment_mode
                            #     ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            # ),
                            # ft.Divider(height=1, thickness=1),
                            # ft.Row(
                            #     controls=[
                            #         ft.Text("Encaissé", size=16, font_family="PPM", color="grey"),
                            #         self.espece
                            #     ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            # ),
                            # ft.Divider(height=1, thickness=1),
                            # ft.Row(
                            #     controls=[
                            #         ft.Text("Rendu", size=16, font_family="PPM", color="grey"),
                            #         self.due
                            #     ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            # ),
                            StyledButton(
                                "Annuler commande", "close", self.annuler_commande
                            ),
                            MyButton(
                                "Valider Achat",
                                resource_path("assets/icons/white/check.svg"),
                                self.open_valid_basket_container
                            )
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER
                    )
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            )
        )

        self.content = ft.Container(
            expand=True,
            content=ft.Row(
                expand=True,
                controls=[
                    self.left_container,
                    ft.VerticalDivider(width=1, color=ft.Colors.TRANSPARENT),
                    self.right_container,
                ], spacing=10
            )
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
        await self.load_categories()
        await self.load_datas()

    async def load_categories(self):
        """Charge les catégories de produits"""
        params = {
            'select': "product_type",
            'order': 'product_type.asc'
        }

        categories = await supabase_request_async(
            access_token=self.access_token,
            tenant_id=self.tenant_id,
            table_name="products",
            method="GET",
            params=params
        )

        categories_uniques = set(list({cat['product_type'] for cat in categories}))
        print("categories uniques", categories_uniques)

        for category in categories_uniques:
            self.row_filter_categories.controls.append(
                FilterItem(self, category, False, self.row_filter_categories.controls))

        self.cp.page.update()

    async def load_datas(self):
        self.progress_container.visible = True
        self.empty_message.visible = False  # Réinitialiser à chaque rechargement
        self.grid.controls.clear()
        self.cp.page.update()

        print("Entree dans le BUILD GRID ASYNC")
        self.filtered_list = []

        params = {
            'select': "*",
        }

        try:
            produits = await supabase_request_async(
                access_token=self.access_token,
                tenant_id=self.tenant_id,
                table_name="products",
                method="GET",
                params=params
            )
        except Exception as e:
            print(f"Erreur lors de la récupération des produits : {e}")
            produits = []

        # Masquer le chargement dès que la réponse Supabase arrive
        self.progress_container.visible = False

        # Si le tenant n'a aucun produit dans sa base
        if not produits:
            self.nb_products.value = "0"
            self.empty_message.visible = True
            self.cp.page.update()
            return  # On arrête la méthode ici proprement

        print("produits récupérés :", len(produits))
        valeur_du_filtre = ""

        for item in self.row_filter_categories.controls:
            if getattr(item, 'selected', False):
                valeur_du_filtre = item.title
                break

        self.valeur_du_filtre = valeur_du_filtre
        print("valeur du filtre actif :", valeur_du_filtre)

        # Filtrage par catégorie
        if valeur_du_filtre == "Tous":
            filtered_list = produits
        else:
            filtered_list = list(filter(lambda p: self.valeur_du_filtre == p['product_type'], produits))

        self.filtered_list = filtered_list
        self.nb_products.value = str(len(self.filtered_list))

        # Si le filtre actif (ex: une catégorie spécifique) ne retourne rien
        if not self.filtered_list:
            self.empty_message.visible = True
            self.cp.page.update()
            return

        # CHARGEMENT PAR LOTS (Optimisation UI pour l'affichage des cartes)
        batch_size = 20
        for i in range(0, len(filtered_list), batch_size):
            batch = self.filtered_list[i: i + batch_size]
            for product in batch:
                self.grid.controls.append(CardItem(self, product, self.basket))

            # Mise à jour progressive pour le confort visuel de l'utilisateur
            self.cp.page.update()
            await asyncio.sleep(0.05)

        # Rafraîchissement final de sécurité
        self.cp.page.update()

    def filter_data_by_typing(self, e):
        # 1. On récupère la valeur en minuscule pour la comparaison
        val_cherchee = self.search_field.value.lower().strip() if self.search_field.value else ""

        self.grid.controls.clear()

        # 2. Filtrage logique
        # On filtre la liste originale (self.all_products) ou une liste maîtresse
        # plutôt que de filtrer sur filtered_list déjà réduite

        def match_criteria(p):
            # Vérifie si le nom contient la recherche
            name_match = val_cherchee in p.get('designation', '').lower()

            # Vérifie si c'est la catégorie active (ou "Tous")
            category_match = (self.valeur_du_filtre == "Tous") or (self.valeur_du_filtre == p.get('product_type'))

            return name_match and category_match

        filtered_list = list(filter(match_criteria, self.filtered_list))  # Utilise self.all_products ici !

        # Si le tenant n'a aucun produit dans sa base
        if not filtered_list:
            self.nb_products.value = "0"
            self.empty_message.visible = True
            self.cp.page.update()
            return  # On arrête la méthode ici proprement

        self.nb_products.value = str(len(filtered_list))

        # 3. Affichage
        batch_size = 20
        for i in range(0, len(filtered_list), batch_size):
            batch = filtered_list[i: i + batch_size]
            for product in batch:
                self.grid.controls.append(CardItem(self, product, self.basket))
            self.cp.page.update()
            time.sleep(0.05)

        self.cp.page.update()  # Rafraîchissement final

    def changing_payment(self, e):
        if self.payment_mode.value == "Cash":
            self.espece.disabled = False
            self.espece.value = 0
        else:
            self.espece.disabled = True
            self.espece.value = self.amount.value

        self.cp.page.update()

    def on_blur_espece(self, e):
        self.due.value = int(self.espece.value) - int(self.amount.value)
        self.cp.page.update()

    def open_valid_basket_container(self, e):
        # on vide les précédents élements...
        self.cp.valid_basket_form.content = None
        self.basket_copy.controls.clear()

        self.amount_copy.value = self.amount.value

        for item in self.basket.controls:
            d = item.datas_item
            self.basket_copy.controls.append(
                ft.ListTile(
                    title=ft.Text(d['designation'], size=14, font_family="PPB"),
                    subtitle=ft.Text(f"{d['qty']} x {d['price']}", size=13, font_family="PPM", color="grey"),
                    trailing=ft.Text(f"{d['qty'] * d['price']}", size=14, font_family="PPM"),
                )
            )

        self.cp.valid_basket_form.content = content = ft.Column(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN, expand=True,
            controls=[
                ft.Column(
                    expand=True,
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Row(
                                    controls=[
                                        ft.Image(src="assets/icons/grey/badge-cent.svg", width=24, height=24),
                                        ft.Text("Valider achat", size=22, font_family="PEB"),
                                    ]
                                ),
                                ft.Container(
                                    content=ft.Image(
                                        src=resource_path("assets/icons/black/x.svg"),
                                        width=24, height=24
                                    ),
                                    on_click=lambda e: self.cp.hide_container(self.cp.valid_basket_container)
                                )
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                        ),
                        self.basket_copy,
                    ]
                ),
                ft.Column(
                    controls=[
                        ft.Divider(height=1, thickness=1),
                        ft.Row(
                            controls=[
                                ft.Row(
                                    controls=[
                                        ft.Text("Activer table", size=16, font_family="PPM"),
                                        self.switch_table
                                    ]
                                ),
                                self.table_number
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                        ),
                        ft.Row(
                            controls=[
                                ft.Text("Total", size=16, font_family="PPM", color="grey"),
                                ft.Row(
                                    controls=[
                                        self.amount_copy, ft.Text("FCFA", size=16, font_family="PEB")
                                    ], spacing=10
                                )
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                        ),
                        ft.Divider(height=1, thickness=1),
                        ft.Row(
                            controls=[
                                ft.Text("Mode", size=16, font_family="PPM", color="grey"),
                                self.payment_mode
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                        ),
                        ft.Divider(height=1, thickness=1),
                        ft.Row(
                            controls=[
                                ft.Text("Encaissé", size=16, font_family="PPM", color="grey"),
                                self.espece
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                        ),
                        ft.Divider(height=1, thickness=1),
                        ft.Row(
                            controls=[
                                ft.Text("Rendu", size=16, font_family="PPM", color="grey"),
                                self.due
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        MyButton(
                            title="Valider achat", icon=resource_path(''),
                            click=self.valider_panier
                        ),
                        StyledButton(
                            "Abandonner", ft.Icons.CHECK, self.annuler_commande
                        ),

                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER
                )
            ]
        )
        self.cp.show_container(self.cp.valid_basket_container)
        self.cp.page.update()

    def on_switch_change(self, e):
        if self.switch_table.value:
            self.table_number.disabled = False
        else:
            self.table_number.disabled = True

    def annuler_commande(self, e):
        if self.cp.valid_basket_container.visible:
            self.cp.hide_container(self.cp.valid_basket_container)

        self.basket_copy.controls.clear()
        self.basket.controls.clear()
        self.due.value = "0"
        self.amount.value = "0"
        self.espece.value = '0'
        self.switch_table.value = False
        self.table_number.disabled = True
        self.cp.page.update()

    async def valider_panier(self, e):
        # 1. Vérifications de sécurité de caisse
        if not self.basket.controls or int(self.espece.value) < int(self.amount.value):
            return

        # 2. Récupération préalable des configurations de la boutique (tenant)
        tenant_infos = {}
        try:
            reponse = supabase_client.table("tenants") \
                .select("nom_entreprise, slogan, logo_url, contact, adresse") \
                .eq("id", self.tenant_id) \
                .execute()

            if reponse.data and len(reponse.data) > 0:
                tenant_infos = reponse.data[0]

        except Exception as e_tenant:
            print(f"Avis: Échec de la récupération synchrone des détails du tenant ({e_tenant})")

        # 3. Préparation des données d'articles
        datas_details = []

        for item in self.basket.controls:
            d = item.datas_item
            quantite = int(d['qty'])
            prix_unitaire = float(d['price'])
            # CORRECTION : Calcul strict du total de la ligne pour le ticket
            total_ligne = quantite * prix_unitaire

            datas_details.append({
                "id": int(d["id"]),
                "designation": d.get('designation', 'Produit'),
                "qte": quantite,
                "prix": prix_unitaire,
                "total": total_ligne,  # AJOUTÉ : Requis pour éviter le "0 FCFA"
                "new_stock": int(d['stock']) - quantite,
                "product_type": d.get('product_type', '')
            })

        # Sauvegarde des variables UI pour la génération post-requête
        total_facture = float(self.amount.value)
        mode_reglement = self.payment_mode.value
        argent_encaisse = float(self.espece.value)
        argent_rendu = float(self.due.value)

        # 4. Appel du RPC unique de validation de transaction
        try:
            facture_id_brut = await supabase_request_async(
                access_token=self.access_token,
                tenant_id=self.tenant_id,
                table_name="valider_panier_rpc",
                method="POST",
                data={
                    "p_username": self.user_name,
                    "p_amount": total_facture,
                    "p_mode": mode_reglement,
                    "p_items": datas_details
                }
            )

            if isinstance(facture_id_brut, dict) and "error" in facture_id_brut:
                raise Exception(facture_id_brut["error"])

            facture_reference = str(facture_id_brut)

            # 5. Extraction du ticket de caisse physique 80mm & Ouverture (avec await)
            url_ticket = await self.generer_ticket_de_caisse(
                facture_id=facture_reference,
                items=datas_details,
                total=total_facture,
                mode_paiement=mode_reglement,
                encaisse=argent_encaisse,
                rendu=argent_rendu,
                tenant_infos=tenant_infos
            )

            if url_ticket:
                self.ouvrir_et_imprimer_ticket(url_ticket)

            # 6. Réinitialisation complète de l'interface utilisateur (Reset UI)
            self.basket.controls.clear()
            self.cp.hide_container(self.cp.valid_basket_container)
            self.basket_copy.controls.clear()

            self.search_field.value = ""
            self.due.value = "0"
            self.amount.value = "0"
            self.espece.value = '0'
            self.switch_table.value = False
            self.table_number.disabled = True

            self.cp.show_alert(
                "Achat validé & Ticket imprimé", ft.Icons.CHECK_CIRCLE, ft.Colors.LIGHT_GREEN_400
            )

            self.run_async_in_thread(self.load_datas())

        except Exception as err:
            print(f"Erreur fatale lors de la validation : {err}")
            self.cp.show_alert(f"Erreur de validation : {err}", ft.Icons.ERROR_OUTLINE, ft.Colors.RED)

    def charger_police_inter(self):
        """Charge la police Inter depuis les fichiers TTF locaux."""
        nom_police = "Inter"
        nom_police_bold = "Inter-Bold"

        if nom_police in pdfmetrics.getRegisteredFontNames():
            return nom_police, nom_police_bold

        try:
            chemin_regular = resource_path("assets/fonts/Inter-Regular.ttf")
            chemin_bold = resource_path("assets/fonts/Inter-Bold.ttf")

            if os.path.exists(chemin_regular) and os.path.exists(chemin_bold):
                pdfmetrics.registerFont(TTFont(nom_police, chemin_regular))
                pdfmetrics.registerFont(TTFont(nom_police_bold, chemin_bold))
                return nom_police, nom_police_bold
            else:
                print("[REPORTLAB] Fichiers TTF introuvables. Repli sur Helvetica.")
                return "Helvetica", "Helvetica-Bold"
        except Exception as e:
            print(f"[REPORTLAB] Erreur fichiers TTF ({e}). Repli sur Helvetica.")
            return "Helvetica", "Helvetica-Bold"

    async def generer_ticket_de_caisse(self, facture_id, **kwargs):
        """
        Génère un ticket de caisse 80mm stable avec une hauteur fixe pour éviter
        les coupures sauvages et les sauts de page sur les imprimantes thermiques.
        """
        font_reg, font_bold = self.charger_police_inter()

        # Récupération des données passées en kwargs
        date_heure = kwargs.get('date_heure', datetime.datetime.now().strftime("%d/%m/%Y %H:%M"))
        self_user_name = kwargs.get('self_user_name', self.user_name if hasattr(self, 'user_name') else "Caissier")
        mode_paiement = kwargs.get('mode_paiement', "Espèces")
        total = kwargs.get('total', 0)
        encaisse = kwargs.get('encaisse', 0)
        rendu = kwargs.get('rendu', 0)
        items = kwargs.get('items', kwargs.get('articles', []))

        tenant_infos = kwargs.get('tenant_infos', {})
        if isinstance(tenant_infos, dict):
            nom_boutique = tenant_infos.get('nom_entreprise', kwargs.get('nom_boutique', 'Ma Boutique'))
            slogan = tenant_infos.get('slogan', kwargs.get('slogan', 'Vos actes parlent pour vous'))
            logo_url = tenant_infos.get('logo_url', kwargs.get('logo_url', None))
            adresse = tenant_infos.get('adresse', kwargs.get('adresse', ''))
            contact = tenant_infos.get('contact', kwargs.get('contact', ''))
        else:
            nom_boutique = getattr(tenant_infos, 'nom_entreprise', kwargs.get('nom_boutique', 'Ma Boutique'))
            slogan = getattr(tenant_infos, 'slogan', kwargs.get('slogan', 'Vos actes parlent pour vous'))
            logo_url = getattr(tenant_infos, 'logo_url', kwargs.get('logo_url', None))
            adresse = getattr(tenant_infos, 'adresse', kwargs.get('adresse', ''))
            contact = getattr(tenant_infos, 'contact', kwargs.get('contact', ''))

        # --- CONFIGURATION IMPRIMANTE THERMIQUE STABLE ---
        largeur_ticket = 80 * mm

        # On définit une hauteur fixe standard et confortable pour un ticket de caisse de supermarché / boutique.
        # Cela évite que le pilote de l'imprimante ne panique avec des tailles de pages exotiques.
        hauteur_ticket = 280 * mm

        chemin_pdf = "ticket_temp.pdf"
        c = canvas.Canvas(chemin_pdf, pagesize=(largeur_ticket, hauteur_ticket))

        # Définition de la CropBox pour guider le pilote d'impression
        c.setCropBox((0, 0, largeur_ticket, hauteur_ticket))

        # Positionnement de départ du curseur (en haut du rouleau)
        y_cursor = hauteur_ticket - 8 * mm
        M_LEFT = 4 * mm
        M_RIGHT = largeur_ticket - 4 * mm
        C_CENTER = largeur_ticket / 2

        # --- SECTION EN-TÊTE & LOGO ---
        if logo_url:
            try:
                response = requests.get(logo_url, timeout=5)
                if response.status_code == 200:
                    img_data = BytesIO(response.content)
                    img = ImageReader(img_data)
                    c.drawImage(img, C_CENTER - (19 * mm), y_cursor - (14 * mm), width=38 * mm, height=14 * mm,
                                preserveAspectRatio=True)
                    y_cursor -= 16 * mm
            except Exception as e:
                print(f"[REPORTLAB] Erreur logo : {e}")

        c.setFont(font_bold, 12)
        c.drawCentredString(C_CENTER, y_cursor, nom_boutique)
        y_cursor -= 5 * mm

        c.setFont(font_reg, 8.5)
        c.setFillColorRGB(0.3, 0.3, 0.3)
        c.drawCentredString(C_CENTER, y_cursor, slogan)
        c.setFillColorRGB(0, 0, 0)
        y_cursor -= 6 * mm

        # --- SECTION INFOS DU TICKET ---
        c.setFont(font_reg, 8.5)
        c.drawString(M_LEFT, y_cursor, f"Ticket N° : {facture_id}")
        y_cursor -= 4 * mm
        c.drawString(M_LEFT, y_cursor, f"Date : {date_heure}")
        y_cursor -= 4 * mm
        c.drawString(M_LEFT, y_cursor, f"Caissier(e) : {self_user_name}")
        y_cursor -= 5 * mm

        # Ligne de séparation
        c.setStrokeColorRGB(0, 0, 0)
        c.setLineWidth(0.5)
        c.setDash(2, 2)
        c.line(M_LEFT, y_cursor, M_RIGHT, y_cursor)
        y_cursor -= 4 * mm

        # --- TABLEAU DES ARTICLES ---
        c.setDash()
        c.setFont(font_bold, 8.5)
        c.drawString(M_LEFT, y_cursor, "Désignation")
        c.drawRightString(M_RIGHT, y_cursor, "Total")
        y_cursor -= 3 * mm

        c.line(M_LEFT, y_cursor, M_RIGHT, y_cursor)
        y_cursor -= 4.5 * mm

        # Parcours des articles
        for art in items:
            c.setFont(font_bold, 8.5)
            texte_art = art.get('designation', 'Article')
            if len(texte_art) > 26:
                texte_art = texte_art[:23] + "..."
            c.drawString(M_LEFT, y_cursor, texte_art)

            c.setFont(font_reg, 8.5)
            total_ligne = f"{int(art.get('total', 0)):,} FCFA"
            c.drawRightString(M_RIGHT, y_cursor, total_ligne)
            y_cursor -= 4 * mm

            c.setFillColorRGB(0.4, 0.4, 0.4)
            calcul_txt = f"{art.get('qte', 1)} x {int(art.get('prix', 0)):,}"
            c.drawString(M_LEFT, y_cursor, calcul_txt)
            c.setFillColorRGB(0, 0, 0)

            y_cursor -= 6 * mm

        # --- SECTION FINANCIÈRE ---
        c.setDash(2, 2)
        c.line(M_LEFT, y_cursor, M_RIGHT, y_cursor)
        y_cursor -= 4.5 * mm
        c.setDash()

        c.setFont(font_bold, 11)
        c.drawString(M_LEFT, y_cursor, "TOTAL FACTURE :")
        c.drawRightString(M_RIGHT, y_cursor, f"{int(total):,} FCFA")
        y_cursor -= 5 * mm

        c.setFont(font_reg, 8.5)
        c.drawString(M_LEFT, y_cursor, "Mode de paiement :")
        c.drawRightString(M_RIGHT, y_cursor, mode_paiement)
        y_cursor -= 4 * mm

        if str(mode_paiement).lower() in ["cash", "espèces", "especes"]:
            c.drawString(M_LEFT, y_cursor, "Montant Encaissé :")
            c.drawRightString(M_RIGHT, y_cursor, f"{int(encaisse):,} FCFA")
            y_cursor -= 4 * mm

            c.drawString(M_LEFT, y_cursor, "Montant Rendu :")
            c.drawRightString(M_RIGHT, y_cursor, f"{int(rendu):,} FCFA")
            y_cursor -= 5 * mm

        # --- FOOTER ---
        c.setDash(2, 2)
        c.line(M_LEFT, y_cursor, M_RIGHT, y_cursor)
        y_cursor -= 4.5 * mm
        c.setDash()

        # 1. Message de confiance
        c.setFont(font_bold, 8.5)
        c.drawCentredString(C_CENTER, y_cursor, "Merci de votre confiance !")
        y_cursor -= 4 * mm

        # 2. Adresse
        if adresse:
            c.setFont(font_reg, 8)
            c.drawCentredString(C_CENTER, y_cursor, f"Adresse : {adresse}")
            y_cursor -= 3.8 * mm

        # 3. Contact
        if contact:
            c.setFont(font_reg, 8)
            c.drawCentredString(C_CENTER, y_cursor, f"Contact : {contact}")
            y_cursor -= 3.8 * mm

        # 4. Message de fin
        c.setFont(font_reg, 7.5)
        c.drawCentredString(C_CENTER, y_cursor, "*** À bientôt ***")
        y_cursor -= 3.8 * mm
        c.drawCentredString(C_CENTER, y_cursor, "")
        y_cursor -= 3.8 * mm
        c.drawCentredString(C_CENTER, y_cursor, "")

        # 5. ESPACE BLANC DE FIN DE TICKET
        # On descend le curseur pour laisser la place physique au massicot sans toucher le texte
        y_cursor -= 14 * mm

        # Sécurité pour s'assurer que ReportLab alloue bien l'espace jusqu'en bas
        c.drawString(M_LEFT, y_cursor, "")

        c.showPage()
        c.save()
        y_cursor -= 15 * mm

        return chemin_pdf

    def ouvrir_et_imprimer_ticket(self, url_publique):
        """Ouvre automatiquement le ticket via son URL Supabase dans le navigateur par défaut."""
        if not url_publique:
            return

        try:
            # Ouvre l'URL directement dans le navigateur internet de la machine
            webbrowser.open(url_publique)
            print(f"Ouverture du ticket dans le navigateur : {url_publique}")
        except Exception as err:
            print(f"Erreur lors de l'ouverture de l'URL du ticket : {str(err)}")


