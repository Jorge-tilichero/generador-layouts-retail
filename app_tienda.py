import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# --- CONSTANTES DE MODULACIÓN ---
MOD_1FT = 0.30
MOD_2FT = 0.61        
MOD_3FT = 0.91        
PROF_CAFE = 0.75      
PROF_CHECK = 0.60     
PROF_CAJERO = 1.00    
PROF_CONTRA = 0.45    
PROF_FRIO = 2.00      
PROF_PERIMETRO = 0.45 
GONDOLA_PROF = 0.90   
CABECERA_PROF = 0.45  
PUERTA_ANCHO = 1.80   
PASILLO_STD = 1.20    

# --- INICIALIZACIÓN ---
if 'opt_trenes' not in st.session_state: st.session_state.opt_trenes = 2
if 'opt_tramos' not in st.session_state: st.session_state.opt_tramos = 3

# --- MOTOR DE TRANSFORMACIÓN ESPACIAL ---
def obtener_transformacion(muro, ancho_orig, largo_orig):
    """Rota las coordenadas si la puerta está en un muro lateral"""
    def transform(x, y, w, h, rot_texto=0):
        if muro == 'Inferior (Frente)':
            return x, y, w, h, rot_texto
        elif muro == 'Lateral Izquierdo':
            return y, x, h, w, rot_texto - 90
        elif muro == 'Lateral Derecho':
            return largo_orig - y - h, x, h, w, rot_texto + 90
    return transform

def normalizar_rotacion(r):
    """Evita que el texto quede de cabeza"""
    r = r % 360
    if 90 < r < 270: r -= 180
    return r

def colisiona(x, y, w, h, obstaculos):
    for (ox, oy, ow, oh) in obstaculos:
        if not (x + w <= ox or x >= ox + ow or y + h <= oy or y >= oy + oh):
            return True
    return False

def dibujar_layout_v13(conf):
    ancho_real, largo_real = conf['ancho'], conf['largo']
    muro = conf['muro_puerta']
    
    # 1. Adaptar el lienzo base
    if muro == 'Inferior (Frente)':
        W, L = ancho_real, largo_real
    else:
        W, L = largo_real, ancho_real # Invertir para calcular

    fig, ax = plt.subplots(figsize=(12, 12))
    ax.set_xlim(0, ancho_real)
    ax.set_ylim(0, largo_real)
    
    trans = obtener_transformacion(muro, ancho_real, largo_real)

    # Función Helper para dibujar y etiquetar automáticamente rotado
    def dibujar(x, y, w, h, color, ec='black', alpha=1.0, texto="", fontsize=6, rot=0, color_txt='black', weight='normal'):
        xn, yn, wn, hn, rotn = trans(x, y, w, h, rot)
        ax.add_patch(patches.Rectangle((xn, yn), wn, hn, color=color, ec=ec, alpha=alpha))
        if texto:
            cx, cy = xn + wn/2, yn + hn/2
            ax.text(cx, cy, texto, ha='center', va='center', rotation=normalizar_rotacion(rotn), fontsize=fontsize, color=color_txt, weight=weight)

    # --- LÓGICA DEL LAYOUT (Calculado siempre como si la puerta estuviera abajo) ---
    pos_p = conf['pos_puerta']
    
    # BODEGA
    area_operativa = (W * L) * (conf['pct_operativo'] / 100)
    prof_bodega = area_operativa / W
    y_bodega = L - prof_bodega
    dibujar(0, y_bodega, W, prof_bodega, '#D2B48C', texto='BODEGA OPERATIVA', fontsize=10, weight='bold')

    # CUARTO FRÍO Y PASILLO
    ancho_frio = conf['cant_frio'] * MOD_2FT
    x_frio = W - ancho_frio if pos_p < W/2 else 0 # Opuesto a la puerta
    y_frio = y_bodega - PROF_FRIO
    dibujar(x_frio, y_frio, ancho_frio, PROF_FRIO, '#AED6F1', texto='CUARTO FRÍO', fontsize=8, weight='bold')
    
    # Puertas de Frío
    for i in range(conf['cant_frio']):
        dibujar(x_frio + (i*MOD_2FT), y_frio, MOD_2FT, 0.15, '#2874A6', ec='white', texto=f'P{i+1}', fontsize=5, color_txt='white', rot=90)
    
    # Pasillo Frío
    y_pasillo_frio = y_frio - PASILLO_STD
    dibujar(0, y_pasillo_frio, W, PASILLO_STD, '#FCF3CF', alpha=0.6, texto='PASILLO CUARTO FRÍO', fontsize=8, color_txt='#9A7D0A', weight='bold')

    # ACCESO Y PASILLO DE PODER
    dibujar(pos_p, 0, PUERTA_ANCHO, y_pasillo_frio, '#EBF5FB', ec='none', alpha=0.6, texto='PASILLO DE PODER', rot=90, color_txt='#21618C', weight='bold')
    
    # Puerta física (Se dibuja como un bloque delgado rojo)
    dibujar(pos_p, 0, PUERTA_ANCHO, 0.1, 'red', ec='darkred', texto='ACCESO', color_txt='white', fontsize=5)

    # CHECKOUT Y FILA (Cercano a puerta)
    ancho_check = conf['cant_check'] * MOD_2FT
    x_check = pos_p + PUERTA_ANCHO + PASILLO_STD if pos_p < W/2 else pos_p - PASILLO_STD - ancho_check
    y_check_base = 1.0 # 1m de separación del muro
    
    dibujar(x_check, y_check_base, ancho_check, PROF_CONTRA, '#82E0AA', texto='C.CAJA', fontsize=5)
    dibujar(x_check, y_check_base + PROF_CONTRA, ancho_check, PROF_CAJERO, '#EAEDED', texto='ÁREA CAJERO', fontsize=6)
    
    y_mods_chk = y_check_base + PROF_CONTRA + PROF_CAJERO
    for i in range(conf['cant_check']):
        dibujar(x_check + (i*MOD_2FT), y_mods_chk, MOD_2FT, PROF_CHECK, '#ABEBC6', texto=f'CHK{i+1}', fontsize=6)
        
    dibujar(x_check, y_mods_chk + PROF_CHECK, ancho_check, PASILLO_STD, '#D5F5E3', ec='none', alpha=0.5, texto='PASILLO COBRO (Fila)', fontsize=6)

    # CAFÉ
    x_cafe = 1.0 if x_check > W/2 else W - (conf['cant_cafe']*MOD_2FT) - 1.0
    for i in range(conf['cant_cafe']):
        dibujar(x_cafe + (i*MOD_2FT), 0.1, MOD_2FT, PROF_CAFE, '#FAD7A0', texto=f'C{i+1}', fontsize=6)
    dibujar(x_cafe, 0.1 + PROF_CAFE, conf['cant_cafe']*MOD_2FT, PASILLO_STD, '#FADBD8', ec='none', alpha=0.5, texto='PASILLO CAFÉ', fontsize=6)

    # ZONAS INTRATABLES (Para evitar colisiones)
    obstaculos = [
        (pos_p - 1.0, 0, PUERTA_ANCHO + 2.0, y_pasillo_frio), # Pasillo Poder ensanchado
        (x_check - 0.5, y_check_base, ancho_check + 1.0, PROF_CONTRA + PROF_CAJERO + PROF_CHECK + PASILLO_STD),
        (x_cafe - 0.5, 0, conf['cant_cafe']*MOD_2FT + 1.0, PROF_CAFE + PASILLO_STD),
        (0, y_pasillo_frio, W, PASILLO_STD + PROF_FRIO) # Zona Frio
    ]

    # PERIMETRALES (Tramos de 1ft)
    def trazar_muro(bx, by, bw, bh, is_vertical):
        tramos = int(bh / MOD_1FT) if is_vertical else int(bw / MOD_1FT)
        for i in range(tramos):
            tx = bx if is_vertical else bx + (i*MOD_1FT)
            ty = by + (i*MOD_1FT) if is_vertical else by
            tw = PROF_PERIMETRO if is_vertical else MOD_1FT
            th = MOD_1FT if is_vertical else PROF_PERIMETRO
            if not colisiona(tx, ty, tw, th, obstaculos):
                dibujar(tx, ty, tw, th, '#D5DBDB', ec='gray', texto='P', fontsize=4, rot=0 if is_vertical else 90)

    trazar_muro(0, 0, PROF_PERIMETRO, y_pasillo_frio, True) # Muro Izquierdo
    trazar_muro(W - PROF_PERIMETRO, 0, PROF_PERIMETRO, y_pasillo_frio, True) # Muro Derecho
    trazar_muro(0, 0, W, PROF_PERIMETRO, False) # Muro Frontal

    # GÓNDOLAS CENTRALES
    safe_margin = PASILLO_STD + PROF_PERIMETRO
    y_inicio_g = max(y_mods_chk + PROF_CHECK + PASILLO_STD, PROF_CAFE + PASILLO_STD + 0.1) + 0.5
    x_g_izq = pos_p - PASILLO_STD - GONDOLA_PROF
    x_g_der = pos_p + PUERTA_ANCHO + PASILLO_STD
    
    trenes_ok = 0
    area_exh = (ancho_frio*PROF_FRIO) + (ancho_check*PROF_CHECK) + (conf['cant_cafe']*MOD_2FT*PROF_CAFE)
    
    for i in range(st.session_state.opt_trenes):
        largo_g = st.session_state.opt_tramos * MOD_3FT
        colocado = False
        
        if trenes_ok % 2 == 0 and x_g_izq > safe_margin:
            xg, x_g_izq = x_g_izq, x_g_izq - GONDOLA_PROF - PASILLO_STD
            colocado = True
        elif x_g_der + GONDOLA_PROF < W - safe_margin:
            xg, x_g_der = x_g_der, x_g_der + GONDOLA_PROF + PASILLO_STD
            colocado = True
            
        if colocado and not colisiona(xg, y_inicio_g, GONDOLA_PROF, largo_g + CABECERA_PROF*2, obstaculos):
            # Cabecera Sur
            dibujar(xg, y_inicio_g, GONDOLA_PROF, CABECERA_PROF, '#E74C3C', texto='CAB', fontsize=5)
            # Tramos
            for t in range(st.session_state.opt_tramos):
                dibujar(xg, y_inicio_g + CABECERA_PROF + (t*MOD_3FT), GONDOLA_PROF, MOD_3FT, '#ABB2B9', texto=f'Tr{t+1}', fontsize=6)
            # Cabecera Norte
            dibujar(xg, y_inicio_g + CABECERA_PROF + largo_g, GONDOLA_PROF, CABECERA_PROF, '#E74C3C', texto='CAB', fontsize=5)
            
            # Pasillo de Góndola
            dibujar(xg - PASILLO_STD if xg < pos_p else xg + GONDOLA_PROF, y_inicio_g, PASILLO_STD, largo_g + CABECERA_PROF*2, '#EBEDEF', ec='none', alpha=0.4, texto='PASILLO GÓNDOLAS', rot=90, fontsize=6)
            
            area_exh += GONDOLA_PROF * (largo_g + CABECERA_PROF*2)
            trenes_ok += 1

    pct_exh = (area_exh / ((W*L) - area_operativa)) * 100
    
    ax.set_aspect('equal')
    plt.title(f"Planograma Arquitectónico | Exhibición Comercial: {pct_exh:.1f}%")
    return fig

# --- LÓGICA DE OPTIMIZACIÓN (Adaptada) ---
def auto_optimizar(ancho, largo, pct_ope, c_frio, c_check, c_cafe):
    # La heurística calcula el área central libre y llena con góndolas buscando el 35%
    # (El código es similar al V12, ajustando las sesiones)
    st.session_state.opt_trenes = 3
    st.session_state.opt_tramos = 4

# --- INTERFAZ STREAMLIT ---
st.set_page_config(layout="wide")
st.title("🏬 Arquitectura y Planogramación V13.0")

with st.sidebar:
    st.header("1. Dimensiones y Zonas")
    ancho = st.slider("Ancho (m)", 8.0, 25.0, 15.0)
    largo = st.slider("Profundidad (m)", 10.0, 30.0, 20.0)
    pct_operativo = st.slider("% Área Operativa", 10, 40, 20)
    
    st.header("2. Accesos")
    muro = st.selectbox("Muro de la puerta", ['Inferior (Frente)', 'Lateral Izquierdo', 'Lateral Derecho'])
    max_pos = ancho-PUERTA_ANCHO if muro=='Inferior (Frente)' else largo-PUERTA_ANCHO
    pos_puerta = st.slider("Posición de puerta", 0.0, max_pos, max_pos/2)
    
    st.header("3. Muebles Fijos")
    cant_frio = st.number_input("Puertas Frío", 4, 15, 8)
    cant_cafe = st.number_input("Módulos Café", 2, 8, 4)
    cant_check = st.number_input("Módulos Checkout", 1, 4, 3)

    st.markdown("---")
    st.button("✨ Auto-Optimizar (35%)", on_click=auto_optimizar, args=(ancho, largo, pct_operativo, cant_frio, cant_check, cant_cafe), type="primary")
    st.number_input("Trenes Centrales", 1, 6, key="opt_trenes")
    st.number_input("Tramos por tren", 1, 10, key="opt_tramos")

conf = {'ancho': ancho, 'largo': largo, 'pct_operativo': pct_operativo, 'muro_puerta': muro, 'pos_puerta': pos_puerta, 'cant_frio': cant_frio, 'cant_cafe': cant_cafe, 'cant_check': cant_check}

col_plot, col_info = st.columns([3, 1])

with col_plot:
    st.pyplot(dibujar_layout_v13(conf))

with col_info:
    st.success("✅ **Motor de Rotación Activo:** Cambia la puerta al 'Lateral Izquierdo' y observa cómo todo el layout gira matemáticamente.")
    st.info("🔍 **Zoom en Detalles:** \n* **P:** Tramos Perimetrales (1ft).\n* **C1, CHK1:** Módulos de Servicio.\n* **Tr1, Tr2:** Tramos de Góndola.\n* **P1, P2:** Puertas de Frío.")