import flet as ft
from navbar.menu import NavBar
from styles import ct_style, intern_ct_style, login_style
from components.components import StateButton, MyButton
import os
from datetime import date
from utils import (
    ACCESS_TOKEN, TENANT_ID, USER_ID, USER_NAME, TENANT_NAME, EXPIRATION_DATE, 
    ROLE, PLAN_CHOISI, resource_path, RED_COLOR, GREEN_COLOR, MAIN_COLOR, USER_EMAIL, BG_COLOR, IS_FIRST_LOGIN
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
            content=ft.Row(
                controls=[self.icone_abo, self.abo],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=6,
                vertical_alignment=ft.CrossAxisAlignment.CENTER
            )
        )
        
        # contenu de la section principale
        self.my_content = ft.Column(
            expand=True,
            controls=[
                ft.Text(
                    f"Bienvenue, {self.user_name}", size=18, font_family="PEB"
                )
            ]
        )
        
        # --- AMÉLIORATION DU CONTENEUR DU TENANT ---
        self.top_container = ft.Container(
            padding=ft.padding.symmetric(horizontal=20, vertical=10),
            bgcolor="white",
            content=ft.Row(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Container(
                                bgcolor="#F8F9FA", 
                                padding=ft.padding.symmetric(horizontal=14, vertical=6), 
                                border_radius=8,
                                border=ft.border.all(1, "#E9ECEF"),
                                alignment=ft.alignment.center,
                                content=ft.Row(
                                    controls=[
                                        ft.Image(
                                            resource_path("assets/icons/grey/store.svg"),
                                            width=16, height=16,
                                            color=MAIN_COLOR 
                                        ),
                                        ft.Text(
                                            self.tenant_name.upper() if self.tenant_name else "", 
                                            size=13, 
                                            font_family="PEB", 
                                            color="#495057"
                                        )
                                    ],
                                    spacing=8,
                                    vertical_alignment=ft.CrossAxisAlignment.CENTER
                                )
                            ),
                            self.ct_abo
                        ],
                        spacing=12,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER
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
                vertical_alignment=ft.CrossAxisAlignment.CENTER
            ),
        )
        
        # Sidebar
        self.left_container = ft.Container(
            width=215, bgcolor="white", border=ft.border.only(
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
                width=380, 
                height=420,  # Légèrement augmenté pour aérer l'avatar et les infos
                content=ft.Container(
                    padding=24,
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=0,
                        controls=[
                            # Entête du modal avec bouton de fermeture discret
                            ft.Row(
                                controls=[
                                    ft.Text("Mon Profil", size=18, font_family="PEB", color="#6C757D"),
                                    StateButton(
                                        icon=resource_path("assets/icons/black/x.svg"),
                                        badge=None, data=None,
                                        click=lambda e: self.hide_container(self.data_container)
                                    )
                                ], 
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            ),
                            ft.Divider(height=15, thickness=1, color="#F1F3F5"),
                            
                            # Zone d'Avatar Moderne
                            ft.Container(
                                width=64, height=64,
                                bgcolor=ft.Colors.with_opacity(0.1, MAIN_COLOR),
                                border_radius=32,
                                alignment=ft.alignment.center,
                                margin=ft.margin.only(top=10, bottom=8),
                                content=ft.Text(
                                    initiales,
                                    size=22,
                                    font_family="PEB",
                                    color=MAIN_COLOR
                                )
                            ),
                            
                            # Nom d'utilisateur principal
                            ft.Text(
                                self.user_name,
                                size=18,
                                font_family="PEB",
                                color="#212529",
                                text_align=ft.TextAlign.CENTER
                            ),
                            
                            # Badge de Rôle Dynamique
                            ft.Container(
                                padding=ft.padding.symmetric(horizontal=10, vertical=4),
                                bgcolor="#E8F4FD" if self.role.lower() == "admin" else "#F1F3F5",
                                border_radius=6,
                                margin=ft.margin.only(top=4, bottom=20),
                                content=ft.Text(
                                    self.role.upper(),
                                    size=11,
                                    font_family="PPM",
                                    weight=ft.FontWeight.BOLD,
                                    color="#1A73E8" if self.role.lower() == "admin" else "#495057"
                                )
                            ),
                            
                            # Bloc d'informations épuré (Lignes d'infos style List Tile)
                            ft.Container(
                                bgcolor="#F8F9FA",
                                border_radius=10,
                                padding=14,
                                margin=ft.margin.only(bottom=24),
                                content=ft.Column(
                                    spacing=12,
                                    controls=[
                                        # Ligne Email
                                        ft.Row(
                                            controls=[
                                                ft.Image(resource_path("assets/icons/black/mail.svg"), width=16, height=16, color="#6C757D") if os.path.exists(resource_path("assets/icons/black/mail.svg")) else ft.Icon(ft.Icons.EMAIL_OUTLINED, size=16, color="#6C757D"),
                                                ft.Text(self.user_email, size=13, font_family="PPM", color="#495057", overflow=ft.TextOverflow.ELLIPSIS)
                                            ],
                                            spacing=10
                                        ),
                                        # Ligne ID Établissement (Tenant Name)
                                        ft.Row(
                                            controls=[
                                                ft.Image(resource_path("assets/icons/black/building.svg"), width=16, height=16, color="#6C757D") if os.path.exists(resource_path("assets/icons/black/building.svg")) else ft.Icon(ft.Icons.BUSINESS_OUTLINED, size=16, color="#6C757D"),
                                                ft.Text(self.tenant_name if self.tenant_name else "Aucun établissement", size=13, font_family="PPM", color="#495057")
                                            ],
                                            spacing=10
                                        ),
                                    ]
                                )
                            ),
                            
                            # Bouton de déconnexion stylisé
                            ft.Container(
                                width=float("inf"),
                                content=MyButton(
                                    icon=resource_path('assets/icons/white/circle-x.svg'),
                                    title="Se déconnecter",
                                    click=None,  # Relie ta fonction de déconnexion ici
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
        self.st_form = ft.Container(padding=30)
        self.st_container = ft.Container(
            **ct_style,
            content=ft.Container(
                **intern_ct_style, width=500, height=600,
                content=self.st_form
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
            **login_style,
            label="Nouveau mot de passe",
            password=True,
            can_reveal_password=True,
            prefix_icon=ft.Icons.LOCK_RESET_OUTLINED,
        )
        
        self.confirm_password_tf = ft.TextField(
            **login_style,
            label="Confirmer le mot de passe",
            password=True,
            can_reveal_password=True,
            prefix_icon=ft.Icons.LOCK_OUTLINED,
            height=48
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
            self.show_modal_error("Veuillez remplir les deux champs.")
            return

        if len(new_pwd) < 6:
            self.show_modal_error("Le mot de passe doit contenir au moins 6 caractères.")
            return

        if new_pwd != confirm_pwd:
            self.show_modal_error("Les mots de passe ne correspondent pas.")
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

            # B. Mise à jour de la table profiles pour lever définitivement le flag de blocage
            supabase_client.table("profiles").update({"is_first_login": False}).eq("id", self.user_id).execute()

            # C. Nettoyage et mise à jour locale
            self.page.client_storage.set("IS_FIRST_LOGIN", False)
            self.is_first_login = False

            # Fermeture de la boîte modale
            self.password_modal.open = False
            self.page.update()

            # Message général de félicitations
            self.show_alert("Votre mot de passe a été configuré avec succès !", ft.Icons.CHECK_CIRCLE, GREEN_COLOR)

        except Exception as err:
            print(f"Erreur lors de la réinitialisation initiale : {err}")
            self.show_modal_error("Échec de la configuration. Réessayez.")
    
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

        elif 1 <= delay <= 30: 
            self.icone_abo.src = resource_path("assets/icons/others/calendar-heart-red.svg")
            self.abo.value = f"Expire dans {delay} jrs"
            self.abo.color = ft.Colors.RED_700
            self.ct_abo.bgcolor = ft.Colors.with_opacity(0.08, ft.Colors.RED)
            self.ct_abo.border = ft.border.all(1, ft.Colors.with_opacity(0.2, ft.Colors.RED))

        elif 30 < delay <= 60: 
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
        self.show_alert("Déconnexion réussie. À bientôt !", ft.Icons.CHECK_CIRCLE_ROUNDED, GREEN_COLOR)
        
        # Un léger délai pour laisser le SnackBar s'afficher avant la redirection
        time.sleep(0.5)

        # 4. Redirection vers la vue de login/connexion
        # Remplace "/" par ta route de login réelle (ex: "/login") si nécessaire
        self.page.go("/")
        
        