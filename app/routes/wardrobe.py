from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import os
import uuid
from werkzeug.utils import secure_filename
from ..models import Prenda
from .. import db

wardrobe_bp = Blueprint('wardrobe', __name__, url_prefix='/armario')

UPLOAD_FOLDER = 'app/static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def subir_a_azure_blob(file, filename):
    """
    Sube el archivo a Azure Blob Storage y devuelve la URL publica del blob.
    Requiere las variables de entorno AZURE_STORAGE_CONNECTION_STRING y
    AZURE_STORAGE_CONTAINER definidas (ver .env.example).
    """
    from azure.storage.blob import BlobServiceClient, ContentSettings

    connection_string = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
    container_name = os.getenv('AZURE_STORAGE_CONTAINER', 'kevission-prendas')

    if not connection_string:
        raise RuntimeError(
            'STORAGE_TYPE=azure pero falta AZURE_STORAGE_CONNECTION_STRING en el entorno.'
        )

    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(container_name)

    try:
        container_client.create_container()
    except Exception:
        pass  # ya existe

    blob_name = f"{uuid.uuid4().hex}_{filename}"
    content_type = file.mimetype or 'application/octet-stream'

    blob_client = container_client.get_blob_client(blob_name)
    file.stream.seek(0)
    blob_client.upload_blob(
        file.stream,
        overwrite=True,
        content_settings=ContentSettings(content_type=content_type)
    )

    return blob_client.url

@wardrobe_bp.route('/')
def index():
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
    
    prendas_bd = Prenda.query.filter_by(usuario_id=session['usuario_id']).all()
    
    prendas_agrupadas = {}
    for prenda in prendas_bd:
        cat = prenda.categoria
        if cat not in prendas_agrupadas:
            prendas_agrupadas[cat] = []
        prendas_agrupadas[cat].append(prenda)
        
    return render_template('wardrobe/index.html', prendas_agrupadas=prendas_agrupadas, total_prendas=len(prendas_bd))

@wardrobe_bp.route('/subir', methods=['POST'])
def upload():
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))

    if 'imagen' not in request.files:
        flash('No seleccionaste ninguna imagen.', 'danger')
        return redirect(url_for('wardrobe.index'))
    
    file = request.files['imagen']
    categoria = request.form.get('categoria')
    color = request.form.get('color')
    marca = request.form.get('marca')
    talla = request.form.get('talla')
    
    estilos_seleccionados = request.form.getlist('estilo')
    estilo = ",".join(estilos_seleccionados) if estilos_seleccionados else "casual"

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        tipo_storage = os.getenv('STORAGE_TYPE')
        
        if tipo_storage == 'azure':
            try:
                ruta_bd = subir_a_azure_blob(file, filename)
            except Exception as e:
                flash(f'Error al subir a Azure Blob Storage: {e}', 'danger')
                return redirect(url_for('wardrobe.index'))
        else:
            ruta_guardado = os.path.join(UPLOAD_FOLDER, filename)
            file.save(ruta_guardado)
            ruta_bd = f'uploads/{filename}'

        nueva_prenda = Prenda(
            usuario_id=session['usuario_id'],
            imagen_ruta=ruta_bd,
            categoria=categoria,
            color=color,
            marca=marca,
            talla=talla,
            estilo=estilo 
        )
        db.session.add(nueva_prenda)
        db.session.commit()
        
        flash('Prenda subida exitosamente.', 'success')
    else:
        flash('Formato de archivo no permitido. Usa JPG o PNG.', 'danger')

    return redirect(url_for('wardrobe.index'))

# --- NUEVA RUTA: ELIMINAR PRENDA ---
@wardrobe_bp.route('/eliminar/<int:prenda_id>', methods=['POST'])
def eliminar(prenda_id):
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
        
    prenda = Prenda.query.get_or_404(prenda_id)
    
    # Por seguridad, verificamos que la prenda sea del usuario activo
    if prenda.usuario_id == session['usuario_id']:
        db.session.delete(prenda)
        db.session.commit()
        flash('Prenda eliminada de tu armario.', 'success')
    else:
        flash('No tienes permiso para eliminar esto.', 'danger')
        
    return redirect(url_for('wardrobe.index'))

# --- NUEVA RUTA: EDITAR PRENDA ---
@wardrobe_bp.route('/editar/<int:prenda_id>', methods=['POST'])
def editar(prenda_id):
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
        
    prenda = Prenda.query.get_or_404(prenda_id)
    
    if prenda.usuario_id == session['usuario_id']:
        prenda.categoria = request.form.get('categoria')
        prenda.color = request.form.get('color')
        prenda.marca = request.form.get('marca')
        prenda.talla = request.form.get('talla')
        
        estilos_seleccionados = request.form.getlist('estilo')
        prenda.estilo = ",".join(estilos_seleccionados) if estilos_seleccionados else "casual"
        
        db.session.commit()
        flash('Datos de la prenda actualizados.', 'success')
        
    return redirect(url_for('wardrobe.index'))