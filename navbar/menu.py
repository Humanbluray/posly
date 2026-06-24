import flet as ft
from navbar.item_menu import ItemMenu
from utils import MAIN_COLOR, SECOND_COLOR, resource_path, TEXT_PRIMARY, TEXT_SECONDARY, BORDER_COLOR
from views.sections.sales import Sales
from views.sections.reports import Reports
from views.sections.users import Users
from views.sections.settings import Settings
from views.sections.produits import Products
from views.sections.board import Board
from views.sections.inventory import Inventory
from views.sections.entries import Entries
from views.sections.billing import BillingSection
from utils import ROLE


roles = {
    "admin": {
        "Board": True, "Ventes": True, "Rapports": True, "Inventaires": True, "Produits": True,
        "Paramètres": True, 'Entrées': True, "Utilisateurs": True , "Facturation": False
    },
    "cashier": {
        "Board": False, "Ventes": True, "Rapports": True, "Inventaires": True, "Produits": True,
        "Paramètres": False, 'Entrées': True, "Utilisateurs": False, "Facturation": False
    },
    "manager": {
        "Board": True, "Ventes": True, "Rapports": True, "Inventaires": True, "Produits": True,
        "Paramètres": True, 'Entrées': True, "Utilisateurs": False, "Facturation": False
    },
}

class NavBar(ft.Column):
    def __init__(self, cp: object):
        super().__init__(
            expand=True, alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )
        # container parent _____________________________________________________
        self.cp = cp
        
        self.role = self.cp.page.client_storage.get(ROLE)

        # items ____________________________________________________________________________
        self.dashboard = ItemMenu(
            "Tableau de bord", "assets/icons/grey/layout-dashboard.svg", "assets/icons/black/layout-dashboard.svg",
            roles[self.role]['Board']
        )
        self.sales = ItemMenu(
            "Ventes", "assets/icons/grey/badge-cent.svg", "assets/icons/black/badge-cent.svg",
            roles[self.role]['Ventes']
        )
        self.reports = ItemMenu(
            "Rapports", "assets/icons/grey/folder-kanban.svg", "assets/icons/black/folder-kanban.svg",
            roles[self.role]['Rapports']
        )
        self.products = ItemMenu(
            "Produits", "assets/icons/grey/store.svg", "assets/icons/black/store.svg",
            roles[self.role]['Produits']
        )
        self.inventory = ItemMenu(
            "Inventaires", "assets/icons/grey/list-check.svg", "assets/icons/black/list-check.svg",
            roles[self.role]['Inventaires']
        )
        self.settings = ItemMenu(
            "Paramètres", "assets/icons/grey/bolt.svg", "assets/icons/black/bolt.svg",
            roles[self.role]['Paramètres']
        )
        self.users = ItemMenu(
            "Utilisateurs", "assets/icons/grey/users.svg", "assets/icons/black/users.svg",
            roles[self.role]['Utilisateurs']
        )
        self.billing = ItemMenu(
            "Facturation", "assets/icons/grey/credit-card.svg", "assets/icons/black/credit-card.svg",
            roles[self.role]['Facturation']
        )

        self.children = [
            self.dashboard, self.sales, self.reports, self.products, self.inventory, self.settings, self.users,
            self.billing
        ]

        for child in self.children:
            child.on_click = self.click_on_menu

        self.controls = [
            ft.Column(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                expand=True,
                controls=[
                    ft.Column(
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Row(
                                        controls=[
                                            ft.Text("Alti", size=26, font_family="PEB", color=TEXT_PRIMARY),
                                            ft.Text("Pos", size=26, font_family="PEB", color=MAIN_COLOR),
                                        ],
                                        spacing=0
                                    )
                                ],
                                spacing=8,
                                alignment=ft.MainAxisAlignment.CENTER
                            ),
                            ft.Divider(height=20, color=BORDER_COLOR),
                            ft.Column(
                                controls=[
                                    ft.Text("Principal", size=12, font_family="PPM", color=TEXT_SECONDARY, weight=ft.FontWeight.W_600),
                                    self.dashboard, self.sales, self.reports, self.products, self.inventory,
                                ],
                                spacing=12
                            )
                        ]
                    ),
                    ft.Column(
                        controls=[
                            ft.Text(
                                "Administration",
                                size=12,
                                font_family="PPM",
                                color=TEXT_SECONDARY,
                                weight=ft.FontWeight.W_600,
                                visible=roles[self.role]['Utilisateurs']
                            ),
                            self.billing,
                            self.users, self.settings,
                        ],
                        spacing=12
                    )
                ]
            )
        ]
        self.load()

    def load(self):
        for child in self.children:
            child.set_is_clicked_false()
            child.is_clicked = False

        if self.role != "cashier":
            self.dashboard.set_is_clicked_true()
            self.cp.my_content.controls.clear()
            self.cp.my_content.controls.append(Board(self.cp))
        
        else:
            self.sales.set_is_clicked_true()
            self.cp.my_content.controls.clear()
            self.cp.my_content.controls.append(Sales(self.cp))
        
        self.cp.page.update()

    def click_on_menu(self, e):
        for child in self.children:
            child.set_is_clicked_false()
            child.is_clicked = False
            child.update()

        e.control.set_is_clicked_true()
        e.control.is_clicked = True
        e.control.update()

        self.cp.my_content.controls.clear()

        if e.control.name.value.lower() == "board".lower():
            pass

        elif e.control.name.value.lower() == "ventes".lower():
            self.cp.my_content.controls.append(Sales(self.cp))

        elif e.control.name.value.lower() == "Rapports".lower():
            self.cp.my_content.controls.append(Reports(self.cp))

        elif e.control.name.value.lower() == "utilisateurs".lower():
            self.cp.my_content.controls.append(Users(self.cp))

        elif e.control.name.value.lower() == "paramètres".lower():
            self.cp.my_content.controls.append(Settings(self.cp))
        
        elif e.control.name.value.lower() == "produits".lower():
            self.cp.my_content.controls.append(Products(self.cp))
        
        elif e.control.name.value.lower() == "inventaires".lower():
            self.cp.my_content.controls.append(Inventory(self.cp))
        
        elif e.control.name.value.lower() == "tableau de bord".lower():
            self.cp.my_content.controls.append(Board(self.cp))
        
        elif e.control.name.value.lower() == "entrées".lower():
            self.cp.my_content.controls.append(Entries(self.cp))

        elif e.control.name.value.lower() == "facturation".lower():
            self.cp.my_content.controls.append(BillingSection(self.cp))
            
        else:
            print("ok")

        self.cp.page.update()
















