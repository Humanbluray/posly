import flet as ft
from views.login import LoginView
from views.home import HomeView
from views.register import RegisterView
from views.forgot_password import ForgotPasswordView
import os
from utils import resource_path


SIGNIN_ROUTE = "/"
HOME_ROUTE = '/home'
REGISTER_ROUTE = '/register'
RECOVERY_ROUTE = "/forgot-password"


def main(page: ft.Page):
    # --- POLICES ---
    page.fonts = {
        "PPR": resource_path("assets/fonts/Figtree-Regular.ttf"),
        "PPM": resource_path("assets/fonts/GoogleSans-Medium.ttf"),
        "PPB": resource_path("assets/fonts/Figtree-Bold.ttf"),
        "PEB": resource_path("assets/fonts/Figtree-ExtraBold.ttf"),
        "PPI": resource_path("assets/fonts/Figtree-Italic.ttf"),
        "PPL": resource_path("assets/fonts/Figtree-Light.ttf"),
        "PPN": resource_path("assets/fonts/Figtree-Medium.ttf"),
    }

    # --- RÉCUPÉRATION DU THÈME STOCKÉ ---
    stored_theme = page.client_storage.get("theme_mode")
    if stored_theme == "dark":
        page.theme_mode = ft.ThemeMode.DARK
    else:
        page.theme_mode = ft.ThemeMode.LIGHT

    page.title = "Posly"

    # --- ROUTES ---
    route_views = {
        SIGNIN_ROUTE: LoginView,
        HOME_ROUTE: HomeView,
        REGISTER_ROUTE: RegisterView,
        RECOVERY_ROUTE: ForgotPasswordView
    }

    def route_change(event: ft.RouteChangeEvent):
        page.views.clear()
        current_route = event.route

        if current_route in route_views:
            page.views.append(route_views[current_route](page))
            page.update()
        else:
            page.views.append(LoginView(page))
            page.update()

    def view_pop(view):
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = lambda e: route_change(e)
    page.on_view_pop = view_pop
    page.go(page.route)


if __name__ == "__main__":
    port = int(os.getenv('PORT', 8080))
    ft.app(
        target=main,
        assets_dir="assets",
        route_url_strategy="default",
        port=port
    )
    
    