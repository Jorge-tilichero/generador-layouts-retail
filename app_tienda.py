import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# --- CONSTANTES EXACTAS ---
MOD_2FT = 0.61        
MOD_3FT = 0.91        
PROF_CAFE = 0.75      
PROF_CHECK = 0.60     
PROF_CAJERO = 1.00    # Pasillo operativo del cajero
PROF_CONTRA = 0.45    # Contracaja
PROF_FRIO = 2.00      
GONDOLA_PROF = 0.90   
CABECERA_PROF = 0.45  
PUERTA_ANCHO = 1.80   
PASILLO_STD = 1.20    
ISLA_DIM = 0.60       

def dibujar_layout_v8(conf):
    ancho = conf['ancho']
    largo = conf['largo']
    
    fig, ax = plt.subplots(figsize=(12, 14))
    ax.set_xlim(0, ancho)
    ax.set_ylim(0, largo)
    
    # ==========================================
    # 1. ANCLAJE PRINCIPAL: ACCESO Y PASILLO DE PODER
    # ==========================================
    x_puerta = conf['distancia_puerta']
    centro_tienda = ancho / 2
    
    # Pasillo de Poder (Paralelo a la profundidad, cruza la tienda)
    ax.add_patch(patches.Rectangle((x_puerta, 0), PUERTA_ANCHO, largo, color='#EBF5FB', alpha=0.8, label='Pasillo Poder'))
    plt.text(x_puerta + PUERTA_ANCHO/2, largo/2, 'PASILLO DE PODER', ha='center', va='center', rotation=90, color='#21618C', weight='bold')
    
    # Puerta Física
    plt.plot([x_puerta, x_puerta + PUERTA_ANCHO], [0, 0], color='red', linewidth=12)
    ax.add_patch(patches.Circle((x_puerta + PUERTA_ANCHO/2, 0), 2.0, color='#85C1E9', alpha=0.2)) # Descompresión

    # ==========================================
    # 2. INTELIGENCIA DE FLUJO: CHECKOUT, CAFÉ Y FRÍO
    # ==========================================
    # El sistema decide las posiciones basándose en el acceso
    ancho_check = conf['cant_checkout'] * MOD_2FT
    ancho_cafe = conf['cant_cafe'] * MOD_2FT
    ancho_frio = conf['cant_frio'] * MOD_2FT
    
    if x_puerta + (PUERTA_ANCHO/2) <= centro_tienda:
        # Puerta a la Izquierda -> Checkout a la Derecha, Café a la Izquierda, Frío al Fondo Derecha
        x_check_bloque = ancho - ancho_check
        x_cafe = 0
        x_frio = ancho - ancho_frio
    else:
        # Puerta a la Derecha -> Checkout a la Izquierda, Café a la Derecha, Frío al Fondo Izquierda
        x_check_bloque = 0
        x_cafe = ancho - ancho_cafe
        x_frio = 0

    # ==========================================
    # 3. BODEGA Y CUARTO FRÍO
    # ==========================================
    area_bodega = (ancho * largo) * 0.20
    prof_bodega = area_bodega / ancho
    y_bodega = largo - prof_bodega
    ax.add_patch(patches.Rectangle((0, y_bodega), ancho, prof_bodega, color='#D2B48C', ec='black'))
    plt.text(ancho/2, y_bodega + prof_bodega/2, 'BODEGA', ha='center', va='center', weight='bold')

    y_frio = y_bodega - PROF_FRIO
    # Bloque Cuarto Frío
    ax.add_patch(patches.Rectangle((x_frio, y_frio), ancho_frio, PROF_FRIO, color='#AED6F1', ec='black'))
    
    for i in range(conf['cant_frio']):
        ax.add_patch(patches.Rectangle((x_frio + (i * MOD_2FT), y_frio), MOD_2FT, 0.15, color='#2874A6', ec='white'))
        plt.text(x_frio + (i * MOD_2FT) + MOD_2FT/2, y_frio + 0.3, f'P{i+1}', ha='center', va='center', fontsize=5, rotation=90)
        
    # Pasillo Frío
    y_limite_frio = y_frio - PASILLO_STD
    ax.add_patch(patches.Rectangle((0, y_limite_frio), ancho, PASILLO_STD, color='#FCF3CF', alpha=0.7))
    plt.text(ancho/2, y_limite_frio + PASILLO_STD/2, 'PASILLO CUARTO FRÍO', ha='center', va='center', color='#9A7D0A', weight='bold')

    # ==========================================
    # 4. ÁREAS DE SERVICIO FRONTAL (Bloque Completo)
    # ==========================================
    
    # --- ÁREA DE CHECKOUT (Contracaja + Cajero + Módulos) ---
    # Contracaja (Y=0 a Y=0.45)
    ax.add_patch(patches.Rectangle((x_check_bloque, 0), ancho_check, PROF_CONTRA, color='#82E0AA', ec='black'))
    plt.text(x_check_bloque + ancho_check/2, PROF_CONTRA/2, 'CONTRACAJA', ha='center', va='center', fontsize=6)
    
    # Pasillo Cajero (Y=0.45 a Y=1.45)
    ax.add_patch(patches.Rectangle((x_check_bloque, PROF_CONTRA), ancho_check, PROF_CAJERO, color='#EAEDED'))
    plt.text(x_check_bloque + ancho_check/2, PROF_CONTRA + PROF_CAJERO/2, 'PASILLO CAJERO (1m)', ha='center', va='center', fontsize=6, color='gray')
    
    # Módulos Checkout (Y=1.45 a Y=2.05)
    y_modulos_check = PROF_CONTRA + PROF_CAJERO
    for i in range(conf['cant_checkout']):
        x_mod = x_check_bloque + (i * MOD_2FT)
        ax.add_patch(patches.Rectangle((x_mod, y_modulos_check), MOD_2FT, PROF_CHECK, color='#ABEBC6', ec='black'))
        plt.text(x_mod + MOD_2FT/2, y_modulos_check + PROF_CHECK/2, f'CHK{i+1}', ha='center', va='center', fontsize=6)
        
    # Pasillo de Cobro (Fila) frente al Checkout
    y_fila = y_modulos_check + PROF_CHECK
    ax.add_patch(patches.Rectangle((x_check_bloque, y_fila), ancho_check, PASILLO_STD, color='#D5F5E3', alpha=0.5))
    plt.text(x_check_bloque + ancho_check/2, y_fila + PASILLO_STD/2, 'PASILLO COBRO (Fila)', ha='center', va='center', fontsize=7)

    # --- ÁREA DE CAFÉ ---
    for i in range(conf['cant_cafe']):
        x_mod = x_cafe + (i * MOD_2FT)
        # Evitar sobreponer con el pasillo de poder
        if not (x_mod >= x_puerta and x_mod <= x_puerta + PUERTA_ANCHO):
            ax.add_patch(patches.Rectangle((x_mod, 0), MOD_2FT, PROF_CAFE, color='#FAD7A0', ec='black'))
            plt.text(x_mod + MOD_2FT/2, PROF_CAFE/2, f'C{i+1}', ha='center', va='center', fontsize=6)
            
    # Pasillo de Servicio Café
    ax.add_patch(patches.Rectangle((x_cafe, PROF_CAFE), ancho_cafe, PASILLO_STD, color='#FADBD8', alpha=0.5))
    plt.text(x_cafe + ancho_cafe/2, PROF_CAFE + PASILLO_STD/2, 'PASILLO SERVICIO CAFÉ', ha='center', va='center', fontsize=7)

    # ==========================================
    # 5. GÓNDOLAS CENTRALES (Orientación Visibilidad)
    # ==========================================
    # La orientación dictada es paralela al pasillo de poder para asegurar línea de visión cajero-fondo
    largo_cuerpo = conf['cant_tramos'] * MOD_3FT
    largo_total_tren = CABECERA_PROF*2 + largo_cuerpo
    y_inicio_gondolas = max(y_fila + PASILLO_STD, PROF_CAFE + PASILLO_STD) + 0.5
    
    x_izq = x_puerta - PASILLO_STD - GONDOLA_PROF
    x_der = x_puerta + PUERTA_ANCHO + PASILLO_STD
    
    trenes_colocados = 0
    while trenes_colocados < conf['cant_trenes']:
        colocado = False
        if trenes_colocados % 2 == 0 and x_izq >= 0:
            x_g = x_izq
            x_izq -= (GONDOLA_PROF + PASILLO_STD)
            colocado = True
        elif x_der + GONDOLA_PROF <= ancho:
            x_g = x_der
            x_der += (GONDOLA_PROF + PASILLO_STD)
            colocado = True
            
        if not colocado: break

        # Dibujar Góndola
        ax.add_patch(patches.Rectangle((x_g, y_inicio_gondolas), GONDOLA_PROF, CABECERA_PROF, color='#E74C3C', ec='black'))
        for t in range(conf['cant_tramos']):
            y_t = y_inicio_gondolas + CABECERA_PROF + (t * MOD_3FT)
            ax.add_patch(patches.Rectangle((x_g, y_t), GONDOLA_PROF, MOD_3FT, color='#ABB2B9', ec='black'))
        ax.add_patch(patches.Rectangle((x_g, y_inicio_gondolas + CABECERA_PROF + largo_cuerpo), GONDOLA_PROF, CABECERA_PROF, color='#E74C3C', ec='black'))
        
        # Pasillos entre Góndolas
        ax.add_patch(patches.Rectangle(((x_g - PASILLO_STD if x_g < x_puerta else x_g + GONDOLA_PROF), y_inicio_gondolas), PASILLO_STD, largo_total_tren, color='#EBEDEF', alpha=0.7))
        plt.text((x_g - PASILLO_STD/2 if x_g < x_puerta else x_g + GONDOLA_PROF + PASILLO_STD/2), y_inicio_gondolas + largo_total_tren/2, 'PASILLO GÓNDOLAS', ha='center', va='center', rotation=90, fontsize=6, color='gray')
            
        trenes_colocados += 1

    ax.set_aspect('equal')
    plt.title(f"Layout Estratégico V8.0 | Flujo Condicionado")
    return fig

# --- UI STREAMLIT ---
st.set_page_config(layout="wide")
st.title("🏗️ Arquitectura Estratégica V8.0")

st.sidebar.header("Paso 1: Huella del Local")
ancho = st.sidebar.number_input("Ancho (m)", 10.0, 30.0, 15.0, 0.5)
largo = st.sidebar.number_input("Profundidad (m)", 15.0, 40.0, 20.0, 0.5)

st.sidebar.header("Paso 2: Acceso Arquitectónico")
st.sidebar.write("Ubicación de la puerta (separación desde la pared izquierda):")
max_distancia = float(ancho - PUERTA_ANCHO)
distancia_puerta = st.sidebar.slider("Separación (m)", 0.0, max_distancia, float(ancho/2 - PUERTA_ANCHO/2), 0.1)

st.sidebar.header("Paso 3: Zonas de Exhibición")
cant_frio = st.sidebar.number_input("Puertas Frío (2ft)", 2, 20, 10)
cant_trenes = st.sidebar.number_input("Trenes Góndola", 1, 6, 2)
cant_tramos = st.sidebar.number_input("Tramos por Tren (3ft)", 1, 8, 3)

st.sidebar.header("Paso 4: Zonas de Servicio")
cant_cafe = st.sidebar.number_input("Módulos Café (2ft)", 2, 10, 4)
cant_checkout = st.sidebar.number_input("Módulos Checkout (2ft)", 1, 5, 3)

conf = {
    'ancho': ancho, 'largo': largo, 'distancia_puerta': distancia_puerta,
    'cant_frio': cant_frio, 'cant_trenes': cant_trenes, 'cant_tramos': cant_tramos,
    'cant_cafe': cant_cafe, 'cant_checkout': cant_checkout
}

col_main, col_info = st.columns([3, 1])

with col_main:
    st.pyplot(dibujar_layout_v8(conf))

with col_info:
    st.subheader("Reglas de Dependencia Activas")
    st.info("El sistema evalúa la posición de la puerta y ejecuta la siguiente estrategia de distribución:")
    st.markdown("""
    1. **Checkout Opuesto:** Se ancla en el lado contrario a la entrada para balancear el tráfico frontal y evitar cuellos de botella.
    2. **Zona de Cobro Completa:** Ahora incluye Contracaja (45cm), Pasillo Operativo (1m) y Módulos de Checkout (60cm) como un solo bloque funcional.
    3. **Diagonal de Tráfico:** El Cuarto Frío se ubica al fondo, en el lado opuesto del Checkout, forzando al cliente a navegar la profundidad total de la tienda.
    4. **Visibilidad:** Las góndolas se orientan verticalmente para que los pasillos funcionen como túneles de visión despejados desde el Checkout hacia el Frío.
    """)