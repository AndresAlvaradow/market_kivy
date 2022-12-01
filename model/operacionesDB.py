from .conexion import ConexionBD
def obtener_producto():
    conec = ConexionBD()
    lista_productos=[]
    sql='SELECT * FROM productos'
    conec.cursor.execute(sql)
    lista_productos = conec.cursor.fetchall()
    conec.conexion.close()
    lista_data=[]
    for product in lista_productos:
        dic = {'codigo': product[0], 'nombre': product[1], 'cantidad': product[2], 'precio_c': product[3], 'precio': product[4]}
        lista_data.append(dic)
    return lista_data

def actualizar_cantidad(codigo, new_cantidad):
    conec = ConexionBD()
    sql_cantidad = f"UPDATE productos SET cantidad = '{new_cantidad}' WHERE (codigo = '{codigo}')"
    conec.cursor.execute(sql_cantidad)
    conec.conexion.commit()
    conec.conexion.close()

def obtener_usuario(nameuser):
    conec = ConexionBD()
    lista_datos=[]
    sql_usuarios = f"SELECT * FROM usuarios WHERE name_user = '{nameuser}';"
    conec.cursor.execute(sql_usuarios)
    lista_datos = conec.cursor.fetchall()
    conec.conexion.close()
    dic_user={}
    for user in lista_datos:
        dic_user = {'id_user':user[0],'name':user[1], 'username': user[2], 'password': user[3], 'tipo': user[4]}
    #print(lista_dic_user)
    if dic_user != {}:
        return dic_user
    else:
        dic_user = -1
        return dic_user

def obtener_usuarios():
    conec = ConexionBD()
    lista_usuarios=[]
    sql='SELECT * FROM usuarios'
    conec.cursor.execute(sql)
    lista_usuarios = conec.cursor.fetchall()
    conec.conexion.close()
    lista_data=[]
    for user in lista_usuarios:
        dic = {'id_user': user[0],'nombre': user[1], 'username': user[2], 'password': user[3], 'tipo': user[4]}
        lista_data.append(dic)
    return lista_data

def insertar_producto(tuple_producto):
    conec = ConexionBD()
    sql ="""INSERT INTO productos (codigo, nombre, cantidad, pcvompra, pvp) VALUES (%s, %s, %s, %s, %s)"""
    conec.cursor.execute(sql, tuple_producto)
    conec.conexion.commit()
    conec.conexion.close()

def actualizar_producto(producto):
    conec = ConexionBD()
    sql_update =f"""UPDATE productos set nombre = '{producto['nombre']}', cantidad = '{producto['cantidad']}', pcvompra = '{producto['precio_c']}', pvp = '{producto['precio']}' 
    WHERE (codigo = '{producto['codigo']}')"""
    conec.cursor.execute(sql_update)
    conec.conexion.commit()
    conec.conexion.close()

def eliminar_producto(codigo):
    conec = ConexionBD()
    sql_del =f"""DELETE FROM productos WHERE codigo = '{codigo}'"""
    conec.cursor.execute(sql_del)
    conec.conexion.commit()
    conec.conexion.close()

def agregar_usuario(tupla_user):
    conec = ConexionBD()
    sql ="""INSERT INTO usuarios (idusuarios,name, name_user, password,tipo) VALUES (%s,%s,%s,%s,%s)"""
    conec.cursor.execute(sql, tupla_user)
    conec.conexion.commit()
    conec.conexion.close()

def actualizar_user(user):
    conec = ConexionBD()
    sql_update =f"""UPDATE usuarios SET name = '{user['nombre']}', name_user = '{user['username']}', password = '{user['password']}', tipo = '{user['tipo']}' 
    WHERE (idusuarios = '{user['id_user']}');"""
    conec.cursor.execute(sql_update)
    conec.conexion.commit()
    conec.conexion.close()

def eliminar_usuario(id_user):
    conec = ConexionBD()
    sql_del =f"""DELETE FROM usuarios WHERE idusuarios = '{id_user}'"""
    conec.cursor.execute(sql_del)
    conec.conexion.commit()
    conec.conexion.close()

def insert_venta(tupla_venta):
    conec = ConexionBD()
    sql_ventas = """INSERT INTO ventas (total, fecha, idusuarios) VALUES(%s,%s,%s)"""
    conec.cursor.execute(sql_ventas, tupla_venta)
    conec.conexion.commit()
    conec.conexion.close()

def obtener_id_ventas():
    conec = ConexionBD()
    lista_ids =[]
    sql_id_ventas = "SELECT idventas  FROM ventas ORDER by idventas asc;"
    conec.cursor.execute(sql_id_ventas)
    lista_ids = conec.cursor.fetchall()
    conec.conexion.close()
    ultimo_id = lista_ids[-1][0]
    return ultimo_id

def insert_detalle_ventas(tupla_venta_detalle):
    conec = ConexionBD()
    sql_ventas = """INSERT INTO ventas_detalle (idventas, precio, producto, cantidad) VALUES(%s,%s,%s,%s)"""
    conec.cursor.execute(sql_ventas, tupla_venta_detalle)
    conec.conexion.commit()
    conec.conexion.close()

def cargar_ventas(fecha_in, fecha_fin):
    conec = ConexionBD()
    lista_ventas =[]
    select_ventas_query = f"""SELECT v.idventas, v.total, v.fecha, u.name_user FROM ventas v
                            INNER JOIN usuarios u on v.idusuarios = u.idusuarios
                            WHERE v.fecha BETWEEN '{fecha_in}' AND '{fecha_fin}'"""
    #selec_productos_query = " SELECT * FROM ventas_detalle WHERE idventas = ? "
    conec.cursor.execute(select_ventas_query)
    lista_ventas = conec.cursor.fetchall()
    conec.conexion.close()
    return lista_ventas
def cargar_detalle_venta(idventa):
    conec = ConexionBD()
    lista_detalle =[]
    sql_detalle = f"SELECT * FROM ventas_detalle WHERE idventas= {idventa}"
    conec.cursor.execute(sql_detalle)
    lista_detalle = conec.cursor.fetchall()
    conec.conexion.close()
    return lista_detalle

def detalle_venta_producto(codigo):
    conec = ConexionBD()
    lista_detalle =[]
    sql_detalle = f"SELECT nombre FROM productos WHERE codigo= {codigo}"
    conec.cursor.execute(sql_detalle)
    lista_detalle = conec.cursor.fetchall()
    conec.conexion.close()
    return lista_detalle
