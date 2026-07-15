import os
import requests


def obtener_clima(ciudad):
    """
    Consulta el clima real en OpenWeather para la ciudad dada.
    Si no hay API key configurada o falla la consulta, devuelve un valor
    por defecto (12 grados) para que la app no se rompa, marcando error=True.
    """
    clima = {"temperatura": 12, "ciudad": ciudad, "error": False}

    api_key = os.getenv('OPENWEATHER_KEY')
    if not api_key or api_key == 'tu_clave_api_aqui':
        clima["error"] = True
        return clima

    try:
        url = (
            "http://api.openweathermap.org/data/2.5/weather"
            f"?q={ciudad}&appid={api_key}&units=metric&lang=es"
        )
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            datos = resp.json()
            clima = {
                "temperatura": round(datos['main']['temp']),
                "ciudad": datos['name'],
                "error": False,
            }
        else:
            clima["error"] = True
    except Exception:
        clima["error"] = True

    return clima