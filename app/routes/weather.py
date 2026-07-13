from flask import Blueprint, render_template, request
import requests
import os

weather_bp = Blueprint('weather', __name__, url_prefix='/clima')

@weather_bp.route('/', methods=['GET', 'POST'])
def index():
    # Ciudad por defecto para arrancar la vista
    ciudad = 'Temuco'
    clima_data = None
    error = None

    if request.method == 'POST':
        ciudad = request.form.get('ciudad')

    api_key = os.getenv('OPENWEATHER_KEY')

    # Lógica para consultar la API
    if api_key and api_key != 'tu_clave_api_aqui':
        url = f"http://api.openweathermap.org/data/2.5/weather?q={ciudad}&appid={api_key}&units=metric&lang=es"
        try:
            respuesta = requests.get(url)
            if respuesta.status_code == 200:
                datos = respuesta.json()
                clima_data = {
                    'ciudad': datos['name'],
                    'temperatura': round(datos['main']['temp']),
                    'descripcion': datos['weather'][0]['description'].capitalize(),
                    'icono': datos['weather'][0]['icon']
                }
            else:
                error = "No se pudo encontrar la ciudad. Intenta con otra."
        except Exception as e:
            error = "Error al conectar con el servidor del clima."
    else:
        # Modo de prueba (Mock) si no hay API Key configurada
        clima_data = {
            'ciudad': ciudad,
            'temperatura': 12,
            'descripcion': 'Nublado (Datos simulados)',
            'icono': '04d'
        }
        error = "Aviso: Mostrando datos de prueba porque falta la OPENWEATHER_KEY en el archivo .env"

    return render_template('weather/index.html', clima=clima_data, error=error)