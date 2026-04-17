import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import math

# --- CONSTANTES ---
MOD_1FT = 0.30        # 1ft = 30cm para tramos perimetrales
MOD_2FT = 0.61        # 2ft para Café y Checkout
MOD_3FT = 0.91        # 3ft para Góndolas
PROF_PERIMETRO = 0.45 # Profundidad 45cm
PROF_CAFE = 0.75      
PROF_CHECK = 0.60     
PROF_CAJERO = 1.00    
PROF_CONTRA = 0.45    
PROF_FRIO = 2.00      
GONDOLA_PROF = 0.90   
CABECERA_PROF = 0.45  
PUERTA_ANCHO = 1.80   
PASILLO_STD = 1.20    

def dibujar_layout_v10(conf):
    ancho = conf['ancho']
    largo = conf['largo']
    
    fig, ax = plt.subplots(figsize=(12, 12))
    ax.set_xlim(0, ancho)
    ax.set_ylim(0, largo)
    
    alertas = []

    # 1. DEFINICIÓN DE ACCESO
    if conf['muro_puerta'] == 'Inferior (Frente)':
        x_p, y_p = conf['pos_puerta'], 0
        orientacion = 'vertical'
    elif conf['muro_puerta'] == 'Lateral Izquierdo':
        x_p, y_p = 0, conf['pos_puerta']
        orientacion = 'horizontal'
    else: # Lateral Derecho
        x_p, y_p = ancho, conf['pos_puerta']
        orientacion = 'horizontal'

    # Zona de Descompresión (2m)
    ax.add_patch(patches.Circle((x_p + (PUERTA_ANCHO/2 if orientacion=='vertical' else 0), 
                                 y_p + (PUERTA_ANCHO/2 if orientacion=='horizontal' else 0)), 
                                2.0, color='#85C1E9', alpha=0.1))

    # 2. ALGORITMO DE PERIMETRALES (Tramos de 1ft)
    def colocar_perimetrales_en_linea(x_start, y_start, largo_disponible, eje='H', sentido=1):
        count = 0
        num_tramos = int(largo_disponible / MOD_1FT)
        for i in range(num_tramos):
            if eje == 'H':
                x = x_start + (i * MOD_1FT * sentido)
                y = y_start if sentido == 1 else y_start - PROF_PERIMETRO
                # Evitar chocar con la puerta
                if not (x_p - 0.5 <= x <= x_p + PUERTA_ANCHO + 0.5 and y_p < 1.0):
                    ax.add_patch(patches.Rectangle((x if sentido==1 else x-MOD_1FT, y), MOD_1FT, PROF_PERIMETRO, color='#D5DBDB', ec='gray'))
                    plt.text(x + MOD_1FT/2 * sentido, y + PROF_PERIMETRO/2, 'P', fontsize=5, ha='center', va='center')
                    count += 1
            else: # Eje Vertical
                x = x_start if sentido == 1 else x_start - PROF_PERIMETRO
                y = y_start + (i * MOD_1FT * sentido)
                if not (y_p - 0.5 <= y <= y_p + PUERTA_ANCHO + 0.5 and (x_p < 1.0 or x_p > ancho-1.0)):
                    ax.add_patch(patches.Rectangle((x, y if sentido==1 else y-MOD_1FT), PROF_PERIMETRO, MOD_1FT, color='#D5DBDB', ec='gray'))
                    plt.text(x + PROF_PERIMETRO/2, y + MOD_1FT/2 * sentido, 'P', fontsize=5, ha='center', va='center', rotation=90)
                    count += 1
        return count

    # Colocar perimetrales en muros (Donde no haya puerta/frío)
    if conf['muro_puerta'] != 'Inferior (Frente)':
        colocar_perimetrales_en_linea(0, 0, ancho, eje='H')
    
    # 3. CAFÉ (En Escuadra si es necesario)
    x_c, y_c = (1.2, largo - 1.5) if conf['muro_puerta'] != 'Lateral Izquierdo' else (ancho - 3.0, largo - 1.5)
    for i in range(conf['cant_cafe']):
        # Verificación de colisión con descompresión
        if math.sqrt((x_c - x_p)**2 + (y_c - y_p)**2) < 2.2:
            alertas.append("⚠️ Módulos de café limitados por acceso.")
            break
        ax.add_patch(patches.Rectangle((x_c, y_c), MOD_2FT, PROF_CAFE, color='#FAD7A0', ec='black'))
        plt.text(x_c + MOD_2FT/2, y_c + PROF_CAFE/2, f'C{i+1}', fontsize=7, ha='center')
        x_c += MOD_2FT
        if x_c + MOD_2FT > ancho - 1.0: # Escuadra
            x_c = ancho - PROF_CAFE
            y_c -= MOD_2FT

    # 4. GÓNDOLAS CENTRALES (Regla: No pegadas a pared)
    # Safe Box: Margen de 1.2m pasillo + 0.45m perimetral = 1.65m de la pared
    safe_margin = PASILLO_STD + PROF_PERIMETRO
    x_g = safe_margin + 0.5
    for i in range(conf['cant_trenes']):
        largo_g = conf['cant_tramos'] * MOD_3FT
        y_g = safe_margin + 1.0
        if x_g + GONDOLA_PROF < ancho - safe_margin:
            # Cuerpo
            ax.add_patch(patches.Rectangle((x_g, y_g), GONDOLA_PROF, largo_g, color='#ABB2B9', ec='black'))
            # Cabeceras (Rojo)
            ax.add_patch(patches.Rectangle((x_g, y_g - CABECERA_PROF), GONDOLA_PROF, CABECERA_PROF, color='#E74C3C'))
            ax.add_patch(patches.Rectangle((x_g, y_g + largo_g), GONDOLA_PROF, CABECERA_PROF, color='#E74C3C'))
            plt.text(x_g + GONDOLA_PROF/2, y_g + largo_g/2, f'TREN {i+1}', rotation=90, fontsize=8, color='white')
            x_g += GONDOLA_PROF + PASILLO_STD
        else:
            alertas.append(f"⚠️ Tren {i+1} no cabe respetando pasillos.")

    # 5. PASILLO DE PODER (Visualización)
    if orientacion == 'vertical':
        ax.add_patch(patches.Rectangle((x_p, 0), PUERTA_ANCHO, largo, color='#EBF5FB', alpha=0.3))
    
    # Puerta Física
    plt.plot([x_p, x_p + (PUERTA_ANCHO if orientacion=='vertical' else 0)], 
             [y_p, y_p + (PUERTA_ANCHO if orientacion=='horizontal' else 0)], color='red', linewidth=10)

    ax.set_aspect('equal')
    plt.title("Layout V10.0: Perimetrales Modulados y Seguridad de Flujos")
    return fig, alertas

# --- INTERFAZ ---
st.set_page_config(layout="wide")
st.title("🏗️ Retail Brain V10.0")

with st.sidebar:
    st.header("Configuración del Local")
    ancho = st.slider("Ancho (m)", 5.0, 20.0, 15.0)
    largo = st.slider("Profundidad (m)", 5.0, 20.0, 15.0)
    
    st.header("Ubicación del Acceso")
    muro = st.selectbox("Muro de la puerta", ['Inferior (Frente)', 'Lateral Izquierdo', 'Lateral Derecho'])
    pos_puerta = st.slider("Posición en muro (m)", 0.0, ancho-PUERTA_ANCHO if muro=='Inferior (Frente)' else largo-PUERTA_ANCHO, 5.0)
    
    st.header("Mobiliario")
    cant_trenes = st.number_input("Trenes Góndola", 1, 4, 2)
    cant_tramos = st.number_input("Tramos por tren", 1, 6, 4)
    cant_cafe = st.number_input("Módulos Café", 2, 10, 4)

conf = {'ancho': ancho, 'largo': largo, 'muro_puerta': muro, 'pos_puerta': pos_puerta, 
        'cant_trenes': cant_trenes, 'cant_tramos': cant_tramos, 'cant_cafe': cant_cafe}

col_p, col_m = st.columns([3, 1])
with col_p:
    fig, alertas = dibujar_layout_v10(conf)
    st.pyplot(fig)
with col_m:
    st.subheader("Validación")
    if not alertas: st.success("Layout OK")
    else:
        for a in alertas: st.warning(a)
    st.info("ℹ️ Cada 'P' en el muro representa un tramo perimetral de 1ft (30cm).")