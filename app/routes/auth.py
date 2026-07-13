from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from ..models import Usuario
from .. import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        email = request.form.get('email')
        password = request.form.get('password')

        user_exists = Usuario.query.filter_by(email=email).first()
        if user_exists:
            flash('El correo ya está registrado.', 'danger')
            return redirect(url_for('auth.register'))

        nuevo_usuario = Usuario(nombre=nombre, email=email)
        nuevo_usuario.set_password(password)
        
        db.session.add(nuevo_usuario)
        db.session.commit()
        
        flash('Registro exitoso. Ya puedes iniciar sesión.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        usuario = Usuario.query.filter_by(email=email).first()
        if usuario and usuario.check_password(password):
            session['usuario_id'] = usuario.id
            session['usuario_nombre'] = usuario.nombre
            return redirect(url_for('dashboard')) # Cambiaremos esto al home luego
        else:
            flash('Error en las credenciales. Inténtalo de nuevo.', 'danger')

    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))