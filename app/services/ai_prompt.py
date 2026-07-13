import random

def construir_prompt(ocasion, temperatura, prendas):
    system_prompt = """Eres KeVission, un Personal Shopper y experto en moda multimodal. 
    Tu objetivo es analizar visualmente las prendas del usuario.
    Se te pedirá una ocasión específica. DEBES generar 3 opciones distintas EXCLUSIVAMENTE para esa ocasión, seleccionando las imágenes exactas de su armario respetando el estilo."""
    
    user_prompt = f"""
    Contexto actual:
    - Ocasión: {ocasion.upper()}
    - Clima: {temperatura}°C
    - Prendas: {prendas}
    
    Instrucciones: Selecciona las prendas. Devuelve las opciones incluyendo las URLs de las imágenes para mostrarlas en pantalla.
    """
    return system_prompt, user_prompt

def simular_respuesta_ia(ocasion, prendas_bd):
    # 1. FILTRO MULTI-ESTILO: 
    prendas_filtradas = [p for p in prendas_bd if p.estilo and ocasion in p.estilo.split(',')]

    if not prendas_filtradas:
        return {"error_ia": f"No tienes ropa asociada al estilo '{ocasion.capitalize()}'. ¡Ve al armario, sube prendas y marca la casilla de este estilo!"}

    # 2. Clasificamos TODAS las categorías (¡Ahora sí incluimos las chaquetas!)
    tops = [p for p in prendas_filtradas if p.categoria in ['poleras', 'camisas']]
    pantalones = [p for p in prendas_filtradas if p.categoria == 'pantalones']
    zapatillas = [p for p in prendas_filtradas if p.categoria == 'zapatillas']
    accesorios = [p for p in prendas_filtradas if p.categoria == 'accesorios']
    chaquetas = [p for p in prendas_filtradas if p.categoria == 'chaquetas'] # <-- NUEVO: Agregamos la categoría

    # 3. Validar mínimos indispensables
    if not tops:
        return {"error_ia": f"Tienes prendas marcadas como '{ocasion}', pero te falta agregar una polera o camisa con este estilo para armar el outfit."}
    if not pantalones:
        return {"error_ia": f"Tienes prendas marcadas como '{ocasion}', pero te falta agregar un pantalón con este estilo."}

    # 4. Generar las 3 opciones usando EXCLUSIVAMENTE la ropa filtrada
    opciones = []
    nombres_estilos = {
        'formal': ['Formal Clásico', 'Ejecutivo', 'Smart Casual'],
        'casual': ['Día a Día', 'Urbano Relajado', 'Minimalista'],
        'deporte': ['Modo Gym', 'Running', 'Sportswear'],
        'fiesta': ['Fiesta Urbana', 'Nocturno', 'Drip']
    }
    
    estilos = nombres_estilos.get(ocasion, nombres_estilos['casual'])

    for i in range(3):
        # Elegimos obligatoriamente parte de arriba y de abajo
        top_elegido = random.choice(tops)
        bot_elegido = random.choice(pantalones)
        
        # Opcionales: Solo elegimos si existen para ese estilo
        zap_elegido = random.choice(zapatillas) if zapatillas else None
        acc_elegido = random.choice(accesorios) if accesorios else None
        chaq_elegida = random.choice(chaquetas) if chaquetas else None # <-- NUEVO: Elegimos chaqueta

        # Juntamos las fotos
        imagenes_outfit = [top_elegido.imagen_ruta, bot_elegido.imagen_ruta]
        
        # Agregamos la chaqueta al outfit visual si es que salió sorteada
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
            "motivo": f"Estas piezas fueron seleccionadas porque tienen marcada la casilla '{ocasion}'.",
            "icono": "bi-check-circle-fill",
            "imagenes": imagenes_outfit 
        })

    return opciones