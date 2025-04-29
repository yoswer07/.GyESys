import flet as ft


class TableGenerator:
    def __init__(self, controller):
        self.controller = controller
    def create_table(self, table_type, width, data, on_row_select=None):
        self.valor_total_acumulado = 0
        self.cantidad_total = 0
        columns = self.get_columns_definition(table_type)
        rows = []
        for item in data:
            if table_type == 'report':

                entrada_salida = item['entrada_salida']
                cantidad = item['unidad']
                costo_unitario = item['costo']
                costo_total = cantidad * costo_unitario

                # Actualización de cantidades acumuladas
                if entrada_salida:
                    self.cantidad_total += cantidad
                    self.valor_total_acumulado += costo_total
                else:
                    self.cantidad_total -= cantidad
                    self.valor_total_acumulado -= costo_total

                # Cálculo del costo promedio ponderado
                if self.cantidad_total != 0:
                    costo_promedio = self.valor_total_acumulado / self.cantidad_total

                valor_total = self.cantidad_total * costo_promedio
                
                cells = self._create_cells(table_type, item, self.cantidad_total, costo_total, costo_promedio, valor_total)
            else:
                cells = self._create_cells(table_type, item)
            row = ft.DataRow(
                cells=cells,
                data= item["id"] if table_type == "main" else item["fecha_hora"],
                on_select_changed=on_row_select,
            )
            if table_type == "report":
                row.color = self.get_row_color(item)
            rows.append(row)
        return ft.DataTable(
            columns=columns,
            rows=rows,
            expand=True,
            show_checkbox_column=True,
            width=width,
        )

    def get_row_color(self, item):
        """
        Determina el color de fondo de la fila en función de la entrada/salida.
        """
        entrada_salida = item["entrada_salida"]
        cantidad_cell_bgcolor = (
            ft.Colors.GREEN_ACCENT_700 if entrada_salida else ft.Colors.RED_ACCENT_700
        )
        cantidad_cell_bgcolor_selected = (
            ft.Colors.GREEN_700 if entrada_salida else ft.Colors.RED_700
        )
        return {
            ft.ControlState.DEFAULT: cantidad_cell_bgcolor,
            ft.ControlState.SELECTED: cantidad_cell_bgcolor_selected,
        }

    def get_columns_definition(self, table_type):
        if table_type == "main":
            return [
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Nombre")),
                ft.DataColumn(ft.Text("Categoría")),
                ft.DataColumn(ft.Text("Cantidad")),
                ft.DataColumn(ft.Text("Costo Promedio")),
                ft.DataColumn(ft.Text("Código de Barras")),
            ]
        elif table_type == "report":
            return [
                ft.DataColumn(ft.Text("Fecha/Hora", selectable=True), data="fecha_hora"),
                ft.DataColumn(ft.Text("Descripción", selectable=True), data="descripcion"),
                ft.DataColumn(ft.Text("Cantidad", selectable=True), data="cantidad"),
                ft.DataColumn(ft.Text("Costo Unitario", selectable=True), data="costo"),
                ft.DataColumn(ft.Text("Costo Total", selectable=True), data="costo_total"),
                ft.DataColumn(ft.Text("Cantidad Total", selectable=True), data="cantidad_total"),
                ft.DataColumn(ft.Text("Costo Promedio", selectable=True), data="costo_promedio"),
                ft.DataColumn(ft.Text("Valor Total", selectable=True), data="valor_total"),
            ]
        return []

    def _create_cells(self, table_type, item, cantidad_total = 0, costo_total = 0, costo_promedio = 0, valor_total = 0):
        if table_type == "main":
            return [
                ft.DataCell(ft.Text(item.get("id"))),
                ft.DataCell(ft.Text(item.get("nombre"))),
                ft.DataCell(ft.Text(item.get("categoria"))),
                ft.DataCell(ft.Text(item.get("cantidad"))),
                ft.DataCell(
                    ft.Text(f"{item.get('costo'):.2f}")
                    if item.get("costo") is not None
                    else ft.Text("")
                ),
                ft.DataCell(ft.Text(item.get("bar_code"))),
            ]
        elif table_type == "report":
            return [
                ft.DataCell(ft.Text(item.get("fecha_hora").strftime("%Y-%m-%d %H:%M:%S") if item.get("fecha_hora") else "")),
                ft.DataCell(ft.Text(item.get("descripcion"))),
                ft.DataCell(ft.Text(str(item.get("unidad")))),
                ft.DataCell(ft.Text(f"{item.get('costo'):.2f}" if item.get("costo") is not None else "")),
                ft.DataCell(ft.Text(f"{costo_total:.2f}")),  # Costo total calculado
                ft.DataCell(ft.Text(f"{cantidad_total}")),  # Cantidad total calculada
                ft.DataCell(ft.Text(f"{costo_promedio:.2f}")),  # Costo promedio calculado
                ft.DataCell(ft.Text(f"{valor_total:.2f}")),  # Valor total calculado
            ]
        return []
