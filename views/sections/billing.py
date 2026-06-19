import flet as ft
from utils import (
    BG_COLOR, CARD_BG, MAIN_COLOR, TEXT_PRIMARY, TEXT_SECONDARY,
    BORDER_COLOR, SHADOW_COLOR, resource_path
)
import datetime


class BillingSection(ft.Container):
    def __init__(self, cp: object):
        super().__init__(expand=True, bgcolor=BG_COLOR, padding=20)
        self.cp = cp

        # Données de simulation des plans
        self.is_annual = False
        self.current_plan = "Pro"  # Exemple: récupéré dynamiquement depuis ta table 'paiements'

        # --- EN-TÊTE DE LA SECTION ---
        self.title = ft.Text("Abonnement & Facturation", size=26, font_family="PEB", color=TEXT_PRIMARY)
        self.subtitle = ft.Text("Gérez le plan de votre entreprise et consultez vos factures.", size=14,
                                font_family="PPM", color=TEXT_SECONDARY)

        # --- SÉLECTEUR DE PÉRIODE (Mensuel vs Annuel) ---
        self.period_switch = ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=15,
            controls=[
                ft.Text("Mensuel", size=14, font_family="PPB", color=TEXT_PRIMARY),
                ft.Switch(
                    value=self.is_annual,
                    active_color=MAIN_COLOR,
                    on_change=self.toggle_billing_period
                ),
                ft.Row(
                    spacing=5,
                    controls=[
                        ft.Text("Annuel", size=14, font_family="PPB", color=TEXT_PRIMARY),
                        ft.Container(
                            content=ft.Text("-20%", size=11, font_family="PEB", color="white"),
                            bgcolor=ft.Colors.GREEN_500,
                            padding=ft.padding.only(left=6, right=6, top=2, bottom=2),
                            border_radius=10
                        )
                    ]
                )
            ]
        )

        # Conteneur qui va accueillir les 3 cartes de prix
        self.cards_row = ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20,
            wrap=True
        )

        # --- TABLEAU DES HISTORIQUES DE PAIEMENT ---
        self.history_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Date", font_family="PPB")),
                ft.DataColumn(ft.Text("Plan", font_family="PPB")),
                ft.DataColumn(ft.Text("Mode", font_family="PPB")),
                ft.DataColumn(ft.Text("Montant", font_family="PPB")),
                ft.DataColumn(ft.Text("Statut", font_family="PPB")),
            ],
            rows=[]
        )

        # Assemblage de la vue complète
        self.content = ft.ListView(
            expand=True,
            spacing=30,
            controls=[
                ft.Column([self.title, self.subtitle], spacing=5),
                self.period_switch,
                self.cards_row,
                ft.Divider(height=1, color=BORDER_COLOR),
                ft.Column(
                    controls=[
                        ft.Text("Historique des transactions", size=18, font_family="PEB", color=TEXT_PRIMARY),
                        ft.Container(
                            content=self.history_table,
                            border=ft.border.all(1, BORDER_COLOR),
                            border_radius=12,
                            padding=10,
                            bgcolor=CARD_BG
                        )
                    ],
                    spacing=15
                )
            ]
        )

        # Initialisation de l'affichage
        self.build_pricing_cards()
        self.load_payment_history()

    def build_pricing_cards(self):
        """Génère les cartes de prix dynamiquement selon la période choisie"""
        self.cards_row.controls.clear()

        # Configuration des offres
        plans = [
            {
                "name": "Starter",
                "desc": "Idéal pour les petites boutiques ou caisses uniques.",
                "price_month": 15000,
                "price_year": 144000,  # 12000 / mois
                "features": ["1 Utilisateur standard", "Gestion de stock basique", "Export Excel des ventes",
                             "Support par email"],
                "popular": False
            },
            {
                "name": "Pro",
                "desc": "Le choix parfait pour les entreprises en croissance.",
                "price_month": 35000,
                "price_year": 336000,  # 28000 / mois
                "features": ["Utilisateurs illimités", "Multi-boutiques / Tenants", "Analytiques & Graphiques avancés",
                             "Générateur de tickets PDF", "Support prioritaire 24/7"],
                "popular": True  # Applique un style distinctif "Recommandé"
            },
            {
                "name": "Enterprise",
                "desc": "Pour les infrastructures lourdes avec besoins sur mesure.",
                "price_month": 75000,
                "price_year": 720000,  # 60000 / mois
                "features": ["Tout le plan Pro", "Accès API dédié", "Base de données isolée",
                             "Accompagnement et formation", "SLA de disponibilité 99.9%"],
                "popular": False
            }
        ]

        for p in plans:
            price = p["price_year"] if self.is_annual else p["price_month"]
            period_label = "/ an" if self.is_annual else "/ mois"
            is_current = self.current_plan == p["name"]

            # Liste des features de l'offre
            features_list = ft.Column(spacing=10)
            for f in p["features"]:
                features_list.controls.append(
                    ft.Row([
                        ft.Icon(ft.Icons.CHECK_CIRCLE_ROUNDED,
                                color=MAIN_COLOR if p["popular"] else ft.Colors.GREEN_500, size=18),
                        ft.Text(f, size=13, font_family="PPM", color=TEXT_PRIMARY)
                    ], alignment=ft.MainAxisAlignment.START)
                )

            # Gestion du bouton d'action
            if is_current:
                action_btn = ft.ElevatedButton(
                    text="Plan actuel",
                    disabled=True,
                    style=ft.ButtonStyle(
                        bgcolor=ft.Colors.GREY_300,
                        color=ft.Colors.GREY_600,
                        shape=ft.RoundedRectangleBorder(radius=8)
                    ),
                    width=250, height=45
                )
            else:
                action_btn = ft.ElevatedButton(
                    text=f"Choisir {p['name']}",
                    bgcolor=MAIN_COLOR if p["popular"] else "black",
                    color="white",
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                    width=250, height=45,
                    on_click=lambda e, plan_name=p["name"], plan_price=price: self.change_plan_request(plan_name,
                                                                                                       plan_price)
                )

            # Design de la carte individuelle
            card = ft.Container(
                width=290,
                height=460,
                bgcolor=CARD_BG,
                border_radius=16,
                padding=24,
                border=ft.border.all(2, MAIN_COLOR if p["popular"] else BORDER_COLOR),
                shadow=ft.BoxShadow(
                    spread_radius=1, blur_radius=15,
                    color=ft.Colors.with_opacity(0.15, MAIN_COLOR) if p["popular"] else SHADOW_COLOR
                ),
                content=ft.Column(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Column([
                            # Badge "Populaire" si applicable
                            ft.Row([
                                ft.Text(p["name"], size=20, font_family="PEB", color=TEXT_PRIMARY),
                                ft.Container(
                                    content=ft.Text("POPULAIRE", size=9, font_family="PEB", color="white"),
                                    bgcolor=MAIN_COLOR,
                                    padding=ft.padding.only(left=8, right=8, top=3, bottom=3),
                                    border_radius=10,
                                    visible=p["popular"]
                                )
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),

                            ft.Text(p["desc"], size=12, font_family="PPM", color=TEXT_SECONDARY, height=40),
                            ft.Divider(height=10, color=BORDER_COLOR),

                            # Prix
                            ft.Row([
                                    ft.Text(f"{price:,}", size=28, font_family="PEB", color=TEXT_PRIMARY),
                                    ft.Text(f" FCFA{period_label}", size=12, font_family="PPM", color=TEXT_SECONDARY)
                                ], alignment=ft.MainAxisAlignment.START,
                            ),

                            ft.Divider(height=15, color=ft.Colors.TRANSPARENT),
                            features_list
                        ]),
                        action_btn
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                )
            )
            self.cards_row.controls.append(card)

    def toggle_billing_period(self, e):
        """Bascule entre l'affichage mensuel et annuel"""
        self.is_annual = e.control.value
        self.build_pricing_cards()
        self.update()

    def load_payment_history(self):
        """Simule le chargement de l'historique depuis ta table `public.paiements`"""
        # À remplacer par ton appel supabase_request_async à terme !
        mock_data = [
            {"date": "15/05/2026", "plan": "Pro (Mensuel)", "mode": "MOMO", "amount": "35,000 FCFA",
             "status": "Réussi"},
            {"date": "15/04/2026", "plan": "Pro (Mensuel)", "mode": "Cash", "amount": "35,000 FCFA",
             "status": "Réussi"},
            {"date": "15/03/2026", "plan": "Starter (Mensuel)", "mode": "OM", "amount": "15,000 FCFA",
             "status": "Réussi"}
        ]

        self.history_table.rows.clear()
        for txn in mock_data:
            self.history_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(txn["date"], font_family="PPM")),
                        ft.DataCell(ft.Text(txn["plan"], font_family="PPM")),
                        ft.DataCell(ft.Text(txn["mode"], font_family="PPM")),
                        ft.DataCell(ft.Text(txn["amount"], font_family="PPB")),
                        ft.DataCell(
                            ft.Container(
                                content=ft.Text(txn["status"], size=12, color="white", font_family="PPB"),
                                bgcolor=ft.Colors.GREEN_400,
                                padding=ft.padding.only(left=8, right=8, top=3, bottom=3),
                                border_radius=6
                            )
                        ),
                    ]
                )
            )

    def change_plan_request(self, plan_name: str, price: int):
        """Déclenche la logique de changement de plan ou ouvre le tunnel de paiement"""
        print(f"Demande de migration vers : {plan_name} au prix de {price} FCFA")

        # Exemple d'alerte / Dialogue de confirmation d'achat
        self.current_plan = plan_name
        self.build_pricing_cards()

        # Tu peux appeler ici une fonction globale pour afficher une alerte de succès :
        if hasattr(self.cp, 'show_alert'):
            self.cp.show_alert(
                f"Demande d'abonnement au plan {plan_name} enregistrée !",
                ft.Icons.CREDIT_CARD_ROUNDED,
                MAIN_COLOR
            )
        self.update()

