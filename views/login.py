import flet as ft
from datetime import date
from utils import (
    MAIN_COLOR, ACCESS_TOKEN, USER_ID, TENANT_ID, USER_NAME,
    ROLE, TENANT_NAME, PLAN_CHOISI, EXPIRATION_DATE, resource_path, USER_EMAIL, BG_COLOR, IS_FIRST_LOGIN,
    SHADOW_COLOR, TEXT_PRIMARY, TEXT_SECONDARY, CARD_BG, SURFACE_COLOR
)
from styles import input_style, button_primary_style, stat_style
from services.supabase_client import supabase_client
from components.components import MyTextButton


class LoginView(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(
            vertical_alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            bgcolor=BG_COLOR,
            route="/",
            padding=0,
        )
        self.page = page

        # --- BARRE DE NAVIGATION HAUTE (FIXE) ---
        top_bar = ft.Container(
            padding=ft.padding.symmetric(horizontal=30, vertical=14),
            bgcolor=CARD_BG,
            border=ft.border.only(bottom=ft.BorderSide(1, SHADOW_COLOR)),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Row(
                        spacing=2,
                        controls=[
                            ft.Text("Alti", size=24, font_family="PEB", color=TEXT_PRIMARY),
                            ft.Text("Pos", size=24, font_family="PEB", color=MAIN_COLOR),
                        ],
                    ),
                    ft.Row(
                        spacing=12,
                        controls=[
                            ft.TextButton(
                                "Se connecter",
                                style=ft.ButtonStyle(
                                    color=MAIN_COLOR,
                                    text_style=ft.TextStyle(size=14, font_family="PEB"),
                                ),
                                on_click=lambda e: self.scroll_to_form(),
                            ),
                            ft.TextButton(
                                "S'inscrire",
                                style=ft.ButtonStyle(
                                    color=TEXT_SECONDARY,
                                    text_style=ft.TextStyle(size=14, font_family="PPM"),
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

        # =====================================================================
        # 🌟 SECTION 1 : PRÉSENTATION DE L'APPLICATION (HERO SECTION)
        # =====================================================================
        presentation_section = ft.Container(
            padding=ft.padding.symmetric(horizontal=20, vertical=60),
            alignment=ft.alignment.center,
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=20,
                controls=[
                    ft.Container(
                        padding=ft.padding.all(8),
                        bgcolor=ft.Colors.with_opacity(0.1, MAIN_COLOR),
                        border_radius=10,
                        content=ft.Text(
                            "SOLUTION DE GESTION MULTI-TENANT",
                            size=11,
                            font_family="PEB",
                            color=MAIN_COLOR,
                            # letter_spacing=1.5,
                        )
                    ),
                    ft.Text(
                        "Pilotez votre entreprise en toute simplicité",
                        size=36,
                        font_family="PEB",
                        color=TEXT_PRIMARY,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Container(
                        width=600,
                        content=ft.Text(
                            "Posly est une application cloud moderne conçue pour centraliser vos ventes, gérer vos utilisateurs et suivre la croissance de vos établissements en temps réel. Simple, fluide et sécurisé.",
                            size=16,
                            font_family="PPM",
                            color=TEXT_SECONDARY,
                            text_align=ft.TextAlign.CENTER,
                        ),
                    ),
                    ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                    ft.ElevatedButton(
                        content=ft.Row(
                            [
                                ft.Text("Accéder à mon espace", size=15, font_family="PEB"),
                                ft.Icon(ft.Icons.ARROW_DOWNWARD_ROUNDED, size=18)
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            tight=True,
                        ),
                        style=ft.ButtonStyle(
                            bgcolor=MAIN_COLOR,
                            color="white",
                            padding=ft.padding.symmetric(horizontal=25, vertical=15),
                            shape=ft.RoundedRectangleBorder(radius=10),
                        ),
                        on_click=lambda e: self.scroll_to_form(),
                    ),
                ]
            )
        )

        # =====================================================================
        # 🔐 SECTION 2 : FORMULAIRE DE CONNEXION EXISTANT
        # =====================================================================
        self.login_field = ft.TextField(
            **input_style,
            prefix_icon=ft.Icons.EMAIL_OUTLINED,
            label="Email",
        )
        self.password_field = ft.TextField(
            **input_style,
            prefix_icon=ft.Icons.LOCK_OUTLINED,
            label="Mot de passe",
            password=True,
            can_reveal_password=True,
        )

        self.error_text = ft.Text("", color="red", font_family="PPM", size=13, visible=False)

        self.loader = ft.ProgressRing(width=20, height=20, stroke_width=2, color="white", visible=False)
        self.btn_text = ft.Text("Connexion", size=16, font_family="PPM", color="white")

        self.login_button = ft.ElevatedButton(
            content=ft.Row(
                controls=[self.loader, self.btn_text],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            style=button_primary_style,
            on_click=self.sign_in,
            width=float("inf"),
            height=48,
        )

        self.forgot_password_link = ft.TextButton(
            "Mot de passe oublié ?",
            style=ft.ButtonStyle(
                color=MAIN_COLOR,
                text_style=ft.TextStyle(size=14, font_family="PPM"),
                overlay_color=ft.Colors.with_opacity(0.1, MAIN_COLOR),
            ),
            on_click=lambda e: self.page.go("/forgot-password"),
        )

        self.register_link = MyTextButton(
            "Inscrivez-vous",
            lambda e: self.page.go("/register")
        )

        self.form_card = ft.Container(
            bgcolor="white",
            border_radius=16,
            border=ft.border.all(1, "#E2E8F0"), # Bordure Slate 200 très fine
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=4,
                color=ft.Colors.with_opacity(0.04, "#000000"),
                offset=ft.Offset(0, 2),
            ),
            width=420,
            padding=ft.padding.symmetric(horizontal=40, vertical=40),
            content=ft.Column(
                spacing=16,
                tight=True,
                horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                controls=[
                    ft.Text(
                        "Se connecter à votre compte",
                        size=22,
                        font_family="PEB",
                        color=TEXT_PRIMARY,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Divider(height=8, color=ft.Colors.TRANSPARENT),
                    self.login_field,
                    self.password_field,
                    ft.Container(
                        content=self.forgot_password_link,
                        alignment=ft.alignment.center_right,
                    ),
                    self.error_text,
                    self.login_button,
                    ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=5,
                        controls=[
                            ft.Text(
                                "Vous n'avez pas un compte ?",
                                size=14,
                                font_family="PPM",
                                color=TEXT_SECONDARY,
                            ),
                            self.register_link,
                        ],
                    ),
                ],
            ),
        )

        # Une clé ou référence directe sur le conteneur du formulaire pour pouvoir scroller dessus
        self.form_section = ft.Container(
            content=self.form_card,
            padding=ft.padding.only(bottom=80, top=20),
            alignment=ft.alignment.center,
        )

        # --- CONTENEUR DÉFILABLE GLOBAL ---
        self.scrollable_content = ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,  # Activation du défilement fluide
            spacing=0,
            controls=[
                presentation_section,
                self.form_section
            ]
        )

        # --- STRUCTURE DE LA VUE ---
        self.controls = [
            ft.Column(
                expand=True,
                spacing=0,
                controls=[
                    top_bar,
                    ft.Container(
                        expand=True,
                        content=self.scrollable_content,
                    )
                ]
            )
        ]

    # --- MÉTHODE DE DÉFILEMENT AUTOMATIQUE ---
    def scroll_to_form(self):
        """ Fait défiler le contenu de manière fluide jusqu'au formulaire de connexion """
        self.scrollable_content.scroll_to(key=self.form_section.key, delta=400, duration=600, curve=ft.AnimationCurve.EASE_IN_OUT)
        self.page.update()

    # --- MÉTHODES AUTHENTIFICATION ---
    def sign_in(self, e):
        email = self.login_field.value.strip()
        password = self.password_field.value.strip()

        if not email or not password:
            self.show_error("Veuillez remplir tous les champs.")
            return

        self.error_text.visible = False
        self.loader.visible = True
        self.btn_text.value = "Connexion..."
        self.login_button.disabled = True
        self.page.update()

        try:
            auth_response = supabase_client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })

            if auth_response.session:
                user_data = auth_response.user
                metadata = user_data.user_metadata or {}

                try:
                    profil_res = supabase_client.table("profiles") \
                        .select("is_first_login, role, nom, tenant_id") \
                        .eq("id", user_data.id) \
                        .single() \
                        .execute()
                    if profil_res.data:
                        tenant_id = profil_res.data.get("tenant_id")
                        user_role = profil_res.data.get("role", "cashier")
                        user_name = profil_res.data.get("nom", "Utilisateur")
                        is_first_login = profil_res.data.get("is_first_login", False)
                    else:
                        tenant_id = metadata.get("tenant_id")
                        user_role = metadata.get("role", "cashier")
                        user_name = metadata.get("nom_complet", "Utilisateur")
                        is_first_login = False
                except Exception as e:
                    print(f"[DEBUG LOGIN] Erreur profils RLS: {e}")
                    tenant_id = metadata.get("tenant_id")
                    user_role = metadata.get("role", "cashier")
                    user_name = metadata.get("nom_complet", "Utilisateur")
                    is_first_login = False

                if not tenant_id:
                    self.show_error("Votre compte n'est rattaché à aucun établissement.")
                    return

                try:
                    paiement = supabase_client.table("paiements") \
                        .select("date_expiration, plan_choisi, tenants(nom_entreprise)") \
                        .eq("tenant_id", tenant_id) \
                        .order("date_paiement", desc=True) \
                        .execute()

                    if not paiement.data:
                        exp_date_str = "2026-12-31"
                        tenant_name = "Nouvel Établissement"
                        plan_choisi = "Essai Gratuit"
                    else:
                        data = paiement.data[0]
                        exp_date_str = data.get("date_expiration")
                        tenant_name = data.get("tenants", {}).get("nom_entreprise", "Entreprise")
                        plan_choisi = data.get("plan_choisi", "Standard")

                    y, m, d = map(int, exp_date_str.split('-'))
                    if date(y, m, d) < date.today():
                        self.show_error("Votre abonnement a expiré.")
                        return
                except Exception as e:
                    print(f"[DEBUG LOGIN] Erreur table paiements: {e}")
                    self.show_error("Erreur lors de la vérification des droits d'accès.")
                    return

                self.page.client_storage.set(ACCESS_TOKEN, auth_response.session.access_token)
                self.page.client_storage.set(USER_ID, user_data.id)
                self.page.client_storage.set(USER_NAME, user_name)
                self.page.client_storage.set(USER_EMAIL, user_data.email)
                self.page.client_storage.set(TENANT_ID, tenant_id)
                self.page.client_storage.set(TENANT_NAME, tenant_name)
                self.page.client_storage.set(ROLE, user_role)
                self.page.client_storage.set(PLAN_CHOISI, plan_choisi)
                self.page.client_storage.set(EXPIRATION_DATE, exp_date_str)
                self.page.client_storage.set(IS_FIRST_LOGIN, is_first_login)

                self.page.go('/home')

        except Exception as error:
            import traceback
            traceback.print_exc()
            self.show_error(f"Erreur système : {str(error)}")

    def show_error(self, message: str):
        self.error_text.value = message
        self.error_text.visible = True
        self.loader.visible = False
        self.btn_text.value = "Connexion"
        self.login_button.disabled = False
        self.page.update()
        