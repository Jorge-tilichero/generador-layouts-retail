import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import math

# --- CONSTANTES DE MODULACIÓN ---
MOD_1FT = 0.30
MOD_2FT = 0.61        
MOD_3FT = 0.91        
PROF_CAFE = 0.75      
PROF_CHECK = 0.60     
PROF_FRIO = 2.00      
PROF_PERIMETRO = 0.45 
GONDOLA_PROF = 0.90   
CABECERA_PROF = 0.45  
PUERTA_ANCHO = 1.80   
PASILLO_STD = 1.20    

# --- INICIALIZACIÓN DE VARIABLES DE ESTADO ---
if 'opt_trenes' not in st.session_state:
    st.session_state.opt_trenes = 2
if 'opt_tramos' not in st.session_state:
    st.session_state.opt_tramos = 3

def auto_optimizar(ancho, largo, pct_operativo, cant_frio, cant_check, cant_cafe):
    """Algoritmo heurístico para buscar el 35% de exhibición perfecto"""
    area_total = ancho * largo
    area_operativa = area_total * (pct_operativo / 100)
    area_comercial = area_total - area_operativa
    
    # Meta perfecta de exhibición (35%)
    meta_exhibicion = area_comercial * 0.35
    
    # Calcular áreas fijas (Frío, Checkout, Café, Perimetral estimado)
    area_fija = (cant_frio * MOD_2FT * PROF_FRIO) + \
                (cant_check * MOD_2FT * PROF_CHECK) + \
                (cant_cafe * MOD_2FT * PROF_CAFE)
    # Estimación de perimetrales (Muro Izq + Muro Der aprox)
    prof_frio_estimada = area_operativa / ancho + PROF_FRIO
    y_frio_estimado = largo - prof_frio_estimada
    area_fija += (PROF_PERIMETRO * y_frio_estimado * 2) 
    
    area_restante_meta = meta_exhibicion - area_fija
    
    # Límites físicos del local para góndolas centrales
    safe_margin_x = PASILLO_STD + PROF_PERIMETRO
    espacio_x = ancho - (safe_margin_x * 2)
    max_trenes = max(1, int(espacio_x / (GONDOLA_PROF + PASILLO_STD)))
    
    espacio_y = y_frio_estimado - (1.0 + PROF_CHECK + PASILLO_STD) - PASILLO_STD
    max_tramos = max(1, int((espacio_y - (CABECERA_PROF * 2)) / MOD_3FT))
    
    # Buscar la mejor combinación
    mejor_diferencia = float('inf')
    mejor_trenes = 1
    mejor_tramos = 1
    
    for trenes in range(1, max_trenes + 1):
        for tramos in range(1, max_tramos + 1):
            area_gondolas = trenes * (GONDOLA_PROF * ((tramos * MOD_3FT) + (CABECERA_PROF * 2)))
            diferencia = abs(area_restante_meta - area_gondolas)
            
            if diferencia < mejor_diferencia:
                mejor_diferencia = diferencia
                mejor_trenes = trenes
                mejor_tramos = tramos
                
    st.session_state.opt_trenes = mejor_trenes
    st.session_state.opt_tramos = mejor_tramos

def dibujar_layout_v12(conf):
    ancho = conf['ancho']
    largo = conf['largo']
    fig, ax = plt.subplots(figsize=(12, 12))
    ax.set_xlim(0, ancho)
    ax.set_ylim(0, largo)
    
    alertas = []
    area_total = ancho * largo
    area_exhibicion = 0 

    # 1. ACCESO Y UMBRAL
    if conf['muro_puerta'] == 'Inferior (Frente)':
        x_p, y_p, orientacion = conf['pos_puerta'], 0, 'vertical'
    elif conf['muro_puerta'] == 'Lateral Izquierdo':
        x_p, y_p, orientacion = 0, conf['pos_puerta'], 'horizontal'
    else: 
        x_p, y_p, orientacion = ancho, conf['pos_puerta'], 'horizontal'

    ax.add_patch(patches.Circle((x_p + (PUERTA_ANCHO/2 if orientacion=='vertical' else 0), 
                                 y_p + (PUERTA_ANCHO/2 if orientacion=='horizontal' else 0)), 
                                2.0, color='#85C1E9', alpha=0.2))

    if orientacion == 'vertical':
        ax.add_patch(patches.Rectangle((x_p, 0), PUERTA_ANCHO, largo, color='#EBF5FB', alpha=0.4))
        plt.text(x_p + PUERTA_ANCHO/2, largo/3, 'PASILLO PODER', rotation=90, ha='center', fontsize=8, color='#21618C')

    # 2. OPERATIVO Y CUARTO FRÍO
    area_operativa = area_total * (conf['pct_operativo'] / 100)
    prof_bodega = area_operativa / ancho
    rect_bodega = (0, largo - prof_bodega, ancho, prof_bodega)
    y_frio = largo - prof_bodega - PROF_FRIO
    x_frio = (ancho - (conf['cant_frio'] * MOD_2FT)) / 2 if conf['muro_puerta'] == 'Inferior (Frente)' else (0 if conf['muro_puerta'] == 'Lateral Derecho' else ancho - (conf['cant_frio'] * MOD_2FT))

    ax.add_patch(patches.Rectangle((rect_bodega[0], rect_bodega[1]), rect_bodega[2], rect_bodega[3], color='#D2B48C', ec='black'))
    plt.text(rect_bodega[0] + rect_bodega[2]/2, rect_bodega[1] + rect_bodega[3]/2, 'ZONA OPERATIVA', ha='center', va='center')

    ancho_frio = conf['cant_frio'] * MOD_2FT
    ax.add_patch(patches.Rectangle((x_frio, y_frio), ancho_frio, PROF_FRIO, color='#AED6F1', ec='black'))
    plt.text(x_frio + ancho_frio/2, y_frio + PROF_FRIO/2, 'FRÍO (7 ft)', ha='center', va='center', fontsize=8)
    area_exhibicion += (ancho_frio * PROF_FRIO)

    # 3. CHECKOUT
    x_check = x_p + PUERTA_ANCHO + PASILLO_STD if x_p + PUERTA_ANCHO < ancho/2 else x_p - PASILLO_STD - (conf['cant_check']*MOD_2FT)
    ancho_check_total = conf['cant_check']*MOD_2FT
    ax.add_patch(patches.Rectangle((x_check, 1.0), ancho_check_total, PROF_CHECK, color='#ABEBC6', ec='black'))
    plt.text(x_check + ancho_check_total/2, 1.0 + PROF_CHECK/2, 'CHK (3.5 ft)', ha='center', va='center', fontsize=6)
    area_exhibicion += (ancho_check_total * PROF_CHECK)

    # 4. CAFÉ Y PERIMETRALES
    x_c = 1.0 if x_check > ancho/2 else ancho - (conf['cant_cafe']*MOD_2FT) - 1.0
    for i in range(conf['cant_cafe']):
        ax.add_patch(patches.Rectangle((x_c, 1.0), MOD_2FT, PROF_CAFE, color='#FAD7A0', ec='black'))
        area_exhibicion += (MOD_2FT * PROF_CAFE)
        x_c += MOD_2FT

    if conf['muro_puerta'] == 'Inferior (Frente)':
        ax.add_patch(patches.Rectangle((0, 0), PROF_PERIMETRO, y_frio, color='#D5DBDB', ec='gray'))
        ax.add_patch(patches.Rectangle((ancho-PROF_PERIMETRO, 0), PROF_PERIMETRO, y_frio, color='#D5DBDB', ec='gray'))
        area_exhibicion += (PROF_PERIMETRO * y_frio * 2)

    # 5. GÓNDOLAS CENTRALES
    safe_margin = PASILLO_STD + PROF_PERIMETRO
    x_g = safe_margin + 0.5
    for i in range(st.session_state.opt_trenes):
        largo_g = st.session_state.opt_tramos * MOD_3FT
        y_g = max(1.0 + PROF_CHECK, 1.0 + PROF_CAFE) + PASILLO_STD
        
        if x_g + GONDOLA_PROF < ancho - safe_margin and y_g + largo_g + CABECERA_PROF < y_frio - PASILLO_STD:
            ax.add_patch(patches.Rectangle((x_g, y_g), GONDOLA_PROF, largo_g, color='#ABB2B9', ec='black'))
            ax.add_patch(patches.Rectangle((x_g, y_g - CABECERA_PROF), GONDOLA_PROF, CABECERA_PROF, color='#E74C3C', ec='black'))
            ax.add_patch(patches.Rectangle((x_g, y_g + largo_g), GONDOLA_PROF, CABECERA_PROF, color='#E74C3C', ec='black'))
            
            area_exhibicion += (GONDOLA_PROF * (largo_g + CABECERA_PROF*2))
            x_g += GONDOLA_PROF + PASILLO_STD
        else:
            alertas.append(f"⚠️ Tren {i+1} bloqueado (Falta de espacio).")

    plt.plot([x_p, x_p + (PUERTA_ANCHO if orientacion=='vertical' else 0)], [y_p, y_p + (PUERTA_ANCHO if orientacion=='horizontal' else 0)], color='red', linewidth=10)

    area_comercial = area_total - area_operativa
    pct_exhibicion = (area_exhibicion / area_comercial) * 100
    
    ax.set_aspect('equal')
    plt.title(f"Layout Inteligente | Exhibición Comercial: {pct_exhibicion:.1f}%")
    return fig, alertas, pct_exhibicion

# --- INTERFAZ ---
st.set_page_config(layout="wide")
st.title("🏬 Store Planning - AI Optimizer V12.0")

with st.sidebar:
    st.header("1. Dimensiones y Zonas")
    ancho = st.slider("Ancho (m)", 8.0, 25.0, 15.0)
    largo = st.slider("Profundidad (m)", 10.0, 30.0, 20.0)
    pct_operativo = st.slider("% Área Operativa", 10, 40, 20)
    
    st.header("2. Accesos")
    muro = st.selectbox("Muro de la puerta", ['Inferior (Frente)', 'Lateral Izquierdo', 'Lateral Derecho'])
    pos_puerta = st.slider("Posición de puerta", 0.0, ancho-PUERTA_ANCHO if muro=='Inferior (Frente)' else largo-PUERTA_ANCHO, ancho/2 - PUERTA_ANCHO/2)
    
    st.header("3. Muebles Fijos")
    cant_frio = st.number_input("Puertas Frío", 4, 15, 8)
    cant_cafe = st.number_input("Módulos Café", 2, 8, 4)
    cant_check = st.number_input("Módulos Checkout", 1, 4, 3)

    st.markdown("---")
    st.header("4. Góndolas (Optimizables)")
    st.button("✨ Auto-Optimizar Rentabilidad (35%)", 
              on_click=auto_optimizar, 
              args=(ancho, largo, pct_operativo, cant_frio, cant_check, cant_cafe),
              type="primary")
    
    st.number_input("Trenes Centrales", 1, 6, key="opt_trenes")
    st.number_input("Tramos por tren", 1, 10, key="opt_tramos")

conf = {
    'ancho': ancho, 'largo': largo, 'pct_operativo': pct_operativo, 
    'muro_puerta': muro, 'pos_puerta': pos_puerta, 
    'cant_frio': cant_frio, 'cant_cafe': cant_cafe, 'cant_check': cant_check
}

col_plot, col_kpis = st.columns([2.5, 1.5])

with col_plot:
    fig, alertas, pct_exh = dibujar_layout_v12(conf)
    st.pyplot(fig)

with col_kpis:
    st.subheader("🎯 Auditoría de Negocio")
    st.metric("Nivel de Exhibición", f"{pct_exh:.1f}%")
    st.progress(min(pct_exh / 100, 1.0))
    
    if 30 <= pct_exh <= 40:
        st.success("Estado: **ÓPTIMO** (Balance 80/20 y 60/40 respetado) [cite: 164, 214]")
    elif pct_exh > 40:
        st.error("Estado: **SATURADO** (Poca navegación, mala experiencia) [cite: 622, 624]")
    else:
        st.warning("Estado: **SUBUTILIZADO** (Oportunidad de agregar muebles) [cite: 630]")
        
    if alertas:
        st.markdown("---")
        for a in alertas:
            st.warning(a)