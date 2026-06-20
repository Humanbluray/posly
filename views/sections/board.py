import flet as ft
from utils import (
    TENANT_ID, TENANT_NAME, ROLE, USER_ID, ACCESS_TOKEN, USER_NAME, EXPIRATION_DATE, PLAN_CHOISI,
    resource_path, BG_COLOR, convert_date_to_string, CARD_BG, SHADOW_COLOR, BORDER_COLOR, TEXT_PRIMARY, MAIN_COLOR,
    TEXT_SECONDARY, format_milliers_fr
)
from services.async_function import supabase_request_async
import asyncio, threading
from styles import stat_style


class Board(ft.Container):
    def __init__(self, cp: object):
        super().__init__(
            expand=True,
            alignment=ft.alignment.top_center,
            padding=ft.padding.only(left=30, right=30, top=30, bottom=40),
        )
        self.cp = cp
        self.access_token = self.cp.page.client_storage.get(ACCESS_TOKEN)
        self.role = self.cp.page.client_storage.get(ROLE)
        self.user_id = self.cp.page.client_storage.get(USER_ID)
        self.tenant_id = self.cp.page.client_storage.get(TENANT_ID)
        self.tenant_name = self.cp.page.client_storage.get(TENANT_NAME)
        self.user_name = self.cp.page.client_storage.get(USER_NAME)
        self.plan_choisi = self.cp.page.client_storage.get(PLAN_CHOISI)
        self.expiration_date = self.cp.page.client_storage.get(EXPIRATION_DATE)

        # ----- KPI containers -----
        self.ca_global = ft.Text("-", size=22, font_family="PEB")
        self.ca_mois = ft.Text("-", size=22, font_family="PEB")
        self.ca_jour = ft.Text("-", size=22, font_family="PEB")
        self.ca_stats = ft.ResponsiveRow(spacing=20, run_spacing=20)

        self.marge_global = ft.Text("-", size=22, font_family="PEB")
        self.marge_mois = ft.Text("-", size=22, font_family="PEB")
        self.marge_jour = ft.Text("-", size=22, font_family="PEB")
        self.marge_stats = ft.ResponsiveRow(spacing=20, run_spacing=20)

        self.panier_val = ft.Text("-", size=22, font_family="PEB")
        self.volume_val = ft.Text("-", size=22, font_family="PEB")
        self.mix_stats = ft.ResponsiveRow(spacing=20, run_spacing=20)

        self.valeur_stock = ft.Text("-", size=22, font_family="PEB")
        self.produits_rupture = ft.Text("-", size=22, font_family="PEB", color="red")
        self.stock_stats = ft.ResponsiveRow(spacing=20, run_spacing=20)

        self.chart_container = ft.Container(
            content=ft.ProgressRing(color=MAIN_COLOR, width=50, height=50),
            alignment=ft.alignment.center,
            height=320,
            expand=True,
        )

        self.top_products_container = ft.Container(
            content=ft.ProgressRing(color=MAIN_COLOR, width=50, height=50),
            alignment=ft.alignment.center,
            height=320,
            expand=True,
        )

        self.type_classement_container = ft.Column(
            controls=[ft.ProgressRing(color=MAIN_COLOR, width=50, height=50)],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

        # ----- Layout principal -----
        self.content = ft.Container(
            expand=True,
            padding=20,

            content=ft.Column(
                scroll=ft.ScrollMode.AUTO,
                spacing=20,

                controls=[

                    # ====================================================
                    # HEADER
                    # ====================================================

                    ft.Container(
                        padding=25,

                        bgcolor=CARD_BG,

                        border_radius=16,

                        border=ft.border.all(
                            1,
                            BORDER_COLOR
                        ),

                        content=ft.Column(
                            spacing=5,

                            controls=[

                                ft.Text(
                                    f"Bonjour {self.user_name} 👋",
                                    size=26,
                                    font_family="PEB"
                                ),

                                ft.Text(
                                    "Voici les performances de votre activité",
                                    size=13,
                                    color=TEXT_SECONDARY,
                                    font_family="PPN"
                                )
                            ]
                        )
                    ),

                    # ====================================================
                    # KPI 1
                    # ====================================================

                    ft.ResponsiveRow(
                        controls=[
                            self.build_card_container(self.ca_stats, 3),
                            self.build_card_container(self.marge_stats, 3),
                            self.build_card_container(self.mix_stats, 3),
                            self.build_card_container(self.stock_stats, 3),
                        ]
                    ),

                    # ====================================================
                    # GRAPHIQUES
                    # ====================================================

                    ft.ResponsiveRow(

                        controls=[

                            ft.Container(
                                col={"xs": 12, "lg": 7},

                                bgcolor=CARD_BG,

                                border_radius=16,

                                border=ft.border.all(
                                    1,
                                    BORDER_COLOR
                                ),

                                padding=20,

                                content=ft.Column(
                                    controls=[

                                        ft.Text(
                                            "Évolution des ventes",
                                            size=18,
                                            font_family="PPM"
                                        ),

                                        self.chart_container
                                    ]
                                )
                            ),

                            ft.Container(
                                col={"xs": 12, "lg": 5},

                                bgcolor=CARD_BG,

                                border_radius=16,

                                border=ft.border.all(
                                    1,
                                    BORDER_COLOR
                                ),

                                padding=20,

                                content=ft.Column(
                                    controls=[

                                        ft.Text(
                                            "Top produits",
                                            size=18,
                                            font_family="PPM"
                                        ),

                                        self.top_products_container
                                    ]
                                )
                            ),
                        ]
                    ),

                    # ====================================================
                    # PERFORMANCE PAR CATEGORIE
                    # ====================================================

                    ft.Container(

                        bgcolor=CARD_BG,

                        border_radius=16,

                        border=ft.border.all(
                            1,
                            BORDER_COLOR
                        ),

                        padding=20,

                        content=ft.Column(
                            controls=[

                                ft.Text(
                                    "Performance par catégorie",
                                    size=18,
                                    font_family="PPM"
                                ),

                                self.type_classement_container
                            ]
                        )
                    ),
                ]
            )
        )

        self.on_mount()

    def build_card_container(self, content, lg=3):

        return ft.Container(
            col={
                "xs": 12,
                "sm": 6,
                "md": 6,
                "lg": lg
            },

            bgcolor=CARD_BG,

            border_radius=16,

            border=ft.border.all(
                1,
                BORDER_COLOR
            ),

            padding=20,

            content=content
        )

    # ---- Méthode utilitaire pour titre de section ----
    def _build_section_title(self, title: str, icon_path: str, icon_size: int = 20):
        return ft.Row(
            controls=[
                ft.Image(src=resource_path(icon_path), width=icon_size, height=icon_size, color=MAIN_COLOR),
                ft.Text(title, size=18 if icon_size <= 20 else 22, font_family="PPM", color=TEXT_PRIMARY, weight=ft.FontWeight.W_600),
            ],
            spacing=10,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

    # ---- build_stat_item avec style pro ----
    def build_stat_item(self, title: str, icon: str, object_value: object, percent: float, unit: str = "XAF"):
        if percent is not None:
            if percent > 0:
                prog_icon = resource_path('assets/icons/others/trending-up.svg')
                color = "green"
            elif percent < 0:
                prog_icon = resource_path('assets/icons/others/trending-down.svg')
                color = 'red'
            else:
                prog_icon = resource_path('assets/icons/others/minus.svg')
                color = 'grey'

            percent_part = ft.Row(
                controls=[
                    ft.Text(f"{percent:.2f}%", size=12, font_family="PPN", color=color),
                    ft.Image(prog_icon, width=13, height=13)
                ],
                spacing=3,
                visible=True if percent is not None else False
            )
        else:
            percent_part = ft.Text("")

        # Carte moderne avec fond blanc, ombre, coins arrondis
        return ft.Container(
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            padding=ft.padding.all(14),
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=8,
                color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK),
                offset=ft.Offset(0, 4),
            ),
            border=ft.border.all(0.5, ft.Colors.with_opacity(0.1, ft.Colors.BLACK)),
            width=220,  # adaptez selon la largeur du parent
            height=90,
            content=ft.Column(
                spacing=4,
                controls=[
                    ft.Row(
                        controls=[
                            ft.Text(title, size=13, font_family="PPM", color=TEXT_SECONDARY, weight=ft.FontWeight.W_500),
                            ft.Image(resource_path(icon), width=16, height=16, color=TEXT_SECONDARY),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                    ft.Row(
                        controls=[
                            object_value,
                            ft.Text(unit, size=13, font_family="PPM", color=TEXT_SECONDARY),
                        ],
                        spacing=4,
                        alignment=ft.MainAxisAlignment.START,
                    ),
                    percent_part,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.START,
                # spacing=2,
            ),
        )

    # ---- Les méthodes asynchrones restent strictement identiques ----
    # (get_ca_kpis, get_marge_kpis, get_operational_kpis, get_stock_kpis, get_chart_7_days, get_top_5_products, get_type_performance)
    # Je ne les recopie pas ici pour éviter de surcharger, mais elles sont inchangées.
    # Assurez-vous de les inclure dans votre fichier final.
    @staticmethod
    def run_async_in_thread(coro):
        """Exécute une coroutine asynchrone dans un thread séparé"""
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
        await self.get_ca_kpis()
        await self.get_marge_kpis()
        await self.get_operational_kpis()
        await self.get_stock_kpis()
        await self.get_chart_7_days()
        await self.get_top_5_products()
        await self.get_type_performance()

    # ----- Les méthodes asynchrones restent inchangées (je les inclus par souci de complet) -----
    # Si vous les avez déjà ailleurs, vous pouvez supprimer les duplications.
    # Mais pour que le fichier soit fonctionnel, je les recopie ici.

    async def get_ca_kpis(self) -> dict:
        try:
            params = {'select': "*"}
            kpi_ca = await supabase_request_async(
                access_token=self.access_token,
                tenant_id=self.tenant_id,
                table_name="v_kpi_chiffre_affaires",
                method="GET",
                params=params
            )
            if isinstance(kpi_ca, list) and len(kpi_ca) > 0:
                ca_global = kpi_ca[0].get('ca_total', 0)
                self.ca_global.value = format_milliers_fr(ca_global)

                ca_mois = kpi_ca[0].get('ca_mois_en_cours')
                ca_mois_passe = kpi_ca[0].get('ca_mois_dernier')
                progres_mois = ca_mois - ca_mois_passe
                percent_mois = 100 if ca_mois_passe == 0 else progres_mois * 100 / ca_mois_passe
                self.ca_mois.value = format_milliers_fr(ca_mois)

                ca_jour = kpi_ca[0].get('ca_aujourdhui')
                ca_hier = kpi_ca[0].get('ca_hier')
                progres_jour = ca_jour - ca_hier
                percent_jour = 100 if ca_hier == 0 else progres_jour * 100 / ca_hier
                self.ca_jour.value = format_milliers_fr(ca_jour)

                self.ca_stats.controls.clear()
                self.ca_stats.controls.extend([
                    self.build_stat_item("CA global", "assets/icons/grey/dollar-sign.svg", self.ca_global, None),
                    self.build_stat_item("CA mois en cours", "assets/icons/grey/badge-cent.svg", self.ca_mois, percent_mois),
                    self.build_stat_item("CA aujourd'hui", "assets/icons/grey/badge-cent.svg", self.ca_jour, percent_jour),
                ])
                self.cp.page.update()
        except Exception as e:
            print(f"[ERREUR KPI CA] : {e}")

    async def get_marge_kpis(self):
        try:
            params = {'select': "*"}
            kpi_marge = await supabase_request_async(
                access_token=self.access_token,
                tenant_id=self.tenant_id,
                table_name="v_kpi_marge_brute",
                method="GET",
                params=params
            )
            if isinstance(kpi_marge, list) and len(kpi_marge) > 0:
                data = kpi_marge[0]
                marge_global = data.get('marge_total', 0)
                self.marge_global.value = format_milliers_fr(marge_global)

                marge_mois = data.get('marge_mois_en_cours', 0)
                marge_mois_passe = data.get('marge_mois_dernier', 0)
                progres_marge_mois = marge_mois - marge_mois_passe
                percent_marge_mois = 100.0 if marge_mois_passe == 0 else (progres_marge_mois * 100.0 / marge_mois_passe)
                self.marge_mois.value = format_milliers_fr(marge_mois)

                marge_jour = data.get('marge_aujourdhui', 0)
                marge_hier = data.get('marge_hier', 0)
                progres_marge_jour = marge_jour - marge_hier
                percent_marge_jour = 100.0 if marge_hier == 0 else (progres_marge_jour * 100.0 / marge_hier)
                self.marge_jour.value = format_milliers_fr(marge_jour)

                self.marge_stats.controls.clear()
                self.marge_stats.controls.extend([
                    self.build_stat_item("Marge globale", "assets/icons/grey/chart-line.svg", self.marge_global, None),
                    self.build_stat_item("Marge mois en cours", "assets/icons/grey/chart-line.svg", self.marge_mois, percent_marge_mois),
                    self.build_stat_item("Marge aujourd'hui", "assets/icons/grey/chart-line.svg", self.marge_jour, percent_marge_jour),
                ])
                self.cp.page.update()
        except Exception as e:
            print(f"[ERREUR KPI MARGE] : {e}")

    async def get_operational_kpis(self):
        try:
            params = {'select': "*"}
            kpi_data = await supabase_request_async(
                access_token=self.access_token,
                tenant_id=self.tenant_id,
                table_name="v_kpi_panier_volume",
                method="GET",
                params=params
            )
            if isinstance(kpi_data, list) and len(kpi_data) > 0:
                data = kpi_data[0]
                panier_mois = data.get('panier_mois_en_cours', 0)
                panier_passe = data.get('panier_mois_dernier', 0)
                progres_panier = panier_mois - panier_passe
                percent_panier = 100.0 if panier_passe == 0 else (progres_panier * 100.0 / panier_passe)
                self.panier_val.value = format_milliers_fr(panier_mois)

                vol_mois = data.get('vol_mois_en_cours', 0)
                vol_passe = data.get('vol_mois_dernier', 0)
                progres_vol = vol_mois - vol_passe
                percent_vol = 100.0 if vol_passe == 0 else (progres_vol * 100.0 / vol_passe)
                self.volume_val.value = format_milliers_fr(vol_mois)

                self.mix_stats.controls.clear()
                self.mix_stats.controls.extend([
                    self.build_stat_item("Panier moyen du mois", "assets/icons/grey/shopping-cart.svg", self.panier_val, percent_panier, "XAF"),
                    self.build_stat_item("Articles vendus ce mois", "assets/icons/grey/package.svg", self.volume_val, percent_vol, "Uts"),
                ])
                self.update()
        except Exception as e:
            print(f"[ERREUR KPI OPERATIONNEL] : {e}")

    async def get_stock_kpis(self):
        try:
            params = {'select': "*"}
            kpi_stock = await supabase_request_async(
                access_token=self.access_token,
                tenant_id=self.tenant_id,
                table_name="v_kpi_stock",
                method="GET",
                params=params
            )
            if isinstance(kpi_stock, list) and len(kpi_stock) > 0:
                data = kpi_stock[0]
                val_stock = data.get('valeur_stock_achat', 0)
                self.valeur_stock.value = format_milliers_fr(val_stock)
                nb_rupture = data.get('nb_produits_rupture', 0)
                self.produits_rupture.value = format_milliers_fr(nb_rupture)

                self.stock_stats.controls.clear()
                self.stock_stats.controls.extend([
                    self.build_stat_item("Valeur du stock (Achat)", "assets/icons/grey/dollar-sign.svg", self.valeur_stock, None, "XAF"),
                    self.build_stat_item("Articles en rupture", "assets/icons/grey/alert-circle.svg", self.produits_rupture, None, "Réf"),
                ])
                self.update()
        except Exception as e:
            print(f"[ERREUR KPI STOCK] : {e}")

    async def get_chart_7_days(self):
        try:
            params = {'select': "*"}
            chart_data = await supabase_request_async(
                access_token=self.access_token,
                tenant_id=self.tenant_id,
                table_name="v_chart_ca_marge_7_jours",
                method="GET",
                params=params
            )
            if isinstance(chart_data, list) and len(chart_data) > 0:
                ca_spots = []
                marge_spots = []
                x_labels = []
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
                                content=ft.Text(date_str, size=10, font_family="PPN", color=TEXT_SECONDARY),
                                margin=ft.margin.only(top=10)
                            )
                        )
                    )

                data_lines = [
                    ft.LineChartData(
                        data_points=ca_spots,
                        color=ft.Colors.BLUE,
                        stroke_width=3,
                        curved=True,
                        below_line_gradient=ft.LinearGradient(
                            begin=ft.alignment.top_center,
                            end=ft.alignment.bottom_center,
                            colors=[ft.Colors.with_opacity(0.1, ft.Colors.BLUE), ft.Colors.TRANSPARENT],
                        ),
                    ),
                    ft.LineChartData(
                        data_points=marge_spots,
                        color=ft.Colors.GREEN,
                        stroke_width=3,
                        curved=True,
                        below_line_gradient=ft.LinearGradient(
                            begin=ft.alignment.top_center,
                            end=ft.alignment.bottom_center,
                            colors=[ft.Colors.with_opacity(0.1, ft.Colors.GREEN), ft.Colors.TRANSPARENT],
                        ),
                    ),
                ]

                line_chart = ft.LineChart(
                    data_series=data_lines,
                    border=ft.Border(
                        bottom=ft.BorderSide(1, BORDER_COLOR),
                        left=ft.BorderSide(1, BORDER_COLOR)
                    ),
                    left_axis=ft.ChartAxis(
                        labels=[
                            ft.ChartAxisLabel(
                                value=0,
                                label=ft.Text("0", size=10, font_family="PPN", color=TEXT_SECONDARY)
                            ),
                            ft.ChartAxisLabel(
                                value=max_value,
                                label=ft.Text(f"{format_milliers_fr(int(max_value))}", size=10, font_family="PPN", color=TEXT_SECONDARY)
                            )
                        ],
                        labels_size=50,
                    ),
                    bottom_axis=ft.ChartAxis(
                        labels=x_labels,
                        labels_size=30,
                    ),
                    horizontal_grid_lines=ft.ChartGridLines(
                        interval=max_value / 4 if max_value > 0 else 1,
                        color=ft.Colors.with_opacity(0.05, TEXT_SECONDARY),
                        width=1,
                    ),
                    tooltip_bgcolor=CARD_BG,
                    expand=True,
                )

                legend = ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        ft.Row([ft.Container(width=12, height=12, bgcolor=ft.Colors.BLUE, border_radius=3), ft.Text("Chiffre d'Affaires", size=12, font_family="PPM")]),
                        ft.VerticalDivider(width=10),
                        ft.Row([ft.Container(width=12, height=12, bgcolor=ft.Colors.GREEN, border_radius=3), ft.Text("Marge brute", size=12, font_family="PPM")]),
                    ]
                )

                self.chart_container.content = ft.Column(
                    controls=[line_chart, legend],
                    expand=True
                )
                self.update()
        except Exception as e:
            print(f"[ERREUR GRAPH_7_JOURS] : {e}")
            self.chart_container.content = ft.Text("Impossible de charger le graphique", color="red")
            self.update()

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
                legend_items = []
                colors_palette = [ft.Colors.BLUE, ft.Colors.GREEN, ft.Colors.ORANGE, ft.Colors.PURPLE, ft.Colors.AMBER]
                max_qty = 5
                for index, row in enumerate(top_data):
                    designation = row.get('designation', 'Produit')
                    qty = float(row.get('quantite_vendue', 0))
                    if qty > max_qty:
                        max_qty = qty
                    color = colors_palette[index % len(colors_palette)]
                    short_name = designation if len(designation) <= 15 else f"{designation[:12]}..."
                    bar_groups.append(
                        ft.BarChartGroup(
                            x=index,
                            bar_rods=[
                                ft.BarChartRod(
                                    from_y=0,
                                    to_y=qty,
                                    color=color,
                                    width=22,
                                    border_radius=4,
                                    tooltip=f"{designation}\n{int(qty)} unités vendues"
                                )
                            ]
                        )
                    )
                    x_labels.append(
                        ft.ChartAxisLabel(
                            value=index,
                            label=ft.Container(
                                content=ft.Text(f"P{index+1}", size=11, font_family="PPM", color=TEXT_SECONDARY),
                                margin=ft.margin.only(top=5)
                            )
                        )
                    )
                    legend_items.append(
                        ft.Row(
                            controls=[
                                ft.Container(width=10, height=10, bgcolor=color, border_radius=2),
                                ft.Text(f"P{index+1}: {short_name} ({int(qty)} Uts)", size=11, font_family="PPN")
                            ],
                            spacing=5
                        )
                    )

                bar_chart = ft.BarChart(
                    bar_groups=bar_groups,
                    border=ft.Border(
                        bottom=ft.BorderSide(1, BORDER_COLOR),
                        left=ft.BorderSide(1, BORDER_COLOR)
                    ),
                    left_axis=ft.ChartAxis(
                        labels=[
                            ft.ChartAxisLabel(value=0, label=ft.Text("0", size=10, font_family="PPN", color=TEXT_SECONDARY)),
                            ft.ChartAxisLabel(value=max_qty, label=ft.Text(f"{int(max_qty)}", size=10, font_family="PPN", color=TEXT_SECONDARY))
                        ],
                        labels_size=30
                    ),
                    bottom_axis=ft.ChartAxis(
                        labels=x_labels,
                        labels_size=25
                    ),
                    horizontal_grid_lines=ft.ChartGridLines(
                        interval=max_qty / 3 if max_qty > 0 else 1,
                        color=ft.Colors.with_opacity(0.05, TEXT_SECONDARY),
                        width=1,
                    ),
                    tooltip_bgcolor=CARD_BG,
                    expand=True
                )

                legend_panel = ft.Row(
                    controls=legend_items,
                    wrap=True,
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=15
                )

                self.top_products_container.content = ft.Column(
                    controls=[
                        ft.Container(content=bar_chart, expand=True, padding=ft.padding.only(bottom=10)),
                        legend_panel
                    ],
                    expand=True
                )
                self.update()
            else:
                self.top_products_container.content = ft.Text("Aucune vente enregistrée ce mois-ci.", font_family="PPM")
                self.update()
        except Exception as e:
            print(f"[ERREUR TOP_5_PRODUCTS] : {e}")
            self.top_products_container.content = ft.Text("Impossible de charger le classement des produits", color="red")
            self.update()

    async def get_type_performance(self):
        try:
            params = {'select': "*"}
            type_data = await supabase_request_async(
                access_token=self.access_token,
                tenant_id=self.tenant_id,
                table_name="v_kpi_classement_types",
                method="GET",
                params=params
            )
            self.type_classement_container.controls.clear()

            if isinstance(type_data, list) and len(type_data) > 0:
                # En-tête du tableau
                header = ft.Container(
                    padding=ft.padding.only(bottom=10),
                    border=ft.Border(bottom=ft.BorderSide(1, BORDER_COLOR)),
                    content=ft.Row(
                        controls=[
                            ft.Text("Type de produit", size=14, font_family="PPM", color=TEXT_SECONDARY, expand=2),
                            ft.Text("CA Généré", size=14, font_family="PPM", color=TEXT_SECONDARY, expand=1, text_align=ft.TextAlign.RIGHT),
                            ft.Text("Marge brute", size=14, font_family="PPM", color=TEXT_SECONDARY, expand=1, text_align=ft.TextAlign.RIGHT),
                        ]
                    )
                )
                self.type_classement_container.controls.append(header)

                for index, row in enumerate(type_data):
                    product_type = row.get('product_type') or "Non spécifié"
                    ca = float(row.get('ca_genere', 0))
                    marge = float(row.get('marge_brute', 0))

                    # Alternance de fond
                    bg = ft.Colors.with_opacity(0.03, TEXT_PRIMARY) if index % 2 == 0 else ft.Colors.TRANSPARENT

                    row_item = ft.Container(
                        padding=ft.padding.symmetric(vertical=10, horizontal=5),
                        bgcolor=bg,
                        border_radius=6,
                        content=ft.Row(
                            controls=[
                                ft.Row([
                                    ft.Container(
                                        content=ft.Text(f"#{index+1}", size=12, font_family="PEB", color=ft.Colors.BLUE if index == 0 else TEXT_SECONDARY),
                                        alignment=ft.alignment.center,
                                        width=28,
                                        height=28,
                                        bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.BLUE) if index == 0 else ft.Colors.with_opacity(0.05, TEXT_SECONDARY),
                                        border_radius=6
                                    ),
                                    ft.Text(product_type, size=15, font_family="PPM", color=TEXT_PRIMARY),
                                ], expand=2, spacing=12),
                                ft.Text(f"{format_milliers_fr(int(ca))} XAF", size=14, font_family="PPN", color=TEXT_PRIMARY, expand=1, text_align=ft.TextAlign.RIGHT),
                                ft.Text(f"{format_milliers_fr(int(marge))} XAF", size=14, font_family="PPN", color=ft.Colors.GREEN, expand=1, text_align=ft.TextAlign.RIGHT),
                            ]
                        )
                    )
                    self.type_classement_container.controls.append(row_item)

                self.update()
            else:
                self.type_classement_container.controls.append(
                    ft.Text("Aucune donnée disponible pour ce mois.", font_family="PPM", color=TEXT_SECONDARY)
                )
                self.update()
        except Exception as e:
            print(f"[ERREUR TYPE_PERFORMANCE] : {e}")
            self.type_classement_container.controls.clear()
            self.type_classement_container.controls.append(
                ft.Text("Impossible de charger le classement des catégories", color="red")
            )
            self.update()