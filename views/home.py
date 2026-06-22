import flet as ft
from navbar.menu import NavBar
from styles import ct_style, intern_ct_style, input_style
from components.components import StateButton, MyButton
import os, time
from datetime import date
from utils import (
    ACCESS_TOKEN, TENANT_ID, USER_ID, USER_NAME, TENANT_NAME, EXPIRATION_DATE, 
    ROLE, PLAN_CHOISI, resource_path, MAIN_COLOR, USER_EMAIL, BG_COLOR, IS_FIRST_LOGIN,
    SHADOW_COLOR, BORDER_COLOR, TEXT_PRIMARY, TEXT_SECONDARY, CARD_BG
)
from services.supabase_client import supabase_client


class HomeView(ft.View):
    def __init__(self, page):
        super().__init__(
            vertical_alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            bgcolor=BG_COLOR, route="/home", padding=0,
        )
        # paramètre de la page
        self.page = page
        
        # parametres généraux
        self.plan_choisi = self.page.client_storage.get(PLAN_CHOISI)
        self.expiration_date = self.page.client_storage.get(EXPIRATION_DATE)
        self.tenant_name = self.page.client_storage.get(TENANT_NAME)
        self.tenant_id = self.page.client_storage.get(TENANT_ID)
        self.user_id = self.page.client_storage.get(USER_ID)
        self.user_name = self.page.client_storage.get(USER_NAME) 
        self.access_token = self.page.client_storage.get(ACCESS_TOKEN)
        self.role = self.page.client_storage.get(ROLE) 
        self.user_email = self.page.client_storage.get(USER_EMAIL) 
        self.is_first_login = self.page.client_storage.get(IS_FIRST_LOGIN) 
        
        # Génération des initiales pour l'avatar (ex: "Van Tech" -> "VT")
        initiales = "".join([part[0].upper() for part in self.user_name.split() if part])[:2] if self.user_name else "U"

        # --- AMÉLIORATION DU BADGE ABONNEMENT ---
        self.icone_abo = ft.Image("", width=16, height=16)
        self.abo = ft.Text(self.expiration_date, size=13, font_family="PPM", weight=ft.FontWeight.W_600)
        self.ct_abo = ft.Container(
            padding=ft.padding.symmetric(horizontal=12, vertical=6),
            border_radius=8,
            border=ft.border.all(1, ft.Colors.TRANSPARENT),
            bgcolor=ft.Colors.with_opacity(0.1, MAIN_COLOR),
            content=ft.Row(
                controls=[self.icone_abo, self.abo],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=6,
            )
        )
        # contenu de la section principale
        self.my_content = ft.Column(
            expand=True,
            controls=[
                
            ]
        )
        
        # --- EN-TÊTE MODERNE ---
        self.top_container = ft.Container(
            padding=ft.padding.symmetric(horizontal=24, vertical=12),
            bgcolor=CARD_BG,
            # shadow=ft.BoxShadow(blur_radius=8, color=SHADOW_COLOR, spread_radius=1),
            content=ft.Row(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Container(
                                bgcolor=BG_COLOR,
                                padding=ft.padding.symmetric(horizontal=14, vertical=8),
                                border_radius=10,
                                border=ft.border.all(1, BORDER_COLOR),
                                content=ft.Row(
                                    controls=[
                                        ft.Icon(ft.Icons.STORE_OUTLINED, size=16, color=MAIN_COLOR),
                                        ft.Text(
                                            self.tenant_name.upper() if self.tenant_name else "",
                                            size=14,
                                            font_family="PEB",
                                            color=TEXT_PRIMARY,
                                        )
                                    ],
                                    spacing=8,
                                )
                            ),
                            self.ct_abo
                        ],
                        spacing=12,
                    ),
                    ft.Row(
                        controls=[
                            StateButton(
                                icon=resource_path("assets/icons/black/bell.svg"),
                                badge=None, data=None, click=None
                            ),
                            StateButton(
                                icon=resource_path("assets/icons/black/user.svg"),
                                badge=None, data=None,
                                click=lambda e: self.show_container(self.data_container)
                            )
                        ],
                        spacing=8
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
        )
        
        # Sidebar
        self.left_container = ft.Container(
            width=230, bgcolor="white", border=ft.border.only(
                right=ft.BorderSide(1, "#f0f0f6")
            ),
            padding=20, 
            content=NavBar(self)
        )
        
        # Contenu de la section droite
        self.right_container = ft.Container(
            bgcolor=BG_COLOR, expand=True, padding=0,
            content=ft.Column(
                controls=[
                    self.top_container,
                    ft.Divider(height=1, thickness=1, color="#E9ECEF"),
                    ft.Container(padding=20, content=self.my_content, expand=True)
                ], spacing=0
            )
        )
        
        # layout principal
        self.main_window = ft.Row(
            expand=True,
            controls=[self.left_container, self.right_container], spacing=0
        )

        # =====================================================================
        # --- ENSEMBLE PRO : REFONTE COMPLÈTE DE SELF.DATA_CONTAINER ---
        # =====================================================================
        self.data_container = ft.Container(
            **ct_style,
            content=ft.Container(
                **intern_ct_style,
                width=400,
                height=450,
                content=ft.Container(
                    padding=30,
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=0,
                        controls=[
                            # Entête
                            ft.Row(
                                controls=[
                                    ft.Text("Mon Profil", size=20, font_family="PEB", color=TEXT_PRIMARY),
                                    ft.IconButton(
                                        icon=ft.Icons.CLOSE_ROUNDED,
                                        icon_color=TEXT_SECONDARY,
                                        on_click=lambda e: self.hide_container(self.data_container)
                                    )
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            ),
                            ft.Divider(height=15, color=BORDER_COLOR),
                            # Avatar avec dégradé
                            ft.Container(
                                width=80,
                                height=80,
                                bgcolor=ft.Colors.with_opacity(0.15, MAIN_COLOR),
                                border_radius=40,
                                alignment=ft.alignment.center,
                                margin=ft.margin.only(top=10, bottom=8),
                                content=ft.Text(
                                    initiales,
                                    size=28,
                                    font_family="PEB",
                                    color=MAIN_COLOR,
                                )
                            ),
                            ft.Text(
                                self.user_name,
                                size=20,
                                font_family="PEB",
                                color=TEXT_PRIMARY,
                            ),
                            ft.Container(
                                padding=ft.padding.symmetric(horizontal=12, vertical=4),
                                bgcolor=ft.Colors.with_opacity(0.1, MAIN_COLOR),
                                border_radius=6,
                                margin=ft.margin.only(top=4, bottom=20),
                                content=ft.Text(
                                    self.role.upper(),
                                    size=12,
                                    font_family="PPM",
                                    weight=ft.FontWeight.BOLD,
                                    color=MAIN_COLOR,
                                )
                            ),
                            # Infos
                            ft.Container(
                                bgcolor=BG_COLOR,
                                border_radius=12,
                                padding=16,
                                margin=ft.margin.only(bottom=24),
                                content=ft.Column(
                                    spacing=12,
                                    controls=[
                                        ft.Row(
                                            controls=[
                                                ft.Icon(ft.Icons.EMAIL_OUTLINED, size=18, color=TEXT_SECONDARY),
                                                ft.Text(self.user_email, size=14, font_family="PPM", color=TEXT_PRIMARY),
                                            ],
                                            spacing=10,
                                        ),
                                        ft.Row(
                                            controls=[
                                                ft.Icon(ft.Icons.BUSINESS_OUTLINED, size=18, color=TEXT_SECONDARY),
                                                ft.Text(self.tenant_name or "Aucun établissement", size=14, font_family="PPM", color=TEXT_PRIMARY),
                                            ],
                                            spacing=10,
                                        ),
                                    ]
                                )
                            ),
                            # Bouton déconnexion
                            ft.Container(
                                width=float("inf"),
                                content=MyButton(
                                    icon=resource_path('assets/icons/white/circle-x.svg'),
                                    title="Se déconnecter",
                                    click=self.deconnexion,
                                )
                            )
                        ]
                    )
                )
            )
        )
        
        # Autres formulaires restants
        self.details_vente_form = ft.Column()
        self.details_vente_container = ft.Container(
            **ct_style,
            content=ft.Container(
                **intern_ct_style, width=800, height=600, padding=0,
                content=self.details_vente_form
            )
        )
        
        self.valid_basket_form = ft.Container()
        self.valid_basket_container = ft.Container(
            **ct_style,
            content=ft.Container(
                **intern_ct_style, width=360, height=720, padding=20,
                content=self.valid_basket_form 
            )
        )

        self.cloture_form = ft.Column()
        self.cloture_container = ft.Container(
            **ct_style,
            content=ft.Container(
                **intern_ct_style, width=380, height=720, padding=20,
                content=self.cloture_form
            )
        )

        # formulaire utilisateur
        self.st_form = ft.Container(padding=30, content=ft.Column(expand=True))
        self.st_container = ft.Container(
            **ct_style,
            content=ft.Container(
                **intern_ct_style, width=500, height=600,
                content=self.st_form
            )
        )
        self.edit_ref_form = ft.Container(padding=30, content=ft.Column(expand=True))
        self.edit_ref_container = ft.Container(
            **ct_style,
            content=ft.Container(
                **intern_ct_style, width=500, height=600,
                content=self.edit_ref_form
            )
        )
        

        self.snack_message = ft.Text(size=15, font_family="PPM", color="white")
        self.snack_icon = ft.Icon(size=20)
        self.snack_alert = ft.SnackBar(
            content=ft.Row(
                controls=[self.snack_icon, self.snack_message],
                alignment=ft.MainAxisAlignment.CENTER
            ),
            show_close_icon=True,
            close_icon_color="white",
            behavior=ft.SnackBarBehavior.FLOATING,
            duration=3000,
            margin=30,
            padding=10,
            elevation=10,
            bgcolor=ft.Colors.with_opacity(0.8, ft.Colors.BLACK87),
            width=600
        )

        self.controls = [
            ft.Stack(
                alignment=ft.alignment.center, expand=True,
                controls=[
                    self.main_window, self.data_container, self.details_vente_container,
                    self.valid_basket_container, self.cloture_container, self.st_container,
                    self.edit_ref_container,
                ]
            )
        ]
        self.verifier_abo()
        # --- ÉTAPE 3 : INITIALISATION DE L'OVERLAY DE SÉCURITÉ PREMIÈRE CONNEXION ---
        if self.is_first_login:
            self._init_password_reset_modal()
            

    def _init_password_reset_modal(self):
        """Crée et affiche de force la boîte de dialogue de configuration de mot de passe."""
        self.new_password_tf = ft.TextField(
            **input_style,
            label="Nouveau mot de passe",
            password=True,
            can_reveal_password=True,
            prefix_icon=ft.Icons.LOCK_RESET_OUTLINED,
        )
        
        self.confirm_password_tf = ft.TextField(
            **input_style,
            label="Confirmer le mot de passe",
            password=True,
            can_reveal_password=True,
            prefix_icon=ft.Icons.LOCK_OUTLINED,
        )
        
        self.modal_error_text = ft.Text("", color="red", size=13, font_family="PPM", visible=False)
        self.modal_loader = ft.ProgressRing(width=20, height=20, stroke_width=2, color="white", visible=False)
        self.modal_btn_text = ft.Text("Enregistrer mon mot de passe", size=14, font_family="PPM", color="white")
        
        self.modal_submit_btn = ft.Container(
            bgcolor=MAIN_COLOR, padding=10, height=45, border_radius=8,
            content=ft.Row(controls=[self.modal_loader, self.modal_btn_text], alignment=ft.MainAxisAlignment.CENTER),
            on_click=self.update_password_first_login
        )

        self.password_modal = ft.AlertDialog(
            modal=True,  # Empêche la fermeture en cliquant à côté ou sur Échap
            title=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.SECURITY_ROUNDED, color=MAIN_COLOR, size=28),
                    ft.Text("Première Connexion", font_family="PEB", size=20)
                ], spacing=10
            ),
            content=ft.Container(
                width=400,
                height=220,
                content=ft.Column(
                    controls=[
                        ft.Text(
                            "Pour des raisons de sécurité, vous devez modifier le mot de passe temporaire fourni par votre administrateur avant d'accéder au système.",
                            size=13, font_family="PPR", color="grey"
                        ),
                        ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                        self.new_password_tf,
                        self.confirm_password_tf,
                        self.modal_error_text,
                    ],
                    spacing=8,
                    scroll=ft.ScrollMode.AUTO
                )
            ),
            actions=[self.modal_submit_btn],
            actions_alignment=ft.MainAxisAlignment.CENTER,
            bgcolor="white"
        )
        
        # Injection automatique dans l'overlay de la page
        self.page.overlay.append(self.password_modal)
        self.password_modal.open = True
    
    def update_password_first_login(self, e):
        """Traite le changement de mot de passe obligatoire et bascule le drapeau SQL."""
        new_pwd = self.new_password_tf.value.strip()
        confirm_pwd = self.confirm_password_tf.value.strip()

        if not new_pwd or not confirm_pwd:
            self.show_alert("Veuillez remplir les deux champs.", ft.Icons.INFO, ft.Colors.AMBER)
            return

        if len(new_pwd) < 6:
            self.show_alert("Le mot de passe doit contenir au moins 6 caractères.", ft.Icons.INFO, ft.Colors.AMBER)
            return

        if new_pwd != confirm_pwd:
            self.show_alert("Les mots de passe ne correspondent pas.", ft.Icons.INFO, ft.Colors.AMBER)
            return

        # Activation du loader visuel interne au bouton modal
        self.modal_error_text.visible = False
        self.modal_loader.visible = True
        self.modal_btn_text.value = "Mise à jour..."
        self.modal_submit_btn.disabled = True
        self.page.update()

        try:
            # A. Mise à jour du mot de passe dans Supabase Auth
            supabase_client.auth.update_user({"password": new_pwd})
            print('Changement du mot de passe réussi')

            # B. Mise à jour de la table profiles pour lever définitivement le flag de blocage
            supabase_client.table("profiles").update({"is_first_login": False}).eq("id", self.user_id).execute()

            # C. Nettoyage et mise à jour locale
            self.page.client_storage.set("IS_FIRST_LOGIN", False)
            self.is_first_login = False

            # Fermeture de la boîte modale
            self.password_modal.open = False
            self.page.update()

            # Message général de félicitations
            self.show_alert("Votre mot de passe a été configuré avec succès !", ft.Icons.CHECK_CIRCLE, ft.Colors.LIGHT_GREEN)

        except Exception as err:
            print(f"Erreur lors de la réinitialisation initiale : {err}")
            self.show_alert("Échec de la configuration. Réessayez.", ft.Icons.INFO, ft.Colors.AMBER)
    
    def show_container(self, container):
        container.visible = True
        container.update()
        container.content.scale = 1
        self.page.update()

    def hide_container(self, container):
        container.content.scale = 0
        container.visible = False
        self.page.update()

    def show_alert(self, message: str, icon: str, icon_color: str):
        self.snack_icon.name = icon
        self.snack_icon.color = icon_color
        self.snack_message.value = message
        self.page.open(self.snack_alert)
        self.page.update()
    
    def verifier_abo(self):
        print("vérifier abonnement...")
        print("date expiration :", self.expiration_date)
        
        y, m, d = map(int, self.expiration_date.split('-'))
        delay = (date(y, m, d) - date.today()).days
        
        print("délai", delay)
        
        if delay <= 0:  
            self.icone_abo.src = resource_path("assets/icons/others/calendar-shield.svg")
            self.abo.value = "Abonnement expiré"
            self.abo.color = ft.Colors.RED_700
            self.ct_abo.bgcolor = ft.Colors.with_opacity(0.08, ft.Colors.RED)
            self.ct_abo.border = ft.border.all(1, ft.Colors.with_opacity(0.2, ft.Colors.RED))

        elif 1 <= delay <= 31:
            self.icone_abo.src = resource_path("assets/icons/others/calendar-heart-red.svg")
            self.abo.value = f"Expire dans {delay} jrs"
            self.abo.color = ft.Colors.RED_700
            self.ct_abo.bgcolor = ft.Colors.with_opacity(0.08, ft.Colors.RED)
            self.ct_abo.border = ft.border.all(1, ft.Colors.with_opacity(0.2, ft.Colors.RED))

        elif 31 < delay <= 60:
            self.icone_abo.src = resource_path("assets/icons/others/calendar-fold.svg")
            self.abo.value = f"Expire dans {delay} jrs"
            self.abo.color = ft.Colors.AMBER_700
            self.ct_abo.bgcolor = ft.Colors.with_opacity(0.08, ft.Colors.AMBER)
            self.ct_abo.border = ft.border.all(1, ft.Colors.with_opacity(0.2, ft.Colors.AMBER))

        else:  
            self.icone_abo.src = resource_path("assets/icons/others/calendar-check.svg")
            self.abo.value = "Abonnement actif"
            self.abo.color = ft.Colors.TEAL_700
            self.ct_abo.bgcolor = ft.Colors.with_opacity(0.08, ft.Colors.TEAL)
            self.ct_abo.border = ft.border.all(1, ft.Colors.with_opacity(0.2, ft.Colors.TEAL))
            
    def deconnexion(self, e):
        """Déconnecte proprement l'utilisateur de Supabase et nettoie le stockage local."""
        try:
            # 1. Appel synchrone au client officiel Supabase pour invalider la session
            from services.supabase_client import supabase_client
            
            supabase_client.auth.sign_out()
            print("[DEBUG AUTH] Déconnexion réussie du serveur Supabase.")
            
        except Exception as err:
            # On log l'erreur mais on continue le nettoyage local au cas où le réseau fail
            print(f"[WARNING AUTH] Erreur lors du sign_out Supabase : {str(err)}")

        # 2. Nettoyage complet du client_storage de Flet
        cles_a_supprimer = [
            ACCESS_TOKEN, TENANT_ID, USER_ID, USER_NAME, 
            TENANT_NAME, EXPIRATION_DATE, ROLE, PLAN_CHOISI, USER_EMAIL
        ]
        
        for cle in cles_a_supprimer:
            try:
                self.page.client_storage.remove(cle)
            except Exception:
                pass
                
        print("[DEBUG STORAGE] Stockage local nettoyé avec succès.")

        # 3. Notification visuelle de succès
        self.show_alert("Déconnexion réussie. À bientôt !", ft.Icons.CHECK_CIRCLE, ft.Colors.LIGHT_GREEN)
        
        # Un léger délai pour laisser le SnackBar s'afficher avant la redirection
        time.sleep(0.5)

        # 4. Redirection vers la vue de login/connexion
        # Remplace "/" par ta route de login réelle (ex: "/login") si nécessaire
        self.page.go("/")
        
        