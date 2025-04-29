import flet as ft
from controller import InventoryController


class CategoryView(ft.Column):
    def __init__(self, page: ft.Page, go_to_main_view_from_categories, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.page = page
        self.controller = InventoryController()
        self.go_to_main_view_from_categories = go_to_main_view_from_categories
        self.spacing = 10
        self.alignment = ft.MainAxisAlignment.START
        self.horizontal_alignment = ft.CrossAxisAlignment.START
        self.expand = True
        self.controls = [
            ft.TextButton("Volver", on_click=self.go_to_main_view_from_categories)
        ]

    def update_category_cards(self):
        categories = self.controller.obtener_categorias()
        category_cards = []
        for category in categories:
            articles_in_category = self.controller.obtener_articulos_por_categoria(category.nombre_categoria)
            card = ft.Card(
                content=ft.Container(
                    padding=10,
                    content=ft.Column(
                        [
                            ft.Text(category.nombre_categoria, weight=ft.FontWeight.BOLD),
                            ft.Text(f"Número de items: {len(articles_in_category)}", size=12),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.START,
                    ),
                    on_click=lambda e, cat=category: self.show_articles_by_category(cat),
                ),
                width=200,
                elevation=2,
            )
            category_cards.append(card)

        # Clear existing cards (except the volver button)
        self.controls = [control for control in self.controls if not isinstance(control, ft.Card) and not isinstance(control, ft.Row) and not isinstance(control, ft.TextButton)] # Keep non-card and non-row controls
        self.controls.insert(0, ft.Row(controls=category_cards, wrap=True)) # Insert the row at the beginning
        self.update()

    def did_mount(self):
        self.update_category_cards()
        
    def show_articles_by_category(self, category):
        self.page.go(f"/categorias/{category.nombre_categoria}")