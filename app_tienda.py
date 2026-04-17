import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# --- CONSTANTES ---
FT_M = 0.3048
IN_M = 0.0254
MOD_2FT = 2 * FT_M    
MOD_3FT = 3 * FT_M    
GONDOLA_PROF = 0.90   
CABECERA_PROF = 0.45  
PUERTA_ANCHO = 1.80   
PUERTA_FRIO = 24 * IN_M

# Diccionario Maestro de Promocionales
CATALOGO_PROMO = {
    'Tarima de Volumen': {'dim': (1.20, 1.00), 'color': '#E67E22'},
    'Hielera de Cerveza': {'dim': (0.80, 0.80), 'color': '#3498DB'},
    'Nevera': {'dim': (0.70, 0.70), 'color': '#5DADE2'},
    'Isla de Novedades': {'dim': (0.60, 0.60), 'color': '#F1C40F'},
    'Isla de Temporada': {'dim': (0.80, 0.80), 'color': '#F4D03F'}
}

def dibujar_layout_v5(ancho, largo, pasillo_var, conf, promos_seleccionadas):
    fig, ax = plt.subplots(figsize=(10, 14))
    ax.set_xlim(0, ancho)
    ax.set_ylim(0, largo)
    
    # 1. PASILLO DE PODER Y FLUJOS
    x_puerta_centro = ancho/2
    x_inicio_pasillo = x_puerta_centro - PUERTA_ANCHO/2
    ax.add_patch(patches.Rectangle((x_inicio_pasillo, 0), PUERTA_ANCHO, largo, color='#EBF5FB', alpha=0.5))
    ax.add_patch(patches.Circle((x_puerta_centro, 0), 2.0, color='#85C1E9', alpha=0.2)) # Descompresión

    # 2. BODEGA Y FRÍO
    area_bodega = (ancho * largo) * 0.20
    prof_bodega = area_bodega / ancho
    ax.add_patch(patches.Rectangle((0, largo - prof_bodega), ancho, prof_bodega, color='#D2B48C'))
    
    ancho_frio = conf['cant_frio'] * PUERTA_FRIO
    y_frio = largo - prof_bodega - 2.0
    x_frio = (ancho - ancho_frio) / 2
    ax.add_patch(patches.Rectangle((x_frio, y_frio), ancho_frio, 2.0, color='#AED6F1'))
    y_limite_pasillo_frio = y_frio - 1.20

    # 3. CHECKOUT Y CAFÉ
    ancho_check = conf['cant_checkout'] * MOD_2FT
    ax.add_patch(patches.Rectangle((ancho - ancho_check, 2.5), ancho_check, 0.60, color='#ABEBC6'))
    ancho_cafe = conf['cant_cafe'] * MOD_2FT
    ax.add_patch(patches.Rectangle((0, 0), ancho_cafe, 1.5, color='#FAD7A0'))

    # 4. GÓNDOLAS
    largo_tren = CABECERA_PROF*2 + (conf['cant_tramos'] * MOD_3FT)
    y_inicio_gondolas = 4.0
    # Lado Izquierdo
    x_izq = x_inicio_pasillo - pasillo_var - GONDOLA_PROF
    if x_izq > 0:
        ax.add_patch(patches.Rectangle((x_izq, y_inicio_gondolas), GONDOLA_PROF, largo_tren, color='#ABB2B9', alpha=0.7))
        ax.add_patch(patches.Rectangle((x_izq, y_inicio_gondolas), GONDOLA_PROF, CABECERA_PROF, color='#E74C3C'))
        ax.add_patch(patches.Rectangle((x_izq, y_inicio_gondolas + largo_tren - CABECERA_PROF), GONDOLA_PROF, CABECERA_PROF, color='#E74C3C'))
    # Lado Derecho
    x_der = x_inicio_pasillo + PUERTA_ANCHO + pasillo_var
    if x_der + GONDOLA_PROF < ancho:
        ax.add_patch(patches.Rectangle((x_der, y_inicio_gondolas), GONDOLA_PROF, largo_tren, color='#ABB2B9', alpha=0.7))
        ax.add_patch(patches.Rectangle((x_der, y_inicio_gondolas), GONDOLA_PROF, CABECERA_PROF, color='#E74C3C'))
        ax.add_patch(patches.Rectangle((x_der, y_inicio_gondolas + largo_tren - CABECERA_PROF), GONDOLA_PROF, CABECERA_PROF, color='#E74C3C'))

    # 5. PRIORIZACIÓN DE EXHIBIDORES SELECCIONADOS
    y_actual_promo = 3.5
    espacio_entre_promos = 1.2 # Espacio para flujo entre exhibidores
    
    for item_nombre in promos_seleccionadas:
        data = CATALOGO_PROMO[item_nombre]
        dim = data['dim']
        if y_actual_promo + dim[1] < y_limite_pasillo_frio:
            x_p = x_puerta_centro - dim[0]/2
            ax.add_patch(patches.Rectangle((x_p, y_actual_promo), dim[0], dim[1], color=data['color']))
            plt.text(x_puerta_centro, y_actual_promo + dim[1]/2, item_nombre.upper(), ha='center', va='center', fontsize=6, weight='bold')
            y_actual_promo += dim[1] + espacio_entre_promos

    plt.plot([x_inicio_pasillo, x_inicio_pasillo + PUERTA_ANCHO], [0, 0], color='red', linewidth=10)
    ax.set_aspect('equal')
    return fig

# --- UI STREAMLIT ---
st.set_page_config(layout="wide")
st.title("🏗️ Diseñador V5.0: Priorización de Merchandising")

with st.sidebar:
    st.header("1. Local y Pasillos")
    ancho = st.number_input("Ancho (m)", 10.0, 30.0, 15.0)
    largo = st.number_input("Largo (m)", 15.0, 60.0, 25.0)
    pasillo_var = st.slider("Pasillo Góndolas (m)", 0.90, 1.20, 1.10)
    
    st.header("2. Estrategia de Pasillo de Poder")
    st.info("Selecciona los elementos en el orden que deseas que aparezcan (el primero estará más cerca de la entrada).")
    opciones = list(CATALOGO_PROMO.keys())
    seleccion = st.multiselect("Priorizar Exhibidores:", opciones, default=opciones[:3])
    
    st.header("3. Mobiliario")
    cant_frio = st.number_input("Puertas Frío", 4, 25, 12)
    cant_tramos = st.number_input("Tramos Góndola", 1, 10, 4)
    cant_checkout = st.number_input("Módulos Checkout", 1, 5, 3)
    cant_cafe = st.number_input("Módulos Café", 1, 5, 4)

conf = {'cant_frio': cant_frio, 'cant_tramos': cant_tramos, 'cant_checkout': cant_checkout, 'cant_cafe': cant_cafe}

st.pyplot(dibujar_layout_v5(ancho, largo, pasillo_var, conf, seleccion))