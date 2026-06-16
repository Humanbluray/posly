import flet as ft
from navbar.item_menu import ItemMenu
from utils import MAIN_COLOR, SECOND_COLOR, resource_path
from views.sections.sales import Sales
from views.sections.reports import Reports
from views.sections.users import Users
from views.sections.settings import Settings
from views.sections.produits import Products
from utils import ROLE


roles = {
    "admin": {
        "Board": True, "Ventes": True, "Rapports": True, "Inventaires": True, "Produits": True,
        "Paramètres": True, 'Entrées': True, "Utilisateurs": True 
    },
    "cashier": {
        "Board": False, "Ventes": True, "Rapports": True, "Inventaires": True, "Produits": True,
        "Paramètres": False, 'Entrées': True, "Utilisateurs": False 
    },
    "manager": {
        "Board": True, "Ventes": True, "Rapports": True, "Inventaires": True, "Produits": True,
        "Paramètres": True, 'Entrées': True, "Utilisateurs": False 
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
            "Board", "assets/icons/grey/layout-dashboard.svg", "assets/icons/black/layout-dashboard.svg",
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
        self.entries = ItemMenu(
            "Entrées", "assets/icons/grey/package-check.svg", "assets/icons/black/package-check.svg",
            roles[self.role]['Entrées']
        )
        self.users = ItemMenu(
            "Utilisateurs", "assets/icons/grey/users.svg", "assets/icons/black/users.svg",
            roles[self.role]['Utilisateurs']
        )

        self.children = [
            self.dashboard, self.sales, self.reports, self.products, self.inventory, self.entries, self.settings, self.users
        ]

        for child in self.children:
            child.on_click = self.click_on_menu

        self.controls = [
            ft.Column(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN, expand=True,
                controls=[
                    ft.Column(
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Image(src="assets/icons/black/chart-line.svg", width=24, height=24),
                                    ft.Row(
                                        controls=[
                                            ft.Text("Pos", size=24, font_family="PEB"),
                                            ft.Text("ly", size=24, font_family="PEB", color=MAIN_COLOR),
                                        ], spacing=0
                                    )
                                ], spacing=5,
                                alignment=ft.MainAxisAlignment.CENTER
                            ),
                            ft.Divider(height=20, thickness=1),
                            ft.Column(
                                controls=[
                                    ft.Text(
                                        "Principal", size=13, font_family="PPM", color="grey"
                                    ),
                                    self.dashboard, self.sales, self.reports, self.products, self.inventory, self.entries,
                                ], spacing=10
                            )
                        ]
                    ),
                    ft.Column(
                        controls=[
                            ft.Text(
                                "Administration", size=13, font_family="PPM", color="grey",
                                visible=roles[self.role]['Utilisateurs']
                            ),
                            self.users, self.settings,
                        ], spacing=10
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
            
        else:
            print("ok")

        self.cp.page.update()
















