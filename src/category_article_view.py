import flet as ft
from button_generator import ButtonGenerator
from controller import InventoryController
from table_generator import TableGenerator


class CategoryArticleView(ft.Column):
    def __init__(self, page: ft.Page, category, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.page = page
        self.controller = InventoryController()
        self.category = category
        self.margin_main_rigth = self.page.width * 0.015
        self.spacing = 10
        self.expand = True
        self.alignment = ft.MainAxisAlignment.CENTER
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.table_generator = TableGenerator()

        self.selected_row = None
        self.button_generator = ButtonGenerator(
            page=self.page,
            selected_row=self.selected_row,
            toggle_sidebar_callback=self.go_back_to_categories,
            on_refresh_table=self.refresh_table,
        )

        self.controls = [
            ft.Container(
                margin=ft.margin.only(top=10, right=15),
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.END,
                    spacing=10,
                    controls=self.button_generator.generate_buttons(),  # Botones
                ),
            ),
            ft.Row(controls=[
                ft.Container(
                    bgcolor=ft.Colors.BLUE_GREY,
                    content=ft.Column(
                        [
                            ft.Container(
                                content=self.create_article_table(),
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
                ),
            ]),
        ]

    def get_index(self, e):
        row_id = int(e.control.cells[0].content.value)
        container = self.controls[1].controls[0]  # El primer contenedor dentro del Row
        table = container.content.controls[0].content  # Acceder al contenido de la tabla

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

        # Actualizamos el estado de selected_row en ButtonGenerator
        self.button_generator.selected_row = self.selected_row

        # Actualizamos los botones
        self.refresh_buttons()
        self.update()

    def refresh_buttons(self):
        # Actualiza los botones con el estado actual de selected_row
        action_buttons = self.button_generator.generate_buttons()

        # Actualiza la interfaz con los nuevos botones
        self.controls[0].content = [
            ft.Row(
                alignment=ft.MainAxisAlignment.END,
                spacing=10,
                controls=action_buttons,
            )
        ]
        self.page.update()

    def create_article_table(self):
        # Obtenemos los artículos de la categoría
        articles = self.controller.obtener_articulos_por_categoria(self.category)
        updated_articles = []
        for article in articles:
            cantidad_total = self.controller.calcular_cantidad_actual(article.id)
            costo_promedio = self.controller.calcular_costo_promedio_articulo(article.id)
            updated_articles.append(
                {
                    "id": article.id,
                    "nombre": article.nombre,
                    "categoria": article.categoria,
                    "cantidad": cantidad_total,
                    "costo": costo_promedio,
                    "bar_code": article.bar_code,
                }
            )

        # Usamos el método `create_table` de TableGenerator para generar la tabla
        return self.table_generator.create_table(
            table_type="main",  # Tipo de tabla (usamos "main" aquí)
            width=self.page.width * 0.95,  # Ajustamos el ancho al 95% de la página
            data=updated_articles,
            on_row_select=self.get_index,
        )

    def go_back_to_categories(self, e):
        # Volver a la vista de categorías
        self.page.go("/categorias")

    def refresh_table(self):
        """Método para refrescar la tabla después de una acción (crear, editar, eliminar)"""
        # Re-generar la tabla con los artículos actualizados
        self.controls[1].controls[0].content = self.create_article_table()
        self.page.update()
