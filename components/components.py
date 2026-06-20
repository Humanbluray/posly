import flet as ft
from utils import (
    format_milliers_fr, MAIN_COLOR, resource_path, BG_COLOR, CARD_BG, TEXT_PRIMARY, TEXT_SECONDARY,
    
)
from styles import switch_style, button_primary_style
DEFAULT_IMAGE = "https://hojfmjmrhtsvgfzynelr.supabase.co/storage/v1/object/public/images/no%20image.jpeg"


class MyButton(ft.ElevatedButton):
    def __init__(self, title: str, icon: str = None, click=None):
        content_row = []
        if icon:
            content_row.append(ft.Image(src=icon, width=18, height=18))
        content_row.append(ft.Text(title, size=15, font_family="PPM", color="white"))

        super().__init__(
            content=ft.Row(content_row, alignment=ft.MainAxisAlignment.CENTER, spacing=8),
            style=button_primary_style,
            on_click=click,
            height=44,
        )
        

class ActionButton(ft.Container):
    """
    classe qui définit les boutons d'actions
    """
    def __init__(self, tooltip: str, icon: str, data, click):
        super().__init__(
            tooltip=tooltip, bgcolor='#f2f2f2', height=50,
            border_radius=4, width=50, alignment=ft.alignment.center,
            border=ft.border.all(1, BG_COLOR),
            on_click=click, data=data,
            scale=ft.Scale(1),
            animate_scale=ft.Animation(300, ft.AnimationCurve.EASE_IN_OUT),
            on_hover=self.hover_effect
        )
        self.content = ft.Row(
            controls=[ft.Image(icon, width=14, height=14),],
            alignment=ft.MainAxisAlignment.CENTER
        )

    def hover_effect(self, e):
        if e.data == "true":
            self.scale = 1.05
        else:
            self.scale = 1

        self.update()


class MyTextButton(ft.Container):
    def __init__(self, title: str, click):
        super().__init__(
            padding=ft.padding.only(10, 3, 10, 3),
            bgcolor="white", alignment=ft.alignment.center,
            on_click=click, on_hover=self.hover_effect, border_radius=10
        )
        self.content=ft.Text(title, size=14, font_family="PPM", color=MAIN_COLOR)

    def hover_effect(self, e):
        if e.data == "true":
            self.bgcolor = BG_COLOR
        else:
            self.bgcolor = None

        self.update()


class StateButton(ft.Container):
    """
    classe qui définit les boutons d'actions
    """
    def __init__(self, icon: str, badge: ft.Badge, data: dict, click):
        super().__init__(
            shape=ft.BoxShape.CIRCLE, padding=5, alignment=ft.alignment.center,
            on_click=click, data=data, badge=badge,
            scale=ft.Scale(1),
            animate_scale=ft.Animation(300, ft.AnimationCurve.EASE_IN_OUT),
            on_hover=self.hover_effect,
            bgcolor="white"
        )
        self.content = ft.Image(icon, width=22, height=22)

    def hover_effect(self, e):
        if e.data == "true":
            self.scale = 1.01
        else:
            self.scale = 1

        self.update()


class CardItem(ft.Card):
    def __init__(self, container_parent: object, infos: dict, basket: ft.ListView):
        super().__init__(
            elevation=2, 
            shape=ft.RoundedRectangleBorder(radius=12),
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS 
        )
        
        self.container_parent = container_parent
        self.basket = basket
        self.infos = infos
        
        img_src = infos.get('image') if infos.get('image') else DEFAULT_IMAGE
        
        # --- Nouveaux éléments pour la gestion de la réduction ---
        self.tf_reduction = ft.TextField(
            value="0",
            width=70,
            height=30,
            text_size=12,
            dense=True,
            disabled=True,  # Désactivé par défaut
            content_padding=5,
            border_radius=6,
            text_align=ft.TextAlign.RIGHT,
            input_filter=ft.NumbersOnlyInputFilter(),  # Uniquement des chiffres
            focused_border_color=MAIN_COLOR
        )
        
        self.switch_reduction = ft.Switch(
            **switch_style,
            value=False,
            scale=0.7,
            on_change=self.toggle_reduction_field
        )
        
        self.content = ft.Container(
            on_click=self.add_to_cart,
            on_hover=self.hover_effect,
            animate_scale=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
            scale=1,
            bgcolor=CARD_BG,
            border_radius=16,
            content=ft.Column(
                spacing=0,
                controls=[
                    ft.Image(
                        src=img_src,
                        width=220,
                        height=140,
                        fit=ft.ImageFit.COVER,
                    ),
                    ft.Container(
                        padding=ft.padding.all(12),
                        bgcolor=CARD_BG,
                        content=ft.Column(
                            spacing=6,
                            controls=[
                                ft.Text(
                                    infos["designation"].upper(),
                                    size=12,
                                    font_family="PPM",
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                    max_lines=1,
                                    color=TEXT_PRIMARY,
                                ),
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                    controls=[
                                        ft.Text(
                                            f"{format_milliers_fr(infos['price'])} FCFA",
                                            size=14,
                                            font_family="PEB",
                                            color=MAIN_COLOR,
                                        ),
                                        ft.Container(
                                            content=ft.Text(
                                                f"Qté: {format_milliers_fr(infos['stock'])}",
                                                size=10,
                                                font_family="PPM",
                                                color="white"if self.infos['stock'] > 0 else  ft.Colors.RED,
                                            ),
                                            bgcolor=TEXT_SECONDARY if self.infos['stock'] > 0 else  ft.Colors.RED_50,
                                            padding=ft.padding.symmetric(horizontal=6, vertical=2),
                                            border_radius=4,
                                            visible=(infos['product_type'] != 'repas')
                                        )
                                    ]
                                ),
                                # Switch et champ de réduction (inchangé)
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                    controls=[
                                        ft.Row(
                                            controls=[
                                                self.switch_reduction,
                                                ft.Text("Réduc.", size=11, font_family="PPM", color=TEXT_SECONDARY)
                                            ],
                                            spacing=0
                                        ),
                                        self.tf_reduction
                                    ]
                                )
                            ]
                        )
                    )
                ]
            )
        )
        
        
    def toggle_reduction_field(self, e):
        """Active ou désactive le champ de texte selon l'état du switch"""
        self.tf_reduction.disabled = not self.switch_reduction.value
        if not self.switch_reduction.value:
            self.tf_reduction.value = "0"  # Réinitialise à 0 si on décoche
        self.tf_reduction.update()

    def add_to_cart(self, e):
        # 1. Détermination du prix final (initial ou remisé)
        prix_final = self.infos['price']
        
        if self.switch_reduction.value and self.tf_reduction.value:
            try:
                valeur_reduc = int(self.tf_reduction.value)
                if valeur_reduc > 0:
                    prix_final = valeur_reduc
            except ValueError:
                pass  # En cas d'erreur de conversion, on garde le prix initial

        # 2. Logique d'ajout pour le type 'repas'
        if self.infos['product_type'] == "repas":
            datas = {
                "id": self.infos["id"],
                "designation": self.infos['designation'],
                "qty": 1,
                "price": prix_final,  # Utilisation du prix calculé
                'stock': self.infos['stock'],
                'product_type': self.infos['product_type']
            }
            self.basket.controls.append(
                BasketItem(self.container_parent, datas, self.basket)
            )
            self.basket.update()
            total = 0 if len(self.basket.controls) == 0 else int(self.container_parent.amount.value)
            self.container_parent.amount.value = total + prix_final
            self.container_parent.amount.update()

        # 3. Logique d'ajout pour les autres types de produits
        else:
            if self.infos['stock'] == 0:
                self.container_parent.cp.show_alert(
                    "Ajout impossible. stock nul", ft.Icons.INFO_OUTLINED, ft.Colors.AMBER
                )
                self.container_parent.cp.page.update()
            else:
                datas = {
                    "id": self.infos["id"],
                    "designation": self.infos['designation'],
                    "qty": 1,
                    "price": prix_final,  # Utilisation du prix calculé
                    'stock': self.infos['stock'],
                    'product_type': self.infos['product_type']
                }
                self.basket.controls.append(
                    BasketItem(self.container_parent, datas, self.basket)
                )
                self.basket.update()
                total = 0 if len(self.basket.controls) == 0 else int(self.container_parent.amount.value)
                self.container_parent.amount.value = total + prix_final
                self.container_parent.amount.update()

    def hover_effect(self, e):
        if e.data == "true":
            self.content.scale = 1.03
        else:
            self.content.scale = 1
        self.content.update()       
            

class BasketItem(ft.Container):  # Item du panier...
    def __init__(self, container_parent: object, datas_item: dict, basket: ft.ListView):
        super().__init__(
            data=datas_item,
        )
        self.container_parent = container_parent
        self.datas_item = datas_item
        self.basket = basket

        self.remove_button = ft.Container(
            bgcolor=BG_COLOR,
            height=50, width=20, alignment=ft.alignment.center,
            border_radius=ft.border_radius.only(
                top_left=10, bottom_left=10
            ),
            content=ft.Text("-", size=18, font_family="PPB"),
            on_click=self.remove_quantity
        )
        self.add_button = ft.Container(
            bgcolor=BG_COLOR,
            height=50, width=20, alignment=ft.alignment.center,
            border_radius=ft.border_radius.only(
                top_right=10, bottom_right=10
            ),
            content=ft.Text("+", size=18, font_family="PPB"),
            on_click=self.add_quantity
        )
        self.qty = ft.Text(
            datas_item['qty'], size=16, font_family="PPM"
        )
        self.total = ft.Text(datas_item["price"], size=14, font_family="PEB")

        self.content = ft.Row(
            controls=[
                ft.Column(
                    controls=[
                        ft.Text(
                            datas_item["designation"].upper(), size=14, font_family="PPM",
                            max_lines=1, width=150, overflow=ft.TextOverflow.ELLIPSIS
                        ),
                        self.total,
                    ], horizontal_alignment=ft.CrossAxisAlignment.START,
                    spacing=0
                ),
                ft.Row(
                    controls=[
                        self.remove_button,
                        self.qty,
                        self.add_button,
                        # ft.IconButton(
                        #     ft.Icons.DELETE_OUTLINE_ROUNDED, icon_size=24, icon_color="red",
                        #     on_click=self.remove_to_basket
                        # ),
                        ft.Container(
                            content=ft.Image(
                                src=resource_path("assets/icons/grey/trash-2.svg"), width=16, height=18
                            ),
                            on_click=self.remove_to_basket
                        )
                    ]
                )
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        )

    def add_quantity(self, e) -> None:
        # Si le produit n'est pas de type repas...
        if self.datas_item['product_type'] != "repas":
            if self.datas_item['stock'] == self.datas_item['qty']:
                self.container_parent.cp.page.open(self.container_parent.cp.bad_stock_alert)
                self.container_parent.cp.page.update()
            else:
                qty = int(self.qty.value)
                new_qty = qty + 1
                self.qty.value = new_qty
                self.datas_item["qty"] = new_qty  # MAJ des données
                new_total = new_qty * self.datas_item['price']
                self.total.value = f"{new_total}"  # Maj du total

                total = 0 if len(self.basket.controls) == 0 else int(self.container_parent.amount.value)
                total += self.datas_item['price']
                self.container_parent.amount.value = total

                # on met à jour l'affichage...
                self.total.update()
                self.qty.update()
                self.container_parent.amount.update()

        # Si le produit est de type repas...
        else:
            qty = int(self.qty.value)
            new_qty = qty + 1
            self.qty.value = new_qty
            self.datas_item["qty"] = new_qty  # MAJ des données
            new_total = new_qty * self.datas_item['price']
            self.total.value = f"{new_total}"  # Maj du total

            total = 0 if len(self.basket.controls) == 0 else int(self.container_parent.amount.value)
            total += self.datas_item['price']
            self.container_parent.amount.value = total

            # on met à jour l'affichage...
            self.total.update()
            self.qty.update()
            self.container_parent.amount.update()

    def remove_quantity(self, e) -> None:
        qty = int(self.qty.value)
        if qty > 1:
            new_qty = qty - 1
            self.qty.value = new_qty
            self.datas_item["qty"] = new_qty  # MAJ des données
            new_total = new_qty * self.datas_item['price']
            self.total.value = f"{new_total}"

            total = 0 if len(self.basket.controls) == 0 else int(self.container_parent.amount.value)
            total -= self.datas_item['price']
            self.container_parent.amount.value = total

            self.total.update()
            self.qty.update()
            self.container_parent.amount.update()

    def remove_to_basket(self, e):
        self.basket.controls.remove(self)
        self.basket.update()
        total = int(self.container_parent.amount.value)
        total -= self.datas_item['price'] * self.datas_item['qty']
        self.container_parent.amount.value = total
        self.container_parent.amount.update()


class FilterItem(ft.Container):
    def __init__(self, cp, title: str, seleted: bool, liste_des_filtres: list):
        super().__init__(
            padding=ft.padding.only(10, 5, 10, 5),
            border_radius=6,
            bgcolor=MAIN_COLOR if seleted else BG_COLOR,
            on_click=self.action_afcter_click
        )
        self.cp = cp
        self.liste_des_filtres = liste_des_filtres
        self.title = title # Dictionnaire avec uniquement le nom de la catégorie pour filtrer...
        self.selected = seleted

        self.text = ft.Text(
            self.title, size=14,
            font_family="PPM",
            color="white" if self.selected else ft.Colors.BLACK54
        )

        self.content = ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                self.text
            ]
        )

    def set_selected(self):
        self.selected = True
        self.text.color = "white"
        self.text.font_family = "PPB"
        self.bgcolor = MAIN_COLOR
        self.text.update()
        self.update()

    def set_unselected(self):
        self.selected = False
        self.bgcolor = BG_COLOR
        self.text.font_family = "PPM"
        self.text.color = ft.Colors.BLACK54
        self.text.update()
        self.update()
    
    async def action_afcter_click(self, e):
        if self.selected:
            pass
            
        else:
            
            for i, item in enumerate(self.liste_des_filtres):
                item.set_unselected()
            
            self.set_selected()

            await self.cp.load_datas()
        
        self.cp.cp.page.update()


class StyledButton(ft.Container):
    def __init__(self, title: str, my_icon: str, click):
        super().__init__(
            padding=ft.padding.only(10, 8, 10, 8),
            border_radius=10, bgcolor=BG_COLOR,
            on_click=click, on_hover=self.hover_effect,
            content=ft.Row(
                controls=[
                    ft.Icon(my_icon, size=16, color=ft.Colors.BLACK87),
                    ft.Text(title.capitalize(), size=16, font_family="PPB", color=ft.Colors.BLACK87)
                ], alignment=ft.MainAxisAlignment.CENTER
            )
        )

    def hover_effect(self, e):
        if e.data == "true":
            for item in self.content.controls:
                item.color = MAIN_COLOR
                item.update()
        else:
            for item in self.content.controls:
                item.color = ft.Colors.BLACK87
                item.update()


class BarGraphic(ft.BarChart):
    def __init__(self, infos: list, max_value: int, title: str, color: str):
        super().__init__(
            bar_groups=[
                ft.BarChartGroup(
                    x=i,
                    bar_rods=[
                        ft.BarChartRod(
                            from_y=0,
                            to_y=infos[i]['montant'],
                            width=25,  # Largeur de la barre
                            color=color,  # Couleur principale
                            tooltip=format_milliers_fr(infos[i]['montant']),
                            border_radius=16,  # Bords arrondis
                            bg_to_y=max_value,  # Hauteur de la zone de fond
                            bg_color="#f0f0f6",  # Couleur de fond
                        )
                    ]
                )
                for i in range(len(infos))
            ],
            # left_axis=ft.ChartAxis(
            #     labels_size=12, title=ft.Text(title, size=12, font_family='PPM'), title_size=40
            # ),
            bottom_axis=ft.ChartAxis(
                labels=[
                    ft.ChartAxisLabel(
                        value=i, label=ft.Text(
                            infos[i]['catégorie'], size=13, font_family='PPM'
                            )
                        )
                    for i in range(len(infos))
                ],
                labels_size=30,
            ),
            max_y=max_value,  # Définit la hauteur maximale de l'axe Y
            interactive=True,
            expand=True,
        )






