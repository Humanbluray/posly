import flet as ft
from datetime import date
from utils import (
    MAIN_COLOR, ACCESS_TOKEN, USER_ID, TENANT_ID, USER_NAME, 
    ROLE, TENANT_NAME, PLAN_CHOISI, EXPIRATION_DATE, resource_path, USER_EMAIL, BG_COLOR, IS_FIRST_LOGIN
)
from styles import input_style, login_style, config_tf_style
from services.supabase_client import supabase_client
from components.components import MyTextButton


class LoginView(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(
            vertical_alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            bgcolor=BG_COLOR, route="/", padding=0,
        )
        self.page = page
        
        # --- CONFIGURATION DES INPUTS (Optimisation visuelle) ---
        self.login = ft.TextField(
            **login_style, 
            prefix_icon=ft.Icons.EMAIL_OUTLINED, 
            label="Adresse Email",
            height=48
        )
        self.password = ft.TextField(
            **login_style, 
            prefix_icon=ft.Icons.LOCK_OUTLINED, 
            can_reveal_password=True, 
            password=True, 
            label="Mot de passe",
            height=48
        )
        
        self.error_text = ft.Text("", color="red", font_family="PPM", size=13, visible=False)
        
        self.loader = ft.ProgressRing(width=20, height=20, stroke_width=2, color="white", visible=False)
        self.btn_text = ft.Text("Se connecter", size=16, font_family="PPM", color='white')
        
        self.login_button = ft.Container(
            bgcolor=MAIN_COLOR, padding=10, height=48, border_radius=12,
            content=ft.Row(controls=[self.loader, self.btn_text], alignment=ft.MainAxisAlignment.CENTER),
            on_click=self.sign_in,
            
        )

        # ============================================================
        # 1. SECTION GAUCHE : PRÉSENTATION MARKETING / SAAS SHOWCASE
        # ============================================================
        presentation_side = ft.Container(
            expand=6,
            bgcolor=BG_COLOR,
            padding=80,
            alignment=ft.alignment.center_left,
            content=ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.START,
                spacing=25,
                controls=[
                    # Logo en négatif blanc
                    ft.Row(
                        controls=[
                            ft.Text("Pos", size=42, color="black", font_family="PEB"),
                            ft.Text("ly", size=42, color=MAIN_COLOR, font_family="PEB")
                        ], spacing=0
                    ),
                    ft.Text(
                        "Pilotez votre commerce\nen toute simplicité.", 
                        size=36, color="grey",
                        font_family="PEB",
                        weight=ft.FontWeight.BOLD,
                        height=1.2
                    ),
                    ft.Text(
                        "La plateforme SaaS tout-en-un de gestion de point de vente, suivi des stocks en temps réel et clôtures comptables automatisées.",
                        size=18,
                        font_family="PPR",
                        max_lines=3
                    ),
                    ft.Divider(height=20, color=ft.Colors.with_opacity(0.2, "white")),
                    
                    # Petites puces de démonstration des features
                    ft.Column(
                        spacing=12,
                        controls=[
                            self._build_feature_row(ft.Icons.CHECK_CIRCLE_OUTLINE, "Gestion de caisse fluide"),
                            self._build_feature_row(ft.Icons.MONEY_OFF_CSRED_OUTLINED, "Zéro frais cachés, pack d'essai gratuit"),
                            self._build_feature_row(ft.Icons.ANALYTICS_OUTLINED, "Rapports d'activité et statistiques en 1 clic"),
                            
                        ]
                    )
                ]
            )
        )

        # ============================================================
        # 2. SECTION DROITE : FORMULAIRE DE CONNEXION PUR
        # ============================================================
        form_side = ft.Container(
            expand=4,
            bgcolor="white",
            padding=ft.padding.symmetric(horizontal=100, vertical=40),
            alignment=ft.alignment.center,
            content=ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                spacing=18,
                controls=[
                    ft.Column(
                        spacing=4,
                        controls=[
                            ft.Text("Bienvenue", size=28, font_family="PEB", color="black"),
                            ft.Text("Connectez-vous à votre espace de gestion", size=14, font_family="PPM", color="grey"),
                        ]
                    ),
                    ft.Divider(height=15, color=ft.Colors.TRANSPARENT),
                    
                    self.login,
                    self.password,
                    
                    self.error_text,
                    ft.Divider(height=5, color=ft.Colors.TRANSPARENT),
                    
                    self.login_button,
                    
                    ft.Divider(height=5, color=ft.Colors.TRANSPARENT),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        wrap=True,
                        controls=[
                            ft.Text("Pas encore de compte ?", size=14, font_family="PPI", color="grey"),
                            MyTextButton("Créer un espace", lambda e: self.page.go("/register"))
                        ]
                    ),
                ]
            )
        )

        # Assemblage final en ligne responsive split-screen
        self.controls = [
            ft.Row(
                expand=True,
                spacing=0,
                controls=[
                    presentation_side,
                    form_side
                ]
            )
        ]

    def _build_feature_row(self, icon: str, text: str):
        """Helper interne pour dessiner les lignes de fonctionnalités à gauche"""
        return ft.Row(
            spacing=10,
            controls=[
                ft.Icon(icon, color=MAIN_COLOR, size=18),
                ft.Text(text, size=16, font_family="PPR")
            ]
        )

    def sign_in(self, e):
        # email = self.login.value.strip()
        # password = self.password.value.strip()
        
        email = "test@mail.com"
        password = "123456"
        
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
                
                # 1. RÉCUPÉRATION DU PROFIL EN PREMIER (Pour valider le Tenant et ouvrir les RLS)
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
                        # Si pas de profil SQL, on se rabat temporairement sur les metadatas
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

                # 2. VÉRIFICATION DE L'ABONNEMENT
                try:
                    paiement = supabase_client.table("paiements") \
                        .select("date_expiration, plan_choisi, tenants(nom_entreprise)") \
                        .eq("tenant_id", tenant_id) \
                        .order("date_paiement", desc=True) \
                        .execute()

                    if not paiement.data:
                        # CAS NOUVEAU TENANT : Si aucun paiement n'existe encore, on applique une valeur par défaut (Période d'essai)
                        print("[DEBUG LOGIN] Aucun paiement trouvé, initialisation d'une période d'essai virtuelle.")
                        exp_date_str = "2026-12-31" # Donne une date de sécurité ou gère l'essai
                        tenant_name = "Nouvel Établissement"
                        plan_choisi = "Essai Gratuit"
                    else:
                        data = paiement.data[0]
                        exp_date_str = data.get("date_expiration")
                        tenant_name = data.get("tenants", {}).get("nom_entreprise", "Entreprise")
                        plan_choisi = data.get("plan_choisi", "Standard")

                    # Vérification de la date
                    y, m, d = map(int, exp_date_str.split('-'))
                    if date(y, m, d) < date.today():
                        self.show_error("Votre abonnement a expiré.")
                        return

                except Exception as e:
                    print(f"[DEBUG LOGIN] Erreur table paiements: {e}")
                    self.show_error("Erreur lors de la vérification des droits d'accès.")
                    return

                # 3. TOUT EST OK -> STOCKAGE LOCAL
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
            # Ce print est magique : il va t'afficher le VRAI message d'erreur dans ta console (ex: IndexError, AuthApiError, etc.)
            import traceback
            print("--- TRACEBACK DE L'ERREUR DE CONNEXION ---")
            traceback.print_exc()
            print("------------------------------------------")
            
            self.show_error(f"Erreur système : {str(error)}")

    def show_error(self, message: str):
        self.error_text.value = message
        self.error_text.visible = True
        self.loader.visible = False
        self.btn_text.value = "Se connecter"
        self.login_button.disabled = False
        self.page.update()