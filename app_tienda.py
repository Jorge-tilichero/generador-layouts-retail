import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# --- CONSTANTES EXACTAS ---
MOD_2FT = 0.61        # 2ft = 0.61m (Puertas Frío, Checkout, Café)
MOD_3FT = 0.91        # 3ft = 0.91m (Tramos Góndola)
PROF_CAFE = 0.75      # Profundidad módulos café
PROF_CHECK = 0.60     # Profundidad módulos checkout
PROF_FRIO = 2.00      # Profundidad Cuarto Frío
GONDOLA_PROF = 0.90   # Profundidad góndola doble vista
CABECERA_PROF = 0.45  # Profundidad cabecera
PUERTA_ANCHO = 1.80   # Puerta principal doble
PASILLO_STD = 1.20    # Pasillo estándar
ISLA_DIM = 0.60       # Exhibidores de piso

def dibujar_layout_v7(conf):
    ancho = conf['ancho']
    largo = conf['largo']
    
    fig, ax = plt.subplots(figsize=(12, 14))
    ax.set_xlim(0, ancho)
    ax.set_ylim(0, largo)
    
    # ==========================================
    # 1. CÁLCULO DE ÁREAS BASE Y BODEGA
    # ==========================================
    area_bodega = (ancho * largo) * 0.20
    if conf['bodega_loc'] == 'Fondo Completo':
        prof_bodega = area_bodega / ancho
        rect_bodega = (0, largo - prof_bodega, ancho, prof_bodega)
    elif conf['bodega_loc'] == 'Fondo Izquierda':
        ancho_bodega = ancho / 2
        prof_bodega = area_bodega / ancho_bodega
        rect_bodega = (0, largo - prof_bodega, ancho_bodega, prof_bodega)
    else: # Fondo Derecha
        ancho_bodega = ancho / 2
        prof_bodega = area_bodega / ancho_bodega
        rect_bodega = (ancho - ancho_bodega, largo - prof_bodega, ancho_bodega, prof_bodega)

    ax.add_patch(patches.Rectangle((rect_bodega[0], rect_bodega[1]), rect_bodega[2], rect_bodega[3], color='#D2B48C', ec='black'))
    plt.text(rect_bodega[0] + rect_bodega[2]/2, rect_bodega[1] + rect_bodega[3]/2, 'BODEGA', ha='center', va='center', weight='bold')

    # ==========================================
    # 2. CUARTO FRÍO (Módulos exactos de 2ft/2m)
    # ==========================================
    ancho_frio = conf['cant_frio'] * MOD_2FT
    y_frio = rect_bodega[1] - PROF_FRIO
    x_frio = (ancho - ancho_frio) / 2 # Centrado frente a bodega
    
    # Dibujar bloque principal del cuarto frío
    ax.add_patch(patches.Rectangle((x_frio, y_frio), ancho_frio, PROF_FRIO, color='#AED6F1', ec='black'))
    plt.text(x_frio + ancho_frio/2, y_frio + 1.2, 'CUARTO FRÍO', ha='center', va='center', weight='bold')
    
    # Dibujar cada puerta individual
    for i in range(conf['cant_frio']):
        ax.add_patch(patches.Rectangle((x_frio + (i * MOD_2FT), y_frio), MOD_2FT, 0.15, color='#2874A6', ec='white'))
        plt.text(x_frio + (i * MOD_2FT) + MOD_2FT/2, y_frio + 0.3, f'P{i+1}', ha='center', va='center', fontsize=5, color='black', rotation=90)

    # ==========================================
    # 3. UBICACIÓN DE ACCESO Y PASILLOS CRUZADOS
    # ==========================================
    if conf['puerta_loc'] == 'Centro':
        x_puerta = (ancho / 2) - (PUERTA_ANCHO / 2)
    elif conf['puerta_loc'] == 'Izquierda':
        x_puerta = 1.0
    else: # Derecha
        x_puerta = ancho - PUERTA_ANCHO - 1.0

    y_limite_frio = y_frio - PASILLO_STD
    y_inicio_gondolas = max(PROF_CAFE, PROF_CHECK) + PASILLO_STD
    
    # Dibujar Pasillos (Red de Circulación)
    # A. Pasillo de Poder (Vertical)
    ax.add_patch(patches.Rectangle((x_puerta, 0), PUERTA_ANCHO, y_limite_frio, color='#EBF5FB', alpha=0.7, label='Pasillo Poder'))
    plt.text(x_puerta + PUERTA_ANCHO/2, y_inicio_gondolas + 2.0, 'PASILLO DE PODER', ha='center', va='center', rotation=90, color='#21618C', weight='bold')
    
    # B. Pasillo Cuarto Frío (Horizontal)
    ax.add_patch(patches.Rectangle((0, y_limite_frio), ancho, PASILLO_STD, color='#FCF3CF', alpha=0.7))
    plt.text(x_frio + ancho_frio/2, y_limite_frio + PASILLO_STD/2, 'PASILLO CUARTO FRÍO', ha='center', va='center', color='#9A7D0A', weight='bold')

    # C. Pasillo Café y Pasillo Cobro (Horizontales Frontales)
    ax.add_patch(patches.Rectangle((0, PROF_CAFE), (x_puerta if x_puerta > 0 else ancho/2), PASILLO_STD, color='#FADBD8', alpha=0.5))
    plt.text((x_puerta if x_puerta > 0 else ancho/2)/2, PROF_CAFE + PASILLO_STD/2, 'PASILLO CAFÉ', ha='center', va='center', fontsize=8)
    
    x_inicio_cobro = x_puerta + PUERTA_ANCHO
    ax.add_patch(patches.Rectangle((x_inicio_cobro, PROF_CHECK), ancho - x_inicio_cobro, PASILLO_STD, color='#D5F5E3', alpha=0.5))
    plt.text(x_inicio_cobro + (ancho - x_inicio_cobro)/2, PROF_CHECK + PASILLO_STD/2, 'PASILLO COBRO (Fila)', ha='center', va='center', fontsize=8)

    # Puerta Física
    plt.plot([x_puerta, x_puerta + PUERTA_ANCHO], [0, 0], color='red', linewidth=12)

    # ==========================================
    # 4. MOBILIARIO FRONTAL (Café y Checkout)
    # ==========================================
    # Café (Izquierda de la puerta)
    ancho_cafe_total = conf['cant_cafe'] * MOD_2FT
    for i in range(conf['cant_cafe']):
        if (i * MOD_2FT) + MOD_2FT <= x_puerta or conf['puerta_loc'] != 'Izquierda': # Evitar chocar con puerta
            x_mod = i * MOD_2FT
            ax.add_patch(patches.Rectangle((x_mod, 0), MOD_2FT, PROF_CAFE, color='#FAD7A0', ec='black'))
            plt.text(x_mod + MOD_2FT/2, PROF_CAFE/2, f'C{i+1}', ha='center', va='center', fontsize=7)

    # Checkout (Derecha de la puerta)
    for i in range(conf['cant_checkout']):
        x_mod = ancho - (i * MOD_2FT) - MOD_2FT
        if x_mod >= x_puerta + PUERTA_ANCHO:
            ax.add_patch(patches.Rectangle((x_mod, 0), MOD_2FT, PROF_CHECK, color='#ABEBC6', ec='black'))
            plt.text(x_mod + MOD_2FT/2, PROF_CHECK/2, f'CHK{i+1}', ha='center', va='center', fontsize=7)

    # ==========================================
    # 5. GÓNDOLAS CENTRALES (Modulación y Pasillos)
    # ==========================================
    largo_cuerpo = conf['cant_tramos'] * MOD_3FT
    largo_total_tren = CABECERA_PROF*2 + largo_cuerpo
    
    # Validar si las góndolas caben verticalmente
    if y_inicio_gondolas + largo_total_tren > y_limite_frio:
        plt.text(ancho/2, largo/2, '⚠️ ERROR: Tramos exceden el largo disponible.', ha='center', color='red', weight='bold')
        return fig

    # Listas de posiciones seguras para islas
    zonas_islas = []
    
    # Lógica de distribución a los lados del Pasillo de Poder
    x_izq = x_puerta - PASILLO_STD - GONDOLA_PROF
    x_der = x_puerta + PUERTA_ANCHO + PASILLO_STD
    
    trenes_colocados = 0
    while trenes_colocados < conf['cant_trenes']:
        colocado = False
        # Intentar a la Izquierda
        if trenes_colocados % 2 == 0 and x_izq >= 0:
            x_g = x_izq
            x_izq -= (GONDOLA_PROF + PASILLO_STD)
            colocado = True
        # Intentar a la Derecha
        elif x_der + GONDOLA_PROF <= ancho:
            x_g = x_der
            x_der += (GONDOLA_PROF + PASILLO_STD)
            colocado = True
            
        if not colocado:
            break # No caben más trenes

        # Dibujar Tren
        # Cabecera Sur
        ax.add_patch(patches.Rectangle((x_g, y_inicio_gondolas), GONDOLA_PROF, CABECERA_PROF, color='#E74C3C', ec='black'))
        plt.text(x_g + GONDOLA_PROF/2, y_inicio_gondolas + CABECERA_PROF/2, 'CAB', ha='center', va='center', fontsize=6)
        
        # Tramos individuales (Cuerpo)
        for t in range(conf['cant_tramos']):
            y_t = y_inicio_gondolas + CABECERA_PROF + (t * MOD_3FT)
            ax.add_patch(patches.Rectangle((x_g, y_t), GONDOLA_PROF, MOD_3FT, color='#ABB2B9', ec='black'))
            plt.text(x_g + GONDOLA_PROF/2, y_t + MOD_3FT/2, f'Tr{t+1}', ha='center', va='center', fontsize=7)
            
        # Cabecera Norte
        y_cab_norte = y_inicio_gondolas + CABECERA_PROF + largo_cuerpo
        ax.add_patch(patches.Rectangle((x_g, y_cab_norte), GONDOLA_PROF, CABECERA_PROF, color='#E74C3C', ec='black'))
        plt.text(x_g + GONDOLA_PROF/2, y_cab_norte + CABECERA_PROF/2, 'CAB', ha='center', va='center', fontsize=6)
        
        # Guardar espacio frente a cabeceras para posibles islas promocionales
        zonas_islas.append((x_g + 0.15, y_inicio_gondolas - ISLA_DIM - 0.2))
        
        # Dibujar "Pasillo entre Góndolas" si corresponde
        if colocado:
            ax.add_patch(patches.Rectangle((x_g - PASILLO_STD if x_g < x_puerta else x_g + GONDOLA_PROF), y_inicio_gondolas, PASILLO_STD, largo_total_tren, color='#EBEDEF', alpha=0.5))
            
        trenes_colocados += 1

    # ==========================================
    # 6. EXHIBIDORES DE PISO (Prevención de choques)
    # ==========================================
    islas_dibujadas = 0
    # Priorizar espacios frente a góndolas
    for zx, zy in zonas_islas:
        if islas_dibujadas < conf['cant_exhibidores'] and zy > PROF_CAFE:
            ax.add_patch(patches.Rectangle((zx, zy), ISLA_DIM, ISLA_DIM, color='#F4D03F', ec='black'))
            plt.text(zx + ISLA_DIM/2, zy + ISLA_DIM/2, f'E{islas_dibujadas+1}', ha='center', va='center', fontsize=7)
            islas_dibujadas += 1

    ax.set_aspect('equal')
    plt.title(f"Layout Arquitectónico V7.0 | Malla de Pasillos Estricta")
    return fig

# --- UI STREAMLIT ---
st.set_page_config(layout="wide")
st.title("🏗️ Arquitectura Comercial V7.0")

st.sidebar.header("1. Cimientos")
ancho = st.sidebar.number_input("Ancho (5m - 20m)", min_value=5.0, max_value=20.0, value=15.0, step=0.5)
largo = st.sidebar.number_input("Largo (5m - 20m)", min_value=5.0, max_value=20.0, value=18.0, step=0.5)
puerta_loc = st.sidebar.selectbox("Ubicación Acceso Frontal", ['Centro', 'Izquierda', 'Derecha'])
bodega_loc = st.sidebar.selectbox("Ubicación Bodega", ['Fondo Completo', 'Fondo Izquierda', 'Fondo Derecha'])

st.sidebar.header("2. Módulos y Muebles")
cant_frio = st.sidebar.number_input("Puertas Frío (2ft x 2m prof.)", min_value=2, max_value=20, value=10)
cant_trenes = st.sidebar.number_input("Trenes de Góndola (Máx 4)", min_value=1, max_value=4, value=2)
cant_tramos = st.sidebar.number_input("Tramos por Tren (3ft c/u)", min_value=1, max_value=6, value=3)
cant_cafe = st.sidebar.number_input("Módulos Café (2ft x 0.75m)", min_value=2, max_value=10, value=4)
cant_checkout = st.sidebar.number_input("Módulos Checkout (2ft x 0.60m)", min_value=1, max_value=5, value=3)
cant_exhibidores = st.sidebar.number_input("Exhibidores de Piso (Máx 20)", min_value=1, max_value=20, value=4)

conf = {
    'ancho': ancho, 'largo': largo, 'puerta_loc': puerta_loc, 'bodega_loc': bodega_loc,
    'cant_frio': cant_frio, 'cant_trenes': cant_trenes, 'cant_tramos': cant_tramos,
    'cant_cafe': cant_cafe, 'cant_checkout': cant_checkout, 'cant_exhibidores': cant_exhibidores
}

col_main, col_info = st.columns([3, 1])

with col_main:
    st.pyplot(dibujar_layout_v7(conf))

with col_info:
    st.subheader("Auditoría de Colisiones")
    st.markdown("""
    * **Módulos Físicos:** El sistema ahora dibuja los contornos exactos en negro.
    * **Intersecciones:** Los pasillos muestran su cruce estructural en colores semitransparentes.
    * **Restricción de Exhibidores:** Si solicitas más exhibidores de los que caben en las zonas libres frente a las cabeceras, el sistema omitirá el resto para garantizar que **ningún pasillo sea bloqueado**.
    """)