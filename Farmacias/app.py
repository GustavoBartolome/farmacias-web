import smtplib
from email.message import EmailMessage
import sqlite3
from flask import Flask, render_template, request, flash, redirect, url_for

app = Flask(__name__)
app.secret_key = 'clave_secreta_segura'

# Configuración del correo
EMAIL_ORIGEN = 'gustavovelix@gmail.com'
CONTRASENA_APP = 'wyng pweq pwxo ddyl'

def crear_tabla():
    conn = sqlite3.connect('usuarios.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            correo TEXT NOT NULL UNIQUE,
            contrasena TEXT NOT NULL,
            dni TEXT,
            naf TEXT
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['username']
        contrasena = request.form['password']

        conn = sqlite3.connect('usuarios.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE nombre = ? AND contrasena = ?", (usuario, contrasena))
        usuario_encontrado = cursor.fetchone()
        conn.close()

        if usuario_encontrado:
            flash('✅ Iniciado correctamente.', 'success')
            return redirect(url_for('home'))
        else:
            flash('❌ Usuario o contraseña incorrectos.', 'error')
            return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nombre = request.form['nombre']
        correo = request.form['email']
        contrasena = request.form.get('contrasena')
        dni = request.form.get('dni')
        naf = request.form.get('naf')

        try:
            conn = sqlite3.connect('usuarios.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO usuarios (nombre, correo, contrasena,dni,naf) VALUES (?, ?, ?, ?, ?)",
                           (nombre, correo, contrasena, dni, naf))
            conn.commit()
            conn.close()

            # Enviar correo de bienvenida
            msg = EmailMessage()
            msg.set_content(f"""
Hola {nombre},

Gracias por registrarte en Farmacias Online. ¡Nos alegra tenerte con nosotros!

Saludos,
El equipo de Farmacias Online
""", charset='utf-8')
            msg['Subject'] = "¡Bienvenido a Farmacias Online!"
            msg['From'] = EMAIL_ORIGEN
            msg['To'] = correo

            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as servidor:
                servidor.login(EMAIL_ORIGEN, CONTRASENA_APP)
                servidor.send_message(msg)

            flash('✅ Usuario registrado y correo de bienvenida enviado.')
            return redirect(url_for('login'))

        except sqlite3.IntegrityError:
            flash('❌ El correo ya está registrado.')
            return redirect(url_for('register'))
        except Exception as e:
            flash(f'⚠️ Usuario registrado, pero error al enviar correo: {str(e)}')
            return redirect(url_for('login'))
        print(request.form)

    return render_template('register.html')

@app.route('/products')
def products():
    return render_template('products.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/cart')
def cart():
    return render_template('cart.html')

@app.route('/forgot-password')
def forgot_password():
    return render_template('forgot_password.html')
#revisar este punto porque creo que no hace nada...
@app.route('/send-reset-email', methods=['POST'])
def send_reset_email():
    email_destino = request.form.get('email')

    msg = EmailMessage()
    msg.set_content(
        "Haz clic en este enlace para restablecer tu contraseña: http://localhost:5000/reset",
        charset='utf-8'
    )
    msg['Subject'] = "Recuperación de contraseña"
    msg['From'] = EMAIL_ORIGEN
    msg['To'] = email_destino

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as servidor:
            servidor.login(EMAIL_ORIGEN, CONTRASENA_APP)
            servidor.send_message(msg)
        flash(f'Se ha enviado una contraseña nueva a {email_destino}.')
    except Exception as e:
        flash(f'Error al enviar el correo: {str(e)}')

    return redirect(url_for('forgot_password'))

@app.route('/usuarios')
def ver_usuarios():
    conn = sqlite3.connect('usuarios.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios")
    usuarios = cursor.fetchall()
    conn.close()
    return render_template('usuarios.html', usuarios=usuarios)

@app.route('/send-contact', methods=['POST'])
def send_contact():
    nombre = request.form.get('nombre')
    apellido = request.form.get('apellido')
    dni = request.form.get('DNI')
    nss = request.form.get('NAF')
    mensaje_usuario = request.form.get('mensaje')

    # Crear el contenido del correo
    contenido = f"""
    Nuevo mensaje de contacto recibido:

    Nombre: {nombre}
    Apellido: {apellido}
    DNI: {dni}
    Nº Seguridad Social: {nss}
    Mensaje:
    {mensaje_usuario}
    """

    msg = EmailMessage()
    msg.set_content(contenido, charset='utf-8')
    msg['Subject'] = "Nuevo mensaje desde el formulario de contacto"
    msg['From'] = EMAIL_ORIGEN
    msg['To'] = EMAIL_ORIGEN  # Puedes cambiar esto si quieres que llegue a otro correo

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as servidor:
            servidor.login(EMAIL_ORIGEN, CONTRASENA_APP)
            servidor.send_message(msg)
        flash('✅ Tu mensaje ha sido enviado correctamente.')
    except Exception as e:
        flash(f'⚠️ Error al enviar el mensaje: {str(e)}')

    return redirect(url_for('contact'))


if __name__ == '__main__':
    crear_tabla()
    app.run(debug=True)
