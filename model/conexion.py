import mysql.connector

class ConexionBD:
    def __init__(self):
        self.conexion = mysql.connector.connect(user='root', password='', host='localhost', database='market', port='3306')
        self.cursor = self.conexion.cursor()