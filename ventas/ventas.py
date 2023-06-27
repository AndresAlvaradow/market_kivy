from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.properties import BooleanProperty
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.popup import Popup
from datetime import datetime, timedelta
from kivy.clock import Clock
from kivy.lang import Builder
Builder.load_file('ventas/ventas.kv')
import sys
sys.path.append(r"C:\\proyectosPython\\market_kivy-main")
from model.operacionesDB import obtener_producto, actualizar_cantidad, insert_venta, obtener_id_ventas, insert_detalle_ventas


'''inventario=[
    {'codigo': '111', 'nombre': 'leche 1L', 'precio': 20.0, 'cantidad': 20},
    {'codigo': '222', 'nombre': 'cereal 500g', 'precio': 50.5, 'cantidad': 15}, 
    {'codigo': '333', 'nombre': 'yogurt 1L', 'precio': 25.0, 'cantidad': 10},
    {'codigo': '444', 'nombre': 'helado 2L', 'precio': 80.0, 'cantidad': 20},
    {'codigo': '555', 'nombre': 'alimento para perro 20kg', 'precio': 750.0, 'cantidad': 5},
    {'codigo': '666', 'nombre': 'shampoo', 'precio': 100.0, 'cantidad': 25},
    {'codigo': '777', 'nombre': 'papel higiénico 4 rollos', 'precio': 35.5, 'cantidad': 30},
    {'codigo': '888', 'nombre': 'jabón para trastes', 'precio': 65.0, 'cantidad': 5},
    {'codigo': '999', 'nombre': 'refresco 600ml', 'precio': 15.0, 'cantidad': 10},
    {'codigo': '123', 'nombre': 'leche nutri', 'precio': 15.0, 'cantidad': 15}
]'''


class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior,
                                RecycleBoxLayout):
    ''' Adds selection and focus behaviour to the view. '''
    touch_deselect_last = BooleanProperty(True)


class SelectableBoxLayout(RecycleDataViewBehavior, BoxLayout):
    ''' Add selection support to the Label '''
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        self.ids['_codigo'].text = str(1+index)
        self.ids['_articulo'].text = data['nombre'].capitalize()
        self.ids['_cantidad'].text = str(data['cantidad_carrito'])
        self.ids['_precio_compra'].text = str("{:.2f}".format(data['precio']))
        self.ids['_pvp'].text = str("{:.2f}".format(data['precio_total']))
        return super(SelectableBoxLayout, self).refresh_view_attrs(
            rv, index, data)

    def on_touch_down(self, touch):
        ''' Add selection on touch down '''
        if super(SelectableBoxLayout, self).on_touch_down(touch):
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


class SelectableBoxLayoutPopup(RecycleDataViewBehavior, BoxLayout):
    ''' Add selection support to the Label '''
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        self.ids['_code'].text = data['codigo']
        self.ids['_articulo'].text = data['nombre'].capitalize()
        self.ids['_cantidad'].text = str(data['cantidad'])
        self.ids['_precio'].text = str("{:.2f}".format(data['precio']))
        return super(SelectableBoxLayoutPopup, self).refresh_view_attrs(
            rv, index, data)

    def on_touch_down(self, touch):
        ''' Add selection on touch down '''
        if super(SelectableBoxLayoutPopup, self).on_touch_down(touch):
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

class RV(RecycleView):
    def __init__(self, **kwargs):
        super(RV, self).__init__(**kwargs)
        self.data = []
        self.modificar_producto =None

    def agregar_articulo(self, articulo):
        articulo['seleccionado']=False
        indice=-1
        if self.data:
            for i in range(len(self.data)):
                if articulo['codigo']==self.data[i]['codigo']:
                    indice=i
            if indice >=0:
                self.data[indice]['cantidad_carrito']+=1
                self.data[indice]['precio_total']=self.data[indice]['precio']*self.data[indice]['cantidad_carrito']
                self.refresh_from_data() 
            else:
                self.data.append(articulo)
        else:
            self.data.append(articulo)

    def eliminar_articulo(self):
        indice=self.articulo_seleccionado()
        precio=0
        if indice>=0:
            self._layout_manager.deselect_node(self._layout_manager._last_selected_node)
            precio=self.data[indice]['precio_total']
            self.data.pop(indice)
            self.refresh_from_data()
        return precio

    def modificar_articulo(self):
        indice=self.articulo_seleccionado()
        if indice>=0:
            popup=CambiarCantidadPopup(self.data[indice], self.actualizar_articulo)
            popup.open()

    def actualizar_articulo(self, valor):
        indice=self.articulo_seleccionado()
        if indice>=0:
            if valor==0:
                self.data.pop(indice)
                self._layout_manager.deselect_node(self._layout_manager._last_selected_node)
            else:
                self.data[indice]['cantidad_carrito']=valor
                self.data[indice]['precio_total']=self.data[indice]['precio']*valor
            self.refresh_from_data()
            nuevo_total=0
            for data in self.data:
                nuevo_total+=float(data['precio_total'])# cambio 14/11/22
            self.modificar_producto(False, nuevo_total)
    def articulo_seleccionado(self):
            indice=-1
            for i in range(len(self.data)):
                if self.data[i]['seleccionado']:
                    indice=i
                    break
            return indice


class ProductoPorNombrePopup(Popup):
    def __init__(self, input_nombre, agregar_producto_callback, **kwargs):
        super(ProductoPorNombrePopup, self).__init__(**kwargs)
        self.input_nombre=input_nombre
        self.agregar_producto=agregar_producto_callback

    def mostrar_articulos(self):
        inventario= obtener_producto()
        self.open()
        for nombre in inventario:
            if nombre['nombre'].lower().find(self.input_nombre)>=0:
                producto={'codigo': nombre['codigo'], 'nombre': nombre['nombre'], 'precio': nombre['precio'], 'cantidad': nombre['cantidad']}
                self.ids.rvs.agregar_articulo(producto)

    def seleccionar_articulo(self):
        indice=self.ids.rvs.articulo_seleccionado()
        if indice>=0:
            _articulo=self.ids.rvs.data[indice]
            articulo={}
            articulo['codigo']=_articulo['codigo']
            articulo['nombre']=_articulo['nombre']
            articulo['precio']=_articulo['precio']
            articulo['cantidad_carrito']=1
            articulo['cantidad_inventario']=_articulo['cantidad']
            articulo['precio_total']=_articulo['precio']
            if callable(self.agregar_producto):
                self.agregar_producto(articulo)
            self.dismiss()
class CambiarCantidadPopup(Popup):
    def __init__(self, data, actualizar_articulo_callback, **kwargs):
        super(CambiarCantidadPopup, self).__init__(**kwargs)
        self.data=data
        self.actualizar_articulo=actualizar_articulo_callback
        self.ids.info_nueva_cant_1.text = "Producto: " + self.data['nombre'].capitalize()
        self.ids.info_nueva_cant_2.text = "Cantidad: "+str(self.data['cantidad_carrito'])

    def validar_input(self, texto_input):
        try:
            nueva_cantidad = int(texto_input)
            self.ids.notificacion_no_valido.text=''
            self.actualizar_articulo(nueva_cantidad)
            self.dismiss()
        except:
            self.ids.notificacion_no_valido.text='Cantidad no valida'

class PagarPopup(Popup):
    def __init__(self, total, pago_callback ,**kwargs):
        super(PagarPopup, self).__init__(**kwargs)
        self.total = total
        self.pagado = pago_callback
        self.ids.total.text ="{:.2f}".format(self.total)
    def mostrar_cambio(self):
        recibido = self.ids.recibido.text
        try:
            cambio = float(recibido)- float(self.total)
            if cambio>=0:
                self.ids.cambio.text="{:.2f}".format(cambio)
                self.ids.boton_pagar.disabled = False
            else:
                self.ids.cambio.text="Cambio es menor a la cantidad ingresada"
        except:
            self.ids.cambio.text= "Pago no valido"
    def terminar_pago(self):
        self.pagado()
        self.dismiss()

class NuevaCompraPopup(Popup):
    def __init__(self,nuevo_callback, **kwargs):
        super(NuevaCompraPopup, self).__init__(**kwargs)
        self.nueva_compra = nuevo_callback
        self.ids.aceptar.bind(on_release= self.dismiss)

class VentasWindow(BoxLayout):
    usuario = None
    def __init__(self,actualizar_productos_callback, **kwargs):
        super().__init__(*kwargs)
        self.total=0.0
        self.ids.rvs.modificar_producto=self.modificar_producto
        self.actualizar_productos = actualizar_productos_callback
        self.date_now = datetime.now()
        self.ids.fecha.text=self.date_now.strftime("%d/%m/%y")
        Clock.schedule_interval(self.hora_actual, 1)
        
    def agregar_producto_codigo(self, codigo):
        inventario= obtener_producto()
        for producto in inventario:
            if codigo==producto['codigo']:
                articulo={}
                articulo['codigo']=producto['codigo']
                articulo['nombre']=producto['nombre']
                articulo['precio']=producto['precio']
                articulo['cantidad_carrito']=1
                articulo['cantidad_inventario']=producto['cantidad']
                articulo['precio_total']=producto['precio']
                self.agregar_producto(articulo)
                self.ids.buscar_codigo.text=''
                break

    def agregar_producto_nombre(self, nombre):
        self.ids.buscar_nombre.text=''
        popup=ProductoPorNombrePopup(nombre, self.agregar_producto)
        popup.mostrar_articulos()

    def agregar_producto(self, articulo):
        self.total+=float(articulo['precio'])
        self.ids.sub_total.text= '$ '+"{:.2f}".format(self.total)
        self.ids.rvs.agregar_articulo(articulo)

    def hora_actual(self, *args):
        self.date_now = self.date_now+timedelta(seconds=1)
        self.ids.hora.text=self.date_now.strftime("%H:%M:%S")

    def eliminar_producto(self):
        menos_precio=self.ids.rvs.eliminar_articulo()
        self.total-=float(menos_precio)
        self.ids.sub_total.text='$ '+"{:.2f}".format(self.total)

    def modificar_producto(self, cambio=True, nuevo_total=None):
        if cambio:
            self.ids.rvs.modificar_articulo()
        else:
            self.total=nuevo_total
            self.ids.sub_total.text='$ '+"{:.2f}".format(self.total)

    def pagar(self):
        if self.ids.rvs.data:
            popup = PagarPopup(self.total, self.pago)
            popup.open()
        else:
            self.ids.notificacion_falla.text='No existen elementos a pagar'
    def pago(self):
        self.ids.notificacion_exito.text = 'Compra realizada con exito'
        self.ids.notificacion_falla.text=''
        self.ids.total.text="{:.2f}".format(self.total)
        self.ids.buscar_codigo.disabled=True
        self.ids.buscar_nombre.disabled=True
        nueva_cantidad = []
        venta_tuple = (self.total, self.date_now, self.usuario['id_user'])
        insert_venta(venta_tuple)
        id_venta = obtener_id_ventas()
        #print("aqui va el ultima venta ", id_venta)

        for producto in self.ids.rvs.data:
            cantidad = producto['cantidad_inventario']-producto['cantidad_carrito']
            if cantidad >=0:
                nueva_cantidad.append({'codigo':producto['codigo'], 'cantidad':cantidad})
            else:
                nueva_cantidad.append({'codigo':producto['codigo'], 'cantidad':0})

            ventas_detalle_tuple = (id_venta, producto['precio'], producto['codigo'], producto['cantidad_carrito'])
            insert_detalle_ventas(ventas_detalle_tuple)
        inventario= obtener_producto()
        for cantidad in nueva_cantidad:
            res = next((producto for producto in inventario if producto['codigo']==cantidad['codigo']), None)
            res['cantidad']= cantidad['cantidad']
        #print("cantidad nueva", cantidad['codigo'], cantidad['cantidad'])
        actualizar_cantidad(cantidad['codigo'], cantidad['cantidad'])

        self.actualizar_productos(nueva_cantidad)

        
    def nueva_compra(self, desde_pop= False):
        if desde_pop:
            self.ids.rvs.data = []
            self.total = 0.0
            self.ids.sub_total.text = '0.00'
            self.ids.total.text = '0.00'
            self.ids.notificacion_exito.text = ''
            self.ids.notificacion_falla.text=''
            self.ids.buscar_codigo.disabled=False
            self.ids.buscar_nombre.disabled=False
            self.ids.rvs.refresh_from_data()
        elif len(self.ids.rvs.data):
            popup = NuevaCompraPopup(self.nueva_compra)
            popup.open()


    def admin(self):
        #print("Admin presionado",inventario)
        self.parent.parent.current='scrn_admin'

    def signout(self):
        self.parent.parent.current='scrn_signin'

    def cargar_nombre(self, dic_user):
        self.ids.bienvenido_label.text =f"Bienvenido: {dic_user['name']}"
        self.usuario = dic_user
        if dic_user['tipo'] == 'trabajador':
            self.ids.admin_boton.disabled=True
        else:
            self.ids.admin_boton.disabled=False
        #print(dic_user)

class VentasApp(App):
    def build(self):
        return VentasWindow()


if __name__=='__main__':
    VentasApp().run()