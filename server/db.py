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
        if bcrypt.check_password_hash(usuario['password'], password):
            return usuario
    return None

def crear_usuario(nombre, correo, password):
    try:
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor()
        
        # Encriptamos la contraseña antes de guardarla
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        
        # Insertar en la tabla Usuario
        sql = "INSERT INTO Usuario (nombre, correo, password) VALUES (%s, %s, %s)"
        cursor.execute(sql, (nombre, correo, hashed_password))
        
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