import mysql.connector
import os
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

# Configuración usando tus variables de entorno
db_config = {
    'user' : os.getenv("DB_USER"),
    'password' : os.getenv("DB_PASSWORD"),
    'host' : os.getenv("DB_HOST"),
    'database' : os.getenv("DB_NAME")
}

# --- FUNCIÓN DE CONEXIÓN (ESTA ES LA QUE TE FALTABA) ---
def conectar_db():
    return mysql.connector.connect(**db_config)

# --- FUNCIONES DE USUARIO ---

def validar_login(email, password):
    usuario = obtener_usuario_por_email(email)
    if usuario:
        if bcrypt.check_password_hash(usuario['contraseña'], password):
            return usuario
    return None

def crear_usuario(nombre, correo, password):
    try:
        cnx = conectar_db()
        cursor = cnx.cursor()
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        
        sql = "INSERT INTO Usuario (nombre, correo, contraseña) VALUES (%s, %s, %s)"
        cursor.execute(sql, (nombre, correo, hashed_password))
        
        user_id = cursor.lastrowid
        cursor.execute("INSERT INTO Cliente (id_usuario) VALUES (%s)", (user_id,))
        
        cnx.commit()
        cursor.close()
        cnx.close()
        return True
    except mysql.connector.Error as err:
        print("Error al crear usuario:", err)
        return False

def obtener_usuario_por_email(email):
    try:
        cnx = conectar_db()
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Usuario WHERE correo = %s", (email,))
        usuario = cursor.fetchone()
        cursor.close()
        cnx.close()
        return usuario
    except mysql.connector.Error as err:
        print("Error al obtener usuario:", err)
        return None

def obtener_usuario_por_id(user_id):
    try:
        cnx = conectar_db()
        cursor = cnx.cursor(dictionary=True)
        sql = "SELECT * FROM Usuario WHERE id_usuario = %s"
        cursor.execute(sql, (user_id,))
        usuario = cursor.fetchone()
        cursor.close()
        cnx.close()

        # --- VALIDACIÓN ANTICRASH ---
        if usuario:
            # Si 'puntos' no está en el diccionario, lo agregamos como 0
            if 'puntos' not in usuario or usuario['puntos'] is None:
                usuario['puntos'] = 0
                
        return usuario
    except mysql.connector.Error as err:
        print("Error al obtener usuario por ID:", err)
        return None

# --- FUNCIONES DE PRODUCTOS ---

def obtener_productos():
    try:
        cnx = conectar_db()
        cursor = cnx.cursor(dictionary=True) 
        cursor.execute("SELECT * FROM Producto")
        productos = cursor.fetchall()
        cursor.close()
        cnx.close()
        return productos
    except mysql.connector.Error as err:
        print("Error al obtener productos:", err)
        return []

def obtener_producto_por_id(producto_id):
    try:
        cnx = conectar_db()
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Producto WHERE id_producto = %s", (producto_id,))
        producto = cursor.fetchone()
        cursor.close()
        cnx.close()
        return producto
    except mysql.connector.Error as err:
        print("Error al obtener el producto:", err)
        return None

# --- FUNCIONES DE PEDIDOS Y PUNTOS ---

def guardar_pedido(user_id, total, detalles):
    try:
        cnx = conectar_db()
        cursor = cnx.cursor()
        query = """
        INSERT INTO pedidos (id_usuario, total, detalles, fecha, status) 
        VALUES (%s, %s, %s, NOW(), 'En proceso')
        """
        cursor.execute(query, (user_id, total, detalles))
        cnx.commit()
        cursor.close()
        cnx.close()
        return True
    except mysql.connector.Error as err:
        print("Error al guardar pedido:", err)
        return False
    
def sumar_puntos_usuario(id_usuario, puntos_nuevos):
    try:
        cnx = conectar_db()
        cursor = cnx.cursor()
        # COALESCE asegura que si es NULL empiece en 0
        query = "UPDATE Usuario SET puntos = COALESCE(puntos, 0) + %s WHERE id_usuario = %s"
        cursor.execute(query, (puntos_nuevos, id_usuario))
        cnx.commit()
        cursor.close()
        cnx.close()
    except mysql.connector.Error as err:
        print("Error al sumar puntos:", err)

def obtener_historial(user_id):
    try:
        cnx = conectar_db()
        cursor = cnx.cursor(dictionary=True)
        query = """
        SELECT id_pedido, detalles, fecha, status, total 
        FROM pedidos 
        WHERE id_usuario = %s 
        ORDER BY fecha DESC
        """
        cursor.execute(query, (user_id,))
        pedidos = cursor.fetchall()
        cursor.close()
        cnx.close()
        return pedidos
    except mysql.connector.Error as err:
        print("Error al obtener historial:", err)
        return []