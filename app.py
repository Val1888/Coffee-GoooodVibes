from dotenv import load_dotenv
load_dotenv()

import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_bcrypt import Bcrypt
from server.db import obtener_usuario_por_id, validar_login, crear_usuario # Asegúrate de tener estas en db.py

app = Flask(__name__, template_folder='client/templates')
app.secret_key = os.environ.get('SECRET_KEY', 'WUATAJAI')
bcrypt = Bcrypt(app)

# Decorador para proteger rutas
def login_required(f):
    from functools import wraps 
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# --- RUTAS PÚBLICAS ---

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/menu')
def menu():
    return render_template('menu.html')

@app.route('/nosotros')
def nosotros():
    return render_template('nosotros.html')

@app.route('/locales')
def locales():
    return render_template('locales.html')

# --- RUTAS DE AUTENTICACIÓN (LOGIN/SIGNUP) ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        correo = request.form.get('correo')
        password = request.form.get('password')
        
        # Aquí llamarías a tu función de db.py
        user = validar_login(correo, password)
        if user:
            session['logged_in'] = True
            session['user_id'] = user['id_usuario']
            session['nombre'] = user['nombre']
            return redirect(url_for('home'))
        else:
            flash('Correo o contraseña incorrectos')
            return redirect(url_for('login'))
            
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        correo = request.form.get('correo')
        password = request.form.get('password')
        
        # Lógica para crear usuario en la DB
        if crear_usuario(nombre, correo, password):
            flash('¡Cuenta creada con éxito! Ya puedes iniciar sesión.')
            return redirect(url_for('login'))
        else:
            flash('Error al crear la cuenta. El correo ya podría estar registrado.')
            
    return render_template('signin.html')

# --- RUTAS PROTEGIDAS (CLIENTE LOGUEADO) ---

@app.route('/cuenta')
@login_required
def cuenta():
    user_id = session.get('user_id')
    user_data = obtener_usuario_por_id(user_id)
    
    # Lógica de niveles
    puntos = user_data.get('puntos', 0)
    nivel = (puntos // 100) + 1
    
    if nivel <= 3: rango = "Amante del Café"
    elif nivel <= 6: rango = "Entusiasta del Café"
    elif nivel <= 10: rango = "Maestro Cafetero"
    else: rango = "Leyenda del Café"

    return render_template('auth/cuenta.html', usuario=user_data, nivel=nivel, rango=rango)

@app.route('/pago')
@login_required
def pago():
    return render_template('auth/pago.html', total=163.00, puntos_precio=500)

@app.route('/compra-exitosa')
@login_required
def exito():
    return render_template('auth/exito.html')

@app.route('/historial')
@login_required
def historial():
    return render_template('auth/historial.html')

@app.route('/cerrar-sesion-confirmacion')
@login_required
def cerrar_sesion_vista():
    return render_template('auth/cerrarsecion.html')

@app.route('/logout')
def logout(): 
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)