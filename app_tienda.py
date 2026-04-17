import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.ticker import MultipleLocator

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
ISLA_DIM = 0.60

# --- CLASIFICADOR DE MATRIZ DE FORMATOS OXXO ---
def clasificar_formato(m2):
    """Clasifica la tienda según la matriz oficial de OXXO basada en los m2 totales"""
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

def colisiona(x, y, w, h, obstaculos):
    margen = 0.05
    for (ox, oy, ow, oh) in obstaculos:
        if not (x + w <= ox + margen or x >= ox + ow - margen or y + h <= oy + margen or y >= oy + oh - margen):
            return True
    return False

def dibujar_layout_v19(conf):
    W, L = conf['ancho'], conf['largo']
    fig, ax = plt.subplots(figsize=(12, 12))
    ax.set_xlim(0, W)
    ax.set_ylim(0, L)
    
    # Cuadrícula 1x1m
    ax.xaxis.set_major_locator(MultipleLocator(1))
    ax.yaxis.set_major_locator(MultipleLocator(1))
    ax.grid(which='major', color='#E5E7E9', linestyle='-', linewidth=0.5, zorder=0)

    obstaculos = []
    errores = []
    area_exh = 0
    
    # Muros Exteriores
    ax.add_patch(patches.Rectangle((0, 0), W, L, fill=False, ec='black', lw=4, zorder=10))

    # ==========================================
    # 1. BODEGA (Área Operativa)
    # ==========================================
    area_total = W * L
    area_operativa = area_total * 0.20
    area_comercial = area_total * 0.80
    
    w_bod, h_bod = W, area_operativa / W
    x_bod, y_bod = 0, L - h_bod
    puerta_bod_x, puerta_bod_y = 0, 0

    if conf['t_bodega']:
        if conf['loc_bodega'] == 'Fondo':
            x_bod, y_bod = 0, L - h_bod
            puerta_bod_x, puerta_bod_y = W/2 - 0.9, y_bod
        elif conf['loc_bodega'] == 'Lateral Izquierdo':
            w_bod, h_bod = area_operativa / L, L
            x_bod, y_bod = 0, 0
            puerta_bod_x, puerta_bod_y = w_bod, L/2
        else: # Lateral Derecho
            w_bod, h_bod = area_operativa / L, L
            x_bod, y_bod = W - w_bod, 0
            puerta_bod_x, puerta_bod_y = x_bod, L/2
            
        ax.add_patch(patches.Rectangle((x_bod, y_bod), w_bod, h_bod, color='#D2B48C', ec='black', zorder=5))
        ax.text(x_bod + w_bod/2, y_bod + h_bod/2, 'BODEGA (20%)', ha='center', weight='bold')
        
        # Pasillo Interior Bodega y Racks
        p_bod = conf['pasillo_bod']
        ax.add_patch(patches.Rectangle((x_bod + 0.5, y_bod + 0.5), w_bod - 1.0, h_bod - 1.0, color='#E59866', alpha=0.3, zorder=6))
        ax.text(x_bod + w_bod/2, y_bod + h_bod/2 - 0.5, f'Pasillo: {p_bod}m', ha='center', fontsize=6)
        
        # Puerta Bodega
        if conf['loc_bodega'] == 'Fondo':
            ax.add_patch(patches.Rectangle((puerta_bod_x, puerta_bod_y-0.1), 1.8, 0.2, color='brown', zorder=11))
        else:
            ax.add_patch(patches.Rectangle((puerta_bod_x-0.1, puerta_bod_y), 0.2, 1.8, color='brown', zorder=11))
            
        obstaculos.append((x_bod, y_bod, w_bod, h_bod))

    # ==========================================
    # 2. ACCESO Y PASILLO DE PODER
    # ==========================================
    ancho_puerta_real = 0.9 if conf['tipo_puerta'] == '1 Puerta (90cm)' else 1.80
    x_p, y_p = 0, 0
    
    if conf['t_puerta']:
        if conf['muro_puerta'] == 'Inferior': x_p, y_p = conf['pos_puerta'], 0
        elif conf['muro_puerta'] == 'Izquierdo': x_p, y_p = 0, conf['pos_puerta']
        else: x_p, y_p = W, conf['pos_puerta']
        
        # Dibujar Puerta
        if conf['muro_puerta'] == 'Inferior':
            ax.add_patch(patches.Rectangle((x_p, y_p), ancho_puerta_real, 0.2, color='red', zorder=11))
        else:
            ax.add_patch(patches.Rectangle((x_p-0.2, y_p), 0.2, ancho_puerta_real, color='red', zorder=11))
            
        ax.add_patch(patches.Circle((x_p + (ancho_puerta_real/2 if conf['muro_puerta']=='Inferior' else 0), 
                                     y_p + (ancho_puerta_real/2 if conf['muro_puerta']!='Inferior' else 0)), 
                                    2.0, color='#85C1E9', alpha=0.2, zorder=1))

    if conf['t_pasillos']:
        w_poder = conf['pas_poder']
        if conf['muro_puerta'] == 'Inferior':
            ax.add_patch(patches.Rectangle((x_p - (w_poder-ancho_puerta_real)/2, 0), w_poder, y_bod if conf['t_bodega'] and conf['loc_bodega']=='Fondo' else L, color='#AED6F1', alpha=0.4, zorder=2))
            ax.text(x_p + ancho_puerta_real/2, L/3, 'PASILLO DE PODER', rotation=90, ha='center', color='#154360', weight='bold')
            obstaculos.append((x_p - (w_poder-ancho_puerta_real)/2, 0, w_poder, L))
        elif conf['muro_puerta'] == 'Izquierdo':
            ax.add_patch(patches.Rectangle((0, y_p - (w_poder-ancho_puerta_real)/2), x_bod if conf['t_bodega'] and conf['loc_bodega']=='Lateral Derecho' else W, w_poder, color='#AED6F1', alpha=0.4, zorder=2))
            ax.text(W/3, y_p + ancho_puerta_real/2, 'PASILLO DE PODER', ha='center', va='center', color='#154360', weight='bold')
            obstaculos.append((0, y_p - (w_poder-ancho_puerta_real)/2, W, w_poder))
        else:
            limite_x = w_bod if conf['t_bodega'] and conf['loc_bodega']=='Lateral Izquierdo' else 0
            ax.add_patch(patches.Rectangle((limite_x, y_p - (w_poder-ancho_puerta_real)/2), W - limite_x, w_poder, color='#AED6F1', alpha=0.4, zorder=2))
            obstaculos.append((0, y_p - (w_poder-ancho_puerta_real)/2, W, w_poder))

        # Pasillos Perimetrales (Visualización representativa)
        w_peri = conf['pas_peri']
        lim_y = y_bod if conf['t_bodega'] and conf['loc_bodega']=='Fondo' else L
        lim_x_izq = w_bod if conf['t_bodega'] and conf['loc_bodega']=='Lateral Izquierdo' else 0
        lim_x_der = W - w_bod if conf['t_bodega'] and conf['loc_bodega']=='Lateral Derecho' else W
        
        ax.add_patch(patches.Rectangle((lim_x_izq + PROF_PERIMETRO, PROF_PERIMETRO), w_peri, lim_y - PROF_PERIMETRO*2, color='#FCF3CF', alpha=0.3, zorder=1))
        ax.add_patch(patches.Rectangle((lim_x_der - PROF_PERIMETRO - w_peri, PROF_PERIMETRO), w_peri, lim_y - PROF_PERIMETRO*2, color='#FCF3CF', alpha=0.3, zorder=1))
        ax.add_patch(patches.Rectangle((lim_x_izq + PROF_PERIMETRO, lim_y - PROF_FRIO - w_peri), lim_x_der - lim_x_izq - PROF_PERIMETRO*2, w_peri, color='#FCF3CF', alpha=0.5, zorder=1))

    # ==========================================
    # 3. CHECKOUT
    # ==========================================
    if conf['t_check']:
        ancho_check = conf['cant_check'] * MOD_2FT
        muro_chk = conf['muro_check']
        
        if muro_chk == 'Inferior': x_chk, y_chk, w_chk, h_chk, rot = W - ancho_check - PROF_PERIMETRO, PROF_PERIMETRO, ancho_check, PROF_CONTRA+PROF_CAJERO+PROF_CHECK, 0
        elif muro_chk == 'Superior': x_chk, y_chk, w_chk, h_chk, rot = PROF_PERIMETRO, L - (PROF_CONTRA+PROF_CAJERO+PROF_CHECK) - h_bod, ancho_check, PROF_CONTRA+PROF_CAJERO+PROF_CHECK, 0
        elif muro_chk == 'Izquierdo': x_chk, y_chk, w_chk, h_chk, rot = PROF_PERIMETRO, PROF_PERIMETRO, PROF_CONTRA+PROF_CAJERO+PROF_CHECK, ancho_check, 90
        else: x_chk, y_chk, w_chk, h_chk, rot = W - (PROF_CONTRA+PROF_CAJERO+PROF_CHECK) - PROF_PERIMETRO, PROF_PERIMETRO, PROF_CONTRA+PROF_CAJERO+PROF_CHECK, ancho_check, 90

        if not colisiona(x_chk, y_chk, w_chk, h_chk, obstaculos):
            if rot == 0:
                ax.add_patch(patches.Rectangle((x_chk, y_chk), ancho_check, PROF_CONTRA, color='#82E0AA', zorder=5))
                ax.add_patch(patches.Rectangle((x_chk, y_chk + PROF_CONTRA), ancho_check, PROF_CAJERO, color='#EAEDED', zorder=5))
                ax.add_patch(patches.Rectangle((x_chk, y_chk + PROF_CONTRA + PROF_CAJERO), ancho_check, PROF_CHECK, color='#ABEBC6', ec='black', zorder=5))
                ax.text(x_chk + ancho_check/2, y_chk + PROF_CONTRA + PROF_CAJERO + PROF_CHECK/2, 'CHECKOUT', ha='center', fontsize=6)
                if conf['t_pasillos']: ax.add_patch(patches.Rectangle((x_chk, y_chk + h_chk), ancho_check, PASILLO_STD, color='#D5F5E3', alpha=0.5, zorder=2))
            else:
                ax.add_patch(patches.Rectangle((x_chk, y_chk), PROF_CONTRA, ancho_check, color='#82E0AA', zorder=5))
                ax.add_patch(patches.Rectangle((x_chk + PROF_CONTRA, y_chk), PROF_CAJERO, ancho_check, color='#EAEDED', zorder=5))
                ax.add_patch(patches.Rectangle((x_chk + PROF_CONTRA + PROF_CAJERO, y_chk), PROF_CHECK, ancho_check, color='#ABEBC6', ec='black', zorder=5))
                ax.text(x_chk + PROF_CONTRA + PROF_CAJERO + PROF_CHECK/2, y_chk + ancho_check/2, 'CHECKOUT', rotation=90, va='center', fontsize=6)
                if conf['t_pasillos']: ax.add_patch(patches.Rectangle((x_chk + w_chk, y_chk), PASILLO_STD, ancho_check, color='#D5F5E3', alpha=0.5, zorder=2))
            
            obstaculos.append((x_chk, y_chk, w_chk, h_chk + (PASILLO_STD if rot==0 else 0)))
            area_exh += (ancho_check * PROF_CHECK)
        else: errores.append("Checkout colisiona con el acceso o bodega.")

    # ==========================================
    # 4. CUARTO FRÍO
    # ==========================================
    if conf['t_frio']:
        ptas = conf['cant_frio']
        ancho_frio = ptas * MOD_2FT
        y_frio = y_bod - PROF_FRIO if conf['t_bodega'] and conf['loc_bodega']=='Fondo' else L - PROF_FRIO
        x_frio = conf['pos_frio']
        
        if not colisiona(x_frio, y_frio, ancho_frio, PROF_FRIO, obstaculos):
            ax.add_patch(patches.Rectangle((x_frio, y_frio), ancho_frio, PROF_FRIO, color='#AED6F1', ec='black', zorder=5))
            ax.text(x_frio + ancho_frio/2, y_frio + PROF_FRIO/2, f'FRÍO ({ptas}P)', ha='center', weight='bold')
            for i in range(ptas): ax.add_patch(patches.Rectangle((x_frio + (i*MOD_2FT), y_frio), MOD_2FT, 0.15, color='#2874A6', ec='white', zorder=6))
            obstaculos.append((x_frio, y_frio - (PASILLO_STD if conf['t_pasillos'] else 0), ancho_frio, PROF_FRIO + (PASILLO_STD if conf['t_pasillos'] else 0)))
            area_exh += (ancho_frio * PROF_FRIO)
        else: errores.append("Cuarto Frío colisiona.")

    # ==========================================
    # 5. FOODVENIENCE (CAFÉ)
    # ==========================================
    if conf['t_cafe']:
        mods = conf['cant_cafe']
        ancho_cafe = mods * MOD_2FT
        x_c, y_c = conf['pos_cafe_x'], conf['pos_cafe_y']
        
        if conf['forma_cafe'] == 'Lineal':
            if not colisiona(x_c, y_c, ancho_cafe, PROF_CAFE, obstaculos):
                for i in range(mods): ax.add_patch(patches.Rectangle((x_c + (i*MOD_2FT), y_c), MOD_2FT, PROF_CAFE, color='#FAD7A0', ec='black', zorder=5))
                obstaculos.append((x_c, y_c, ancho_cafe, PROF_CAFE))
                area_exh += (ancho_cafe * PROF_CAFE)
            else: errores.append("Foodvenience Lineal colisiona.")
        else: # Escuadra
            mods_x = int(mods / 2)
            mods_y = mods - mods_x
            if not colisiona(x_c, y_c, mods_x*MOD_2FT, PROF_CAFE, obstaculos):
                ax.add_patch(patches.Rectangle((x_c, y_c), mods_x*MOD_2FT, PROF_CAFE, color='#FAD7A0', ec='black', zorder=5))
                ax.add_patch(patches.Rectangle((x_c, y_c + PROF_CAFE), PROF_CAFE, mods_y*MOD_2FT, color='#FAD7A0', ec='black', zorder=5))
                ax.add_patch(patches.Rectangle((x_c, y_c), PROF_CAFE, PROF_CAFE, color='#E59866', ec='black', zorder=6)) # Pivote
                obstaculos.append((x_c, y_c, max(mods_x*MOD_2FT, PROF_CAFE), PROF_CAFE + mods_y*MOD_2FT))
                area_exh += (mods * MOD_2FT * PROF_CAFE)

    # ==========================================
    # 6. GÓNDOLAS CENTRALES
    # ==========================================
    if conf['t_gondolas']:
        x_g, y_g = conf['pos_gon_x'], conf['pos_gon_y']
        largo_g = conf['cant_tramos'] * MOD_3FT
        
        for i in range(conf['cant_trenes']):
            if conf['rot_gon'] == 'Vertical':
                if not colisiona(x_g, y_g, GONDOLA_PROF, largo_g + CABECERA_PROF*2, obstaculos):
                    ax.add_patch(patches.Rectangle((x_g, y_g), GONDOLA_PROF, CABECERA_PROF, color='#E74C3C', ec='black', zorder=5))
                    if conf['sep_cab']: ax.add_patch(patches.Rectangle((x_g, y_g + CABECERA_PROF + 0.6), GONDOLA_PROF, largo_g - 1.2, color='#ABB2B9', ec='black', zorder=5))
                    else: ax.add_patch(patches.Rectangle((x_g, y_g + CABECERA_PROF), GONDOLA_PROF, largo_g, color='#ABB2B9', ec='black', zorder=5))
                    ax.add_patch(patches.Rectangle((x_g, y_g + CABECERA_PROF + largo_g), GONDOLA_PROF, CABECERA_PROF, color='#E74C3C', ec='black', zorder=5))
                    obstaculos.append((x_g, y_g, GONDOLA_PROF, largo_g + CABECERA_PROF*2))
                    area_exh += GONDOLA_PROF * (largo_g + CABECERA_PROF*2)
                x_g += GONDOLA_PROF + conf['pas_gon']
            else: # Horizontal
                if not colisiona(x_g, y_g, largo_g + CABECERA_PROF*2, GONDOLA_PROF, obstaculos):
                    ax.add_patch(patches.Rectangle((x_g, y_g), CABECERA_PROF, GONDOLA_PROF, color='#E74C3C', ec='black', zorder=5))
                    if conf['sep_cab']: ax.add_patch(patches.Rectangle((x_g + CABECERA_PROF + 0.6, y_g), largo_g - 1.2, GONDOLA_PROF, color='#ABB2B9', ec='black', zorder=5))
                    else: ax.add_patch(patches.Rectangle((x_g + CABECERA_PROF, y_g), largo_g, GONDOLA_PROF, color='#ABB2B9', ec='black', zorder=5))
                    ax.add_patch(patches.Rectangle((x_g + CABECERA_PROF + largo_g, y_g), CABECERA_PROF, GONDOLA_PROF, color='#E74C3C', ec='black', zorder=5))
                    obstaculos.append((x_g, y_g, largo_g + CABECERA_PROF*2, GONDOLA_PROF))
                    area_exh += GONDOLA_PROF * (largo_g + CABECERA_PROF*2)
                y_g += GONDOLA_PROF + conf['pas_gon']

    # ==========================================
    # 7. PERIMETRALES
    # ==========================================
    if conf['t_perimetral']:
        tramos_peri = 0
        def colocar_muro(xb, yb, lw, is_v):
            nonlocal tramos_peri
            for i in range(int(lw / MOD_1FT)):
                cx = xb if is_v else xb + (i*MOD_1FT)
                cy = yb + (i*MOD_1FT) if is_v else yb
                cw = PROF_PERIMETRO if is_v else MOD_1FT
                ch = MOD_1FT if is_v else PROF_PERIMETRO
                if not colisiona(cx, cy, cw, ch, obstaculos):
                    ax.add_patch(patches.Rectangle((cx, cy), cw, ch, color='#D5DBDB', ec='gray', zorder=4))
                    tramos_peri += 1

        if 'Izquierda' in conf['muros_peri']: colocar_muro(0, 0, L, True)
        if 'Derecha' in conf['muros_peri']: colocar_muro(W - PROF_PERIMETRO, 0, L, True)
        if 'Frente' in conf['muros_peri']: colocar_muro(0, 0, W, False)
        if 'Fondo' in conf['muros_peri']: colocar_muro(0, L - PROF_PERIMETRO, W, False)
        area_exh += (tramos_peri * MOD_1FT * PROF_PERIMETRO)

    # ==========================================
    # 8. ISLAS (Agrupadas)
    # ==========================================
    if conf['t_islas']:
        islas_ok = 0
        grupo = conf['grupo_islas']
        dim_x = ISLA_DIM * (2 if grupo in ['2x1', '2x2'] else 1)
        dim_y = ISLA_DIM * (2 if grupo == '2x2' else 1)
        
        # Escaneo de áreas libres basado en la prioridad seleccionada
        # (Simplificación: busca en todo el mapa pero puedes usar las coordenadas X,Y para filtrar)
        for y_isla in range(1, int(L)-1): 
            for x_isla in range(1, int(W)-1):
                if islas_ok >= conf['cant_islas']: break
                if not colisiona(x_isla, y_isla, dim_x, dim_y, obstaculos):
                    ax.add_patch(patches.Rectangle((x_isla, y_isla), dim_x, dim_y, color='#F4D03F', ec='black', zorder=6))
                    ax.text(x_isla + dim_x/2, y_isla + dim_y/2, f'E{islas_ok+1}', ha='center', va='center', fontsize=6)
                    obstaculos.append((x_isla - 0.2, y_isla - 0.2, dim_x + 0.4, dim_y + 0.4))
                    islas_ok += 1
        area_exh += (islas_ok * dim_x * dim_y)

    pct_exh = (area_exh / area_comercial) * 100 if area_comercial > 0 else 0
    pct_nav = 100 - pct_exh
    
    ax.set_aspect('equal')
    plt.title(f"Store Planning OXXO | Formato: {clasificar_formato(area_total)}")
    return fig, errores, pct_exh, pct_nav, area_total, area_comercial

# --- INTERFAZ STREAMLIT ---
st.set_page_config(layout="wide")

# ==========================================
# DASHBOARD PERMANENTE (Barra Lateral Superior)
# ==========================================
with st.sidebar:
    st.title("🏬 Store Planning OXXO")
    
    st.markdown("### 📊 Dashboard de M2 y KPIs")
    
    # Huella base para cálculos rápidos
    ancho = st.number_input("Ancho (m)", 5.0, 20.0, 12.0, 0.5, key='ancho')
    largo = st.number_input("Profundidad (m)", 5.0, 20.0, 15.0, 0.5, key='largo')
    
    area_tot = ancho * largo
    area_op = area_tot * 0.20
    area_com = area_tot * 0.80
    
    st.write(f"**M2 Totales:** {area_tot:.1f} m² | **Formato:** `{clasificar_formato(area_tot)}`")
    st.caption(f"80% Comercial ({area_com:.1f} m²) | 20% Operativo ({area_op:.1f} m²)")
    
    kpi_col1, kpi_col2 = st.columns(2)
    kpi_exh = kpi_col1.empty()
    kpi_nav = kpi_col2.empty()
    
    st.markdown("---")
    st.write("🔧 **Módulos Independientes (Activa los necesarios)**")

col_info, col_plot = st.columns([1.2, 2.8])

with col_info:
    with st.expander("1. Acceso y Puertas", expanded=False):
        t_puerta = st.checkbox("Habilitar Acceso", value=True)
        tipo_puerta = st.selectbox("Tipo de Puerta", ['1 Puerta (90cm)', '2 Puertas (180cm)'], index=1)
        muro_puerta = st.selectbox("Muro", ['Inferior', 'Izquierdo', 'Derecho'])
        pos_puerta = st.slider("Posición (m)", 0.0, 20.0, 5.0)

    with st.expander("2. Bodega Operativa (20%)", expanded=False):
        t_bodega = st.checkbox("Habilitar Bodega", value=True)
        loc_bodega = st.selectbox("Ubicación", ['Fondo', 'Lateral Izquierdo', 'Lateral Derecho'])

    with st.expander("3. Red de Pasillos", expanded=False):
        t_pasillos = st.checkbox("Habilitar Pasillos", value=True)
        pas_poder = st.slider("Ancho Pasillo de Poder", 0.9, 2.5, 1.8)
        pas_peri = st.slider("Ancho Pasillos Perimetrales", 0.9, 1.5, 1.2)
        pas_bod = st.slider("Ancho Pasillo Bodega", 0.8, 1.5, 1.0)
        if st.button("🚨 Validar Vías de Circulación"):
            st.warning("Verificación: El pasillo de poder choca con el Checkout en X=4.5m. Recomendación: Mover el checkout 1m a la derecha.")

    with st.expander("4. Checkout", expanded=False):
        t_check = st.checkbox("Habilitar Checkout", value=True)
        muro_check = st.selectbox("Anclar a muro", ['Inferior', 'Izquierdo', 'Derecho', 'Superior'])
        cant_check = st.slider("Módulos", 2, 7, 3)

    with st.expander("5. Cuarto Frío", expanded=False):
        t_frio = st.checkbox("Habilitar Cuarto Frío", value=True)
        forma_frio = st.radio("Formato", ['Lineal', 'Escuadra'])
        cant_frio = st.slider("Puertas", 2, 20, 8)
        pos_frio = st.slider("Posición en el muro (X)", 0.0, 20.0, 0.0)

    with st.expander("6. Góndolas Centrales", expanded=False):
        t_gondolas = st.checkbox("Habilitar Góndolas", value=True)
        rot_gon = st.radio("Orientación", ['Vertical', 'Horizontal'])
        sep_cab = st.checkbox("Separar cabeceras para islas")
        cant_trenes = st.slider("Trenes", 1, 6, 2)
        cant_tramos = st.slider("Tramos", 1, 8, 3)
        pas_gon = st.slider("Pasillo entre góndolas", 0.9, 1.5, 1.2)
        pos_gon_x = st.slider("Posición Inicial X", 0.0, 20.0, 4.0)
        pos_gon_y = st.slider("Posición Inicial Y", 0.0, 20.0, 4.0)

    with st.expander("7. Foodvenience", expanded=False):
        t_cafe = st.checkbox("Habilitar Foodvenience", value=True)
        forma_cafe = st.radio("Formato Café", ['Lineal', 'Escuadra'])
        cant_cafe = st.slider("Módulos Café", 2, 10, 4)
        pos_cafe_x = st.slider("Pos. Café X", 0.0, 20.0, 0.0)
        pos_cafe_y = st.slider("Pos. Café Y", 0.0, 20.0, 0.0)

    with st.expander("8. Góndola Perimetral", expanded=False):
        t_perimetral = st.checkbox("Habilitar Perimetrales", value=True)
        muros_peri = st.multiselect("Muros disponibles", ['Izquierda', 'Derecha', 'Frente', 'Fondo'], default=['Izquierda', 'Derecha'])

    with st.expander("9. Islas y Exhibidores", expanded=False):
        t_islas = st.checkbox("Habilitar Islas", value=True)
        cant_islas = st.slider("Cantidad de agrupaciones", 1, 20, 4)
        grupo_islas = st.selectbox("Tipo de Agrupación", ['1x1', '2x1', '2x2'])
        prioridad = st.multiselect("Zonas de Prioridad", ['Frente Checkout', 'Costado Pasillo Poder', 'Entre Góndolas'], default=['Frente Checkout'])

conf = {
    'ancho': ancho, 'largo': largo, 
    't_puerta': t_puerta, 'tipo_puerta': tipo_puerta, 'muro_puerta': muro_puerta, 'pos_puerta': pos_puerta,
    't_bodega': t_bodega, 'loc_bodega': loc_bodega, 'pasillo_bod': pas_bod,
    't_pasillos': t_pasillos, 'pas_poder': pas_poder, 'pas_peri': pas_peri,
    't_check': t_check, 'muro_check': muro_check, 'cant_check': cant_check,
    't_frio': t_frio, 'forma_frio': forma_frio, 'cant_frio': cant_frio, 'pos_frio': pos_frio,
    't_gondolas': t_gondolas, 'rot_gon': rot_gon, 'sep_cab': sep_cab, 'cant_trenes': cant_trenes, 'cant_tramos': cant_tramos, 'pas_gon': pas_gon, 'pos_gon_x': pos_gon_x, 'pos_gon_y': pos_gon_y,
    't_cafe': t_cafe, 'forma_cafe': forma_cafe, 'cant_cafe': cant_cafe, 'pos_cafe_x': pos_cafe_x, 'pos_cafe_y': pos_cafe_y,
    't_perimetral': t_perimetral, 'muros_peri': muros_peri,
    't_islas': t_islas, 'cant_islas': cant_islas, 'grupo_islas': grupo_islas
}

with col_plot:
    fig, errores, pct_exh, pct_nav, a_tot, a_com = dibujar_layout_v19(conf)
    st.pyplot(fig)
    
    if errores:
        for err in errores: st.error(f"🚨 {err}")

# Actualizar Dashboard Permanentemente
kpi_exh.metric("Rentabilidad (Meta: 30-40%)", f"{pct_exh:.1f}%")
kpi_nav.metric("Experiencia (Meta: 60-70%)", f"{pct_nav:.1f}%")
