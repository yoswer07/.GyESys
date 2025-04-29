import flet as ft
from main_view import mainView
from sidebar import Sidebar
from report_view import ReportView
from category_view import CategoryView


class AppLayout(ft.Row):
    def __init__(self, app, page: ft.Page, *args, **kwargs):
        super().__init__(spacing=5, *args, **kwargs)
        self.app = app
        self.page = page
        self.toggle_nav_rail_button = ft.IconButton(
            icon=ft.Icons.ARROW_CIRCLE_LEFT,
            icon_color=ft.Colors.BLUE_GREY_400,
            selected=False,
            selected_icon=ft.Icons.ARROW_CIRCLE_RIGHT,
            selected_icon_color=ft.Colors.BLUE_GREY_600,
            on_click=self.toggle_nav_rail,
            style=ft.ButtonStyle(
                overlay_color=ft.Colors.with_opacity(0.3, ft.Colors.BLUE_GREY_300)
            ),
        )
        self.sidebar = Sidebar(self)
        self.content_view = ft.Container(expand=True)  # <--- Aquí se inicializa content_view
        self.main_view_instance = None # Para guardar la instancia de mainView
        self.controls = [self.sidebar, self.toggle_nav_rail_button, self.content_view]
        self.vertical_alignment = ft.CrossAxisAlignment.START

    def toggle_nav_rail(self, e):
        self.sidebar.visible = not self.sidebar.visible
        self.toggle_nav_rail_button.selected = not self.toggle_nav_rail_button.selected
        self.page.update()

    def go_to_report_view(self, articulo_id: int):
        self.page.go(f"/report/{articulo_id}")
        self.sidebar.visible = False
        self.toggle_nav_rail_button.selected = True
        self.page.update()

    def go_to_main_view(self, e):
        self.toggle_nav_rail(None)
        self.page.go("/")

    def go_to_categories_view(self, e=None):
        self.page.go("/categorias")
        self.sidebar.visible = False
        self.toggle_nav_rail_button.selected = True
        self.page.update()

    def go_to_main_view_from_categories(self, e):
        self.page.go("/")

    def route_change(self, route):
        self.content_view.content = self.get_view_for_route(route.route)
        self.page.update()

    def get_view_for_route(self, route):
        print(f"Route changed to: {route}")
        if route == "/":
            self.main_view_instance = mainView(self.page, self.toggle_nav_rail)
            return self.main_view_instance
        elif route == "/categorias":
            return CategoryView(self.page, self.go_to_main_view_from_categories)
        elif route.startswith("/categorias/"):
            category_id = route.split("/")[-1]  # Extraemos el ID de la categoría
            return mainView(self.page, self.toggle_nav_rail, category_id)
        elif route.startswith("/report/"):
            try:
                articulo_id = int(route.split("/")[-1])
                return ReportView(self.page, self.go_to_main_view, articulo_id)
            except ValueError:
                return ft.Text("Error: ID de artículo inválido")
        return ft.Text("Error: Página no encontrada")