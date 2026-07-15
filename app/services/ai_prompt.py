import random


def construir_prompt(ocasion, temperatura, prendas):
    system_prompt = """Eres KeVission, un Personal Shopper y experto en moda multimodal.
    Tu objetivo es analizar visualmente las prendas del usuario.
    Se te pedirá una ocasión específica y la temperatura actual. DEBES generar 3 opciones
    distintas EXCLUSIVAMENTE para esa ocasión, seleccionando las imágenes exactas de su
    armario, respetando el estilo, y ajustando el abrigo (chaquetas, capas) según el clima."""

    user_prompt = f"""
    Contexto actual:
    - Ocasión: {ocasion.upper()}
    - Clima: {temperatura}°C
    - Prendas: {prendas}

    Instrucciones: Selecciona las prendas considerando el clima (si hace frío, prioriza
    chaquetas/capas; si hace calor, evita sobrecargar el outfit). Devuelve las opciones
    incluyendo las URLs de las imágenes para mostrarlas en pantalla.
    """
    return system_prompt, user_prompt


def _nivel_abrigo(temperatura):
    """Clasifica la temperatura en niveles simples que determinan cuánto abrigo necesita el outfit."""
    if temperatura <= 10:
        return "frio"
    elif temperatura <= 18:
        return "templado"
    else:
        return "calor"


def simular_respuesta_ia(ocasion, prendas_bd, temperatura=18):
    # 1. FILTRO MULTI-ESTILO:
    prendas_filtradas = [p for p in prendas_bd if p.estilo and ocasion in p.estilo.split(',')]

    if not prendas_filtradas:
        return {"error_ia": f"No tienes ropa asociada al estilo '{ocasion.capitalize()}'. ¡Ve al armario, sube prendas y marca la casilla de este estilo!"}

    # 2. Clasificamos TODAS las categorías
    tops = [p for p in prendas_filtradas if p.categoria in ['poleras', 'camisas']]
    pantalones = [p for p in prendas_filtradas if p.categoria == 'pantalones']
    zapatillas = [p for p in prendas_filtradas if p.categoria == 'zapatillas']
    accesorios = [p for p in prendas_filtradas if p.categoria == 'accesorios']
    chaquetas = [p for p in prendas_filtradas if p.categoria == 'chaquetas']

    # 3. Validar mínimos indispensables
    if not tops:
        return {"error_ia": f"Tienes prendas marcadas como '{ocasion}', pero te falta agregar una polera o camisa con este estilo para armar el outfit."}
    if not pantalones:
        return {"error_ia": f"Tienes prendas marcadas como '{ocasion}', pero te falta agregar un pantalón con este estilo."}

    nivel = _nivel_abrigo(temperatura)

    # Si hace frío y el usuario tiene chaquetas para esta ocasión, el abrigo pasa a ser
    # obligatorio en vez de un extra al azar. Si hace calor, no se agrega chaqueta.
    chaqueta_obligatoria = (nivel == "frio" and len(chaquetas) > 0)
    permitir_chaqueta = nivel in ("frio", "templado")

    if chaqueta_obligatoria and not chaquetas:
        return {"error_ia": f"Hace frío ({temperatura}°C) y no tienes chaquetas marcadas con el estilo '{ocasion}'. ¡Agrega una en tu armario!"}

    # 4. Generar las 3 opciones usando EXCLUSIVAMENTE la ropa filtrada
    opciones = []
    nombres_estilos = {
        'formal': ['Formal Clásico', 'Ejecutivo', 'Smart Casual'],
        'casual': ['Día a Día', 'Urbano Relajado', 'Minimalista'],
        'deporte': ['Modo Gym', 'Running', 'Sportswear'],
        'fiesta': ['Fiesta Urbana', 'Nocturno', 'Drip']
    }

    estilos = nombres_estilos.get(ocasion, nombres_estilos['casual'])

    frases_clima = {
        "frio": f"hace frío ({temperatura}°C), así que priorizamos abrigo",
        "templado": f"el clima está templado ({temperatura}°C), así que sumamos una capa opcional",
        "calor": f"hace calor ({temperatura}°C), así que mantuvimos el outfit liviano",
    }

    for i in range(3):
        # Elegimos obligatoriamente parte de arriba y de abajo
        top_elegido = random.choice(tops)
        bot_elegido = random.choice(pantalones)

        # Opcionales: solo si existen para ese estilo
        zap_elegido = random.choice(zapatillas) if zapatillas else None
        acc_elegido = random.choice(accesorios) if accesorios else None

        # La chaqueta ahora depende del clima, no solo del azar:
        # - Frío + hay chaquetas -> siempre se agrega
        # - Templado + hay chaquetas -> se agrega con 50% de probabilidad (capa opcional)
        # - Calor -> nunca se agrega
        chaq_elegida = None
        if chaquetas and permitir_chaqueta:
            if nivel == "frio" or random.random() < 0.5:
                chaq_elegida = random.choice(chaquetas)

        # Juntamos las fotos
        imagenes_outfit = [top_elegido.imagen_ruta, bot_elegido.imagen_ruta]

        if chaq_elegida:
            imagenes_outfit.append(chaq_elegida.imagen_ruta)

        if zap_elegido:
            imagenes_outfit.append(zap_elegido.imagen_ruta)

        if acc_elegido:
            imagenes_outfit.append(acc_elegido.imagen_ruta)

        marca_texto = top_elegido.marca if top_elegido.marca else "tu prenda principal"

        opciones.append({
            "estilo": estilos[i],
            "descripcion": f"Look {ocasion} destacando {marca_texto}.",
            "motivo": f"Elegimos estas piezas porque tienen marcada la casilla '{ocasion}' y {frases_clima[nivel]}.",
            "icono": "bi-check-circle-fill",
            "imagenes": imagenes_outfit
        })

    return opciones