import flet as ft
from utils import (
    MAIN_COLOR, BG_COLOR, CARD_BG, TEXT_PRIMARY, TEXT_SECONDARY, SHADOW_COLOR
)
from styles import input_style, button_primary_style
from services.supabase_client import supabase_client


class ResetPasswordView(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(
            vertical_alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            bgcolor=BG_COLOR,
            route="/reset-password",
            padding=0,
        )
        self.page = page

        # --- BARRE DE NAVIGATION HAUTE ---
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
                    ft.Text(
                        "Sécurisation du compte",
                        size=14,
                        font_family="PPM",
                        color=TEXT_SECONDARY,
                    )
                ],
            ),
        )

        # --- CHAMPS DE SAISIE ---
        self.password_field = ft.TextField(
            **input_style,
            prefix_icon=ft.Icons.LOCK_OUTLINED,
            label="Nouveau mot de passe *",
            hint_text="Entrez votre nouveau mot de passe",
            password=True,
            can_reveal_password=True,
        )

        self.confirm_password_field = ft.TextField(
            **input_style,
            prefix_icon=ft.Icons.LOCK_CLOCK_OUTLINED,
            label="Confirmer le mot de passe *",
            hint_text="Répétez le mot de passe",
            password=True,
            can_reveal_password=True,
        )

        self.error_text = ft.Text("", color="red", font_family="PPM", size=13, visible=False)
        self.success_text = ft.Text("", color="green", font_family="PPM", size=13, visible=False)

        # --- BOUTON D'ACTION ---
        self.loader = ft.ProgressRing(width=20, height=20, stroke_width=2, color="white", visible=False)
        self.btn_text = ft.Text("Mettre à jour le mot de passe", size=16, font_family="PPM", color="white")

        self.submit_button = ft.ElevatedButton(
            content=ft.Row(
                controls=[self.loader, self.btn_text],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            style=button_primary_style,
            on_click=self.handle_password_change,
            width=float("inf"),
            height=48,
        )

        # --- CARTE DU FORMULAIRE ---
        self.form_card = ft.Container(
            width=440,
            padding=ft.padding.symmetric(horizontal=40, vertical=40),
            bgcolor="white",
            border_radius=36,
            border=ft.border.all(1, "#E2E8F0"),
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
                        "Nouveau mot de passe",
                        size=24,
                        font_family="PEB",
                        color=TEXT_PRIMARY,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Text(
                        "Choisissez un mot de passe fort pour sécuriser définitivement l'accès à votre catalogue.",
                        size=14,
                        font_family="PPM",
                        color=TEXT_SECONDARY,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Divider(height=8, color=ft.Colors.TRANSPARENT),
                    self.password_field,
                    self.confirm_password_field,
                    self.error_text,
                    self.success_text,
                    self.submit_button,
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

    async def handle_password_change(self, e):
        new_password = self.password_field.value.strip()
        confirm_password = self.confirm_password_field.value.strip()

        # Validations basiques
        if not new_password or not confirm_password:
            await self.show_message("Veuillez remplir tous les champs.", is_error=True)
            return

        if new_password != confirm_password:
            await self.show_message("Les deux mots de passe ne correspondent pas.", is_error=True)
            return

        if len(new_password) < 6:
            await self.show_message("Le mot de passe doit contenir au moins 6 caractères.", is_error=True)
            return

        # UI en état de chargement
        self.error_text.visible = False
        self.success_text.visible = False
        self.loader.visible = True
        self.btn_text.value = "Modification en cours..."
        self.submit_button.disabled = True
        self.page.update()

        try:
            # Envoi de la mise à jour à Supabase sur l'utilisateur de la session courante
            supabase_client.auth.update_user({"password": new_password})

            await self.show_message(
                "Mot de passe mis à jour avec succès ! Redirection...",
                is_error=False
            )
            self.page.update()

            # Petite pause pour laisser l'utilisateur lire le message de succès avant de l'envoyer au Login
            import asyncio
            await asyncio.sleep(2)

            # Redirection vers la page de connexion
            self.page.go("/")

        except Exception as error:
            print(f"[ERROR RESET UPDATE] : {error}")
            await self.show_message(
                "Le lien a expiré ou une erreur est survenue. Veuillez refaire une demande.",
                is_error=True
            )

    async def show_message(self, message: str, is_error: bool = True):
        if is_error:
            self.error_text.value = message
            self.error_text.visible = True
            self.success_text.visible = False
        else:
            self.success_text.value = message
            self.success_text.visible = True
            self.error_text.visible = False

        self.loader.visible = False
        self.btn_text.value = "Mettre à jour le mot de passe"
        self.submit_button.disabled = False
        self.page.update()

