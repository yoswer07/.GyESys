import flet as ft
from app_layout import AppLayout
 
class TrelloApp(AppLayout):
    def __init__(self, page: ft.Page):
        super().__init__(app=self, page=page)
        self.page = page
        self.page.on_route_change = super().route_change 
        self.test_image = ft.Image(src="Icon2.png", width=75, height=75, tooltip="Image Tooltip")
        page.fonts = {
        "Play Fair": "PlayfairDisplay-VariableFont_wght.ttf"
        }
        self.appbar_items = [
            ft.PopupMenuItem(text="Login"),
            ft.PopupMenuItem(),  # divider
            ft.PopupMenuItem(text="Settings")
        ]
        self.appbar = ft.AppBar(
            leading=self.test_image,
            leading_width=60,
            title=ft.Text("Inventario",size=28, text_align="start", font_family="Play Fair", color='#ffffff'),
            center_title=False,
            toolbar_height=45,
            bgcolor='#D9839E',
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
        page.bgcolor = '#FFFCF5'
        page.theme_mode = ft.ThemeMode.LIGHT

        app = TrelloApp(page)
        page.go("/")
        page.add(app)
        page.update()
 
    ft.app(main, assets_dir="assets")