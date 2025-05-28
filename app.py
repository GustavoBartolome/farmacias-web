from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
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


from flask import request, flash, redirect, url_for

app.secret_key = 'clave_secreta_segura'
# Necesario para usar flash

@app.route('/send-reset-email', methods=['POST'])
def send_reset_email():
    email = request.form.get('email')
# Aquí podrías enviar el correo real si lo deseas
    flash(f'Se ha enviado un enlace de recuperación a {email}.')
    return redirect(url_for('forgot_password'))

if __name__ == '__main__':
    app.run(debug=True)
