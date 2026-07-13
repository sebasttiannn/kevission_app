from . import db
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    # Relación para conectar a un usuario con sus prendas
    prendas = db.relationship('Prenda', backref='propietario', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# --- TABLA PARA EL ARMARIO (Actualizada con Marca y Talla) ---
# --- TABLA PARA EL ARMARIO --- actualizado
class Prenda(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    imagen_ruta = db.Column(db.String(255), nullable=False)
    categoria = db.Column(db.String(50), nullable=True)
    color = db.Column(db.String(50), nullable=True)
    marca = db.Column(db.String(100), nullable=True)
    talla = db.Column(db.String(20), nullable=True)
    estilo = db.Column(db.String(50), nullable=True)  # <-- NUEVO: El estilo de la prenda

# --- NUEVA TABLA: Historial de Outfits ---
class HistorialOutfit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    estilo = db.Column(db.String(50), nullable=False)
    # Guardaremos las rutas de las imágenes como un texto largo separado por comas
    imagenes = db.Column(db.Text, nullable=False)