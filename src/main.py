import flet as ft
from app_layout import AppLayout
 
class TrelloApp(AppLayout):
    def __init__(self, page: ft.Page):
        super().__init__(app=self, page=page)
        self.page = page
        self.page.on_route_change = super().route_change 
        self.appbar_items = [
            ft.PopupMenuItem(text="Login"),
            ft.PopupMenuItem(),  # divider
            ft.PopupMenuItem(text="Settings")
        ]
        self.appbar = ft.AppBar(
            leading=ft.Icon(ft.Icons.GRID_GOLDENRATIO_ROUNDED),
            leading_width=75,
            title=ft.Text("Inventario",size=26, text_align="start"),
            center_title=False,
            toolbar_height=50,
            bgcolor=ft.Colors.LIGHT_BLUE_ACCENT_700,
            actions=[
                ft.Container(
                    content=ft.PopupMenuButton(
                        items=self.appbar_items
                    ),
                    margin=ft.margin.only(left=50, right=25)
                )
            ],
        )
        self.page.appbar = self.appbar
        
if __name__ == "__main__":
 
    def main(page: ft.Page):
 
        page.title = "Inventario"
        page.padding = 0
        page.bgcolor = ft.Colors.BLUE_GREY_200

        app = TrelloApp(page)
        page.go("/")
        page.add(app)
        page.update()
 
    ft.app(main)