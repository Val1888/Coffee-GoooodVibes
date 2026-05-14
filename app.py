from dotenv import load_dotenv
load_dotenv()
from server.db import guardar_pedido, obtener_historial
from server.db import obtener_usuario_por_id, validar_login, crear_usuario, obtener_productos
from server.db import obtener_producto_por_id, sumar_puntos_usuario
import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_bcrypt import Bcrypt
from server.db import obtener_usuario_por_id, validar_login, crear_usuario # Asegúrate de tener estas en db.py
from flask import jsonify
# Busca esta línea y asegúrate de que incluya sumar_puntos_usuario


app = Flask(__name__, template_folder='client/templates',static_folder='static')
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
    lista_productos = obtener_productos()
    return render_template('menu.html', productos=lista_productos)

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

@app.route('/signin', methods=['GET', 'POST'])
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
    usuario = obtener_usuario_por_id(user_id) # Usamos tu función de db.py
    
    # Lógica de Niveles (Diseño Digital de Experiencia)
    puntos = usuario['puntos'] if usuario and usuario['puntos'] else 0
    
    if puntos < 500:
        nivel = 1
        rango = "Entuciasta del café"
    elif puntos < 1500:
        nivel = 2
        rango = "Catador cafetero"
    elif puntos < 3000:
        nivel = 3
        rango = "Amante de la cafeina"
    else:
        nivel = 4
        rango = "Buho cafetero"

    return render_template('auth/cuenta.html', 
                           usuario=usuario, 
                           nivel=nivel, 
                           rango=rango)

@app.route('/pago', methods=['GET', 'POST']) # Asegúrate de permitir GET y POST
@login_required
def pago():
    items_sesion = session.get('carrito', [])
    subtotal = 0
    
    for item in items_sesion:
        # Usamos tu función para traer el precio base
        prod_info = obtener_producto_por_id(item['id'])
        
        if prod_info:
            precio_base = float(prod_info['precio'])
            extra = 0
            if item['tamano'] == 'med': extra = 15
            elif item['tamano'] == 'g': extra = 25
            
            precio_unitario = precio_base + extra
            subtotal += precio_unitario * int(item['cantidad'])

    # ¡Aquí está el truco! Pasamos el subtotal al template de pago
    return render_template('auth/pago.html', subtotal=subtotal)

@app.route('/compra-exitosa')
def compra_exitosa():
    items_sesion = session.get('carrito', [])
    user_id = session.get('user_id')
    total_final = 0
    detalles_lista = []

    # 1. Calculamos el total de la compra y armamos los detalles
    for item in items_sesion:
        prod_info = obtener_producto_por_id(item['id'])
        if prod_info:
            precio_base = float(prod_info['precio'])
            extra = 0
            if item['tamano'] == 'med': extra = 15
            elif item['tamano'] == 'g': extra = 25
            
            precio_total_item = (precio_base + extra) * int(item['cantidad'])
            total_final += precio_total_item
            
            detalles_lista.append(f"{item['cantidad']}x {prod_info['nombre']} ({item['tamano']})")

    # 2. Convertimos la lista a string para la DB
    detalles_string = ", ".join(detalles_lista)

    if items_sesion:
        # 3. Guardamos el pedido en el historial
        guardar_pedido(user_id, total_final, detalles_string)
        
        # 4. Calculamos y sumamos los puntos (1 punto por cada $10 pesos)
        puntos_ganados = int(total_final / 10)
        sumar_puntos_usuario(user_id, puntos_ganados)

    # 5. Vaciamos el carrito
    session.pop('carrito', None)
    return render_template('auth/compraExitosa.html')

@app.route('/historial')
def historial():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    mis_pedidos = obtener_historial(session['user_id'])
    
    return render_template('auth/historial.html', pedidos=mis_pedidos)

@app.route('/cerrar-sesion-confirmacion')
@login_required
def cerrar_sesion_vista():
    return render_template('auth/cerrarsecion.html')

@app.route('/logout')
def logout(): 
    session.clear()
    return redirect(url_for('home'))


@app.route('/carrito')
@login_required
def carrito():
    items_sesion = session.get('carrito', [])
    carrito_final = []
    subtotal = 0
    
    for item in items_sesion:
        # Usamos TU función obtener_producto_por_id
        prod_info = obtener_producto_por_id(item['id'])
        
        if prod_info:
            # Calculamos el precio con los extras
            precio_base = float(prod_info['precio'])
            extra = 0
            if item['tamano'] == 'med': extra = 15
            elif item['tamano'] == 'g': extra = 25
            
            precio_unitario = precio_base + extra
            total_item = precio_unitario * int(item['cantidad'])
            
            # Guardamos todo lo necesario para la tabla
            carrito_final.append({
                'nombre': prod_info['nombre'],
                'tamano': item['tamano'],
                'cantidad': item['cantidad'],
                'precio_unitario': precio_unitario,
                'total': total_item
            })
            subtotal += total_item

    # Le pasamos los datos a tu template
    return render_template('auth/carrito.html', items=carrito_final, subtotal=subtotal)
@app.route('/agregar-al-carrito', methods=['POST'])
@login_required
def agregar_al_carrito_route():
    data = request.get_json()
    id_producto = data.get('id')
    cantidad = int(data.get('cantidad'))
    tamano = data.get('tamano')
    
    # Inicializamos el carrito en la sesión si no existe
    if 'carrito' not in session:
        session['carrito'] = []
    
    # Agregamos el producto (puedes mejorar esto luego para sumar cantidades si el ID ya existe)
    session['carrito'].append({
        'id': id_producto,
        'cantidad': cantidad,
        'tamano': tamano
    })
    
    session.modified = True # Importante para que Flask guarde los cambios en la sesión
    return jsonify({"status": "success", "message": "¡Café añadido!"})

@app.route('/eliminar-del-carrito/<int:indice>')
@login_required
def eliminar_del_carrito(indice):
    carrito = session.get('carrito', [])
    
    # Verificamos que el índice sea válido antes de borrar
    if 0 <= indice < len(carrito):
        carrito.pop(indice)
        session['carrito'] = carrito
        session.modified = True
        
    return redirect(url_for('carrito'))



if __name__ == '__main__':
    app.run(debug=True)

