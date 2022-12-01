from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.properties import BooleanProperty
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.uix.dropdown import DropDown
from datetime import datetime, timedelta
import sys
sys.path.append(r"C:\\python\\kivy_hernan")
from model.operacionesDB import obtener_producto, insertar_producto, actualizar_producto, eliminar_producto
from model.operacionesDB import obtener_usuarios, agregar_usuario, actualizar_user, eliminar_usuario
from model.operacionesDB import cargar_ventas, cargar_detalle_venta, detalle_venta_producto
Builder.load_file('admin/admin.kv')

class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior,
                                RecycleBoxLayout):
    ''' Adds selection and focus behaviour to the view. '''
    touch_deselect_last = BooleanProperty(True)

class SelectableProductoLabel(RecycleDataViewBehavior, BoxLayout):
    ''' Add selection support to the Label '''
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        self.ids['_hashtag'].text = str(1+index)
        self.ids['_codigo'].text = str(data['codigo'])
        self.ids['_articulo'].text = data['nombre'].capitalize()
        self.ids['_cantidad'].text = str(data['cantidad'])
        self.ids['_precio_compra'].text = str("{:.2f}".format(data['precio_c']))
        self.ids['_pvp'].text = str("{:.2f}".format(data['precio']))
        return super(SelectableProductoLabel, self).refresh_view_attrs(
            rv, index, data)

    def on_touch_down(self, touch):
        ''' Add selection on touch down '''
        if super(SelectableProductoLabel, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        ''' Respond to the selection of items in the view. '''
        self.selected = is_selected
        if is_selected:
            rv.data[index]['seleccionado']=True
        else:
            rv.data[index]['seleccionado']=False

class SelectableUsuarioLabel(RecycleDataViewBehavior, BoxLayout):
    ''' Add selection support to the Label '''
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        self.ids['_codigo'].text = str(data['id_user'])
        self.ids['_nombre'].text = data['nombre'].title()
        self.ids['_username'].text = data['username']
        self.ids['_tipo'].text = str(data['tipo'])
        
        return super(SelectableUsuarioLabel, self).refresh_view_attrs(
            rv, index, data)

    def on_touch_down(self, touch):
        ''' Add selection on touch down '''
        if super(SelectableUsuarioLabel, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        ''' Respond to the selection of items in the view. '''
        self.selected = is_selected
        if is_selected:
            rv.data[index]['seleccionado']=True
        else:
            rv.data[index]['seleccionado']=False


class ItemVentaLabel(RecycleDataViewBehavior, BoxLayout):
    index = None
    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        self.ids['_hashtag'].text = str(1+index)
        self.ids['_codigo'].text = data['codigo']
        self.ids['_articulo'].text = data['producto'].capitalize()
        self.ids['_cantidad'].text = str(data['cantidad'])
        self.ids['_precio_por_articulo'].text = str("{:.2f}".format(data['precio']))+" /artículo"
        self.ids['_total'].text= str("{:.2f}".format(data['total']))
        return super(ItemVentaLabel, self).refresh_view_attrs(
            rv, index, data)


class SelectableVentaLabel(RecycleDataViewBehavior, BoxLayout):
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        self.ids['_hashtag'].text = str(1+index)
        self.ids['_username'].text = data['username']
        self.ids['_cantidad'].text = str(data['productos'])
        self.ids['_total'].text = '$ '+str("{:.2f}".format(data['total']))
        self.ids['_time'].text = str(data['fecha'].strftime("%H:%M:%S"))
        self.ids['_date'].text = str(data['fecha'].strftime("%d/%m/%Y"))
        return super(SelectableVentaLabel, self).refresh_view_attrs(
            rv, index, data)

    def on_touch_down(self, touch):
        if super(SelectableVentaLabel, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        self.selected = is_selected
        if is_selected:
            rv.data[index]['seleccionado']=True
        else:
            rv.data[index]['seleccionado']=False
            
class AdminRV(RecycleView):
    def __init__(self, **kwargs):
        super(AdminRV, self).__init__(**kwargs)
        self.data = []

    def agregar_datos(self, datos):
        for dato in datos:
            dato['seleccionado']=False
            self.data.append(dato)
        self.refresh_from_data() 


    def dato_seleccionado(self):
        indice=-1
        for i in range(len(self.data)):
            if self.data[i]['seleccionado']:
                indice=i
                break
        return indice
class ProductoPopup(Popup):
    def __init__(self, agregar_callback ,**kwargs):
        super(ProductoPopup, self).__init__(**kwargs)
        self.agregar_callback = agregar_callback

    def abrir(self, agregar, producto=None):
        if agregar:
            self.ids.producto_info_1.text = 'Agregar producto nuevo'
            self.ids.producto_codigo.disabled=False
        else:
            self.ids.producto_info_1.text = 'Modificar producto'
            self.ids.producto_codigo.text = producto['codigo']
            self.ids.producto_codigo.disabled=True
            self.ids.producto_nombre.text = producto['nombre']
            self.ids.producto_cantidad.text = str(producto['cantidad'])
            self.ids.producto_precio_compra.text = str(producto['precio_c'])
            self.ids.producto_precio.text = str(producto['precio'])
        self.open()
    def verificar(self, producto_codigo, producto_nombre, producto_cantidad,producto_precio_compra, producto_precio):
        alerta1 ='Falta: '
        alerta2 = ''
        validado ={}
        if not producto_codigo:
            alerta1 += 'Codigo. '
            validado['codigo'] = False
        else:
            validado['codigo']= producto_codigo
        if not producto_nombre:
            alerta1 += 'Nombre. '
            validado['nombre'] = False
        else:
            validado['nombre']= producto_nombre
        if not producto_cantidad:
            alerta1 += 'Cantidad. '
            validado['cantidad'] = False
        else:
            try:
                numero = int(producto_cantidad)      
                validado['cantidad']= producto_cantidad 
            except:
                alerta2 += ' Cantidad no valida'
                validado['cantidad'] = False           
        if not producto_precio_compra:
            alerta1 += 'Precio compra. '
            validado['precio_c'] = False
        else:
            try:
                numero = float(producto_precio_compra)      
                validado['precio_c']= producto_precio_compra 
            except:
                alerta2 += ' Precio de compra no valido'
                validado['precio_c'] = False       
        if not producto_precio:
            alerta1 += 'Precio venta. '
            validado['precio'] = False
        else:
            try:
                numero = float(producto_precio)      
                validado['precio']= producto_precio 
            except:
                alerta2 += ' precio de venta no valido'
                validado['precio'] = False     
        valores = list(validado.values())
        if False in valores:
            self.ids.no_valid_notif.text = alerta1+alerta2
        else:
            self.ids.no_valid_notif.text = 'Valido'
            validado['cantidad'] = int(validado['cantidad'])
            validado['precio_c'] = float(validado['precio_c'])
            validado['precio'] = float(validado['precio'])
            self.agregar_callback(True, validado)
            self.dismiss()


class VistaProductos(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.cargar_prodcutos,1)

    def cargar_prodcutos(self, *args):
        _productos = obtener_producto()
        self.ids.rv_productos.agregar_datos(_productos)

    def agregar_producto(self, agregar = False, validado=None):
        if agregar:
            producto_tuple = tuple(validado.values())
            insertar_producto(producto_tuple)
            self.ids.rv_productos.data.append(validado)
            self.ids.rv_productos.refresh_from_data()


        else:
            popup= ProductoPopup(self.agregar_producto)
            popup.abrir(True)

    def modificar_producto(self, modificar = False, validado=None):
        index = self.ids.rv_productos.dato_seleccionado()
        if modificar:
            actualizar_producto(validado)
            self.ids.rv_productos.data[index]['nombre']=validado['nombre']
            self.ids.rv_productos.data[index]['cantidad']=validado['cantidad']
            self.ids.rv_productos.data[index]['precio_c']=validado['precio_c']
            self.ids.rv_productos.data[index]['precio']=validado['precio']
            self.ids.rv_productos.refresh_from_data()
        else:
            if index>=0:
                producto = self.ids.rv_productos.data[index]
                popup=ProductoPopup(self.modificar_producto)
                popup.abrir(False, producto)

    def eliminar_producto(self):
        index = self.ids.rv_productos.dato_seleccionado()
        if index>=0:
            codigo = self.ids.rv_productos.data[index]['codigo']
            eliminar_producto(codigo)
            self.ids.rv_productos.data.pop(index)
            self.ids.rv_productos.refresh_from_data()

class UsuarioPopup(Popup):
    def __init__(self, _agregar_callback, **kwargs):
        super(UsuarioPopup, self).__init__(**kwargs)
        self.agregar_usuario=_agregar_callback
    def abrir(self, agregar, usuario=None):
            if agregar:
                self.ids.usuario_info_1.text='Agregar Usuario nuevo'
                self.ids.usuario_username.disabled=False
            else:
                self.ids.usuario_info_1.text='Modificar Usuario'
                self.ids.usuario_id.text = str(usuario['id_user'])
                self.ids.usuario_id.disabled=True
                self.ids.usuario_username.text=usuario['username']
                self.ids.usuario_nombre.text=usuario['nombre']
                self.ids.usuario_password.text=usuario['password']
                if usuario['tipo']=='admin':
                    self.ids.admin_tipo.state='down'
                else:
                    self.ids.trabajador_tipo.state='down'
            self.open()

    def verificar_user(self, usuario_id, usuario_username, usuario_nombre, usuario_password, admin_tipo, trabajador_tipo):
        alert1 = 'Falta: '
        validado = {}
        if not usuario_id:
            alert1 += 'Id usuario. '
            validado['id_user'] = False
        else:
            validado['id_user']= usuario_id

        if not usuario_username:
            alert1+='Username. '
            validado['username']=False
        else:
            validado['username']=usuario_username

        if not usuario_nombre:
            alert1+='Nombre. '
            validado['nombre']=False
        else:
            validado['nombre']=usuario_nombre.lower()

        if not usuario_password:
            alert1+='Password. '
            validado['password']=False
        else:
            validado['password']=usuario_password

        if admin_tipo=='normal' and trabajador_tipo=='normal':
            alert1+='Tipo. '
            validado['tipo']=False
        else:
            if admin_tipo=='down':
                validado['tipo']='administrador'
            else:
                validado['tipo']='trabajador'

        valores = list(validado.values())
        
        if False in valores:
            self.ids.no_valid_notif.text=alert1
        else:
            self.ids.no_valid_notif.text=''
            self.agregar_usuario(True,validado)
            self.dismiss()



class VistaUsuarios(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.cargar_users,1)
    def cargar_users(self, *args):
        _user = obtener_usuarios()
        self.ids.rv_usuarios.agregar_datos(_user)

    def agregar_user(self, agregar = False, validado=None):
        if agregar:
            user_tuple = tuple(validado.values())
            agregar_usuario(user_tuple)
            self.ids.rv_usuarios.data.append(validado)
            self.ids.rv_usuarios.refresh_from_data()
        else:
            popup= UsuarioPopup(self.agregar_user)
            popup.abrir(True)

    def modificar_usuario(self, modificar = False, validado=None):
        index = self.ids.rv_usuarios.dato_seleccionado()
        if modificar:
            actualizar_user(validado)
            self.ids.rv_usuarios.data[index]['nombre']=validado['nombre']
            self.ids.rv_usuarios.data[index]['username']=validado['username']
            self.ids.rv_usuarios.data[index]['tipo']=validado['tipo']
            self.ids.rv_usuarios.refresh_from_data()
        else:
            if index>=0:
                user = self.ids.rv_usuarios.data[index]
                popup=UsuarioPopup(self.modificar_usuario)
                popup.abrir(False, user)

    def eliminar_usuario(self):
        index = self.ids.rv_usuarios.dato_seleccionado()
        if index>=0:
            codigo = self.ids.rv_usuarios.data[index]['id_user']
            eliminar_usuario(codigo)
            self.ids.rv_usuarios.data.pop(index)
            self.ids.rv_usuarios.refresh_from_data()



class InfoVentaPopup(Popup):
    def __init__(self, venta, **kwargs):
        super(InfoVentaPopup, self).__init__(**kwargs)
        self.venta=[{"codigo": producto[3], "producto": detalle_venta_producto(producto[3])[0][0], "cantidad": producto[4], "precio": producto[2], "total": producto[4]*producto[2]} for producto in venta]
        #print(self.venta)
    def mostrar(self):
        self.open()
        total_items=0
        total_dinero=0.0
        for articulo in self.venta:
            total_items+=articulo['cantidad']
            total_dinero+=float(articulo['total'])
        self.ids.total_items.text=str(total_items)
        self.ids.total_dinero.text="$ "+str("{:.2f}".format(total_dinero))
        self.ids.info_rv.agregar_datos(self.venta)
class VistaVentas(Screen):
    productos_actuales=[]
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def mas_info(self):
        indice = self.ids.ventas_rv.dato_seleccionado()
        if indice>=0:
            venta=self.productos_actuales[indice]
            p=InfoVentaPopup(venta)
            p.mostrar()


    def cargar_venta(self, choice='Default'):
        valid_input = True
        final_sum =0
        _ventas=[]
        _total_producto=[]

        f_inicio=datetime.strptime('01/01/00', '%d/%m/%y')
        f_fin=datetime.strptime('31/12/2099', '%d/%m/%Y')
        self.ids.ventas_rv.data=[]
        if choice=='Default': 
            f_inicio=datetime.today().date()
            f_fin=f_inicio+timedelta(days=1)
            self.ids.date_id.text=str(f_inicio.strftime("%d-%m-%y"))
        elif choice == 'Date':
            date = self.ids.single_date.text 
            try:
                f_elegida = datetime.strptime(date, '%d/%m/%y')
            except:
                valid_input = False
            if valid_input:
                f_inicio = f_elegida
                f_fin = f_elegida+timedelta(days=1)
                self.ids.date_id.text = f_elegida.strftime("%d-%m-%y")         
        else:
            if self.ids.initial_date.text:
                initial_date=self.ids.initial_date.text
                try:
                    f_inicio=datetime.strptime(initial_date, '%d/%m/%y')
                except:
                    valid_input=False
            if self.ids.last_date.text:
                last_date=self.ids.last_date.text
                try:
                    f_fin=datetime.strptime(last_date, '%d/%m/%y')
                except:
                    valid_input=False
            if valid_input:
                self.ids.date_id.text=f_inicio.strftime("%d-%m-%y")+" - "+f_fin.strftime("%d-%m-%y")

        if valid_input:
            lista_ventas = cargar_ventas(f_inicio, f_fin)
            if lista_ventas:
                for venta in lista_ventas:
                    final_sum += venta[1]
                    venta_detalle_sql = cargar_detalle_venta(venta[0]) 
                    _total_producto.append(venta_detalle_sql)
                    count =0
                    for producto in venta_detalle_sql:
                        count +=producto[4]
                    _ventas.append({"username": venta[3], "productos":count, "total":venta[1], "fecha":datetime.strptime(str(venta[2]), '%Y-%m-%d %H:%M:%S')})
                self.ids.ventas_rv.agregar_datos(_ventas) 
                self.productos_actuales=_total_producto
        self.ids.final_sum.text='$'+str("{:.2f}".format(final_sum))
        self.ids.initial_date.text =''
        self.ids.last_date.text=''
        self.ids.single_date.text=''
class CustomDropDown(DropDown):
    def __init__(self, cambiar_callback, **kwargs):
        self._succ_cb = cambiar_callback
        super(CustomDropDown, self).__init__(**kwargs)
    def vista(self, vista):
        if callable(self._succ_cb):
            self._succ_cb(True, vista)

class AdminWindow(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.vista_actual='Productos'
        self.vista_manager=self.ids.vista_manager
        self.dropdown = CustomDropDown(self.cambiar_vista)
        self.ids.cambiar_vista.bind(on_release = self.dropdown.open)
           
    def cambiar_vista(self, cambio=False, vista = None):
        if cambio:
            self.vista_actual = vista
            self.vista_manager.current = self.vista_actual
            self.dropdown.dismiss()

    def signout(self):
        self.parent.parent.current='scrn_signin'

    def venta(self):
        self.parent.parent.current='scrn_ventas'


class AdminApp(App):
    def build(self):
        return AdminWindow()

if __name__=="__main__":
    AdminApp().run() 