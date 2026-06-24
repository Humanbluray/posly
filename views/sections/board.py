import flet as ft
from utils import (
    TENANT_ID, TENANT_NAME, ROLE, USER_ID, ACCESS_TOKEN, USER_NAME, EXPIRATION_DATE, PLAN_CHOISI,
    resource_path, BG_COLOR, convert_date_to_string, CARD_BG, SHADOW_COLOR, BORDER_COLOR, TEXT_PRIMARY, MAIN_COLOR,
    TEXT_SECONDARY, format_milliers_fr
)
from services.async_function import supabase_request_async
import asyncio, threading
from styles import stat_style, card_kpi_style
from datetime import datetime


class Board(ft.Container):
    def __init__(self, cp: object):
        super().__init__(
            expand=True,
            alignment=ft.alignment.top_center,
            padding=ft.padding.only(left=30, right=30, top=30, bottom=40),
        )
        self.cp = cp
        self.access_token = self.cp.page.client_storage.get(ACCESS_TOKEN)
        self.tenant_id = self.cp.page.client_storage.get(TENANT_ID)
        self.user_name = self.cp.page.client_storage.get(USER_NAME)

        # ----- 1. CHIFFRE D'AFFAIRES -----
        self.ca_global = ft.Text("-", size=22, font_family="PEB", color=TEXT_PRIMARY)
        self.ca_mois = ft.Text("-", size=22, font_family="PEB", color=TEXT_PRIMARY)
        self.ca_jour = ft.Text("-", size=22, font_family="PEB", color=TEXT_PRIMARY)
        self.ca_stats = ft.Row(spacing=20, wrap=True)

        # ----- 2. RENTABILITÉ & MARGES -----
        self.marge_globale = ft.Text("-", size=20, font_family="PEB", color=TEXT_PRIMARY)
        self.marge_mois = ft.Text("-", size=20, font_family="PEB", color=TEXT_PRIMARY)
        self.taux_marge = ft.Text("-", size=20, font_family="PEB", color=ft.Colors.GREEN)
        self.marge_kpi_container = ft.Column(spacing=14, horizontal_alignment=ft.CrossAxisAlignment.STRETCH)

        # Le conteneur du graphique linéaire de l'évolution
        self.chart_container = ft.Container(
            content=ft.ProgressRing(color=MAIN_COLOR, width=30, height=30),
            alignment=ft.alignment.center,
            expand=True
        )

        # ----- 3. OPÉRATIONNEL & STOCKS -----
        self.nb_ventes_jour = ft.Text("-", size=20, font_family="PEB", color=TEXT_PRIMARY)
        self.panier_moyen = ft.Text("-", size=20, font_family="PEB", color=TEXT_PRIMARY)
        self.valeur_stock = ft.Text("-", size=20, font_family="PEB", color=MAIN_COLOR)
        self.ops_kpi_container = ft.Column(spacing=14, horizontal_alignment=ft.CrossAxisAlignment.STRETCH)
        self.stock_distribution_container = ft.Column(spacing=12, scroll=ft.ScrollMode.AUTO, expand=True)

        # ----- 4. PALMARÈS & ANALYTIQUES -----
        # Le graphique en barres pour le Top 5 des produits
        self.top_products_container = ft.Container(
            content=ft.ProgressRing(color=MAIN_COLOR, width=30, height=30),
            alignment=ft.alignment.center,
            expand=True
        )
        # Le tableau dynamique pour le classement des catégories
        self.type_classement_container = ft.Column(
            spacing=10,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            scroll=ft.ScrollMode.AUTO
        )

        # Injection des écrans de chargement initiaux
        self.ca_stats.controls = [ft.ProgressRing(color=MAIN_COLOR, width=24, height=24)]
        self.marge_kpi_container.controls = [ft.ProgressRing(color=MAIN_COLOR, width=24, height=24)]
        self.ops_kpi_container.controls = [ft.ProgressRing(color=MAIN_COLOR, width=24, height=24)]
        self.stock_distribution_container.controls = [ft.ProgressRing(color=MAIN_COLOR, width=24, height=24)]
        self.type_classement_container.controls = [ft.ProgressRing(color=MAIN_COLOR, width=24, height=24)]

        # ----- LAYOUT PRINCIPAL DE L'INTERFACE -----
        self.content = ft.Column(
            expand=True, scroll=ft.ScrollMode.AUTO,
            spacing=28,
            controls=[
                # En-tête d'accueil personnalisé
                ft.Column(
                    controls=[
                        ft.Text(f"Bonjour {self.user_name} 👋", size=22, font_family="PEB"),
                        ft.Text("Voici les performances de votre activité", size=13, color=TEXT_SECONDARY,
                                font_family="PPN")
                    ], spacing=2
                ),

                # Section 1 : Chiffre d'Affaires Global
                ft.Container(
                    **stat_style,
                    content=ft.Column(
                        spacing=14,
                        controls=[
                            ft.Row(controls=[
                                ft.Image(resource_path('assets/icons/grey/banknote-check.svg'), width=14, height=14),
                                ft.Text("Chiffre d'affaires", size=13, color=TEXT_SECONDARY, font_family="PPM"),
                            ]),
                            self.ca_stats,
                        ]
                    )
                ),

                # Section 2 : Analyse des Marges (Split 1/3 KPIs - 2/3 Graphique Linéaire)
                ft.Row(
                    spacing=20, alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.START,
                    controls=[
                        ft.Container(
                            **stat_style, width=320, height=330,
                            content=ft.Column(spacing=14, controls=[
                                ft.Row(controls=[
                                    ft.Image(resource_path('assets/icons/grey/dollar-sign.svg'), width=14, height=14),
                                    ft.Text("Indicateurs de Marge", size=13, color=TEXT_SECONDARY, font_family="PPM"),
                                ]),
                                self.marge_kpi_container,
                            ])
                        ),
                        # 🌟 GRAPHIQUE REINTEGRÉ ICI : Évolution CA vs Marge sur 7 jours
                        ft.Container(
                            **stat_style, expand=2, height=330,
                            content=ft.Column(spacing=14, expand=True, controls=[
                                ft.Row(controls=[
                                    ft.Icon(name=ft.Icons.TIMELINE, size=16, color=TEXT_SECONDARY),
                                    ft.Text("Évolution des 7 derniers jours (CA vs Marge Brute)", size=13,
                                            color=TEXT_SECONDARY, font_family="PPM"),
                                ]),
                                self.chart_container,
                            ])
                        )
                    ]
                ),

                # Section 3 : Opérationnel & Gestion des Stocks (Split 50 / 50)
                ft.Row(
                    spacing=20, alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.START,
                    controls=[
                        ft.Container(
                            **stat_style, expand=1, height=310,
                            content=ft.Column(spacing=14, controls=[
                                ft.Row(controls=[
                                    ft.Icon(name=ft.Icons.SHOPPING_BAG_OUTLINED, size=16, color=TEXT_SECONDARY),
                                    ft.Text("Efficacité Opérationnelle", size=13, color=TEXT_SECONDARY,
                                            font_family="PPM"),
                                ]),
                                self.ops_kpi_container,
                            ])
                        ),
                        ft.Container(
                            **stat_style, expand=1, height=310,
                            content=ft.Column(spacing=14, controls=[
                                ft.Row(controls=[
                                    ft.Icon(name=ft.Icons.LAYERS_OUTLINED, size=16, color=TEXT_SECONDARY),
                                    ft.Text("Répartition des Stocks par Catégorie", size=13, color=TEXT_SECONDARY,
                                            font_family="PPM"),
                                ]),
                                self.stock_distribution_container,
                            ])
                        )
                    ]
                ),

                # Section 4 : Classements & Décisionnel (Split 50 / 50 avec Graphique en barres)
                ft.Row(
                    spacing=20, alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.START,
                    controls=[
                        # 🌟 GRAPHIQUE EN BARRES RÉINTÉGRÉ ICI : Top 5 Produits
                        ft.Container(
                            **stat_style, expand=1, height=340,
                            content=ft.Column(spacing=14, expand=True, controls=[
                                ft.Row(controls=[
                                    ft.Icon(name=ft.Icons.BAR_CHART_ROUNDED, size=16, color=TEXT_SECONDARY),
                                    ft.Text("Top 5 des Articles les plus vendus ce mois", size=13, color=TEXT_SECONDARY,
                                            font_family="PPM"),
                                ]),
                                self.top_products_container,
                            ])
                        ),

                        # TABLEAU DE CLASSEMENT RÉINTEGRÉ ICI : Performance des Catégories
                        ft.Container(
                            **stat_style, expand=1, height=340,
                            content=ft.Column(spacing=14, expand=True, controls=[
                                ft.Row(controls=[
                                    ft.Icon(name=ft.Icons.LEADERBOARD_OUTLINED, size=16, color=TEXT_SECONDARY),
                                    ft.Text("Classement de Performance par Catégorie", size=13, color=TEXT_SECONDARY,
                                            font_family="PPM"),
                                ]),
                                self.type_classement_container,
                            ])
                        )
                    ]
                )
            ]
        )

        self.on_mount()

    @staticmethod
    def build_stat_card_vertical(title: str, icon: str, value_control: ft.Text, unit: str = "XAF",
                                 icon_is_flet: bool = False):
        icon_element = ft.Icon(name=icon, size=14, color=TEXT_SECONDARY) if icon_is_flet else ft.Image(
            resource_path(icon), width=14, height=14, color=TEXT_SECONDARY)
        return ft.Container(
            bgcolor=ft.Colors.with_opacity(0.02, TEXT_SECONDARY), border_radius=10, padding=ft.padding.all(12),
            border=ft.border.all(0.5, ft.Colors.with_opacity(0.05, TEXT_SECONDARY)),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Column(spacing=2, controls=[
                        ft.Text(title, size=11, font_family="PPM", color=TEXT_SECONDARY),
                        ft.Row(spacing=4, controls=[value_control,
                                                    ft.Text(unit, size=12, font_family="PPM", color=TEXT_SECONDARY)])
                    ]),
                    icon_element
                ]
            )
        )

    @staticmethod
    def build_stat_item(title: str, icon: str, object_value: object, percent, unit: str = "XAF"):
        if percent is not None:
            prog_icon = resource_path('assets/icons/others/trending-up.svg') if float(percent) >= 0 else resource_path(
                'assets/icons/others/trending-down.svg')
            color = "green" if float(percent) >= 0 else "red"
            percent_part = ft.Row(controls=[ft.Text(f"{percent:.2f}%", size=11, font_family="PPN", color=color),
                                            ft.Image(prog_icon, width=12, height=12)], spacing=3)
        else:
            percent_part = ft.Text("")

        return ft.Container(
            bgcolor=ft.Colors.WHITE, border_radius=12, padding=ft.padding.all(14),
            shadow=ft.BoxShadow(spread_radius=0, blur_radius=8, color=ft.Colors.with_opacity(0.06, ft.Colors.BLACK),
                                offset=ft.Offset(0, 4)),
            border=ft.border.all(0.5, ft.Colors.with_opacity(0.08, ft.Colors.BLACK)),
            width=260, height=90,
            content=ft.Column(
                spacing=2,
                controls=[
                    ft.Row(controls=[ft.Text(title, size=12, font_family="PPM", color=TEXT_SECONDARY),
                                     ft.Image(resource_path(icon), width=14, height=14, color=TEXT_SECONDARY)],
                           alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Row(controls=[object_value, ft.Text(unit, size=12, font_family="PPM", color=TEXT_SECONDARY)],
                           spacing=4),
                    percent_part
                ]
            )
        )

    def on_mount(self):
        def runner():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            # Exécution synchronisée globale de TOUTES les requêtes analytiques en parallèle
            loop.run_until_complete(asyncio.gather(
                self.get_ca_kpis(),
                self.get_marge_kpis(),
                self.get_ops_and_stocks_kpis(),
                self.get_chart_7_days(),  # Chargement du graphique linéaire
                self.get_top_5_products(),  # Chargement du graphique en barres
                self.get_type_performance()  # Chargement du tableau des catégories
            ))
            loop.close()

        threading.Thread(target=runner).start()

    async def get_ca_kpis(self):
        try:
            kpi_ca = await supabase_request_async(
                access_token=self.access_token, tenant_id=self.tenant_id,
                table_name="v_kpi_chiffre_affaires", method="GET", params={'select': "*"}
            )
            if isinstance(kpi_ca, list) and len(kpi_ca) > 0:
                self.ca_global.value = format_milliers_fr(kpi_ca[0].get('ca_total', 0))
                ca_mois = kpi_ca[0].get('ca_mois_en_cours', 0)
                ca_mois_passe = kpi_ca[0].get('ca_mois_dernier', 0)
                percent_mois = (ca_mois - ca_mois_passe) * 100 / ca_mois_passe if ca_mois_passe > 0 else 100
                self.ca_mois.value = format_milliers_fr(ca_mois)

                ca_jour = kpi_ca[0].get('ca_aujourdhui', 0)
                ca_hier = kpi_ca[0].get('ca_hier', 0)
                percent_jour = (ca_jour - ca_hier) * 100 / ca_hier if ca_hier > 0 else 100
                self.ca_jour.value = format_milliers_fr(ca_jour)

                self.ca_stats.controls.clear()
                self.ca_stats.controls.extend([
                    self.build_stat_item("CA global", "assets/icons/grey/dollar-sign.svg", self.ca_global, None),
                    self.build_stat_item("CA mois en cours", "assets/icons/grey/badge-cent.svg", self.ca_mois,
                                         percent_mois),
                    self.build_stat_item("CA aujourd'hui", "assets/icons/grey/badge-cent.svg", self.ca_jour,
                                         percent_jour),
                ])
                self.ca_stats.update()

        except Exception as e:
            print(f"[ERREUR KPI CA] : {e}")

    async def get_marge_kpis(self):
        try:
            params = {"select": "qte, prix, factures(creation_month, creation_year), products(price_buy)",
                      "tenant_id": f"eq.{self.tenant_id}"}
            details = await supabase_request_async(access_token=self.access_token, tenant_id=self.tenant_id,
                                                   table_name="factures_details", method="GET", params=params)
            marge_totale, marge_mois_courant, ca_total_calculé = 0, 0, 0
            maintenant = datetime.now()

            if isinstance(details, list) and len(details) > 0:
                for item in details:
                    qte = item.get("qte", 0) or 0
                    prix_vente = item.get("prix", 0) or 0
                    product_info = item.get("products", {}) or {}
                    prix_achat = product_info.get("price_buy", 0) or 0
                    facture_info = item.get("factures", {}) or {}

                    ca_ligne = qte * prix_vente
                    marge_ligne = ca_ligne - (qte * prix_achat)
                    ca_total_calculé += ca_ligne
                    marge_totale += marge_ligne

                    if int(facture_info.get("creation_month", 0)) == maintenant.month and int(
                            facture_info.get("creation_year", 0)) == maintenant.year:
                        marge_mois_courant += marge_ligne

                taux_moyen = (marge_totale / ca_total_calculé * 100) if ca_total_calculé > 0 else 0
                self.marge_globale.value = format_milliers_fr(int(marge_totale))
                self.marge_mois.value = format_milliers_fr(int(marge_mois_courant))
                self.taux_marge.value = f"{taux_moyen:.1f}"

                self.marge_kpi_container.controls.clear()
                self.marge_kpi_container.controls.extend([
                    self.build_stat_card_vertical("Marge globale", "assets/icons/grey/dollar-sign.svg",
                                                  self.marge_globale),
                    self.build_stat_card_vertical("Marge mois en cours", "assets/icons/grey/badge-cent.svg",
                                                  self.marge_mois),
                    self.build_stat_card_vertical("Taux de marge moyen", "assets/icons/grey/trending-up.svg",
                                                  self.taux_marge, unit="%"),
                ])
                self.marge_kpi_container.update()
        except Exception as e:
            print(f"[ERREUR KPI MARGE] : {e}")

    async def get_ops_and_stocks_kpis(self):
        try:
            maintenant = datetime.now()
            date_aujourdhui_str = maintenant.strftime("%d/%m/%Y")

            factures = await supabase_request_async(
                access_token=self.access_token, tenant_id=self.tenant_id,
                table_name="factures", method="GET", params={"select": "*", "tenant_id": f"eq.{self.tenant_id}"}
            )
            ventes_du_jour, factures_mois_courant_count, ca_mois_courant = 0, 0, 0

            if isinstance(factures, list):
                for f in factures:
                    if f.get("creation_date", "") == date_aujourdhui_str:
                        ventes_du_jour += 1
                    if int(f.get("creation_month", 0)) == maintenant.month and int(
                            f.get("creation_year", 0)) == maintenant.year:
                        factures_mois_courant_count += 1
                        ca_mois_courant += (f.get("montant", 0) or 0)

            panier_moyen_val = ca_mois_courant / factures_mois_courant_count if factures_mois_courant_count > 0 else 0
            self.nb_ventes_jour.value = str(ventes_du_jour)
            self.panier_moyen.value = format_milliers_fr(int(panier_moyen_val))

            produits = await supabase_request_async(
                access_token=self.access_token, tenant_id=self.tenant_id,
                table_name="products", method="GET", params={"select": "*", "tenant_id": f"eq.{self.tenant_id}"}
            )
            valeur_totale_achat_stock, quantite_totale_stock, stocks_par_categorie = 0, 0, {}

            if isinstance(produits, list):
                for p in produits:
                    stock_qte = p.get("stock", 0) or 0
                    valeur_totale_achat_stock += (stock_qte * (p.get("price_buy", 0) or 0))
                    quantite_totale_stock += stock_qte
                    cat = p.get("product_type", "Autre") or "Autre"
                    stocks_par_categorie[cat] = stocks_par_categorie.get(cat, 0) + stock_qte

            self.valeur_stock.value = format_milliers_fr(int(valeur_totale_achat_stock))

            self.ops_kpi_container.controls.clear()
            self.ops_kpi_container.controls.extend([
                self.build_stat_card_vertical("Nombre de ventes (Aujourd'hui)", ft.Icons.RECEIPT_LONG_OUTLINED,
                                              self.nb_ventes_jour, unit="factures", icon_is_flet=True),
                self.build_stat_card_vertical("Panier moyen (Mois en cours)", ft.Icons.ADJUST_OUTLINED,
                                              self.panier_moyen, icon_is_flet=True),
                self.build_stat_card_vertical("Valeur du Stock (Prix d'achat)", ft.Icons.INVENTORY_2_OUTLINED,
                                              self.valeur_stock, icon_is_flet=True),
            ])
            self.ops_kpi_container.update()

            self.stock_distribution_container.controls.clear()
            if stocks_par_categorie:
                for cat, qte in sorted(stocks_par_categorie.items(), key=lambda item: item[1], reverse=True):
                    pourcentage = qte / quantite_totale_stock if quantite_totale_stock > 0 else 0
                    self.stock_distribution_container.controls.append(
                        ft.Column(spacing=4, controls=[
                            ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
                                ft.Text(cat, size=12, font_family="PPM", color=TEXT_PRIMARY),
                                ft.Text(f"{qte} pcs ({pourcentage * 100:.1f}%)", size=11, font_family="PPN",
                                        color=TEXT_SECONDARY),
                            ]),
                            ft.ProgressBar(value=pourcentage, color=MAIN_COLOR,
                                           bgcolor=ft.Colors.with_opacity(0.1, MAIN_COLOR), height=5)
                        ])
                    )
            self.stock_distribution_container.update()
        except Exception as e:
            print(f"[ERREUR KPI OPS/STOCKS] : {e}")

    # 🌟 GRAPHIQUE 1 MODIFIÉ : Ajout des magnifiques dégradés sous les courbes
    async def get_chart_7_days(self):
        try:
            chart_data = await supabase_request_async(
                access_token=self.access_token, tenant_id=self.tenant_id,
                table_name="v_chart_ca_marge_7_jours", method="GET", params={'select': "*"}
            )
            if isinstance(chart_data, list) and len(chart_data) > 0:
                ca_spots, marge_spots, x_labels = [], [], []
                max_value = 10000

                for index, row in enumerate(chart_data):
                    ca = float(row.get('chiffre_affaires', 0))
                    marge = float(row.get('marge_brute', 0))
                    date_str = row.get('jour_formate', '')

                    ca_spots.append(ft.LineChartDataPoint(index, ca))
                    marge_spots.append(ft.LineChartDataPoint(index, marge))
                    if max(ca, marge) > max_value:
                        max_value = max(ca, marge)

                    x_labels.append(
                        ft.ChartAxisLabel(
                            value=index,
                            label=ft.Container(
                                content=ft.Text(date_str, size=9, font_family="PPN", color=TEXT_SECONDARY),
                                margin=ft.margin.only(top=10))
                        )
                    )

                # Application correcte des dégradés avec la propriété 'above_line_bgcolor'
                data_lines = [
                    ft.LineChartData(
                        data_points=ca_spots,
                        color=MAIN_COLOR,
                        stroke_width=3,
                        curved=True,
                        below_line_gradient=ft.LinearGradient(
                            begin=ft.alignment.top_center,
                            end=ft.alignment.bottom_center,
                            colors=[
                                ft.Colors.with_opacity(0.18, MAIN_COLOR),  # Teinte semi-transparente en haut
                                ft.Colors.with_opacity(0.0, MAIN_COLOR)  # Disparition totale en bas
                            ]
                        )
                    ),
                    ft.LineChartData(
                        data_points=marge_spots,
                        color=ft.Colors.GREEN,
                        stroke_width=3,
                        curved=True,
                        below_line_gradient=ft.LinearGradient(
                            begin=ft.alignment.top_center,
                            end=ft.alignment.bottom_center,
                            colors=[
                                ft.Colors.with_opacity(0.15, ft.Colors.GREEN),  # Teinte verte en haut
                                ft.Colors.with_opacity(0.0, ft.Colors.GREEN)  # Disparition totale en bas
                            ]
                        )
                    )
                ]

                line_chart = ft.LineChart(
                    data_series=data_lines,
                    border=ft.Border(bottom=ft.BorderSide(1, BORDER_COLOR), left=ft.BorderSide(1, BORDER_COLOR)),
                    left_axis=ft.ChartAxis(
                        labels=[
                            ft.ChartAxisLabel(value=0, label=ft.Text("0", size=9, color=TEXT_SECONDARY)),
                            ft.ChartAxisLabel(value=max_value,
                                              label=ft.Text(f"{format_milliers_fr(int(max_value))}", size=9,
                                                            color=TEXT_SECONDARY))
                        ], labels_size=45
                    ),
                    bottom_axis=ft.ChartAxis(labels=x_labels, labels_size=25),
                    expand=True
                )

                legend = ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER, spacing=20,
                    controls=[
                        ft.Row([ft.Container(width=10, height=10, bgcolor=MAIN_COLOR, border_radius=2),
                                ft.Text("Chiffre d'Affaires", size=11, font_family="PPM")]),
                        ft.Row([ft.Container(width=10, height=10, bgcolor=ft.Colors.GREEN, border_radius=2),
                                ft.Text("Marge brute", size=11, font_family="PPM")]),
                    ]
                )

                self.chart_container.content = ft.Column(controls=[line_chart, legend], expand=True)
                self.chart_container.update()
        except Exception as e:
            print(f"[ERREUR GRAPH_7_JOURS] : {e}")


    # 🌟 GRAPHIQUE 2 VERSION PREMIUM : Top 5 des ventes interactif avec légende optimisée et grille
    async def get_top_5_products(self):
            try:
                params = {'select': "*"}
                top_data = await supabase_request_async(
                    access_token=self.access_token,
                    tenant_id=self.tenant_id,
                    table_name="v_chart_top_5_produits",
                    method="GET",
                    params=params
                )
                if isinstance(top_data, list) and len(top_data) > 0:
                    bar_groups = []
                    x_labels = []

                    # Palette SaaS Premium moderne et harmonieuse
                    colors_palette = [
                        MAIN_COLOR,  # Couleur principale de l'app
                        ft.Colors.GREEN,  # Vert Marge
                        ft.Colors.ORANGE,
                        ft.Colors.PURPLE,
                        ft.Colors.BLUE_GREY
                    ]

                    max_qty = 5
                    for index, row in enumerate(top_data):
                        designation = row.get('designation', 'Produit')
                        qty = float(row.get('quantite_vendue', 0))
                        if qty > max_qty:
                            max_qty = qty

                        color = colors_palette[index % len(colors_palette)]

                        # Construction des barres de données stylisées
                        bar_groups.append(
                            ft.BarChartGroup(
                                x=index,
                                bar_rods=[
                                    ft.BarChartRod(
                                        from_y=0,
                                        to_y=qty,
                                        color=color,
                                        width=24,
                                        border_radius=ft.border_radius.only(top_left=6, top_right=6),
                                        # Coins arrondis uniquement en haut
                                        # Info-bulle enrichie et claire au survol
                                        tooltip=f"{designation}\n{int(qty)} unités vendues"
                                    )
                                ]
                            )
                        )

                        # Étiquettes de l'axe X (P1, P2...)
                        x_labels.append(
                            ft.ChartAxisLabel(
                                value=index,
                                label=ft.Container(
                                    content=ft.Text(f"P{index + 1}", size=10, font_family="PPM", color=TEXT_SECONDARY),
                                    margin=ft.margin.only(top=5)
                                )
                            )
                        )

                    # Calcul dynamique des lignes de repère pour l'axe Y
                    max_qty = max_qty * 1.15 if max_qty > 0 else 5  # 15% d'espace libre au-dessus de la plus haute barre
                    y_step = max_qty / 3 if max_qty > 0 else 1
                    y_labels = []
                    for i in range(4):
                        val_y = i * y_step
                        y_labels.append(
                            ft.ChartAxisLabel(
                                value=val_y,
                                label=ft.Text(f"{int(val_y)}" if val_y > 0 else "0", size=9, color=TEXT_SECONDARY)
                            )
                        )

                    # Configuration du graphique en barres épuré
                    bar_chart = ft.BarChart(
                        bar_groups=bar_groups,
                        border=ft.Border(bottom=ft.BorderSide(0.5, BORDER_COLOR),
                                         left=ft.BorderSide(0.5, BORDER_COLOR)),
                        left_axis=ft.ChartAxis(labels=y_labels, labels_size=28),
                        bottom_axis=ft.ChartAxis(labels=x_labels, labels_size=25),
                        # Intégration d'une grille de fond discrète
                        horizontal_grid_lines=ft.ChartGridLines(
                            interval=y_step,
                            color=ft.Colors.with_opacity(0.04, TEXT_PRIMARY),
                            width=1,
                        ),
                        tooltip_bgcolor=ft.Colors.with_opacity(0.95, CARD_BG),
                        interactive=True,
                        expand=True
                    )

                    # En-tête intelligent unifié : Titre à gauche, Légende compacte à droite
                    header_row = ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Row(spacing=8, controls=[
                                ft.Icon(name=ft.Icons.BAR_CHART_OUTLINED, size=16, color=TEXT_SECONDARY),
                                # ft.Text("Top 5 des Articles les plus vendus ce mois", size=13, color=TEXT_SECONDARY,
                                #         font_family="PPM"),
                            ]),
                            # Légende ultra-compacte alignée horizontalement à l'extrême droite
                            ft.Row(
                                spacing=10,
                                controls=[
                                    ft.Row([ft.Container(width=6, height=6, bgcolor=colors_palette[i], border_radius=3),
                                            ft.Text(f"P{i + 1}", size=10, font_family="PPM", color=TEXT_SECONDARY)],
                                           spacing=3)
                                    for i in range(len(top_data))
                                ]
                            )
                        ]
                    )

                    # Assemblage final sans la grosse liste verticale du bas
                    self.top_products_container.content = ft.Column(
                        spacing=18,
                        expand=True,
                        controls=[
                            header_row,
                            ft.Container(content=bar_chart, expand=True, padding=ft.padding.only(right=10, top=5))
                        ]
                    )
                    self.update()

                else:
                    self.top_products_container.content = ft.Container(
                        content=ft.Text("Aucune vente enregistrée ce mois-ci.", font_family="PPM",
                                        color=TEXT_SECONDARY),
                        alignment=ft.alignment.center
                    )
                    self.update()

            except Exception as e:
                print(f"[ERREUR TOP_5_PRODUCTS] : {e}")
                self.top_products_container.content = ft.Container(
                    content=ft.Text("Impossible de charger le classement des produits", color="red"),
                    alignment=ft.alignment.center
                )
                self.update()

    # 🌟 TABLEAU 3 : Classement dynamique de performance des catégories
    async def get_type_performance(self):
        try:
            type_data = await supabase_request_async(
                access_token=self.access_token, tenant_id=self.tenant_id,
                table_name="v_kpi_classement_types", method="GET", params={'select': "*"}
            )
            self.type_classement_container.controls.clear()

            if isinstance(type_data, list) and len(type_data) > 0:
                header = ft.Container(
                    padding=ft.padding.only(bottom=8),
                    border=ft.Border(bottom=ft.BorderSide(1, BORDER_COLOR)),
                    content=ft.Row(
                        controls=[
                            ft.Text("Type de produit", size=12, font_family="PPM", color=TEXT_SECONDARY, expand=2),
                            ft.Text("CA Généré", size=12, font_family="PPM", color=TEXT_SECONDARY, expand=1,
                                    text_align=ft.TextAlign.RIGHT),
                            ft.Text("Marge", size=12, font_family="PPM", color=TEXT_SECONDARY, expand=1,
                                    text_align=ft.TextAlign.RIGHT),
                        ]
                    )
                )
                self.type_classement_container.controls.append(header)

                for index, row in enumerate(type_data[:4]):  # On prend le top 4 pour rester compact visuellement
                    product_type = row.get('product_type') or "Non spécifié"
                    ca = float(row.get('ca_genere', 0))
                    marge = float(row.get('marge_brute', 0))
                    bg = ft.Colors.with_opacity(0.02, TEXT_PRIMARY) if index % 2 == 0 else ft.Colors.TRANSPARENT

                    row_item = ft.Container(
                        padding=ft.padding.symmetric(vertical=6, horizontal=5),
                        bgcolor=bg, border_radius=6,
                        content=ft.Row(
                            controls=[
                                ft.Row([
                                    ft.Container(
                                        content=ft.Text(f"#{index + 1}", size=11, font_family="PEB",
                                                        color=MAIN_COLOR if index == 0 else TEXT_SECONDARY),
                                        alignment=ft.alignment.center, width=22, height=22,
                                        bgcolor=ft.Colors.with_opacity(0.1,
                                                                       MAIN_COLOR) if index == 0 else ft.Colors.with_opacity(
                                            0.05, TEXT_SECONDARY),
                                        border_radius=4
                                    ),
                                    ft.Text(product_type, size=13, font_family="PPM", color=TEXT_PRIMARY),
                                ], expand=2, spacing=8),
                                ft.Text(f"{format_milliers_fr(int(ca))}", size=12, font_family="PPN",
                                        color=TEXT_PRIMARY, expand=1, text_align=ft.TextAlign.RIGHT),
                                ft.Text(f"{format_milliers_fr(int(marge))}", size=12, font_family="PPN",
                                        color=ft.Colors.GREEN, expand=1, text_align=ft.TextAlign.RIGHT),
                            ]
                        )
                    )
                    self.type_classement_container.controls.append(row_item)
                self.type_classement_container.update()
        except Exception as e:
            print(f"[ERREUR TYPE_PERFORMANCE] : {e}")