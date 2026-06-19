import flet as ft
from styles import radio_style, input_style, stat_style
from components.components import StateButton, MyButton, MyTextButton
from utils import (
    ACCESS_TOKEN, TENANT_ID, USER_ID, USER_NAME, TENANT_NAME, EXPIRATION_DATE,
    ROLE, PLAN_CHOISI, resource_path, MAIN_COLOR, USER_EMAIL, SHADOW_COLOR,
    BG_COLOR
)
import asyncio, threading, os, time
from services.async_function import supabase_request_async
from services.supabase_client import supabase_client, supabase_admin
DEFAULT_IMAGE = "https://hojfmjmrhtsvgfzynelr.supabase.co/storage/v1/object/public/profile_pictures/images.png"


class Users(ft.Container):
    def __init__(self, cp: object):
        super().__init__(expand=True, padding=20)
        self.cp = cp

        # Paramètres généraux récupérés via self.cp.page
        self.plan_choisi = self.cp.page.client_storage.get(PLAN_CHOISI)
        self.expiration_date = self.cp.page.client_storage.get(EXPIRATION_DATE)
        self.tenant_name = self.cp.page.client_storage.get(TENANT_NAME)
        self.tenant_id = self.cp.page.client_storage.get(TENANT_ID)
        self.user_id = self.cp.page.client_storage.get(USER_ID)
        self.user_name = self.cp.page.client_storage.get(USER_NAME)
        self.access_token = self.cp.page.client_storage.get(ACCESS_TOKEN)
        self.role = self.cp.page.client_storage.get(ROLE)
        self.user_email = self.cp.page.client_storage.get(USER_EMAIL)

        # Listes de stockage des données
        self.liste_des_users: list = []

        # --- COMPOSANTS DE L'INTERFACE ---
        self.stat_total = ft.Text("0", size=24, font_family="PEB",)
        self.stat_managers = ft.Text("0", size=24, font_family="PEB",)
        self.stat_cashiers = ft.Text("0", size=24, font_family="PEB", )

        self.table = ft.ListView(expand=True, spacing=15, padding=10,)
        self.loader = ft.ProgressRing(width=20, height=20, stroke_width=2, color=MAIN_COLOR, visible=False)

        self.search_user_field = ft.TextField(
            **input_style, 
            width=350, 
            label="Rechercher un collaborateur...", 
            prefix_icon=ft.Icons.SEARCH_ROUNDED,
            on_change=self.filter_users_locally
        )

        self.open_form_button = MyButton(
            title="Ajouter un utilisateur", 
            icon=resource_path("assets/icons/white/user-plus.svg"),
            click=self.open_new_user_container
        )

        # --- CHAMPS DU FORMULAIRE DE SAISIE ---
        self.new_user_name = ft.TextField(
            **input_style, prefix_icon=ft.Icons.PERSON_OUTLINE_ROUNDED,
            label="Nom complet", width=440, capitalization=ft.TextCapitalization.CHARACTERS
        )
        self.new_user_email = ft.TextField(
            **input_style, prefix_icon=ft.Icons.MAIL_OUTLINED, width=440,
            label="Adresse Email professionnelle"
        )
        self.new_user_password = ft.TextField(
            **input_style, prefix_icon=ft.Icons.LOCK_OUTLINE_ROUNDED, width=440,
            label="Mot de passe initial", password=True, can_reveal_password=True,
            value="123456"
        )
        self.new_role = ft.RadioGroup(
            content=ft.Row(
                controls=[
                    ft.Radio(**radio_style, label="Manager", value="manager"),
                    ft.Radio(**radio_style, label="Caissier / Vendeur", value="cashier")
                ],
                spacing=20
            )
        )

        self.selected_image_path = None
        self.uploaded_avatar_url = None

        self.avatar_preview = ft.CircleAvatar(
            foreground_image_src=DEFAULT_IMAGE,
            radius=45,
        )

        self.file_picker = ft.FilePicker(on_result=self.on_file_selected)
        if self.cp.page:
            self.cp.page.overlay.append(self.file_picker)

        # --- ASSEMBLAGE ---
        self.content = ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Column([
                            ft.Text("Équipe & Utilisateurs", size=26, font_family="PEB"),
                            ft.Text("Gérez les accès et les permissions de vos collaborateurs", size=13, color="grey700"),
                        ], spacing=4),
                        ft.Row([self.loader, self.open_form_button], alignment=ft.MainAxisAlignment.END, vertical_alignment=ft.CrossAxisAlignment.CENTER)
                    ], 
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                ft.Divider(height=15, color=ft.Colors.TRANSPARENT),
                self.build_stats_row(),
                ft.Divider(height=15, color=ft.Colors.TRANSPARENT),
                ft.Container(
                    **stat_style, expand=True,
                    content=ft.Column(
                        controls=[
                            ft.Row([self.search_user_field], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                            ft.Container(content=self.table, expand=True)
                        ]
                    )
                )
            ],
            spacing=10
        )
        self.on_mount()

    @staticmethod
    def run_async_in_thread(coro):
        def runner():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(coro)
            loop.close()
        thread = threading.Thread(target=runner)
        thread.start()

    def on_mount(self):
        self.run_async_in_thread(self.on_init_async())

    async def on_init_async(self):
        self.loader.visible = True
        self.update()
        await self.load_datas()
        self.loader.visible = False
        self.update()

    def build_stats_row(self):
        def create_stat_card(title, text_control, icon):
            return ft.Container(
                **stat_style, width=270,
                content=ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Image(resource_path(icon), width=16, height=16),
                                ft.Text(title, size=13, font_family="PPR", color='grey'),
                            ]
                        ), text_control
                    ], 
                ),

            )
        return ft.Row([
            create_stat_card("Admin", self.stat_total, "assets/icons/others/user-lock.svg"),
            create_stat_card("Manager", self.stat_managers, "assets/icons/others/user-star.svg"),
            create_stat_card("Caissiers", self.stat_cashiers, "assets/icons/others/user.svg"),
        ], spacing=15, wrap=True)

    async def load_datas(self):
        params = {'select': '*', 'tenant_id': f'eq.{self.tenant_id}', 'order': 'nom.asc'}
        utilisateurs = await supabase_request_async(
            access_token=self.access_token, tenant_id=self.tenant_id, table_name="profiles", method="GET", params=params
        )
        self.liste_des_users = utilisateurs if (utilisateurs and isinstance(utilisateurs, list)) else []
        
        self.stat_total.value = str(sum(1 for u in self.liste_des_users if u.get("role") == "admin"))
        self.stat_managers.value = str(sum(1 for u in self.liste_des_users if u.get("role") == "manager"))
        self.stat_cashiers.value = str(sum(1 for u in self.liste_des_users if u.get("role") == "cashier"))
        
        self.render_user_list(self.liste_des_users)

    def render_user_list(self, user_list):
        self.table.controls.clear()

        if not user_list:
            self.table.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.SUPERVISED_USER_CIRCLE_OUTLINED, size=48, color="grey400"),
                        ft.Text("Aucun collaborateur trouvé", size=14, color="grey500", font_family="PPM")
                    ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    alignment=ft.alignment.center, padding=40
                )
            )
            self.cp.page.update()
            return

        for row in user_list:
            is_me = (self.user_id == row.get("id"))
            role_raw = row.get("role", "cashier")
            
            if role_raw == "manager":
                role_label = "Manager / Admin"
                role_color = "indigo"
                role_icon = resource_path("assets/icons/others/user-star.svg")
            elif role_raw == "cashier":
                role_label = "Caissier"
                role_color = "teal"
                role_icon = resource_path("assets/icons/others/user.svg")
            else:
                role_label = "Accès restreint"
                role_color = "red"
                role_icon = resource_path("assets/icons/others/user-plus.svg")

            avatar_img = row.get("avatar_url") if row.get("avatar_url") else DEFAULT_IMAGE

            card_item = ft.Container(
                content=ft.Row([
                    ft.Row([
                        ft.CircleAvatar(foreground_image_src=avatar_img, radius=26, bgcolor="grey200"),
                        ft.Column([
                            ft.Row([
                                ft.Text(row.get("nom", "SANS NOM"), size=16, font_family="PPB"),
                                ft.Container(
                                    content=ft.Text("Moi", size=12, color="white", font_family="PPM", ),
                                    bgcolor=MAIN_COLOR, padding=ft.padding.only(left=6, right=6, top=2, bottom=2),
                                    border_radius=5, visible=is_me
                                )
                            ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                            ft.Text(row.get("email", "Pas d'adresse e-mail"), size=13, color="grey600", font_family="PPM"),
                        ], spacing=3, alignment=ft.MainAxisAlignment.CENTER)
                    ], alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.CENTER),

                    ft.Row([
                        ft.Container(
                            content=ft.Image(resource_path('assets/icons/grey/trash-2.svg'), width=18, height=18),
                            on_click=self.delete_user_from_profile
                        )
                    ], alignment=ft.MainAxisAlignment.END, vertical_alignment=ft.CrossAxisAlignment.CENTER)

                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                bgcolor=ft.Colors.WHITE,
                padding=ft.padding.only(left=20, right=15, top=12, bottom=12),
                border_radius=12,
                shadow=ft.BoxShadow(blur_radius=2, color="grey50"),
                animate=ft.Animation(200, "ease"),
                on_hover=lambda e: self.on_card_hover(e),
                # ÉVÉNEMENT : Clic sur la carte pour ouvrir la fiche détaillée du collaborateur
                on_click=lambda e, r=row: self.open_user_profile_container(r)
            )
            self.table.controls.append(card_item)
            
        self.cp.page.update()

    def on_card_hover(self, e):
        e.control.bgcolor = "grey50" if e.data == "true" else ft.Colors.WHITE
        e.control.update()

    def filter_users_locally(self, e):
        query = self.search_user_field.value.lower().strip()
        if not query:
            self.render_user_list(self.liste_des_users)
            return
        filtered = [u for u in self.liste_des_users if query in u.get("nom", "").lower() or query in u.get("email", "").lower()]
        self.render_user_list(filtered)

    # --- AJOUT : OUVERTURE DE LA FICHE DÉTAILLÉE (CÔTÉ DROIT / DATA_CONTAINER) ---
    def open_user_profile_container(self, user_data):
        """Construit et affiche la fiche du collaborateur dans le conteneur global du Stack d'accueil"""
        is_me = (self.user_id == user_data.get("id"))
        role_raw = user_data.get("role", "cashier")
        avatar_img = user_data.get("avatar_url") if user_data.get("avatar_url") else DEFAULT_IMAGE

        if role_raw == "manager":
            role_label, role_color, role_icon = "Manager / Administrateur", "indigo", ft.Icons.ADMIN_PANEL_SETTINGS_ROUNDED
        else:
            role_label, role_color, role_icon = "Caissier / Vendeur", "teal", ft.Icons.POINT_OF_SALE_ROUNDED

        # Construction dynamique du contenu de la fiche
        self.cp.st_container.content.height = 700
        self.cp.st_container.content.width = 600
        self.cp.st_form.content = ft.Column(
            controls=[
                # En-tête de la fiche
                ft.Row([
                    ft.Text("Fiche Collaborateur", size=22, font_family="PEB"),
                    ft.IconButton(
                        icon=ft.Icons.CLOSE_ROUNDED, icon_color="grey800",
                        on_click=lambda e: self.cp.hide_container(self.cp.st_container)
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Divider(height=5, thickness=1, color="grey200"),
                ft.Divider(height=15, color=ft.Colors.TRANSPARENT),

                # Section Photo centrée
                ft.Row([
                    ft.Container(
                        content=ft.CircleAvatar(foreground_image_src=avatar_img, radius=55, bgcolor="grey100"),
                        padding=4, border=ft.border.all(2, f"{role_color}30"), border_radius=60
                    )
                ], alignment=ft.MainAxisAlignment.CENTER),
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),

                # Nom et statut "Moi"
                ft.Column([
                    ft.Row([
                        ft.Text(user_data.get("nom", "").upper(), size=18, font_family="PEB", text_align=ft.TextAlign.CENTER),
                    ], alignment=ft.MainAxisAlignment.CENTER),
                    ft.Row([
                        ft.Container(
                            content=ft.Text("Votre compte connecté", size=11, color="white", font_family="PPM"),
                            bgcolor=MAIN_COLOR, padding=ft.padding.only(left=8, right=8, top=3, bottom=3),
                            border_radius=5, visible=is_me
                        )
                    ], alignment=ft.MainAxisAlignment.CENTER, visible=is_me)
                ], spacing=4),
                
                ft.Divider(height=15, color=ft.Colors.TRANSPARENT),

                # Infos Détaillées de la carte
                ft.Container(
                    content=ft.Column([
                        # Email
                        ft.Row([
                            ft.Icon(ft.Icons.EMAIL_OUTLINED, size=18, color="grey600"),
                            ft.Column([
                                ft.Text("Adresse Email", size=11, color="grey500", font_family="PPM"),
                                ft.Text(user_data.get("email", "-"), size=14, font_family="PPM", color="grey900")
                            ], spacing=1)
                        ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                        ft.Divider(height=10, color="grey100"),

                        # Rôle
                        ft.Row([
                            ft.Icon(role_icon, size=18, color=f"{role_color}700"),
                            ft.Column([
                                ft.Text("Habilitation / Rôle", size=11, color="grey500", font_family="PPM"),
                                ft.Text(role_label, size=14, font_family="PEB", color=f"{role_color}700")
                            ], spacing=1)
                        ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                        ft.Divider(height=10, color="grey100"),

                        # Identifiant Unique (Donnée supplémentaire utile)
                        ft.Row([
                            ft.Icon(ft.Icons.KEY_ROUNDED, size=18, color="grey600"),
                            ft.Column([
                                ft.Text("ID Utilisateur (UUID)", size=11, color="grey500", font_family="PPM"),
                                ft.Text(user_data.get("id", "-"), size=11, font_family="PPM", color="grey700", selectable=True)
                            ], spacing=1)
                        ], vertical_alignment=ft.CrossAxisAlignment.CENTER),

                    ], spacing=12),
                    bgcolor="grey50", padding=20, border_radius=12, border=ft.border.all(1, "grey200")
                ),

                ft.Divider(height=30, color=ft.Colors.TRANSPARENT),

                # Actions en bas (Bouton supprimer si ce n'est pas mon propre compte)
                ft.Row([
                    ft.TextButton(
                        text="Supprimer ce collaborateur",
                        icon=ft.Icons.DELETE_FOREVER_ROUNDED,
                        icon_color="red",
                        style=ft.ButtonStyle(color="red"),
                        on_click=lambda e: self.delete_user_from_profile(user_data),
                        visible=not is_me,
                    )
                ], alignment=ft.MainAxisAlignment.CENTER)
            ],
            spacing=10,
            scroll=ft.ScrollMode.ADAPTIVE
        )
        
        # Affichage du conteneur lié au stack
        self.cp.show_container(self.cp.st_container)
        self.cp.update()

    def delete_user_from_profile(self, user_data):
        """Handler de suppression lié depuis le volet de profil"""
        self.cp.hide_container(self.cp.st_container) # Ferme le volet en premier
        self._execute_deletion(user_data.get('id'), user_data.get('nom'))

    def delete_user_from_list(self, e):
        """Handler de suppression lié depuis l'icône de ligne directe"""
        user_data = e.control.data
        self._execute_deletion(user_data.get('id'), user_data.get('nom'))

    def _execute_deletion(self, user_uuid, user_name):
        """Centralise le processus technique de suppression de l'utilisateur"""
        self.loader.visible = True
        self.update()

        try:
            supabase_client.table("profiles").delete().eq("id", user_uuid).execute()
            supabase_admin.auth.admin.delete_user(user_uuid)

            self.cp.show_alert(f"Accès révoqué pour {user_name}", ft.Icons.REMOVE_CIRCLE_OUTLINE_ROUNDED, ft.Colors.AMBER)
            self.run_async_in_thread(self.load_datas())

        except Exception as ex:
            print(f"Erreur lors de la destitution du compte : {ex}")
            self.cp.show_alert(f"Action impossible : {ex}", ft.Icons.INFO_OUTLINED, ft.Colors.RED)
        finally:
            self.loader.visible = False
            self.update()

    # --- RESTE DU SCRIPT D'ORIGINE CONSERVÉ ---
    def on_file_selected(self, e: ft.FilePickerResultEvent):
        if e.files:
            file_info = e.files[0]
            self.selected_image_path = file_info.path
            self.avatar_preview.foreground_image_src = self.selected_image_path
            self.avatar_preview.update()
            self.run_async_in_thread(self.upload_avatar_to_bucket(file_info))

    async def upload_avatar_to_bucket(self, file_info):
        try:
            file_ext = os.path.splitext(file_info.name)[1]
            unique_filename = f"{self.tenant_id}/{int(time.time())}{file_ext}"

            with open(file_info.path, "rb") as f:
                file_bytes = f.read()

            supabase_client.storage.from_("profile_pictures").upload(
                path=unique_filename, file=file_bytes,
                file_options={"content-type": f"image/{file_ext.replace('.', '')}"}
            )

            res_url = supabase_client.storage.from_("profile_pictures").get_public_url(unique_filename)
            self.uploaded_avatar_url = getattr(res_url, "public_url", str(res_url))
            self.cp.show_alert("Image de profil synchronisée", ft.Icons.CHECK_CIRCLE, ft.Colors.LIGHT_GREEN)

        except Exception as ex:
            print(f"Erreur Upload Storage : {ex}")
            self.cp.show_alert(f"Erreur d'image : {ex}", ft.Icons.INFO_OUTLINED, ft.Colors.RED)

    def open_new_user_container(self, e):
        self.new_user_name.value = ""
        self.new_user_email.value = ""
        self.new_user_password.value = "123456"
        self.new_role.value = "cashier"
        self.selected_image_path = None
        self.uploaded_avatar_url = None
        self.avatar_preview.foreground_image_src = DEFAULT_IMAGE

        if self.file_picker not in self.cp.page.overlay:
            self.cp.page.overlay.append(self.file_picker)
            self.cp.page.update()

        self.cp.st_container.content.height = 700
        self.cp.st_container.content.width = 500
        self.cp.st_form.content = ft.Column(
            controls=[
                ft.Row([
                    ft.Text("Nouvel Utilisateur", size=22, font_family="PEB"),
                    ft.IconButton(icon=ft.Icons.CLOSE_ROUNDED, icon_color="grey800", on_click=lambda e: self.cp.hide_container(self.cp.st_container))
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Divider(height=5, thickness=1, color="grey200"),
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),

                ft.Container(
                    **stat_style,
                    content=ft.Row([
                        self.avatar_preview,
                        ft.Column([
                            ft.Text("Photo d'identité", size=13, font_family="PEB"),
                            MyTextButton("Parcourir le disque...", lambda _: self.file_picker.pick_files(allow_multiple=False, file_type=ft.FilePickerFileType.IMAGE))
                        ], spacing=2)
                    ], spacing=15),
                ),
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                
                ft.Text("Informations personnelles", size=14, font_family="PEB", color=MAIN_COLOR),
                self.new_user_name,
                self.new_user_email,
                self.new_user_password,
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                ft.Text("Niveau d'habilitation & Rôle", size=14, font_family="PEB", color=MAIN_COLOR),
                self.new_role,
                ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                ft.Row([
                    MyButton("Valider l'inscription", resource_path("assets/icons/white/user-check.svg"), click=lambda e: self.run_async_in_thread(self.add_new_user(e)))
                ], alignment=ft.MainAxisAlignment.END)
            ],
            spacing=10, scroll=ft.ScrollMode.ADAPTIVE
        )
        self.cp.show_container(self.cp.st_container)
        self.cp.update()

    async def add_new_user(self, e):
        if not self.new_user_email.value or not self.new_user_name.value or not self.new_user_password.value:
            self.cp.show_alert("Veuillez remplir tous les critères obligatoires", ft.Icons.INFO_OUTLINED, ft.Colors.AMBER)
            return

        self.loader.visible = True
        self.update()

        try:
            # 2. Création dans Supabase Auth via l'API admin
            auth_response = supabase_admin.auth.admin.create_user({
                "email": self.new_user_email.value,
                "password": self.new_user_password.value,
                "email_confirm": True,
                "user_metadata": {
                    "role": self.new_role.value, 
                    "tenant_id": str(self.tenant_id), 
                    "nom_complet": self.new_user_name.value
                }
            })

            # CORRECTION ICI : Supabase-py encapsule la réponse dans l'attribut .data
            if not auth_response or not hasattr(auth_response, 'data') or not auth_response.data:
                self.cp.show_alert("Le serveur d'authentification a rejeté la requête", ft.Icons.ERROR_OUTLINE_ROUNDED, ft.Colors.RED)
                return

            new_user_auth = auth_response.data

            # 3. Préparation des données du profil
            profile_data = {
                "id": new_user_auth.id, # Récupération de l'ID corrigée
                "tenant_id": str(self.tenant_id),
                "email": self.new_user_email.value,
                "role": self.new_role.value,
                "nom": self.new_user_name.value,
                "avatar_url": self.uploaded_avatar_url if self.uploaded_avatar_url else DEFAULT_IMAGE,
                "is_first_login": True # AJOUT : Flag pour forcer le changement de mot de passe au Home
            }

            # 4. Insertion dans la table publique profiles
            supabase_client.table("profiles").insert(profile_data).execute()

            self.cp.hide_container(self.cp.st_container)
            self.cp.show_alert(f"Le compte de {self.new_user_name.value} est opérationnel", ft.Icons.CHECK_CIRCLE_ROUNDED, ft.Colors.GREEN)
            await self.load_datas()

        except Exception as ex:
            print(f"Erreur d'insertion utilisateur : {ex}")
            self.cp.show_alert(f"Erreur d'inscription : {ex}", ft.Icons.INFO_OUTLINED, ft.Colors.RED)
        finally:
            self.loader.visible = False
            self.update()
            
            