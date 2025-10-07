import flet as ft
from controller import InventoryController
from table_generator import TableGenerator
from button_generator import ButtonGenerator


class mainView(ft.Column):
    def __init__(
        self, page: ft.Page, toggle_sidebar_callback, category_id=None, *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.page = page
        self.controller = InventoryController()
        self.table_generator = TableGenerator(self.controller)
        self.selected_row = None
        self.article_data = self.get_all_articles()
        self.margin_main_rigth = self.page.width * 0.015
        self.toggle_sidebar_callback = toggle_sidebar_callback
        self.category_id = category_id

        self.inventory_table_container = ft.Container(
            bgcolor='#FFE1E6',
            content=ft.Column(
                [
                    ft.Container(
                        content=ft.DataTable(
                            columns=[ft.DataColumn(label=ft.Text("Prueba"))],
                            rows=[],
                            expand=True,
                            show_checkbox_column=True,
                        ),
                        expand=True,
                        padding=ft.padding.all(10),
                    )
                ],
                scroll=ft.ScrollMode.AUTO,
                expand=True,
            ),
            expand=True,
            alignment=ft.alignment.top_center,
            height=self.page.height * 0.82,
            margin=ft.margin.only(right=float(self.margin_main_rigth)),
            border_radius=ft.border_radius.all(10),
        )

        self.list_view_container = ft.Row(
            controls=[
                self.inventory_table_container,
            ],
            expand=True,
        )

        self.button_generator = ButtonGenerator(
            self.page,
            self.selected_row,
            self.toggle_sidebar_callback,
            self.refresh_table,
            origin="principal",
            table_data=self.article_data,
        )
        action_buttons = self.button_generator.generate_buttons()

        self.controls = [
            ft.Row(
                controls=[
                    ft.Container(
                        content=ft.TextField(
                            hint_text="Search all boards",
                            autofocus=False,
                            content_padding=ft.padding.only(left=10),
                            width=200,
                            height=40,
                            text_size=12,
                            border_color=ft.Colors.BLACK26,
                            focused_border_color=ft.Colors.BLUE_ACCENT,
                            suffix_icon=ft.Icons.SEARCH,
                        ),
                        margin=ft.margin.only(top=5),
                    ),
                    ft.Container(
                        margin=ft.margin.only(top=5, right=15),
                        content=ft.Row(
                            alignment=ft.MainAxisAlignment.END,
                            spacing=10,
                            controls=action_buttons,  # Usamos los botones generados aquí
                        ),
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            self.list_view_container,
        ]
        self.expand = True
        self.alignment = ft.MainAxisAlignment.CENTER
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self._first_build = True
        if self.category_id:
            self.refresh_table(self.category_id)
        else:
            self.refresh_table()

    def get_all_articles(self):
        articles = self.controller.obtener_todos_articulos()
        updated_articles = []
        for article in articles:
            cantidad_total = self.controller.calcular_cantidad_actual(article["id"])
            costo_promedio = self.controller.calcular_costo_promedio_articulo(
                article["id"]
            )  # Usar la nueva función
            updated_articles.append(
                {
                    "id": article["id"],
                    "nombre": article["nombre"],
                    "categoria": article["categoria"],
                    "cantidad": cantidad_total,
                    "costo": costo_promedio,
                    "bar_code": article["bar_code"],
                }
            )
        return updated_articles

    def get_index(self, e):
        row_id = int(e.control.cells[0].content.value)
        table = self.inventory_table_container.content.controls[0].content

        # Deselect all rows
        for row in table.rows:
            if row != e.control:
                row.selected = False

        # Toggle the selection of the current row
        e.control.selected = not e.control.selected

        if e.control.selected:
            self.selected_row = self.controller.obtener_articulo(row_id)
        else:
            self.selected_row = None

        self.button_generator.selected_row = self.selected_row
        self.refresh_buttons()
        self.update()

    def refresh_buttons(self):
        # Actualiza los botones con el estado actual de selected_row
        action_buttons = self.button_generator.generate_buttons()

        # Actualiza la interfaz con los nuevos botones
        self.controls[0].controls[1].content.controls = [
            ft.Row(
                alignment=ft.MainAxisAlignment.END,
                spacing=10,
                controls=action_buttons,
            )
        ]
        self.page.update()

    # def did_mount(self):
    #     self.refresh_table()  # Llamar a refresh_table cuando el control se monta

    def refresh_table(self, category_id=None):
        # Si category_id está presente, solo se muestran los artículos de esa categoría
        if category_id:
            articles = self.controller.obtener_articulos_por_categoria(category_id)
        else:
            articles = self.controller.obtener_todos_articulos()

        updated_articles = []
        for article in articles:
            # Aquí accedemos a los atributos del objeto Articulo correctamente
            cantidad_total = self.controller.calcular_cantidad_actual(article["id"])
            costo_promedio = self.controller.calcular_costo_promedio_articulo(
                article["id"]
            )
            updated_articles.append(
                {
                    "id": article["id"],
                    "nombre": article["nombre"],
                    "categoria": article["categoria"],
                    "cantidad": cantidad_total,
                    "costo": costo_promedio,
                    "bar_code": article["bar_code"],
                }
            )

        # Actualizamos la tabla de datos con los artículos de la categoría
        inventory_table = self.table_generator.create_table(
            "main",
            self.page.width * 0.95,
            updated_articles,
            on_row_select=self.get_index,
        )
        self.inventory_table_container.content.controls[0].content = inventory_table
        self.article_data = updated_articles
        self.page.update()
