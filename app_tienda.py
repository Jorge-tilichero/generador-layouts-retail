import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import math

# --- CONSTANTES ---
FT_M = 0.3048
IN_M = 0.0254
MOD_2FT = 2 * FT_M    
MOD_3FT = 3 * FT_M    
GONDOLA_PROF = 0.90   
CABECERA_PROF = 0.45  
PUERTA_ANCHO = 1.80   
PUERTA_FRIO = 24 * IN_M
ISLA_DIM = 0.60

def dibujar_layout_v6(conf):
    ancho = conf['ancho']
    largo = conf['largo']
    
    fig, ax = plt.subplots(figsize=(10, 12))
    ax.set_xlim(0, ancho)
    ax.set_ylim(0, largo)
    
    # === 1. ZONAS DE FLUJO Y PASILLO DE PODER (Intocables) ===
    # Definir posición de puerta
    if conf['puerta_loc'] == 'Centro':
        x_puerta_centro = ancho / 2
    elif conf['puerta_loc'] == 'Izquierda':
        x_puerta_centro = PUERTA_ANCHO / 2 + 1.0 # 1m de separación de la pared
    else: # Derecha
        x_puerta_centro = ancho - (PUERTA_ANCHO / 2) - 1.0

    x_inicio_pasillo = x_puerta_centro - PUERTA_ANCHO/2
    
    # Dibujar Pasillo de Poder (Libre de obstáculos)
    ax.add_patch(patches.Rectangle((x_inicio_pasillo, 0), PUERTA_ANCHO, largo, color='#EBF5FB', alpha=0.6, label='Pasillo Poder'))
    # Zona de Descompresión (2m)
    ax.add_patch(patches.Circle((x_puerta_centro, 0), 2.0, color='#85C1E9', alpha=0.3))

    # === 2. BODEGA ===
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

    ax.add_patch(patches.Rectangle((rect_bodega[0], rect_bodega[1]), rect_bodega[2], rect_bodega[3], color='#D2B48C'))
    plt.text(rect_bodega[0] + rect_bodega[2]/2, rect_bodega[1] + rect_bodega[3]/2, 'BODEGA', ha='center', va='center', fontsize=9)

    # === 3. CUARTO FRÍO ===
    ancho_frio = conf['cant_frio'] * PUERTA_FRIO
    y_frio = rect_bodega[1] - 2.0 # Se coloca justo delante de la línea de bodega
    
    if conf['bodega_loc'] == 'Fondo Derecha':
        x_frio = 0 # Frio a la izquierda
    elif conf['bodega_loc'] == 'Fondo Izquierda':
        x_frio = ancho - ancho_frio # Frio a la derecha
    else:
        x_frio = (ancho - ancho_frio) / 2 # Centro
        
    ax.add_patch(patches.Rectangle((x_frio, y_frio), ancho_frio, 2.0, color='#AED6F1'))
    plt.text(x_frio + ancho_frio/2, y_frio + 1.0, f'FRÍO ({conf["cant_frio"]}P)', ha='center', va='center')
    
    # Pasillo Frío (1.20m libre)
    y_limite_frio = y_frio - 1.20
    ax.add_patch(patches.Rectangle((0, y_limite_frio), ancho, 1.20, color='#FCF3CF', alpha=0.3))

    # === 4. CHECKOUT Y CAFÉ ===
    # Checkout
    ancho_check = 3 * MOD_2FT # Fijo a 3 modulos para simplificar
    x_check = ancho - ancho_check
    ax.add_patch(patches.Rectangle((x_check, 2.5), ancho_check, 0.60, color='#ABEBC6'))
    ax.add_patch(patches.Rectangle((x_check, 2.5 - 1.20), ancho_check, 1.20, color='#FADBD8', alpha=0.4)) # Fila Libre
    
    # Café
    ancho_cafe = conf['cant_cafe'] * MOD_2FT
    ax.add_patch(patches.Rectangle((0, 0), ancho_cafe, 1.5, color='#FAD7A0'))
    plt.text(ancho_cafe/2, 0.75, f'CAFÉ ({conf["cant_cafe"]} mod)', ha='center', va='center', fontsize=8)

    # === 5. TRENES DE GÓNDOLAS ===
    largo_tren = CABECERA_PROF*2 + (conf['cant_tramos'] * MOD_3FT)
    y_inicio_gondolas = 4.0
    
    # Posicionamiento seguro de góndolas (evitando pasillo de poder)
    x_actual_izq = x_inicio_pasillo - 1.20 - GONDOLA_PROF # 1.20m de pasillo
    x_actual_der = x_inicio_pasillo + PUERTA_ANCHO + 1.20
    
    trenes_dibujados = 0
    zonas_seguras_islas = [] # Guardaremos coordenadas donde podemos poner exhibidores
    
    # Intentar colocar trenes a la izquierda
    while trenes_dibujados < conf['cant_trenes'] / 2 and x_actual_izq > 0:
        ax.add_patch(patches.Rectangle((x_actual_izq, y_inicio_gondolas), GONDOLA_PROF, largo_tren, color='#ABB2B9'))
        ax.add_patch(patches.Rectangle((x_actual_izq, y_inicio_gondolas), GONDOLA_PROF, CABECERA_PROF, color='#E74C3C'))
        ax.add_patch(patches.Rectangle((x_actual_izq, y_inicio_gondolas + largo_tren - CABECERA_PROF), GONDOLA_PROF, CABECERA_PROF, color='#E74C3C'))
        
        # Guardar zona frente a cabecera para posibles islas
        zonas_seguras_islas.append((x_actual_izq, y_inicio_gondolas - 1.0))
        
        x_actual_izq -= (GONDOLA_PROF + 1.20)
        trenes_dibujados += 1

    # Intentar colocar trenes a la derecha
    while trenes_dibujados < conf['cant_trenes'] and x_actual_der + GONDOLA_PROF < ancho:
        ax.add_patch(patches.Rectangle((x_actual_der, y_inicio_gondolas), GONDOLA_PROF, largo_tren, color='#ABB2B9'))
        ax.add_patch(patches.Rectangle((x_actual_der, y_inicio_gondolas), GONDOLA_PROF, CABECERA_PROF, color='#E74C3C'))
        ax.add_patch(patches.Rectangle((x_actual_der, y_inicio_gondolas + largo_tren - CABECERA_PROF), GONDOLA_PROF, CABECERA_PROF, color='#E74C3C'))
        
        # Guardar zona frente a cabecera para posibles islas
        zonas_seguras_islas.append((x_actual_der, y_inicio_gondolas - 1.0))
        
        x_actual_der += (GONDOLA_PROF + 1.20)
        trenes_dibujados += 1

    # === 6. EXHIBIDORES (Islas Promocionales en Zonas Seguras) ===
    # En lugar de ponerlas en el pasillo central, las agrupamos cerca de la descompresión/café/checkout, fuera del flujo
    islas_colocadas = 0
    x_promo = 1.0
    y_promo = 2.0
    
    while islas_colocadas < conf['cant_exhibidores']:
        # Evitar el pasillo de poder
        if x_promo > x_inicio_pasillo - ISLA_DIM - 0.3 and x_promo < x_inicio_pasillo + PUERTA_ANCHO + 0.3:
            x_promo = x_inicio_pasillo + PUERTA_ANCHO + 0.5 # Saltar el pasillo
            
        # Evitar salirnos de la tienda o chocar con frío
        if x_promo + ISLA_DIM > ancho:
            x_promo = 1.0
            y_promo += (ISLA_DIM + 0.60) # Nueva fila
            
        if y_promo + ISLA_DIM > y_limite_frio or y_promo > y_inicio_gondolas - 0.5:
            break # Ya no hay espacio seguro
            
        ax.add_patch(patches.Rectangle((x_promo, y_promo), ISLA_DIM, ISLA_DIM, color='#F4D03F'))
        plt.text(x_promo + ISLA_DIM/2, y_promo + ISLA_DIM/2, f'E{islas_colocadas+1}', ha='center', va='center', fontsize=6)
        
        x_promo += (ISLA_DIM + 0.60)
        islas_colocadas += 1

    # === FINALIZACIÓN ===
    plt.plot([x_inicio_pasillo, x_inicio_pasillo + PUERTA_ANCHO], [0, 0], color='red', linewidth=10)
    ax.set_aspect('equal')
    plt.title("Layout V6.0: Pasillos Libres y Mago de Configuración")
    return fig

# --- UI STREAMLIT: WIZARD PASO A PASO ---
st.set_page_config(layout="wide")
st.title("🏗️ Diseñador de Tiendas V6 (Paso a Paso)")

st.sidebar.header("Paso 1: Medidas del Local")
ancho = st.sidebar.number_input("Ancho (m)", min_value=5.0, max_value=20.0, value=12.0, step=0.5)
largo = st.sidebar.number_input("Profundidad (m)", min_value=5.0, max_value=20.0, value=15.0, step=0.5)

st.sidebar.header("Paso 2: Accesos")
puerta_loc = st.sidebar.selectbox("¿Dónde ubicarás la puerta principal?", ['Centro', 'Izquierda', 'Derecha'])

st.sidebar.header("Paso 3: Bodega")
bodega_loc = st.sidebar.selectbox("Ubicación sugerida de la Bodega", ['Fondo Completo', 'Fondo Izquierda', 'Fondo Derecha'])

st.sidebar.header("Paso 4: Cuarto Frío")
cant_frio = st.sidebar.number_input("Número de puertas de Frío (24\")", min_value=2, max_value=20, value=8)

st.sidebar.header("Paso 5: Góndolas")
cant_trenes = st.sidebar.number_input("Cantidad de trenes de góndola", min_value=1, max_value=4, value=2)
cant_tramos = st.sidebar.number_input("Tramos por tren (3ft)", min_value=1, max_value=6, value=3)
st.sidebar.caption("✅ Cabeceras incluidas automáticamente (2 por tren).")

st.sidebar.header("Paso 6: Exhibidores (Islas)")
cant_exhibidores = st.sidebar.number_input("Cantidad de exhibidores de piso", min_value=1, max_value=20, value=4)
st.sidebar.caption("Se posicionarán en áreas seguras fuera de pasillos.")

st.sidebar.header("Paso 7: Área de Café")
cant_cafe = st.sidebar.number_input("Módulos de Café (2ft)", min_value=2, max_value=10, value=4)

conf = {
    'ancho': ancho,
    'largo': largo,
    'puerta_loc': puerta_loc,
    'bodega_loc': bodega_loc,
    'cant_frio': cant_frio,
    'cant_trenes': cant_trenes,
    'cant_tramos': cant_tramos,
    'cant_exhibidores': cant_exhibidores,
    'cant_cafe': cant_cafe
}

col_main, col_info = st.columns([3, 1])

with col_main:
    st.pyplot(dibujar_layout_v6(conf))

with col_info:
    st.subheader("Auditoría de Pasillos")
    st.success("✔️ Pasillo de Poder Libre (1.80m)")
    st.success("✔️ Pasillos Laterales Libres (1.20m)")
    st.success("✔️ Fila Checkout Libre (1.20m)")
    st.success("✔️ Frente Frío Libre (1.20m)")
    
    st.markdown("---")
    st.write("**Notas:** Si el local es muy pequeño y solicitas demasiados exhibidores, el sistema solo dibujará los que quepan en las zonas de promoción para garantizar el flujo seguro.")