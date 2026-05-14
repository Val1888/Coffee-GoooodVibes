import mysql.connector
import os
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

# Configuración usando tus variables de entorno (Asegúrate que en el .env coincidan los nombres)
db_config = {
    'user' : os.getenv("DB_USER"),
    'password' : os.getenv("DB_PASSWORD"),
    'host' : os.getenv("DB_HOST"),
    'database' : os.getenv("DB_NAME")
}

def validar_login(email, password):
    usuario = obtener_usuario_por_email(email)
    if usuario:
        # Comparamos la contraseña escrita con la de la base de datos
        if bcrypt.check_password_hash(usuario['contraseña'], password):
            return usuario
    return None

def crear_usuario(nombre, correo, password): # Dejamos 'password' aquí para que app.py no se confunda
    try:
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor()
        
        # Aquí es donde se usaba 'password', por eso fallaba
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        
        # Lo que SI debe decir 'contraseña' es el nombre de la columna de MySQL
        sql = "INSERT INTO Usuario (nombre, correo, contraseña) VALUES (%s, %s, %s)"
        cursor.execute(sql, (nombre, correo, hashed_password))
        
        # Crear el perfil de Cliente automáticamente (para el carrito)
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
        cnx = mysql.connector.connect(**db_config)
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
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor(dictionary=True)
        sql = """
        SELECT u.*, tp.puntos 
        FROM Usuario u
        LEFT JOIN Cliente c ON u.id_usuario = c.id_usuario
        LEFT JOIN TarjetaPuntos tp ON c.id_cliente = tp.id_cliente
        WHERE u.id_usuario = %s
        """
        cursor.execute(sql, (user_id,))
        usuario = cursor.fetchone()
        cursor.close()
        cnx.close()
        return usuario
    except mysql.connector.Error as err:
        print("Error al obtener usuario por ID:", err)
        return None
    



    
    # ... (mantén tus funciones anteriores igual, están perfectas)

def obtener_productos():
    try:
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor(dictionary=True) 
        cursor.execute("SELECT * FROM Producto")
        productos = cursor.fetchall()
        cursor.close()
        cnx.close()
        return productos
    except mysql.connector.Error as err:
        print("Error al obtener productos:", err)
        return []

# NUEVA: Para obtener un solo producto (útil cuando agregas al carrito)
def obtener_producto_por_id(producto_id):
    try:
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Producto WHERE id_producto = %s", (producto_id,))
        producto = cursor.fetchone()
        cursor.close()
        cnx.close()
        return producto
    except mysql.connector.Error as err:
        print("Error al obtener el producto:", err)
        return None

# NUEVA: Para ver cuánto descuento tiene un cupón (como el de tu imagen)
def validar_promocion(codigo):
    try:
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Promocion WHERE codigo = %s AND activo = TRUE", (codigo,))
        promo = cursor.fetchone()
        cursor.close()
        cnx.close()
        return promo
    except mysql.connector.Error as err:
        print("Error al validar promoción:", err)
        return None


    