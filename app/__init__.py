from flask import Flask, render_template, session, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    # 1. Registrar Módulo de Autenticación
    from .routes.auth import auth_bp
    app.register_blueprint(auth_bp)

    # 2. Registrar Módulo del Armario (Lo crearemos en el siguiente paso)
    from .routes.wardrobe import wardrobe_bp
    app.register_blueprint(wardrobe_bp)

    # 3. Registrar Módulo del Clima
    from .routes.weather import weather_bp
    app.register_blueprint(weather_bp)

    # 4. Registrar Módulo de Recomendación
    from .routes.outfit import outfit_bp
    app.register_blueprint(outfit_bp)

    from . import models
    with app.app_context():
        db.create_all()

    # --- HELPER: resolver URL de imagen (local vs Azure Blob) ---
    @app.template_global()
    def imagen_url(ruta):
        if ruta and (ruta.startswith('http://') or ruta.startswith('https://')):
            return ruta
        return url_for('static', filename=ruta)

    # --- HEALTH CHECK (usado por el Target Group del Load Balancer) ---
    @app.route('/health')
    def health():
        return {'status': 'ok'}, 200

    # --- LA RUTA PRINCIPAL (DASHBOARD) ---
    @app.route('/')
    def dashboard():
        # Si no hay sesión, lo mandamos al login
        if 'usuario_id' not in session:
            return redirect(url_for('auth.login'))

        from .models import Prenda, HistorialOutfit
        import os
        import requests

        prenda_count = Prenda.query.filter_by(usuario_id=session['usuario_id']).count()

        historial_bd = (
            HistorialOutfit.query
            .filter_by(usuario_id=session['usuario_id'])
            .order_by(HistorialOutfit.fecha.desc())
            .limit(3)
            .all()
        )
        ultimos_outfits = []
        for h in historial_bd:
            imgs = h.imagenes.split(',') if h.imagenes else []
            ultimos_outfits.append({
                "estilo": h.estilo,
                "fecha": h.fecha.strftime('%d/%m/%Y %H:%M'),
                "cantidad_prendas": len(imgs),
            })

        # --- Clima real, usando ubicación del navegador si está disponible ---
        lat = request.args.get('lat')
        lon = request.args.get('lon')

        clima = {"temperatura": 12, "ciudad": "Temuco"}
        api_key = os.getenv('OPENWEATHER_KEY')
        if api_key and api_key != 'tu_clave_api_aqui':
            try:
                if lat and lon:
                    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric&lang=es"
                else:
                    url = f"http://api.openweathermap.org/data/2.5/weather?q=Temuco&appid={api_key}&units=metric&lang=es"
                resp = requests.get(url, timeout=5)
                if resp.status_code == 200:
                    datos = resp.json()
                    clima = {
                        "temperatura": round(datos['main']['temp']),
                        "ciudad": datos['name'],
                    }
            except Exception:
                pass

        return render_template(
            'dashboard.html',
            nombre=session.get('usuario_nombre'),
            prenda_count=prenda_count,
            ultimos_outfits=ultimos_outfits,
            clima=clima,
            tiene_ubicacion=bool(lat and lon),
        )
    return app