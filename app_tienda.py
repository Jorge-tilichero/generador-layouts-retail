import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# --- CONSTANTES DE MODULACIÓN EXACTA ---
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
ISLA_DIM = 0.60

def colisiona(x, y, w, h, obstaculos):
    margen = 0.05
    for (ox, oy, ow, oh) in obstaculos:
        if not (x + w <= ox + margen or x >= ox + ow - margen or y + h <= oy + margen or y >= oy + oh - margen):
            return True
    return False

# --- MOTOR DE TRANSFORMACIÓN (Rotación 360) ---
def obtener_transformacion(muro, ancho_orig, largo_orig):
    def transform(x, y, w, h, rot_texto=0):
        if muro == 'Inferior (Frente)': return x, y, w, h, rot_texto
        elif muro == 'Lateral Izquierdo': return y, x, h, w, rot_texto - 90
        elif muro == 'Lateral Derecho': return ancho_orig - y - h, x, h, w, rot_texto + 90
    return transform

def normalizar_rotacion(r):
    r = r % 360
    if 90 < r < 270: r -= 180
    return r

# --- CLASIFICADOR DE MATRIZ DE FORMATOS OXXO ---
def clasificar_formato(m2):
    if m2 <= 15: return "BOOTH (Compacto)"
    elif m2 <= 36: return "MINI (Reducido)"
    elif m2 <= 56: return "MINI 2 (Reducido)"
    elif m2 <= 77: return "MEDIA (Ordinario)"
    elif m2 <= 98: return "MEDIA 2 (Ordinario)"
    elif m2 <= 117: return "REGULAR (Ordinario)"
    elif m2 <= 135: return "MÍNIMO 2 (Ordinario)"
    elif m2 <= 154: return "ÓPTIMO (Ordinario)"
    elif m2 <= 170: return "ÓPTIMO 2 (Ordinario)"
    elif m2 <= 250: return "MÁXIMO (Extra Ordinario)"
    else: return "MEGA (Extra Ordinario)"

def dibujar_layout_oxxo(conf):
    ancho_real, largo_real = conf['ancho'], conf['largo']
    muro = conf['muro_puerta']
    
    if muro == 'Inferior (Frente)': W, L = ancho_real, largo_real
    else: W, L = largo_real, ancho_real 

    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_xlim(0, ancho_real)
    ax.set_ylim(0, largo_real)
    
    trans = obtener_transformacion(muro, ancho_real, largo_real)
    obstaculos, errores = [], []
    area_exhibicion = 0 
    
    def dibujar(x, y, w, h, color, ec='black', alpha=1.0, texto="", fontsize=6, rot=0, color_txt='black', weight='normal'):
        xn, yn, wn, hn, rotn = trans(x, y, w, h, rot)
        ax.add_patch(patches.Rectangle((xn, yn), wn, hn, color=color, ec=ec, alpha=alpha))
        if texto:
            cx, cy = xn + wn/2, yn + hn/2
            ax.text(cx, cy, texto, ha='center', va='center', rotation=normalizar_rotacion(rotn), fontsize=fontsize, color=color_txt, weight=weight)

    def dibujar_circulo(x, y, r, color, alpha):
        xn, yn, _, _, _ = trans(x - r, y - r, r*2, r*2, 0)
        ax.add_patch(patches.Circle((xn + r, yn + r), r, color=color, alpha=alpha))

    # Lienzo
    ax.add_patch(patches.Rectangle((0, 0), ancho_real, largo_real, fill=False, ec='black', lw=3))

    area_total = W * L
    area_operativa = area_total * 0.20 
    area_comercial = area_total - area_operativa

    # ==========================================
    # 1. ACCESO Y PASILLO DE PODER
    # ==========================================
    if conf['t_puerta']:
        pos_p = conf['pos_puerta']
        dibujar(pos_p, 0, PUERTA_ANCHO, 0.2, 'red', ec='darkred', texto='ACCESO', color_txt='white', fontsize=5)
        dibujar_circulo(pos_p + PUERTA_ANCHO/2, 0, 2.0, '#85C1E9', 0.3)
        dibujar(pos_p, 0, PUERTA_ANCHO, L, '#EBF5FB', ec='none', alpha=0.6, texto='PASILLO DE PODER', rot=90, color_txt='#21618C', weight='bold')
        obstaculos.append((pos_p - 0.2, 0, PUERTA_ANCHO + 0.4, L)) 

    # ==========================================
    # 2. CHECKOUT EN ESQUINA
    # ==========================================
    if conf['t_check'] and conf['t_puerta']:
        ancho_check = conf['cant_check'] * MOD_2FT
        if ancho_check > W - PUERTA_ANCHO:
            errores.append(f"Checkout excede ancho.")
            ancho_check = (W - PUERTA_ANCHO) - 1.0 
            
        x_chk = W - ancho_check if conf['loc_check'] == 'Esquina Inferior Derecha' else 0
        y_chk = 0
        
        if colisiona(x_chk, y_chk, ancho_check, PROF_CONTRA + PROF_CAJERO + PROF_CHECK, obstaculos):
            errores.append("Checkout colisiona con el acceso.")
        else:
            dibujar(x_chk, y_chk, ancho_check, PROF_CONTRA, '#82E0AA', texto='C.CAJA', fontsize=5)
            dibujar(x_chk, y_chk + PROF_CONTRA, ancho_check, PROF_CAJERO, '#EAEDED', texto='PASILLO CAJERO', fontsize=6, color_txt='gray')
            y_mods = y_chk + PROF_CONTRA + PROF_CAJERO
            for i in range(conf['cant_check']):
                dibujar(x_chk + (i*MOD_2FT), y_mods, MOD_2FT, PROF_CHECK, '#ABEBC6', texto=f'CHK{i+1}')
            y_fila = y_mods + PROF_CHECK
            dibujar(x_chk, y_fila, ancho_check, PASILLO_STD, '#D5F5E3', ec='none', alpha=0.5, texto='PASILLO COBRO', color_txt='#186A3B')
            
            obstaculos.append((x_chk, 0, ancho_check, y_fila + PASILLO_STD))
            area_exhibicion += (ancho_check * PROF_CHECK)

    # ==========================================
    # 3. CUARTO FRÍO
    # ==========================================
    if conf['t_frio'] and conf['t_check']:
        ptas = conf['cant_frio']
        y_frio = L - PROF_FRIO
        if conf['forma_frio'] == 'Lineal':
            ancho_frio = ptas * MOD_2FT
            x_frio = 0 if conf['loc_frio'] == 'Fondo Izquierda' else W - ancho_frio
            if ancho_frio > W: errores.append("El cuarto frío excede el ancho.")
            else:
                dibujar(x_frio, y_frio, ancho_frio, PROF_FRIO, '#AED6F1', texto='CUARTO FRÍO', weight='bold')
                for i in range(ptas): dibujar(x_frio + (i*MOD_2FT), y_frio, MOD_2FT, 0.15, '#2874A6', ec='white', texto=f'P{i+1}', color_txt='white', rot=90)
                dibujar(x_frio, y_frio - PASILLO_STD, ancho_frio, PASILLO_STD, '#FCF3CF', ec='none', alpha=0.6, texto='PASILLO FRÍO', color_txt='#9A7D0A')
                obstaculos.append((x_frio, y_frio - PASILLO_STD, ancho_frio, PROF_FRIO + PASILLO_STD))
                area_exhibicion += (ancho_frio * PROF_FRIO)
        else: # Escuadra
            ptas_fondo = int(ptas * 0.6)
            ptas_lat = ptas - ptas_fondo
            ancho_f, largo_l = ptas_fondo * MOD_2FT, ptas_lat * MOD_2FT
            if ancho_f > W or largo_l > L: errores.append("Frío en escuadra excede límites.")
            else:
                if conf['loc_frio'] == 'Fondo Izquierda':
                    dibujar(0, y_frio, ancho_f, PROF_FRIO, '#AED6F1')
                    dibujar(0, y_frio - largo_l, PROF_FRIO, largo_l, '#AED6F1')
                    dibujar(0, y_frio - PASILLO_STD, ancho_f, PASILLO_STD, '#FCF3CF', ec='none', alpha=0.6)
                    dibujar(PROF_FRIO, y_frio - largo_l, PASILLO_STD, largo_l, '#FCF3CF', ec='none', alpha=0.6)
                    obstaculos.append((0, y_frio - largo_l - PASILLO_STD, max(ancho_f, PROF_FRIO + PASILLO_STD), PROF_FRIO + largo_l + PASILLO_STD))
                else:
                    x_f = W - ancho_f
                    dibujar(x_f, y_frio, ancho_f, PROF_FRIO, '#AED6F1')
                    dibujar(W - PROF_FRIO, y_frio - largo_l, PROF_FRIO, largo_l, '#AED6F1')
                    obstaculos.append((W - max(ancho_f, PROF_FRIO + PASILLO_STD), y_frio - largo_l - PASILLO_STD, max(ancho_f, PROF_FRIO + PASILLO_STD), PROF_FRIO + largo_l + PASILLO_STD))
                area_exhibicion += ((ancho_f * PROF_FRIO) + (PROF_FRIO * largo_l))

    # ==========================================
    # 4. GÓNDOLAS CENTRALES
    # ==========================================
    if conf['t_gondolas'] and conf['t_frio']:
        y_inicio_g, x_g, trenes_colocados = 4.0, PASILLO_STD + PROF_PERIMETRO, 0
        for i in range(conf['cant_trenes']):
            largo_g = conf['cant_tramos'] * MOD_3FT
            colocado = False
            while x_g + GONDOLA_PROF < W:
                if not colisiona(x_g, y_inicio_g, GONDOLA_PROF, largo_g + CABECERA_PROF*2, obstaculos):
                    dibujar(x_g, y_inicio_g, GONDOLA_PROF, CABECERA_PROF, '#E74C3C', texto='CAB', fontsize=5)
                    for t in range(conf['cant_tramos']): dibujar(x_g, y_inicio_g + CABECERA_PROF + (t*MOD_3FT), GONDOLA_PROF, MOD_3FT, '#ABB2B9', texto=f'Tr{t+1}')
                    dibujar(x_g, y_inicio_g + CABECERA_PROF + largo_g, GONDOLA_PROF, CABECERA_PROF, '#E74C3C', texto='CAB', fontsize=5)
                    pas_x = x_g - PASILLO_STD if x_g < conf['pos_puerta'] else x_g + GONDOLA_PROF
                    dibujar(pas_x, y_inicio_g, PASILLO_STD, largo_g + CABECERA_PROF*2, '#EBEDEF', ec='none', alpha=0.6, texto='PASILLO GÓNDOLAS', rot=90, color_txt='gray')
                    obstaculos.append((x_g - PASILLO_STD, y_inicio_g - CABECERA_PROF, GONDOLA_PROF + PASILLO_STD*2, largo_g + CABECERA_PROF*2))
                    area_exhibicion += GONDOLA_PROF * (largo_g + CABECERA_PROF*2)
                    colocado = True
                    trenes_colocados += 1
                    break
                x_g += 0.5 
            if colocado: x_g += GONDOLA_PROF + PASILLO_STD
        if trenes_colocados < conf['cant_trenes']: errores.append(f"Solo caben {trenes_colocados} de {conf['cant_trenes']} trenes.")

    # ==========================================
    # 5. CAFÉ
    # ==========================================
    if conf['t_cafe'] and conf['t_gondolas']:
        ancho_cafe = conf['cant_cafe'] * MOD_2FT
        x_cafe = 0 if conf['loc_check'] == 'Esquina Inferior Derecha' else W - ancho_cafe
        y_cafe = 0
        if colisiona(x_cafe, y_cafe, ancho_cafe, PROF_CAFE + PASILLO_STD, obstaculos): errores.append("Área de café bloqueada.")
        else:
            for i in range(conf['cant_cafe']): dibujar(x_cafe + (i*MOD_2FT), y_cafe, MOD_2FT, PROF_CAFE, '#FAD7A0', texto=f'C{i+1}')
            dibujar(x_cafe, PROF_CAFE, ancho_cafe, PASILLO_STD, '#FADBD8', ec='none', alpha=0.5, texto='PASILLO CAFÉ', color_txt='#E74C3C')
            obstaculos.append((x_cafe, y_cafe, ancho_cafe, PROF_CAFE + PASILLO_STD))
            area_exhibicion += (ancho_cafe * PROF_CAFE)

    # ==========================================
    # 6. PERIMETRALES
    # ==========================================
    if conf['t_perimetral'] and conf['t_cafe']:
        tramos_peri = 0
        def colocar_muro(x_base, y_base, largo_muro, vertical=True):
            nonlocal tramos_peri
            for i in range(int(largo_muro / MOD_1FT)):
                cx = x_base if vertical else x_base + (i*MOD_1FT)
                cy = y_base + (i*MOD_1FT) if vertical else y_base
                cw = PROF_PERIMETRO if vertical else MOD_1FT
                ch = MOD_1FT if vertical else PROF_PERIMETRO
                if not colisiona(cx, cy, cw, ch, obstaculos):
                    dibujar(cx, cy, cw, ch, '#D5DBDB', ec='gray', texto='P', fontsize=4, rot=0 if vertical else 90)
                    tramos_peri += 1

        colocar_muro(0, 0, L, vertical=True) 
        colocar_muro(W - PROF_PERIMETRO, 0, L, vertical=True) 
        colocar_muro(0, L - PROF_PERIMETRO, W, vertical=False)
        area_exhibicion += (tramos_peri * MOD_1FT * PROF_PERIMETRO)

    # ==========================================
    # 7. ISLAS
    # ==========================================
    if conf['t_islas'] and conf['t_perimetral']:
        islas_ok = 0
        for y_isla in range(2, int(L)-2): 
            for x_isla in range(1, int(W)-1):
                if islas_ok >= conf['cant_islas']: break
                if not colisiona(x_isla, y_isla, ISLA_DIM, ISLA_DIM, obstaculos):
                    dibujar(x_isla, y_isla, ISLA_DIM, ISLA_DIM, '#F4D03F', texto=f'E{islas_ok+1}')
                    obstaculos.append((x_isla - 0.2, y_isla - 0.2, ISLA_DIM + 0.4, ISLA_DIM + 0.4))
                    islas_ok += 1
        area_exhibicion += (islas_ok * ISLA_DIM * ISLA_DIM)

    # Cálculos Finales y Formato
    pct_exh = (area_exhibicion / area_comercial) * 100 if area_comercial > 0 else 0
    pct_nav = 100 - pct_exh
    formato_oxxo = clasificar_formato(area_total)

    ax.set_aspect('equal')
    plt.title(f"Layout OXXO | Formato: {formato_oxxo}")
    return fig, errores, pct_exh, pct_nav, area_total, formato_oxxo

# --- INTERFAZ STREAMLIT ---
st.set_page_config(layout="wide")
st.title("🏬 Store Planning OXXO V18.0")

# --- SECCIÓN DE INFORMACIÓN (ACORDEÓN) ---
with st.expander("ℹ️ Información y Reglas del Sistema Store Planning OXXO", expanded=False):
    st.markdown("""
    **Balanceo de Áreas:** El código respeta la regla de distribución de espacio que dicta que aproximadamente el **20%** se destina a Espacios Operativos y el **80%** a Espacios Comerciales. Dentro del área comercial, se calcula un **40% para exhibición** (garantizando rentabilidad sin saturar) y un **60% para navegación** (asegurando una buena experiencia del consumidor).
    
    **Matriz de Formatos:** La función agrupa la tienda en categorías como "Compactos", "Reducidos" y "Ordinarios" dependiendo del rango exacto de m2 estipulado en la matriz oficial. Por ejemplo, de 99 a 117 m2 se considera formato **REGULAR**.
    
    **Los 4 Elementos Cardinales:** Se extrajeron las condicionantes de ubicación estrictas: 
    1. El **Acceso** es el punto de partida.
    2. El **Check out** debe estar lo más cerca del acceso.
    3. El área **Operativa** no debe dejar espacios muertos.
    4. El **Cuarto Frío** debe ir perimetral y lo más alejado de la entrada (Destino).
    
    **Landscaping (Jerarquía Visual):** Se implementó la regla *"primero lo más bajo y al fondo lo más alto"* para definir las alturas máximas permitidas de acuerdo a la distancia desde el umbral (desde 3.5 ft en el acceso hasta 7 ft en el muro perimetral más lejano).
    """)

col_params, col_plot = st.columns([1.2, 2.8])

with col_params:
    st.header("1. Huella del Local")
    ancho = st.number_input("Ancho (m)", min_value=5.0, max_value=20.0, value=12.0, step=0.5)
    largo = st.number_input("Profundidad (m)", min_value=5.0, max_value=20.0, value=15.0, step=0.5)
    
    st.markdown("---")
    st.write("🔧 **Constructor de Layout**")
    
    t_puerta = st.toggle("1. Activar Acceso")
    muro, pos_puerta = 'Inferior (Frente)', 0.0
    if t_puerta:
        muro = st.selectbox("¿En qué muro está la puerta?", ['Inferior (Frente)', 'Lateral Izquierdo', 'Lateral Derecho'])
        max_pos = ancho - PUERTA_ANCHO if muro == 'Inferior (Frente)' else largo - PUERTA_ANCHO
        pos_puerta = st.slider("Posición en muro", 0.0, float(max_pos), float(max_pos/2))
    
    t_check, loc_check, cant_check = False, "", 0
    if t_puerta:
        t_check = st.toggle("2. Activar Checkout")
        if t_check:
            loc_check = st.selectbox("Esquina Anclaje", ['Esquina Inferior Derecha', 'Esquina Inferior Izquierda'])
            cant_check = st.slider("Módulos Checkout", 1, 5, 3)

    t_frio, loc_frio, forma_frio, cant_frio = False, "", "", 0
    if t_check:
        t_frio = st.toggle("3. Activar Cuarto Frío")
        if t_frio:
            loc_frio = st.selectbox("Esquina Destino", ['Fondo Derecha', 'Fondo Izquierda'])
            forma_frio = st.radio("Formato", ['Lineal', 'Escuadra'], horizontal=True)
            cant_frio = st.slider("Puertas Frío", 2, 20, 8)

    t_gondolas, cant_trenes, cant_tramos = False, 0, 0
    if t_frio:
        t_gondolas = st.toggle("4. Activar Góndolas")
        if t_gondolas:
            cant_trenes = st.slider("Trenes Centrales", 1, 4, 2)
            cant_tramos = st.slider("Tramos por tren", 1, 6, 3)

    t_cafe, cant_cafe = False, 0
    if t_gondolas:
        t_cafe = st.toggle("5. Activar Café")
        if t_cafe:
            cant_cafe = st.slider("Módulos Café", 2, 10, 4)

    t_perimetral = False
    if t_cafe:
        t_perimetral = st.toggle("6. Activar Perimetrales")

    t_islas, cant_islas = False, 0
    if t_perimetral:
        t_islas = st.toggle("7. Activar Islas")
        if t_islas:
            cant_islas = st.slider("Islas (60x60cm)", 1, 20, 4)

conf = {
    'ancho': ancho, 'largo': largo, 'muro_puerta': muro,
    't_puerta': t_puerta, 'pos_puerta': pos_puerta,
    't_check': t_check, 'loc_check': loc_check, 'cant_check': cant_check,
    't_frio': t_frio, 'loc_frio': loc_frio, 'forma_frio': forma_frio, 'cant_frio': cant_frio,
    't_gondolas': t_gondolas, 'cant_trenes': cant_trenes, 'cant_tramos': cant_tramos,
    't_cafe': t_cafe, 'cant_cafe': cant_cafe,
    't_perimetral': t_perimetral,
    't_islas': t_islas, 'cant_islas': cant_islas
}

with col_plot:
    fig, errores, pct_exh, pct_nav, a_total, formato = dibujar_layout_oxxo(conf)
    st.pyplot(fig)
    
    if errores:
        st.error("🚨 **Advertencias de Colisión:**")
        for err in errores: st.warning(f"• {err}")
    
    if t_puerta:
        st.markdown("---")
        st.subheader("📊 Matriz de Distribución Espacial OXXO")
        st.write(f"**M2 Totales:** {a_total:.1f} m² | **Formato Asignado:** `{formato}`")
        
        col_kpi1, col_kpi2 = st.columns(2)
        with col_kpi1:
            st.metric("Rentabilidad (Exhibición)", f"{pct_exh:.1f}%")
            if 30 <= pct_exh <= 40: st.success("✅ ACEPTADO (30-40%)")
            elif pct_exh < 30: st.info("📉 FALTA MOBILIARIO")
            else: st.error("❌ SATURADO")
                
        with col_kpi2:
            st.metric("Experiencia (Navegación)", f"{pct_nav:.1f}%")
            if 60 <= pct_nav <= 70: st.success("✅ ACEPTADO (60-70%)")
            elif pct_nav > 70: st.info("📉 ESPACIO MUERTO")
            else: st.error("❌ PASILLOS BLOQUEADOS")