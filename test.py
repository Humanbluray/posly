import flet as ft  
from utils import (
    TENANT_ID, TENANT_NAME, ROLE, USER_ID, ACCESS_TOKEN, USER_NAME, EXPIRATION_DATE, PLAN_CHOISI, 
    resource_path, BG_COLOR, convert_date_to_string, CARD_BG, SHADOW_COLOR, BORDER_COLOR, TEXT_PRIMARY, MAIN_COLOR,
    TEXT_SECONDARY,  format_milliers_fr
)
from services.async_function import supabase_request_async
import asyncio, threading
from styles import stat_style
    

class Board(ft.Container):
    def __init__(self, cp: object):
        super().__init__(
            expand=True, alignment=ft.alignment.top_left
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
        
        # 🌟 INITIALISATION DES INSTANCES DE TEXTE
        # Chiffre d'affaires
        self.ca_global = ft.Text("-", size=16, font_family="PEB", color=TEXT_PRIMARY)
        self.ca_mois = ft.Text("-", size=16, font_family="PEB", color=TEXT_PRIMARY)
        self.ca_jour = ft.Text("-", size=16, font_family="PEB", color=TEXT_PRIMARY)
        
        # Marge brute
        self.marge_global = ft.Text("-", size=16, font_family="PEB", color=TEXT_PRIMARY)
        self.marge_mois = ft.Text("-", size=16, font_family="PEB", color=TEXT_PRIMARY)
        self.marge_jour = ft.Text("-", size=16, font_family="PEB", color=TEXT_PRIMARY)
        
        # Performance opérationnelle
        self.panier_val = ft.Text("-", size=16, font_family="PEB", color=TEXT_PRIMARY)
        self.volume_val = ft.Text("-", size=16, font_family="PEB", color=TEXT_PRIMARY)
        
        # Stocks
        self.valeur_stock = ft.Text("-", size=16, font_family="PEB", color=TEXT_PRIMARY)
        self.produits_rupture = ft.Text("-", size=16, font_family="PEB", color="red")
        
        # CONTENEURS RESPONSIVE POUR LES GRILLES DE STATS
        # 💡 Correction : On initialise avec des éléments temporaires pour forcer Flet à préparer le layout
        self.ca_stats = ft.ResponsiveRow(
            controls=[
                self.build_stat_item("Global", "assets/icons/grey/dollar-sign.svg", self.ca_global, None),
                self.build_stat_item("Ce mois", "assets/icons/grey/badge-cent.svg", self.ca_mois, 0.0),
                self.build_stat_item("Aujourd'hui", "assets/icons/grey/badge-cent.svg", self.ca_jour, 0.0)
            ],
            spacing=15, run_spacing=15
        )
        
        self.marge_stats = ft.ResponsiveRow(
            controls=[
                self.build_stat_item("Globale", "assets/icons/grey/chart-line.svg", self.marge_global, None),
                self.build_stat_item("Ce mois", "assets/icons/grey/chart-line.svg", self.marge_mois, 0.0),
                self.build_stat_item("Aujourd'hui", "assets/icons/grey/chart-line.svg", self.marge_jour, 0.0)
            ],
            spacing=15, run_spacing=15
        )
        
        self.mix_stats = ft.ResponsiveRow(
            controls=[
                self.build_stat_item("Panier moyen", "assets/icons/grey/shopping-cart.svg", self.panier_val, 0.0, "XAF", {"sm": 12, "md": 6}),
                self.build_stat_item("Articles vendus", "assets/icons/grey/package.svg", self.volume_val, 0.0, "Uts", {"sm": 12, "md": 6})
            ],
            spacing=15, run_spacing=15
        )
        
        self.stock_stats = ft.ResponsiveRow(
            controls=[
                self.build_stat_item("Valeur d'Achat", "assets/icons/grey/dollar-sign.svg", self.valeur_stock, None, "XAF", {"sm": 12, "md": 6}),
                self.build_stat_item("En rupture", "assets/icons/grey/alert-circle.svg", self.produits_rupture, None, "Réf", {"sm": 12, "md": 6})
            ],
            spacing=15, run_spacing=15
        )
        
        # Zone Graphique 7 jours
        self.chart_container = ft.Container(
            content=ft.ProgressRing(color=MAIN_COLOR, width=40, height=40),
            alignment=ft.alignment.center,
            height=260
        )
        
        # Zone Graphique Top 5 produits
        self.top_products_container = ft.Container(
            content=ft.ProgressRing(color=MAIN_COLOR, width=40, height=40),
            alignment=ft.alignment.center,
            height=260
        )
        
        # Zone Tableau Classement Catégories
        self.type_classement_container = ft.Column(
            controls=[ft.ProgressRing(color=MAIN_COLOR, width=40, height=40)],
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            spacing=0
        )
        
        # --- FONCTIONS DE CRÉATION DES CARTES VISUELLES ---
        
        def create_kpi_section(title: str, icon_path: str, stats_layout: ft.ResponsiveRow):
            return ft.Container(
                bgcolor="white",
                padding=20,
                border_radius=12,
                border=ft.border.all(1, BORDER_COLOR),
                content=ft.Column(
                    spacing=15,
                    controls=[
                        ft.Row(
                            spacing=8,
                            controls=[
                                ft.Image(resource_path(icon_path), width=16, height=16),
                                ft.Text(title, size=14, font_family="PPM", color=TEXT_SECONDARY)
                            ]
                        ),
                        stats_layout
                    ]
                )
            )

        def create_visual_card(title: str, icon_path: str, content_control: ft.Control):
            return ft.Container(
                bgcolor="white",
                padding=20,
                border_radius=12,
                border=ft.border.all(1, BORDER_COLOR),
                content=ft.Column(
                    spacing=15,
                    controls=[
                        ft.Row(
                            spacing=8,
                            controls=[
                                ft.Image(resource_path(icon_path), width=16, height=16),
                                ft.Text(title, size=15, font_family="PPM", color=TEXT_PRIMARY)
                            ]
                        ),
                        ft.Divider(height=1, color=BORDER_COLOR),
                        content_control
                    ]
                )
            )

        # --- CONFIGURATION DU CONTENU PRINCIPAL ---
        self.content = ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            spacing=20,
            controls=[
                # En-tête textuel
                ft.Container(
                    padding=ft.padding.only(left=5, top=10),
                    content=ft.Column([
                        ft.Text(f"Bienvenue {self.user_name}", size=18, font_family='PPM', color=TEXT_PRIMARY),
                        ft.Text("Voici l'état d'activité de votre entreprise pour aujourd'hui.", size=13, font_family='PPL', color=TEXT_SECONDARY),
                    ], spacing=2)
                ),
                
                # Bloc Chiffre d'affaires & Marge brute côte à côte
                ft.ResponsiveRow(
                    spacing=20,
                    run_spacing=20,
                    controls=[
                        ft.Container(create_kpi_section("Chiffre d'affaires", 'assets/icons/grey/dollar-sign.svg', self.ca_stats), col={"sm": 12, "md": 6}),
                        ft.Container(create_kpi_section("Marge brute", 'assets/icons/grey/chart-spline.svg', self.marge_stats), col={"sm": 12, "md": 6}),
                    ]
                ),
                
                # Bloc Performance & Stocks côte à côte
                ft.ResponsiveRow(
                    spacing=20,
                    run_spacing=20,
                    controls=[
                        ft.Container(create_kpi_section("Performance opérationnelle (Ce mois)", 'assets/icons/grey/shopping-bag.svg', self.mix_stats), col={"sm": 12, "md": 6}),
                        ft.Container(create_kpi_section("État Stocks (Instant T)", 'assets/icons/grey/package.svg', self.stock_stats), col={"sm": 12, "md": 6}),
                    ]
                ),
                
                # Zone Graphiques Responsives 
                ft.ResponsiveRow(
                    spacing=20,
                    run_spacing=20,
                    controls=[
                        ft.Container(create_visual_card("Tendances des 7 derniers jours", 'assets/icons/grey/activity.svg', self.chart_container), col={"sm": 12, "lg": 6}),
                        ft.Container(create_visual_card("Top 5 des produits les plus vendus (Ce mois)", 'assets/icons/grey/award.svg', self.top_products_container), col={"sm": 12, "lg": 6}),
                    ]
                ),
                
                # Tableau des catégories
                create_visual_card("Performance par Catégorie (Ce mois)", 'assets/icons/grey/list-sort-descending.svg', self.type_classement_container),
                
                # Padding de sécurité bas de page
                ft.Container(height=15)
            ]
        )
        
        self.on_mount()
    
    def build_stat_item(self, title: str, icon: str, object_value: object, percent: float, unit: str = "XAF", columns_dict: dict = None):
        """Génère une sous-carte KPI unifiée et intégrable dans une ResponsiveRow"""
        if columns_dict is None:
            columns_dict = {"sm": 12, "md": 4}
            
        percent_part = ft.Container()
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
                
            percent_part = ft.Container(
                bgcolor=ft.Colors.with_opacity(0.08, color),
                padding=ft.padding.symmetric(horizontal=8, vertical=4),
                border_radius=6,
                content=ft.Row(
                    spacing=4,
                    tight=True,
                    controls=[
                        ft.Text(f"{percent:.1f}%", size=11, font_family="PPM", color=color),
                        ft.Image(prog_icon, width=10, height=10)
                    ]
                )
            )
            
        return ft.Container(
            col=columns_dict,
            bgcolor=ft.Colors.with_opacity(0.2, BG_COLOR),
            border_radius=8,
            padding=12,
            content=ft.Column(
                spacing=8,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text(title, size=12, font_family="PPM", color=TEXT_SECONDARY),
                            ft.Image(resource_path(icon), width=14, height=14, opacity=0.5),
                        ]
                    ),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.BASELINE,
                        controls=[
                            ft.Row(
                                spacing=4,
                                tight=True,
                                vertical_alignment=ft.CrossAxisAlignment.BASELINE,
                                controls=[
                                    object_value,
                                    ft.Text(unit, size=11, font_family="PPM", color=TEXT_SECONDARY)
                                ]
                            ),
                            percent_part
                        ]
                    ),
                ]
            )
        )
        
    @staticmethod
    def run_async_in_thread(coro):
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
    
    async def get_ca_kpis(self) -> dict:
        try:
            params = {'select': "*"}
            kpi_ca = await supabase_request_async(
                access_token=self.access_token, tenant_id=self.tenant_id,
                table_name="v_kpi_chiffre_affaires", method="GET", params=params
            )
            
            if isinstance(kpi_ca, list) and len(kpi_ca) > 0:
                ca_global = kpi_ca[0].get('ca_total', 0)
                ca_mois = kpi_ca[0].get('ca_mois_en_cours', 0)
                ca_mois_passe = kpi_ca[0].get('ca_mois_dernier', 0)
                progres_mois = ca_mois - ca_mois_passe
                percent_mois = 100 if ca_mois_passe == 0 else progres_mois * 100 / ca_mois_passe
                     
                ca_jour = kpi_ca[0].get('ca_aujourdhui', 0)
                ca_hier = kpi_ca[0].get('ca_hier', 0)
                progres_jour = ca_jour - ca_hier
                percent_jour = 100 if ca_hier == 0 else progres_jour * 100 / ca_hier

                # 💡 Correction ici : On change d'abord les valeurs des objets Text
                self.ca_global.value = format_milliers_fr(ca_global)
                self.ca_mois.value = format_milliers_fr(ca_mois)
                self.ca_jour.value = format_milliers_fr(ca_jour)
                
                # On reconstruit proprement la ligne responsive pour mettre à jour les pourcentages (badges de tendance)
                self.ca_stats.controls.clear()
                self.ca_stats.controls.extend([
                    self.build_stat_item("Global", "assets/icons/grey/dollar-sign.svg", self.ca_global, None),
                    self.build_stat_item("Ce mois", "assets/icons/grey/badge-cent.svg", self.ca_mois, percent_mois),
                    self.build_stat_item("Aujourd'hui", "assets/icons/grey/badge-cent.svg", self.ca_jour, percent_jour)
                ])
                self.update()
            
        except Exception as e:
            print(f"[ERREUR KPI CA] : {e}")
            return {"ca_aujourdhui": 0, "ca_mois_en_cours": 0, "ca_total": 0}  
        
    async def get_marge_kpis(self):
        try:
            params = {'select': "*"}
            kpi_marge = await supabase_request_async(
                access_token=self.access_token, tenant_id=self.tenant_id,
                table_name="v_kpi_marge_brute", method="GET", params=params
            )
            
            if isinstance(kpi_marge, list) and len(kpi_marge) > 0:
                data = kpi_marge[0]
                marge_global = data.get('marge_total', 0)
                marge_mois = data.get('marge_mois_en_cours', 0)
                marge_mois_passe = data.get('marge_mois_dernier', 0)
                progres_marge_mois = marge_mois - marge_mois_passe
                percent_marge_mois = 100.0 if marge_mois_passe == 0 else (progres_marge_mois * 100.0 / marge_mois_passe)
                     
                marge_jour = data.get('marge_aujourdhui', 0)
                marge_hier = data.get('marge_hier', 0)
                progres_marge_jour = marge_jour - marge_hier
                percent_marge_jour = 100.0 if marge_hier == 0 else (progres_marge_jour * 100.0 / marge_hier)
                
                # Mise à jour des Text
                self.marge_global.value = format_milliers_fr(marge_global)
                self.marge_mois.value = format_milliers_fr(marge_mois)
                self.marge_jour.value = format_milliers_fr(marge_jour)
                
                self.marge_stats.controls.clear()
                self.marge_stats.controls.extend([
                    self.build_stat_item("Globale", "assets/icons/grey/chart-line.svg", self.marge_global, None),
                    self.build_stat_item("Ce mois", "assets/icons/grey/chart-line.svg", self.marge_mois, percent_marge_mois),
                    self.build_stat_item("Aujourd'hui", "assets/icons/grey/chart-line.svg", self.marge_jour, percent_marge_jour)
                ])
                self.update()
                
        except Exception as e:
            print(f"[ERREUR KPI MARGE] : {e}")
    
    async def get_operational_kpis(self):
        try:
            params = {'select': "*"}
            kpi_data = await supabase_request_async(
                access_token=self.access_token, tenant_id=self.tenant_id,
                table_name="v_kpi_panier_volume", method="GET", params=params
            )
            
            if isinstance(kpi_data, list) and len(kpi_data) > 0:
                data = kpi_data[0]
                panier_mois = data.get('panier_mois_en_cours', 0)
                panier_passe = data.get('panier_mois_dernier', 0)
                progres_panier = panier_mois - panier_passe
                percent_panier = 100.0 if panier_passe == 0 else (progres_panier * 100.0 / panier_passe)
                
                vol_mois = data.get('vol_mois_en_cours', 0)
                vol_passe = data.get('vol_mois_dernier', 0)
                progres_vol = vol_mois - vol_passe
                percent_vol = 100.0 if vol_passe == 0 else (progres_vol * 100.0 / vol_passe)
                
                # Mise à jour des Text
                self.panier_val.value = format_milliers_fr(panier_mois)
                self.volume_val.value = format_milliers_fr(vol_mois)
                
                self.mix_stats.controls.clear()
                self.mix_stats.controls.extend([
                    self.build_stat_item("Panier moyen", "assets/icons/grey/shopping-cart.svg", self.panier_val, percent_panier, "XAF", {"sm": 12, "md": 6}),
                    self.build_stat_item("Articles vendus", "assets/icons/grey/package.svg", self.volume_val, percent_vol, "Uts", {"sm": 12, "md": 6})
                ])
                self.update()
                
        except Exception as e:
            print(f"[ERREUR KPI OPERATIONNEL] : {e}")   
    
    async def get_stock_kpis(self):
        try:
            params = {'select': "*"}
            kpi_stock = await supabase_request_async(
                access_token=self.access_token, tenant_id=self.tenant_id,
                table_name="v_kpi_stock", method="GET", params=params
            )
            
            if isinstance(kpi_stock, list) and len(kpi_stock) > 0:
                data = kpi_stock[0]
                val_stock = data.get('valeur_stock_achat', 0)
                nb_rupture = data.get('nb_produits_rupture', 0)
                
                # Mise à jour des Text
                self.valeur_stock.value = format_milliers_fr(val_stock)
                self.produits_rupture.value = format_milliers_fr(nb_rupture)
                
                self.stock_stats.controls.clear()
                self.stock_stats.controls.extend([
                    self.build_stat_item("Valeur d'Achat", "assets/icons/grey/dollar-sign.svg", self.valeur_stock, None, "XAF", {"sm": 12, "md": 6}),
                    self.build_stat_item("En rupture", "assets/icons/grey/alert-circle.svg", self.produits_rupture, None, "Réf", {"sm": 12, "md": 6})
                ])
                self.update()
                
        except Exception as e:
            print(f"[ERREUR KPI STOCK] : {e}")
            
    # Les fonctions get_chart_7_days, get_top_5_products et get_type_performance restent identiques...