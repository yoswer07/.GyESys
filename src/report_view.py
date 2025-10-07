import datetime
import flet as ft
import pytz
from controller import InventoryController
from table_generator import TableGenerator


class ReportView(ft.Column):

    def __init__(self, page: ft.Page, on_volver, articulo_id: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.page = page
        self.selected_row = None
        self.controller = InventoryController()
        self.table_generator = TableGenerator(self.controller)
        self.on_volver = on_volver
        self.articulo_id = articulo_id
        self.report_data = self.get_report_data()
        self.report_table = self.create_report_table()
        self.margin_main_rigth = self.page.width * 0.015

        self.date_picker_control = ft.DatePicker(
            first_date=datetime.datetime(year=2010, month=10, day=1),
            date_picker_mode=ft.DatePickerMode.DAY,
            date_picker_entry_mode=ft.DatePickerEntryMode.CALENDAR,
        )
        self.date_button = ft.ElevatedButton(
            "Agrega la fecha",
            icon=ft.Icons.CALENDAR_MONTH,
            on_click=lambda e: page.open(self.date_picker_control),
        )

        self.costo_field = ft.TextField(
            label="Costo",
            keyboard_type=ft.KeyboardType.NUMBER,
            data="costo",
            disabled=True,
        )

        self.entrada_salida_selector = ft.RadioGroup(
            content=ft.Row([
                ft.Radio(value=True, label="Entrada"),
                ft.Radio(value=False, label="Salida"),
            ]),
            value=True,
            on_change=self.on_entrada_salida_change,
        )


        self.model_dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Registro"),
            content=ft.Column(
                controls=[
                    ft.TextField(label="Descripcion", data="descripcion"),
                    ft.TextField(
                        label="Cantidad",
                        keyboard_type=ft.KeyboardType.NUMBER,
                        data="cantidad",
                    ),
                    self.costo_field,
                    self.date_button,
                    self.entrada_salida_selector,
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=5,
                tight=True,
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=self.close_popup),
                ft.TextButton("Guardar", on_click=self.save_new_register),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self.controls = [
            ft.Container(
                margin=ft.margin.only(top=5, right=15),
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.END,
                    spacing=10,
                    controls=[
                        ft.ElevatedButton(
                            "Volver",
                            icon=ft.Icons.ARROW_BACK,
                            icon_color=ft.Colors.WHITE,
                            color=ft.Colors.WHITE,
                            width=85,
                            bgcolor={
                                ft.ControlState.DEFAULT: ft.Colors.BLUE_200,
                                ft.ControlState.HOVERED: ft.Colors.BLUE_400,
                            },
                            on_click=self.go_back_to_main,
                        ),
                        ft.ElevatedButton(
                            "Crear",
                            icon=ft.Icons.ADD,
                            icon_color=ft.Colors.WHITE,
                            color=ft.Colors.WHITE,
                            width=85,
                            bgcolor={
                                ft.ControlState.DEFAULT: ft.Colors.BLUE_200,
                                ft.ControlState.HOVERED: ft.Colors.BLUE_400,
                            },
                            on_click=self.open_create_dialog,
                        ),
                        ft.ElevatedButton(
                            "Borrar",
                            icon=ft.Icons.DELETE,
                            icon_color=ft.Colors.WHITE,
                            color=ft.Colors.WHITE,
                            width=85,
                            bgcolor={
                                ft.ControlState.DEFAULT: ft.Colors.BLUE_200,
                                ft.ControlState.HOVERED: ft.Colors.BLUE_400,
                            },
                            on_click=self.borrar_registro,
                        ),
                    ],
                ),
            ),
            ft.Row(controls=[
                ft.Container(
                    bgcolor="#FFE1E6",
                    content=ft.Column(
                        [
                            ft.Container(
                                content=self.report_table,
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
        self.expand = True
        self.alignment = ft.MainAxisAlignment.CENTER
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    def get_report_data(self):
        """
        Llama al controlador para obtener los registros del artículo específico.
        """
        return self.controller.obtener_registros_por_articulo(self.articulo_id)

    def create_report_table(self):
        table = self.table_generator.create_table(
            table_type="report",
            width=self.page.width * 0.95,
            data=self.report_data,
            on_row_select=self.get_index
        )
        return table

    def go_back_to_main(self, e):
        self.on_volver(None)
        self.page.go("/")

    def get_index(self, e):
        row_id = e.control.data

        # Deselect all rows
        for row in self.report_table.rows:
            if row != e.control:
                row.selected = False

        # Toggle the selection of the current row
        e.control.selected = not e.control.selected

        if e.control.selected:
            self.selected_row = self.controller.obtener_registro(row_id)
        else:
            self.selected_row = None

        self.update()

    def close_popup(self, e):
        self.page.close(self.model_dlg)
        self.page.update()

    def save_new_register(self, e):
        descripcion = self.model_dlg.content.controls[0].value
        cantidad = (int(self.model_dlg.content.controls[1].value)
                    if self.model_dlg.content.controls[1].value else 0)
        costo = (float(self.model_dlg.content.controls[2].value)
                 if self.model_dlg.content.controls[2].value else 0.0)
        selected_date = self.date_picker_control.value
        entrada_value = self.entrada_salida_selector.value

        if isinstance(entrada_value, str):
            entrada = True if entrada_value.lower() == "true" else False
        elif isinstance(entrada_value, bool):
            entrada = entrada_value

        fecha_hora = None
        if selected_date:
            # Obtener la hora actual con la zona horaria de Caracas
            caracas_tz = pytz.timezone("America/Caracas")
            now = datetime.datetime.now(caracas_tz).time()

            # Combinar la fecha seleccionada con la hora actual
            fecha_hora = datetime.datetime.combine(selected_date, now)
        else:
            # Si no se seleccionó una fecha, usar la fecha y hora actual
            caracas_tz = pytz.timezone("America/Caracas")
            fecha_hora = datetime.datetime.now(caracas_tz)

        self.controller.registrar_movimiento(self.articulo_id, descripcion,
                                             entrada, cantidad, costo,
                                             fecha_hora)
        print(f"Registro guardado para el artículo ID: {self.articulo_id}")

        self.report_data = self.get_report_data()
        self.report_table = self.create_report_table()
        self.controls[-1].controls[0].content.controls[
            0].content = self.report_table
        self.update()
        self.close_popup(e)


    def borrar_registro(self, e):
        print(self.selected_row)
        if self.selected_row:
            deleted = self.controller.eliminar_registro(self.selected_row.fecha_hora)
            if deleted:
                self.selected_row = None
                self.report_data = self.get_report_data()
                self.report_table = self.create_report_table()
                self.controls[-1].controls[0].content.controls[0].content = self.report_table
                self.update()
            else:
                self.page.open(
                    ft.SnackBar(
                        ft.Text("Error al borrar el registro."),
                        open=True,
                    ))
        else:
            self.page.open(
                ft.SnackBar(
                    ft.Text("Por favor, selecciona un registro para borrar."),
                    open=True,
                ))

    def set_costo_for_salida(self):
        last_average_cost = self.controller.calcular_costo_promedio_articulo(self.articulo_id)
        if last_average_cost >= 0: # Permitir costo promedio 0
            self.costo_field.value = f"{last_average_cost:.2f}"
            self.costo_field.disabled = True
            self.costo_field.update()
        else:
            self.costo_field.value = "" # O algún otro valor por defecto si es necesario
            self.costo_field.disabled = False # Dejar habilitado si no hay costo promedio
            self.costo_field.update()

    def on_entrada_salida_change(self, e):
        selector_value = self.entrada_salida_selector.value
        if selector_value == "false":  # Salida selected (value is "False" string)
            self.set_costo_for_salida()
        else:
            self.costo_field.value = ""
            self.costo_field.disabled = False
            self.costo_field.update()
        self.model_dlg.update()

    def open_create_dialog(self, e):
        self.costo_field.disabled = False  # Aseguramos que esté habilitado por defecto al abrir
        self.costo_field.value = ""
        if not self.entrada_salida_selector.value:  # Si la salida está seleccionada por defecto
            self.set_costo_for_salida()
        self.page.open(self.model_dlg)
        self.page.update()

