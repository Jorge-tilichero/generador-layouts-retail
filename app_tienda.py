import matplotlib.pyplot as plt
import matplotlib.patches as patches

def generar_layout(ancho_local, largo_local, pasillo_minimo=1.2):
    # Crear el lienzo del plano
    fig, ax = plt.subplots(figsize=(8, 10))
    ax.set_xlim(0, ancho_local)
    ax.set_ylim(0, largo_local)
    
    # 1. Cuarto Frío (Lado más alejado del acceso)
    profundidad_frio = 2.5 # metros
    ax.add_patch(patches.Rectangle((0, largo_local - profundidad_frio), ancho_local, profundidad_frio, 
                                   fill=True, color='lightblue', alpha=0.7))
    plt.text(ancho_local/2, largo_local - profundidad_frio/2, 'CUARTO FRÍO', ha='center', va='center', weight='bold')
    
    # 2. Acceso, Checkout y Grab&Go (Zona frontal)
    # Asumimos que el acceso está en el centro de la fachada
    ancho_acceso = 2.0
    plt.plot([ancho_local/2 - ancho_acceso/2, ancho_local/2 + ancho_acceso/2], [0, 0], 
             color='red', linewidth=6, label='Acceso Principal')
    
    # Checkout (A un lado del acceso)
    ancho_cobro = 3.0
    prof_cobro = 2.0
    ax.add_patch(patches.Rectangle((ancho_local - ancho_cobro, 0), ancho_cobro, prof_cobro, 
                                   fill=True, color='lightgreen', alpha=0.7))
    plt.text(ancho_local - ancho_cobro/2, prof_cobro/2, 'CHECKOUT', ha='center', va='center')
    
    # Café & Grab&Go (Frente al acceso, lado opuesto al checkout)
    ancho_cafe = 3.0
    prof_cafe = 2.0
    ax.add_patch(patches.Rectangle((0, 0), ancho_cafe, prof_cafe, 
                                   fill=True, color='orange', alpha=0.7))
    plt.text(ancho_cafe/2, prof_cafe/2, 'CAFÉ / GRAB&GO', ha='center', va='center')
    
    # 3. Góndolas en el centro (Orientadas para visibilidad de pasillos)
    # Calculamos el espacio libre central
    y_inicio_gondolas = max(prof_cobro, prof_cafe) + pasillo_minimo
    y_fin_gondolas = largo_local - profundidad_frio - pasillo_minimo
    largo_gondola = y_fin_gondolas - y_inicio_gondolas
    
    ancho_gondola = 1.0 # Asumimos que cada góndola mide 1 metro de ancho
    x_actual = pasillo_minimo # Empezamos dejando un pasillo contra la pared izquierda
    
    # Bucle de IA: Mientras quepa otra góndola respetando el pasillo, colócala
    while x_actual + ancho_gondola <= ancho_local - pasillo_minimo:
        ax.add_patch(patches.Rectangle((x_actual, y_inicio_gondolas), ancho_gondola, largo_gondola, 
                                       fill=True, color='gray', alpha=0.5))
        plt.text(x_actual + ancho_gondola/2, y_inicio_gondolas + largo_gondola/2, 'Góndola', 
                 ha='center', va='center', rotation=90)
        
        # Saltamos a la siguiente posición sumando el ancho de la góndola + pasillo de 1.20m
        x_actual += ancho_gondola + pasillo_minimo 
        
    # Configuraciones visuales del plano
    plt.title(f'Generador de Layout - Local: {ancho_local}m x {largo_local}m')
    ax.set_aspect('equal') # Para que 1 metro de ancho se vea igual a 1 metro de largo
    plt.grid(True, linestyle='--', alpha=0.4)
    plt.legend()
    plt.show()

# --- PRUEBA DEL CÓDIGO ---
# Aquí le decimos a la herramienta que genere una tienda de 10x15 metros 
# y que respete pasillos de 1.20 metros.
generar_layout(10, 15, 1.20)