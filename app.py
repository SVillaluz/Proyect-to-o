from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from password_validator import PasswordValidator
from dotenv import load_dotenv
from datetime import timedelta
import mysql.connector
import hashlib
import os
import re

# Cargar variables de entorno
load_dotenv()

# Inicializar Flask
app = Flask(__name__)
app.secret_key = os.getenv("secret_key") or "clave_secreta_default"

# Expiración automática de sesión 
app.permanent_session_lifetime = timedelta(minutes=30)

validador_contrasena = PasswordValidator()
validador_contrasena \
    .min(8) \
    .max(14) \
    .has().uppercase() \
    .has().lowercase() \
    .has().symbols() \
    .no().spaces()

# Conexión a la base de datos
def conectar_db():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Meliodas1.",
            database="subastas",
            charset='utf8mb4',
        )
        print("✅ Conexión exitosa a la base de datos.")
        return conn
    except mysql.connector.Error as err:
        print(f"❌ Error al conectar a la base de datos: {err}")
        return None

conectar_db()

from functools import wraps

# Página principal
@app.route('/')
def index():
    nombre = session.get('nombre_usuario') if 'id_usuario' in session else None
    rol = session.get('rol') if 'id_usuario' in session else None
    return render_template('index.html', nombre=nombre, rol=rol)

# Página de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Intentar obtener JSON
        data = request.get_json(silent=True)
        if not data:
            # Si no hay JSON, intentar obtener datos de formulario
            correo = request.form.get('correo', '').strip()
            contrasena = request.form.get('contrasena', '').strip()
        else:
            correo = data.get('correo', '').strip()
            contrasena = data.get('contrasena', '').strip()

        if not correo or not contrasena:
            if request.is_json:
                return jsonify({"error": "Por favor, completa todos los campos."}), 400
            else:
                return render_template('login.html', error="Por favor, completa todos los campos.")

        hashed_password = hashlib.sha256(contrasena.encode()).hexdigest()

        conn = conectar_db()
        if not conn:
            if request.is_json:
                return jsonify({"error": "No se pudo conectar a la base de datos."}), 500
            else:
                return render_template('login.html', error="No se pudo conectar a la base de datos.")

        cursor = conn.cursor()
        cursor.execute("""
            SELECT id_usuario, nombre_usuario, rol
            FROM usuarios
            WHERE correo = %s AND password_hash = %s AND estatus = 'activo'
        """, (correo, hashed_password))
        usuario = cursor.fetchone()
        cursor.close()
        conn.close()

        if usuario:
            session.permanent = True
            session['id_usuario'] = usuario[0]
            session['nombre_usuario'] = usuario[1]
            session['rol'] = usuario[2]
            if request.is_json:
                return jsonify({"message": "Inicio de sesión exitoso", "success": True, "nombre_usuario": usuario[1], "rol": usuario[2]}), 200
            else:
                return redirect(url_for('index'))
        else:
            if request.is_json:
                return jsonify({"error": "Correo o contraseña incorrectos."}), 401
            else:
                return render_template('login.html', error="Correo o contraseña incorrectos.")

    return render_template('login.html')

# Página de logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/reg', methods=['GET', 'POST'])
def reg():
    if request.method == 'POST':
        nombre = request.form.get('name', '').strip()
        apellido1 = request.form.get('apellido1', '').strip()
        apellido2 = request.form.get('apellido2', '').strip()
        fecha_nacimiento = request.form.get('fecha_nacimiento', '').strip()
        domicilio = request.form.get('domicilio', '').strip()
        telefono = request.form.get('telefono', '').strip()
        email = request.form.get('email', '').strip()
        rfc = request.form.get('rfc', '').strip()
        password = request.form.get('password', '').strip()

        # Validación básica
        if not all([nombre, apellido1, apellido2, fecha_nacimiento, domicilio, telefono, email, rfc, password]):
            return render_template('newu.html', error="Por favor, completa todos los campos.")

        # Validar contraseña
        if not validador_contrasena.validate(password):
            return render_template('newu.html', error="La contraseña no cumple con los requisitos de seguridad.")

        # Hash de la contraseña
        password_hash = hashlib.sha256(password.encode()).digest()

        conn = conectar_db()
        if not conn:
            return render_template('newu.html', error="No se pudo conectar a la base de datos.")
        try:
            cursor = conn.cursor()
            cursor.callproc('sp_insertar_usuario', [
                nombre, apellido1, apellido2, fecha_nacimiento, domicilio, telefono, email, rfc, password_hash
            ])
            conn.commit()
            cursor.close()
            conn.close()
            return render_template('newu.html', success="Usuario registrado exitosamente.")
        except Exception as e:
            if conn:
                conn.rollback()
                conn.close()
            return render_template('newu.html', error=f"Error al registrar usuario: {str(e)}")
    # Si es GET
    return render_template('newu.html')

@app.route('/regobj', methods=['GET', 'POST'])
def regobj():
    if request.method == 'POST':
        tipo_articulo = request.form.get('articulo', '').strip()
        descripcion = request.form.get('descripcion', '').strip()
        precio = request.form.get('precio', '').strip()
        estado = request.form.get('estado', '').strip()

        # Validación básica
        if not all([tipo_articulo, descripcion, precio, estado]):
            return render_template('newob.html', error="Por favor, completa todos los campos.")

        try:
            precio_val = float(precio)
        except ValueError:
            return render_template('newob.html', error="El precio debe ser un número válido.")

        conn = conectar_db()
        if not conn:
            return render_template('newob.html', error="No se pudo conectar a la base de datos.")
        try:
            cursor = conn.cursor()
            cursor.callproc('sp_insertar_inventario', [
                tipo_articulo, descripcion, precio_val, estado
            ])
            conn.commit()
            cursor.close()
            conn.close()
            return render_template('newob.html', success="Artículo registrado exitosamente.")
        except Exception as e:
            if conn:
                conn.rollback()
                conn.close()
            return render_template('newob.html', error=f"Error al registrar artículo: {str(e)}")
    # Si es GET
    return render_template('newob.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    return render_template('search.html')

@app.route('/pay', methods=['GET', 'POST'])
def pay():
    return render_template('pay.html')

if __name__ == '__main__':
    app.run(debug=True)