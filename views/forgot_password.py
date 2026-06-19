import flet as ft
from utils import (
    MAIN_COLOR, BG_COLOR, CARD_BG, TEXT_PRIMARY, TEXT_SECONDARY, SHADOW_COLOR
)
from styles import input_style, button_primary_style
from services.supabase_client import supabase_client

class ForgotPasswordView(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(
            vertical_alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            bgcolor=BG_COLOR,
            route="/forgot-password",
            padding=0,
        )
        self.page = page

        # --- BARRE DE NAVIGATION HAUTE COHÉRENTE ---
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
                            ft.Text("Pos", size=24, font_family="PEB", color=TEXT_PRIMARY),
                            ft.Text("ly", size=24, font_family="PEB", color=MAIN_COLOR),
                        ],
                    ),
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
                                    color=TEXT_SECONDARY,
                                    text_style=ft.TextStyle(size=14, font_family="PPM"),
                                ),
                                on_click=lambda e: self.page.go("/register"),
                            ),
                            ft.TextButton(
                                "Mot de passe oublié ?",
                                style=ft.ButtonStyle(
                                    color=MAIN_COLOR,  # Actif sur cette page
                                    text_style=ft.TextStyle(size=14, font_family="PEB"),
                                ),
                                on_click=lambda e: self.page.go("/forgot-password"),
                            ),
                        ],
                    ),
                ],
            ),
        )

        # --- CHAMP EMAIL ---
        self.email_field = ft.TextField(
            **input_style,
            prefix_icon=ft.Icons.EMAIL_OUTLINED,
            label="Adresse Email *",
            hint_text="vantech.infos@gmail.com",
        )

        self.error_text = ft.Text("", color="red", font_family="PPM", size=13, visible=False)
        self.success_text = ft.Text("", color="green", font_family="PPM", size=13, visible=False)

        # --- BOUTON D'ACTION ---
        self.loader = ft.ProgressRing(width=20, height=20, stroke_width=2, color="white", visible=False)
        self.btn_text = ft.Text("Envoyer le lien de récupération", size=16, font_family="PPM", color="white")

        self.submit_button = ft.ElevatedButton(
            content=ft.Row(
                controls=[self.loader, self.btn_text],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            style=button_primary_style,
            on_click=self.handle_reset_request,
            width=float("inf"),
            height=48,
        )

        # --- CARTE DU FORMULAIRE ---
        self.form_card = ft.Container(
            width=440,
            padding=ft.padding.symmetric(horizontal=40, vertical=40),
            bgcolor="white",
            border_radius=36,
            border=ft.border.all(1, "#E2E8F0"), # Bordure Slate 200 très fine
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=4,
                color=ft.Colors.with_opacity(0.04, "#000000"),
                offset=ft.Offset(0, 2),
            ),
            content=ft.Column(
                spacing=16,
                tight=True,
                horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                controls=[
                    ft.Text(
                        "Réinitialiser le mot de passe",
                        size=24,
                        font_family="PEB",
                        color=TEXT_PRIMARY,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Text(
                        "Entrez l'adresse email rattachée à votre compte. Nous vous enverrons un lien sécurisé pour créer un nouveau mot de passe.",
                        size=14,
                        font_family="PPM",
                        color=TEXT_SECONDARY,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Divider(height=8, color=ft.Colors.TRANSPARENT),
                    self.email_field,
                    self.error_text,
                    self.success_text,
                    self.submit_button,
                    ft.TextButton(
                        "Retour à la page de connexion",
                        style=ft.ButtonStyle(
                            color=TEXT_SECONDARY,
                            text_style=ft.TextStyle(size=14, font_family="PPM"),
                        ),
                        on_click=lambda e: self.page.go("/"),
                    ),
                ],
            ),
        )

        # --- INTEGRATION GENERALE ---
        self.controls = [
            ft.Column(
                expand=True,
                spacing=0,
                controls=[
                    top_bar,
                    ft.Container(
                        expand=True,
                        alignment=ft.alignment.center,
                        content=self.form_card,
                    )
                ]
            )
        ]

    def handle_reset_request(self, e):
        email = self.email_field.value.strip()

        if not email:
            self.show_message("Veuillez saisir votre adresse email.", is_error=True)
            return

        self.error_text.visible = False
        self.success_text.visible = False
        self.loader.visible = True
        self.btn_text.value = "Envoi en cours..."
        self.submit_button.disabled = True
        self.page.update()

        try:
            # Appel Supabase pour envoyer le mail de réinitialisation
            # Note : configure bien l'URL de redirection dans ton dashboard Supabase Auth si nécessaire
            supabase_client.auth.reset_password_for_email(email)
            
            self.show_message(
                "Un email de récupération a été envoyé avec succès ! Vérifiez votre boîte de réception.",
                is_error=False
            )
        except Exception as error:
            print(f"[ERROR RESET] : {error}")
            self.show_message(
                "Une erreur est survenue lors de l'envoi de l'email. Veuillez réessayer.",
                is_error=True
            )

    def show_message(self, message: str, is_error: bool = True):
        if is_error:
            self.error_text.value = message
            self.error_text.visible = True
            self.success_text.visible = False
        else:
            self.success_text.value = message
            self.success_text.visible = True
            self.error_text.visible = False

        self.loader.visible = False
        self.btn_text.value = "Envoyer le lien de récupération"
        self.submit_button.disabled = False
        self.page.update()