from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from ventas.ventas import VentasWindow
from signin.signin import SigninWindow
from admin.admin import AdminWindow
from model.operacionesDB import cargar_ventas
class MainWindow(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(*kwargs)
        self.ventas_widget = VentasWindow()
        self.signin_widget = SigninWindow(self.ventas_widget.cargar_nombre)
        self.admin_widget = AdminWindow()
        self.ids.scrn_signin.add_widget(self.signin_widget)
        self.ids.scrn_ventas.add_widget(self.ventas_widget)
        self.ids.scrn_admin.add_widget(self.admin_widget)

class MainApp(App):
    def build(self):
        return MainWindow()
    

if __name__ =="__main__":
    MainApp().run()
    
    