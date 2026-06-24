import flet as ft
import uuid
import os
import datetime
from styles import input_style
from components.components import MyTextButton, MyButton
# Importation de ton client Supabase synchrone et admin
from services.supabase_client import supabase_client, supabase_admin
from utils import (
    ACCESS_TOKEN, USER_ID, TENANT_ID, USER_NAME, ROLE, resource_path, BG_COLOR, MAIN_COLOR,
    CARD_BG, TEXT_PRIMARY, TEXT_SECONDARY, SHADOW_COLOR, SURFACE_COLOR, EXPIRATION_DATE
)


class RegisterView(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(
            vertical_alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            bgcolor=BG_COLOR, 
            route="/register", 
            padding=0,  # Mis à 0 pour coller la barre en haut
        )
        self.page = page
        self.current_step = 1  # Étape 1 : Établissement | Étape 2 : Compte Admin
        
        # Variable pour stocker le chemin du logo sélectionné
        self.selected_file_path = None

        # --- Initialisation du FilePicker ---
        self.file_picker = ft.FilePicker(on_result=self.on_file_selected)
        self.page.overlay.append(self.file_picker)

        # --- BARRE DE NAVIGATION HAUTE COHÉRENTE ---
        top_bar = ft.Container(
            padding=ft.padding.symmetric(horizontal=30, vertical=14),
            bgcolor=CARD_BG,
            border=ft.border.only(bottom=ft.BorderSide(1, SHADOW_COLOR)),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    # Logo à gauche
                    ft.Row(
                        spacing=2,
                        controls=[
                            ft.Text("Alti", size=24, font_family="PEB", color=TEXT_PRIMARY),
                            ft.Text("Pos", size=24, font_family="PEB", color=MAIN_COLOR),
                        ],
                    ),
                    # Actions à droite
                    ft.Row(
                        spacing=12,
                        controls=[
                            ft.TextButton(
                                "Se connecter",
                                style=ft.ButtonStyle(
                                    color=TEXT_SECONDARY,
                                    text_style=ft.TextStyle(size=14, font_family="PPM"),
                                ),
                                on_click=lambda e: self.page.go("/"),
                            ),
                            ft.TextButton(
                                "S'inscrire",
                                style=ft.ButtonStyle(
                                    color=MAIN_COLOR,  # Actif car on est sur la page d'inscription
                                    text_style=ft.TextStyle(size=14, font_family="PEB"),
                                ),
                                on_click=lambda e: self.page.go("/register"),
                            ),
                            ft.TextButton(
                                "Mot de passe oublié ?",
                                style=ft.ButtonStyle(
                                    color=TEXT_SECONDARY,
                                    text_style=ft.TextStyle(size=14, font_family="PPM"),
                                ),
                                on_click=lambda e: self.page.go("/forgot-password"),
                            ),
                        ],
                    ),
                ],
            ),
        )

        # --- CHAMPS ÉTAPE 1 : Établissement/Entreprise ---
        self.company_name = ft.TextField(
            **input_style, label="Nom de l'établissement *", 
            prefix_icon=ft.Icons.STORE_OUTLINED
        )
        self.slogan = ft.TextField(
            **input_style, label="Slogan de la boutique (optionnel)", 
            prefix_icon=ft.Icons.CHAT_BUBBLE_OUTLINE_ROUNDED
        )
        self.contact = ft.TextField(
            **input_style, label="Numéro de téléphone *", 
            prefix_icon=ft.Icons.PHONE_OUTLINED,
            keyboard_type=ft.KeyboardType.PHONE
        )
        self.adresse = ft.TextField(
            **input_style, label="Adresse / Ville *", 
            prefix_icon=ft.Icons.LOCATION_ON_OUTLINED
        )
        
        self.logo_info_text = ft.Text("Aucun logo sélectionné (optionnel)", size=12, color="grey", font_family="PPM")
        self.btn_select_logo = MyButton(
            "Choisir un logo", 
            resource_path("assets/icons/white/cloud-uplaod.svg"), 
            lambda _: self.file_picker.pick_files(
                allow_multiple=False,
                allowed_extensions=["png", "jpg", "jpeg"]
            ),
        )
        
        # --- CHAMPS ÉTAPE 2 : Compte Administrateur ---
        self.admin_name = ft.TextField(
            **input_style, label="Votre nom complet *", 
            prefix_icon=ft.Icons.PERSON_PIN_OUTLINED, expand=True
        )
        self.login = ft.TextField(
            **input_style, label="Adresse Email *", 
            prefix_icon=ft.Icons.EMAIL_OUTLINED,
        )
        self.password = ft.TextField(
            **input_style, label="Mot de passe *", 
            prefix_icon=ft.Icons.LOCK_OUTLINED,
            can_reveal_password=True, password=True
        )

        # Message d'erreur textuel unique
        self.error_text = ft.Text("", color="red", font_family="PPM", size=14, visible=False)

        # --- INDICATEURS VISUELS DE PROGRESSION (DOTS) ---
        self.dot1 = ft.Container(width=25, height=12, border_radius=6, bgcolor=MAIN_COLOR, animate=ft.Animation(300, "ease"))
        self.dot2 = ft.Container(width=12, height=12, border_radius=6, bgcolor="grey300", animate=ft.Animation(300, "ease"))

        # Conteneur dynamique qui accueille le slide en cours
        self.slide_container = ft.Column(spacing=15)
        
        # --- BLOC OVERLAY DE CHARGEMENT PLEIN ÉCRAN ---
        self.loading_overlay = ft.Container(
            expand=True,
            bgcolor=ft.Colors.with_opacity(0.75, "black"),
            alignment=ft.alignment.center,
            visible=False,
            content=ft.Container(
                bgcolor=SURFACE_COLOR,
                padding=30,
                border_radius=16,
                width=300,
                height=180,
                alignment=ft.alignment.center,
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=15,
                    controls=[
                        ft.ProgressRing(width=40, height=40, stroke_width=3, color=MAIN_COLOR),
                        ft.Text("Veuillez patienter...", size=16, font_family="PEB", color="black"),
                        ft.Text("Création de votre espace AltiPos en cours", size=12, font_family="PPM", color="grey", text_align=ft.TextAlign.CENTER),
                    ]
                )
            )
        )

        # Générer l'affichage de la première étape au chargement
        self.build_step()

        # Carte blanche principale du formulaire
        form_card = ft.Container(
            padding=40, width=700,
            bgcolor="white",
            border_radius=16,
            border=ft.border.all(1, "#E2E8F0"), # Bordure Slate 200 très fine
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=4,
                color=ft.Colors.with_opacity(0.04, "#000000"),
                offset=ft.Offset(0, 2),
            ),
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Row(
                        controls=[
                            ft.Text("Alti", size=36, color="black", font_family="PEB"),
                            ft.Text("Pos", size=36, color=MAIN_COLOR, font_family="PEB"),
                        ], spacing=0, alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    ft.Row(
                        controls=[
                            ft.Text("Création de votre espace de gestion", size=15, color="grey", font_family="PPM"),
                        ], alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                    
                    # Injection du slide actif
                    self.slide_container,
                    
                    ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                    
                    # Barre des petits points indicateurs
                    ft.Row([self.dot1, self.dot2], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
                    
                    ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                    
                    # Lien de retour vers la connexion
                    ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        controls=[
                            ft.Text("Déjà inscrit ?", size=14, font_family="PPI", color="grey"),
                            MyTextButton("Se connecter", lambda _: self.page.go("/"))
                        ], 
                    ),
                ], spacing=8
            )
        )

        # --- STRUCTURE FINALE CENTRÉE AVEC LA BARRE DE NAVIGATION ---
        self.controls = [
            ft.Stack(
                expand=True,
                controls=[
                    ft.Column(
                        expand=True,
                        spacing=50,
                        controls=[
                            top_bar,  # Barre fixée en haut
                            ft.Container(
                                # expand=True,
                                alignment=ft.alignment.center,  # Centrage vertical et horizontal parfait
                                content=form_card,
                            )
                        ]
                    ),
                    self.loading_overlay
                ]
            )
        ]

    def build_step(self):
        """ Rafraîchit les contrôles et les indicateurs en fonction de l'étape active """
        self.slide_container.controls.clear()
        self.error_text.visible = False  # Efface l'erreur lors du changement de slide
        
        if self.current_step == 1:
            # Animation des points : Slide 1 actif (Pilule)
            self.dot1.bgcolor = MAIN_COLOR
            self.dot1.width = 25
            self.dot2.bgcolor = "grey300"
            self.dot2.width = 12
            
            self.slide_container.controls = [
                ft.Text("L'ÉTABLISSEMENT", size=12, font_family="PEB", color=MAIN_COLOR),
                ft.Row([self.company_name, self.slogan,]),
                ft.Row([self.contact, self.adresse,]),
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                ft.Row(
                    controls=[self.btn_select_logo, self.logo_info_text],
                    alignment=ft.MainAxisAlignment.START,
                    spacing=10
                ),
                self.error_text,
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                ft.Container(
                    bgcolor=MAIN_COLOR, padding=10, height=45, border_radius=10,
                    alignment=ft.alignment.center,
                    content=ft.Text("Suivant", size=16, font_family="PPM", color=SURFACE_COLOR),
                    on_click=self.go_to_admin_step
                )
            ]

        else:
            # Animation des points : Slide 2 actif (Pilule)
            self.dot1.bgcolor = "grey300"
            self.dot1.width = 12
            self.dot2.bgcolor = MAIN_COLOR
            self.dot2.width = 25
            
            self.slide_container.controls = [
                ft.Text("COMPTE ADMINISTRATEUR", size=12, font_family="PEB", color=MAIN_COLOR),
                ft.Row([self.admin_name, ]),
                ft.Row([self.login, self.password,]),
                self.error_text,
                ft.Divider(height=5, color=ft.Colors.TRANSPARENT),
                ft.Row(
                    controls=[
                        ft.IconButton(
                            icon=ft.Icons.ARROW_BACK_IOS_NEW_ROUNDED,
                            icon_color="grey",
                            icon_size=18,
                            tooltip="Retour aux infos entreprise",
                            on_click=self.go_back_to_tenant
                        ),
                        ft.Container(
                            bgcolor=MAIN_COLOR, padding=10, height=45, border_radius=10, expand=True,
                            alignment=ft.alignment.center,
                            content=ft.Text("Créer mon établissement", size=16, font_family="PPM", color=SURFACE_COLOR),
                            on_click=self.handle_registration
                        )
                    ],
                    spacing=10
                )
            ]
        if self.page:
            self.page.update()

    def go_to_admin_step(self, e):
        """ Valide l'étape 1 avant de basculer sur l'étape 2 """
        self.company_name.border_color = None
        self.contact.border_color = None
        self.adresse.border_color = None

        if not self.company_name.value or not self.contact.value or not self.adresse.value:
            if not self.company_name.value: self.company_name.border_color = "red"
            if not self.contact.value: self.contact.border_color = "red"
            if not self.adresse.value: self.adresse.border_color = "red"
            self.show_error("Veuillez remplir tous les champs obligatoires de l'établissement (*).")
            return
        
        self.current_step = 2
        self.build_step()

    def go_back_to_tenant(self, e):
        """ Permet de revenir en arrière pour corriger les infos du tenant """
        self.current_step = 1
        self.build_step()

    def on_file_selected(self, e: ft.FilePickerResultEvent):
        """ Callback de sélection du logo """
        if e.files:
            file = e.files[0]
            self.selected_file_path = file.path
            self.logo_info_text.value = f"Sélectionné : {file.name}"
            self.logo_info_text.color = "green"
        else:
            self.selected_file_path = None
            self.logo_info_text.value = "Aucun logo sélectionné (optionnel)"
            self.logo_info_text.color = "grey"
        self.page.update()

    def handle_registration(self, e):
        """ Traitement final de l'inscription globale """
        self.admin_name.border_color = None
        self.login.border_color = None
        self.password.border_color = None

        if not self.admin_name.value or not self.login.value or not self.password.value:
            if not self.admin_name.value: self.admin_name.border_color = "red"
            if not self.login.value: self.login.border_color = "red"
            if not self.password.value: self.password.border_color = "red"
            self.show_error("Veuillez remplir tous les champs obligatoires de l'administrateur (*).")
            return

        if len(self.password.value) < 6:
            self.password.border_color = "red"
            self.show_error("Le mot de passe doit contenir au moins 6 caractères.")
            return

        self.error_text.visible = False
        self.loading_overlay.visible = True
        self.page.update() 

        try:
            new_tenant_id = str(uuid.uuid4())
            logo_url_final = None

            if self.selected_file_path and os.path.exists(self.selected_file_path):
                _, ext = os.path.splitext(self.selected_file_path)
                ext = ext.lower() if ext else ".png"
                nom_fichier_storage = f"{new_tenant_id}{ext}"
                
                with open(self.selected_file_path, "rb") as f:
                    supabase_admin.storage.from_("logos").upload(
                        path=nom_fichier_storage,
                        file=f,
                        file_options={"content-type": f"image/{ext.replace('.', '')}"}
                    )
                
                res_url = supabase_client.storage.from_("logos").get_public_url(nom_fichier_storage)
                logo_url_final = str(res_url)

            auth_response = supabase_client.auth.sign_up(
                {
                    "email": self.login.value,
                    "password": self.password.value,
                    "options": {
                        "data": {
                            "tenant_id": new_tenant_id,
                            "role": "admin",
                            "full_name": self.admin_name.value
                        }
                    }
                }
            )

            if auth_response.user:
                self.page.client_storage.set(ACCESS_TOKEN, auth_response.session.access_token)
                self.page.client_storage.set(USER_ID, auth_response.user.id)
                self.page.client_storage.set(USER_NAME, self.admin_name.value)
                self.page.client_storage.set(TENANT_ID, new_tenant_id)
                self.page.client_storage.set(ROLE, "admin")

                supabase_client.table("tenants").insert(
                    {
                        "id": new_tenant_id,
                        "nom_entreprise": self.company_name.value,
                        "slogan": self.slogan.value if self.slogan.value else None,
                        "contact": self.contact.value,
                        "adresse": self.adresse.value,
                        "logo_url": logo_url_final
                    }
                ).execute()

                supabase_client.table("profiles").insert(
                    {
                        "id": auth_response.user.id,
                        "tenant_id": new_tenant_id,
                        "email": self.login.value,
                        "role": "admin",
                        "nom": self.admin_name.value,
                        "is_first_login": False
                    }
                ).execute()

                try:
                    date_debut = datetime.date.today()
                    date_fin = date_debut + datetime.timedelta(days=30)

                    supabase_admin.table("paiements").insert(
                        {
                            "tenant_id": new_tenant_id,
                            "montant": 0,
                            "mode_paiement": "Système (Essai)",
                            "reference_transaction": f"TRIAL-{new_tenant_id[:8].upper()}",
                            "statut": "réussi",
                            "periode_couverte_debut": str(date_debut),
                            "periode_couverte_fin": str(date_fin),
                            "date_expiration": str(date_fin),
                            "plan_choisi": "Freemium 1 Mois"
                        }
                    ).execute()
                    self.page.client_storage.set(EXPIRATION_DATE, str(date_fin))

                except Exception as e_paiement:
                    print(f"⚠️ [ERREUR INTERNE INSCRIPTION PAIEMENT] : {e_paiement}")

                self.loading_overlay.visible = False
                self.page.go("/home")
            else:
                self.show_error("Impossible de finaliser la création de votre profil.")

        except Exception as error:
            print(f"❌ [ERREUR CAPTURÉE ENREGISTREMENT] : {error}")
            self.show_error(f"Une erreur est survenue lors de l'enregistrement : {str(error)}")

    def show_error(self, message: str):
        self.error_text.value = message
        self.error_text.visible = True
        self.loading_overlay.visible = False
        self.page.update()
        
        