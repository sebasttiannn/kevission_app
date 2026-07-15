from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify
from ..models import Prenda
from ..services.ai_prompt import construir_prompt, simular_respuesta_ia
from ..services.clima_service import obtener_clima

outfit_bp = Blueprint('outfit', __name__, url_prefix='/recomendacion')

@outfit_bp.route('/', methods=['GET', 'POST'])
def index():
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
        
    recomendaciones = None
    prompt_debug = None
    
    if request.method == 'POST':
        ocasion = request.form.get('ocasion')

        ciudad_actual = session.get('ciudad_clima', 'Temuco')
        clima = obtener_clima(ciudad_actual)
        temperatura_actual = clima['temperatura']

        prendas_bd = Prenda.query.filter_by(usuario_id=session['usuario_id']).all()
        
        if not prendas_bd:
            prompt_debug = {"error": "Tu armario está vacío."}
        else:
            # Construimos el texto del prompt con los nuevos estilos múltiples para el Backstage
            lista_prendas = [f"{p.categoria} ({p.color}, Marca: {p.marca}, Estilos: {p.estilo}) - URL: {p.imagen_ruta}" for p in prendas_bd]
            prendas_texto = " | ".join(lista_prendas)
            
            sys_prompt, usr_prompt = construir_prompt(ocasion, temperatura_actual, prendas_texto)
            prompt_debug = {"system": sys_prompt, "user": usr_prompt}
            
            # Llamamos a la simulación pasándole la ocasión, la ropa, y el clima real de la ciudad elegida
            recomendaciones = simular_respuesta_ia(ocasion, prendas_bd, temperatura_actual)
            
            # Si la IA devuelve un diccionario con un error por falta de prendas específicas
            if isinstance(recomendaciones, dict) and "error_ia" in recomendaciones:
                prompt_debug["error_ia"] = recomendaciones["error_ia"]
                recomendaciones = None
                
    return render_template('outfit/index.html', recomendaciones=recomendaciones, prompt_debug=prompt_debug)

# --- RUTA OCULTA PARA GUARDAR EL HISTORIAL ---
@outfit_bp.route('/guardar_eleccion', methods=['POST'])
def guardar_eleccion():
    if 'usuario_id' not in session:
        return jsonify({"error": "No authorized"}), 401

    datos = request.get_json()
    estilo = datos.get('estilo')
    imagenes_lista = datos.get('imagenes', [])
    
    # Convertimos la lista de imágenes en un texto separado por comas
    imagenes_str = ",".join(imagenes_lista)

    # Importamos el modelo aquí para evitar errores circulares
    from ..models import HistorialOutfit
    from .. import db

    nuevo_historial = HistorialOutfit(
        usuario_id=session['usuario_id'],
        estilo=estilo,
        imagenes=imagenes_str
    )
    
    db.session.add(nuevo_historial)
    db.session.commit()

    return jsonify({"mensaje": "Guardado correctamente", "status": "success"})

# --- NUEVA RUTA: PARA VER LA PANTALLA DEL HISTORIAL ---
@outfit_bp.route('/historial')
def historial():
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
    
    from ..models import HistorialOutfit
    # Buscamos los outfits del usuario ordenados desde el más nuevo al más viejo
    historial_bd = HistorialOutfit.query.filter_by(usuario_id=session['usuario_id']).order_by(HistorialOutfit.fecha.desc()).all()
    
    historial_procesado = []
    for h in historial_bd:
        historial_procesado.append({
            "id": h.id,
            "fecha": h.fecha.strftime('%d/%m/%Y %H:%M'),
            "estilo": h.estilo,
            "imagenes": h.imagenes.split(',') if h.imagenes else []
        })
        
    return render_template('outfit/history.html', historial=historial_procesado)