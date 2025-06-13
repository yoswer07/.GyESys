import datetime
import flet as ft
import pytz
from controller import InventoryController
from flet import FilePickerResultEvent
from reportlab.pdfgen import canvas


class ButtonGenerator:
    def __init__(self, page, selected_row, toggle_sidebar_callback, on_refresh_table, origin="principal", table_data=None):
        self.page = page
        self.selected_row = selected_row
        self.controller = InventoryController()
        self.toggle_sidebar_callback = toggle_sidebar_callback
        self.on_refresh_table = on_refresh_table
        self.origin = origin
        self.table_data = table_data or []
        self.start_date = None
        self.end_date = None

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

        self.start_date_picker = ft.DatePicker(
            first_date=datetime.datetime(2010, 1, 1),
            date_picker_mode=ft.DatePickerMode.DAY,
            on_change=lambda e: setattr(self, "start_date", e.control.value),
        )
        self.end_date_picker = ft.DatePicker(
            first_date=datetime.datetime(2010, 1, 1),
            date_picker_mode=ft.DatePickerMode.DAY,
            on_change=lambda e: setattr(self, "end_date", e.control.value),
        )
        self.file_picker = ft.FilePicker(on_result=self.on_file_selected)
        self.page.overlay.append(self.file_picker)

        self.selected_file_path = None

        self.generate_pdf_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Generar Reporte PDF"),
            content=ft.Column(
                [
                    ft.Text("Selecciona una fecha para guardar el PDF:"),
                    ft.Row([
                        ft.TextButton("Fecha inicio", on_click=lambda _: self.page.open(self.start_date_picker)),
                        ft.TextButton("Fecha final", on_click=lambda _: self.page.open(self.end_date_picker)),
                    ]),
                    ft.TextButton(
                        "Seleccionar ubicación",
                        on_click=lambda _: self.file_picker.save_file(
                            dialog_title="Guardar reporte PDF",
                            file_name="reporte.pdf"
                        )
                    ),
                ],
                tight=True,
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: self.page.close(self.generate_pdf_dialog)),
                ft.TextButton("Aceptar", on_click=self.generate_pdf),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.model_dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Articulo"),
            content=ft.Column(
                controls=[
                    ft.TextField(label="Nombre", data="nombre"),
                    ft.TextField(label="Categoria", data="categoria"),
                    ft.TextField(
                        label="Cantidad",
                        keyboard_type=ft.KeyboardType.NUMBER,
                        data="cantidad",
                    ),
                    ft.TextField(
                        label="Costo",
                        keyboard_type=ft.KeyboardType.NUMBER,
                        data="costo",
                    ),
                    ft.TextField(label="Codigo de barras", data="bar_code"),
                    self.date_button,
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=5,
                tight=True,
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=self.close_popup),
                ft.TextButton("Guardar", on_click=self.save_new_item),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

    def generate_buttons(self):
        """Genera los botones de acción de la vista principal, con el estado actual de selected_row."""
        reporte_detallado_button = ft.ElevatedButton(
            "Reporte Detallado",
            icon=ft.Icons.PICTURE_AS_PDF,
            icon_color=ft.Colors.WHITE,
            color=ft.Colors.WHITE,
            width=150,
            bgcolor={ft.ControlState.DEFAULT: ft.Colors.GREEN_200, ft.ControlState.HOVERED: ft.Colors.GREEN_400},
            on_click=lambda e: self.page.open(self.generate_pdf_dialog),
        )
        ver_button = ft.ElevatedButton(
            "Ver",
            icon=ft.Icons.REMOVE_RED_EYE_SHARP,
            icon_color=ft.Colors.WHITE,
            color=ft.Colors.WHITE,
            width=85,
            bgcolor={ft.ControlState.DEFAULT: ft.Colors.BLUE_200, ft.ControlState.HOVERED: ft.Colors.BLUE_400},
            on_click=self.ver_articulo_reporte,
        )

        crear_button = ft.ElevatedButton(
            "Crear",
            icon=ft.Icons.ADD,
            icon_color=ft.Colors.WHITE,
            color=ft.Colors.WHITE,
            width=85,
            bgcolor={ft.ControlState.DEFAULT: ft.Colors.BLUE_200, ft.ControlState.HOVERED: ft.Colors.BLUE_400},
            on_click=self.open_popup,
        )

        editar_button = ft.ElevatedButton(
            "Editar",
            icon=ft.Icons.EDIT,
            icon_color=ft.Colors.WHITE,
            color=ft.Colors.WHITE,
            width=85,
            bgcolor={ft.ControlState.DEFAULT: ft.Colors.BLUE_200, ft.ControlState.HOVERED: ft.Colors.BLUE_400},
            on_click=self.open_popup,
        )

        borrar_button = ft.ElevatedButton(
            "Borrar",
            icon=ft.Icons.DELETE,
            icon_color=ft.Colors.WHITE,
            color=ft.Colors.WHITE,
            width=85,
            bgcolor={ft.ControlState.DEFAULT: ft.Colors.BLUE_200, ft.ControlState.HOVERED: ft.Colors.BLUE_400},
            on_click=self.borrar_articulo,
        )

        # Actualizar la habilitación de los botones dependiendo de selected_row
        if not self.selected_row:
            editar_button.disabled = True
            borrar_button.disabled = True
            ver_button.disabled = True
        else:
            editar_button.disabled = False
            borrar_button.disabled = False
            ver_button.disabled = False

        return [reporte_detallado_button, ver_button, crear_button, editar_button, borrar_button]

    def ver_articulo_reporte(self, e):
        """Handles the click event for the 'Ver' button to open the report view using routing."""
        if self.selected_row and self.selected_row.id is not None:
            self.toggle_sidebar_callback(None)
            self.page.go(f"/report/{self.selected_row.id}")
        else:
            self.page.open(
                ft.SnackBar(
                    ft.Text(
                        "Por favor, selecciona un artículo de la tabla para ver el reporte."
                    ),
                    open=True,
                )
            )
    
    def open_popup(self, e):
        if e.control.text == "Editar":
            if self.selected_row:
                self.model_dlg.title.value = "Editar Articulo"
                for control in self.model_dlg.content.controls:
                    if isinstance(control, ft.TextField):
                        control.disabled = (
                            False  # Habilitar todos los campos al principio
                        )
                        if control.data:
                            control.value = str(
                                getattr(self.selected_row, control.data)
                            )
                            if control.data in ["cantidad", "costo"]:
                                control.disabled = (
                                    True  # Deshabilitar Cantidad y Costo para editar
                                )
                    elif (
                        isinstance(control, ft.ElevatedButton)
                        and control.text == "Agrega la fecha"
                    ):
                        control.disabled = True
                self.page.open(self.model_dlg)
                self.page.update()
            else:
                self.page.open(
                    ft.SnackBar(
                        ft.Text(
                            "Por favor, selecciona un artículo de la tabla para editar."
                        ),
                        open=True,
                    )
                )
        else:  # It's the "Crear" button
            self.model_dlg.title.value = "Crear Articulo"
            for control in self.model_dlg.content.controls:
                if isinstance(control, ft.TextField):
                    control.value = ""
                    control.disabled = (
                        False  # Asegurar que los campos estén habilitados para crear
                    )
                elif (
                    isinstance(control, ft.ElevatedButton)
                    and control.text == "Agrega la fecha"
                ):
                    control.disabled = False  # Habilitar el botón de la fecha en crear
            self.selected_row = None
            self.page.open(self.model_dlg)
            self.page.update()

    def close_popup(self, e):
        self.page.close(self.model_dlg)
        self.page.update()

    def save_new_item(self, e):
        nombre = self.model_dlg.content.controls[0].value
        categoria = self.model_dlg.content.controls[1].value
        cantidad = (
            int(self.model_dlg.content.controls[2].value)
            if self.model_dlg.content.controls[2].value
            else 0
        )
        costo = (
            float(self.model_dlg.content.controls[3].value)
            if self.model_dlg.content.controls[3].value
            else 0.0
        )
        bar_code = self.model_dlg.content.controls[4].value
        selected_date = self.date_picker_control.value

        if not self.selected_row and selected_date:
            # Obtener la hora actual con la zona horaria de Caracas
            caracas_tz = pytz.timezone("America/Caracas")
            now = datetime.datetime.now(caracas_tz).time()

            # Combinar la fecha seleccionada con la hora actual
            fecha_hora = datetime.datetime.combine(selected_date, now)
        elif not self.selected_row:
            # Si no se seleccionó una fecha, usar la fecha y hora actual
            caracas_tz = pytz.timezone("America/Caracas")
            fecha_hora = datetime.datetime.now(caracas_tz)
        else:
            fecha_hora = None  # No se guarda fecha al editar

        if self.selected_row:
            updated_articulo_data = self.controller.actualizar_articulo(
                self.selected_row.id, nombre, categoria, cantidad, costo, bar_code
            )
            print(f"Artículo actualizado: {updated_articulo_data}")
            self.selected_row = None
        else:
            nuevo_articulo_data = self.controller.crear_articulo(
                nombre, categoria, cantidad, costo, bar_code, fecha_hora
            )
            print(f"Artículo guardado: {nuevo_articulo_data}")

        self.on_refresh_table()  # Llamar a on_refresh_table después de guardar/actualizar
        self.close_popup(e)

    def borrar_articulo(self, e):
        if self.selected_row:
            delete_register = self.controller.eliminar_todo_registro(
                self.selected_row.id
            )
            deleted = self.controller.eliminar_articulo(self.selected_row.id)
            if delete_register and deleted:
                self.selected_row = None
                self.on_refresh_table()
                self.page.open(
                    ft.SnackBar(
                        ft.Text("Artículo eliminado correctamente."),
                        open=True,
                    )
                )
            else:
                self.page.open(
                    ft.SnackBar(
                        ft.Text("Error al borrar el artículo."),
                        open=True,
                    )
                )
        else:
            self.page.open(
                ft.SnackBar(
                    ft.Text("Por favor, selecciona un artículo para borrar."),
                    open=True,
                )
            )

    def on_file_selected(self, e: FilePickerResultEvent):
        if e.path:
            self.selected_file_path = e.path if e.path.endswith(".pdf") else e.path + ".pdf"
            print("Ruta seleccionada:", self.selected_file_path)

    def generate_pdf(self, e):
        if not self.selected_file_path:
            self.page.open(ft.SnackBar(ft.Text("Por favor selecciona una ubicación para guardar el PDF."), open=True))
            return

        if not self.start_date or not self.end_date:
            self.page.open(ft.SnackBar(ft.Text("Por favor selecciona ambas fechas."), open=True))
            return

        if self.start_date > self.end_date:
            self.page.open(ft.SnackBar(ft.Text("La fecha de inicio debe ser menor o igual a la fecha final."), open=True))
            return

        c = canvas.Canvas(self.selected_file_path)
        y = 800

        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y, f"Reporte Detallado: {self.start_date.strftime('%Y-%m-%d')} al {self.end_date.strftime('%Y-%m-%d')}")
        y -= 30

        registros = self.controller.generar_reporte_detallado(
            self.start_date, self.end_date
        )

        # Filtrar los registros solo si estás en la vista de categoría
        if self.origin == "categoria" and self.table_data:
            ids_filtrados = {articulo["id"] for articulo in self.table_data}
            registros = [r for r in registros if r["articulo_id"] in ids_filtrados]

        for articulo in registros:
            c.setFont("Helvetica-Bold", 10)
            c.drawString(50, y, f"Artículo ID: {articulo['articulo_id']} - {articulo['nombre']} ({articulo['categoria']})")
            y -= 20

            c.setFont("Helvetica", 9)
            c.drawString(60, y, f"Entradas: {articulo['entradas']}")
            c.drawString(180, y, f"Salidas: {articulo['salidas']}")
            c.drawString(300, y, f"% Salidas: {articulo['porcentaje_salida']}%")
            c.drawString(440, y, f"Costo Promedio: {articulo['costo_promedio']:.2f}")
            y -= 30

            if y < 50:
                c.showPage()
                y = 800

        c.save()
        self.page.close(self.generate_pdf_dialog)
        self.page.open(ft.SnackBar(ft.Text("Reporte detallado generado exitosamente."), open=True))