import flet as ft


class Sidebar(ft.Container):

    def __init__(self, app_layout):
        self.app_layout = app_layout
        self.nav_rail_visible = True
        self.top_nav_items = [
            ft.NavigationRailDestination(
                label_content=ft.Text("Articulos"),
                label="Articulos",
                icon=ft.Icons.INVENTORY,
                selected_icon=ft.Icons.INVENTORY,
            ),
            ft.NavigationRailDestination(
                label_content=ft.Text("Categorias"),
                label="Categorias",
                icon=ft.Icons.CATEGORY,
                selected_icon=ft.Icons.CATEGORY,
            ),
            ft.NavigationRailDestination(
                label_content=ft.Text("Usuarios"),
                label="Usuarios",
                icon=ft.Icons.PERSON,
                selected_icon=ft.Icons.PERSON,
            ),
        ]

        self.top_nav_rail = ft.NavigationRail(
            selected_index=None,
            label_type=ft.NavigationRailLabelType.ALL,
            on_change=self.top_nav_change,
            destinations=self.top_nav_items,
            bgcolor='#FFE1E6',
            extended=True,
            height=500,
        )

        self.toggle_nav_rail_button = ft.IconButton(ft.Icons.ARROW_BACK)

        super().__init__(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text("Menu", size=20),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    # divider
                    ft.Container(
                        bgcolor=ft.Colors.BLACK26,
                        border_radius=ft.border_radius.all(30),
                        height=1,
                        alignment=ft.alignment.center_right,
                        width=220,
                    ),
                    self.top_nav_rail,
                ],
                tight=True,
            ),
            padding=ft.padding.all(15),
            margin=ft.margin.all(0),
            width=250,
            bgcolor='#FFE1E6',
            visible=self.nav_rail_visible,
        )

    def top_nav_change(self, e):
        self.top_nav_rail.selected_index = e.control.selected_index
        if e.control.selected_index == 0:
            self.app_layout.page.go("/")  # Navegar a la vista de Artículos (MainView)
        elif e.control.selected_index == 1:
            self.app_layout.go_to_categories_view()  # Navegar a la vista de Categorías
        elif e.control.selected_index == 2:
            print("Ir a la vista de Usuarios")
        self.update()
