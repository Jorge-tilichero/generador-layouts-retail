import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.ticker import MultipleLocator

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
ISLA_DIM = 0.60

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

def colisiona(x, y, w, h, obstaculos):
    margen = 0.05
    for (ox, oy, ow, oh, nombre) in obstaculos:
        if not (x + w <= ox + margen or x >= ox + ow - margen or y + h <= oy + margen or y >= oy + oh - margen):
            return True, nombre
    return False, ""

def dibujar_layout_oxxo_v20(conf):
    W, L = conf['ancho'], conf['largo']
    fig, ax = plt.subplots(figsize=(12, 12))
    ax.set_xlim(0, W)
    ax.set_ylim(0, L)
    
    # Cuadrícula 1x1m
    ax.xaxis.set_major_locator(MultipleLocator(1))
    ax.yaxis.set_major_locator(MultipleLocator(1))
    ax.grid(which='major', color='#E5E7E9', linestyle='-', linewidth=0.5, zorder=0)
    
    # Muros Exteriores
    ax.add_patch(patches.Rectangle((0, 0), W, L, fill=False, ec='black', lw=4, zorder=10))

    obstaculos = []
    errores = []
    area_exh = 0
    area_total = W * L
    area_operativa = area_total * 0.20
    area_comercial = area_total * 0.80

    def registrar_obj(x, y, w, h, color, texto="", rot=0, alpha=1.0, font=6, z=5, is_obs=True, name="Objeto", txt_col='black'):
        if rot == 90 or rot == 270: w, h = h, w
        
        # Validar colisión antes de dibujar si es un objeto físico
        if is_obs:
            choca, obj_chocado = colisiona(x, y, w, h, obstaculos)
            if choca: 
                errores.append(f"{name} colisiona con {obj_chocado}.")
                ec = 'red'
                lw = 2
            else:
                obstaculos.append((x, y, w, h, name))
                ec = 'black'
                lw = 1
        else:
            ec = 'none'
            lw = 0

        ax.add_patch(patches.Rectangle((x, y), w, h, color=color, ec=ec, lw=lw, alpha=alpha, zorder=z))
        if texto:
            ax.text(x + w/2, y + h/2, texto, ha='center', va='center', rotation=rot if rot in [90, 270] else 0, fontsize=font, color=txt_col)
        return w, h

    # ==========================================
    # 1. BODEGA OPERATIVA (20%)
    # ==========================================
    w_bod, h_bod = W, area_operativa / W
    x_bod, y_bod = 0, L - h_bod
    if conf['t_bodega']:
        loc_b = conf['loc_bodega']
        if loc_b == 'Fondo (Norte)': x_bod, y_bod = 0, L - h_bod
        elif loc_b == 'Frente (Sur)': x_bod, y_bod = 0, 0
        elif loc_b == 'Lateral Izq (Oeste)': w_bod, h_bod = area_operativa / L, L; x_bod, y_bod = 0, 0
        elif loc_b == 'Lateral Der (Este)': w_bod, h_bod = area_operativa / L, L; x_bod, y_bod = W - w_bod, 0
        
        registrar_obj(x_bod, y_bod, w_bod, h_bod, '#D2B48C', "BODEGA (20%)", font=8, name="Bodega")
        
        # Pasillo Interior y Racks (50cm)
        pb = conf['pas_bod']
        ax.add_patch(patches.Rectangle((x_bod + 0.5, y_bod + 0.5), w_bod - 1.0, h_bod - 1.0, color='#E59866', alpha=0.3, zorder=6))
        ax.text(x_bod + w_bod/2, y_bod + h_bod/2 - 0.5, f'Pasillo Bodega: {pb}m\nRacks 50cm', ha='center', fontsize=6)

    # ==========================================
    # 2. ACCESO Y PASILLO DE PODER
    # ==========================================
    if conf['t_puerta']:
        pw = 0.9 if conf['tipo_puerta'] == '1 Puerta (90cm)' else 1.80
        xp, yp = conf['pos_puerta_x'], conf['pos_puerta_y']
        registrar_obj(xp, yp, pw if conf['muro_puerta'] in ['Sur', 'Norte'] else 0.2, 0.2 if conf['muro_puerta'] in ['Sur', 'Norte'] else pw, 'red', "ACCESO", font=5, txt_col='white', name="Acceso", z=11)
        ax.add_patch(patches.Circle((xp + (pw/2 if conf['muro_puerta'] in ['Sur', 'Norte'] else 0), yp + (pw/2 if conf['muro_puerta'] in ['Este', 'Oeste'] else 0)), 2.0, color='#85C1E9', alpha=0.3, zorder=1))

        if conf['t_pasillos']:
            wpod = conf['pas_poder']
            if conf['muro_puerta'] == 'Sur':
                registrar_obj(xp - (wpod-pw)/2, yp, wpod, L if not conf['t_bodega'] or conf['loc_bodega'] != 'Fondo (Norte)' else y_bod, '#EBF5FB', "PASILLO DE PODER", rot=90, alpha=0.6, is_obs=False, txt_col='#154360')
                obstaculos.append((xp - (wpod-pw)/2, yp, wpod, L, "Pasillo de Poder"))
            elif conf['muro_puerta'] == 'Norte':
                registrar_obj(xp - (wpod-pw)/2, 0, wpod, yp, '#EBF5FB', "PASILLO DE PODER", rot=90, alpha=0.6, is_obs=False, txt_col='#154360')
                obstaculos.append((xp - (wpod-pw)/2, 0, wpod, yp, "Pasillo de Poder"))

    # ==========================================
    # 3. CHECKOUT (Joystick y Rotación)
    # ==========================================
    if conf['t_check']:
        mods_chk = conf['cant_check']
        xc, yc = conf['pos_chk_x'], conf['pos_chk_y']
        rot_c = conf['rot_check']
        w_chk = mods_chk * MOD_2FT
        
        if rot_c == 0: # Frente al Sur
            registrar_obj(xc, yc, w_chk, PROF_CONTRA, '#82E0AA', "C.CAJA", name="Contracaja")
            registrar_obj(xc, yc + PROF_CONTRA, w_chk, PROF_CAJERO, '#EAEDED', "P. CAJERO (1m)", name="Pasillo Cajero")
            for i in range(mods_chk): registrar_obj(xc + (i*MOD_2FT), yc + PROF_CONTRA + PROF_CAJERO, MOD_2FT, PROF_CHECK, '#ABEBC6', f"CHK{i+1}", font=5, name=f"Modulo CHK{i+1}")
            if conf['t_pasillos']: registrar_obj(xc, yc + PROF_CONTRA + PROF_CAJERO + PROF_CHECK, w_chk, PASILLO_STD, '#D5F5E3', "PASILLO COBRO", alpha=0.5, is_obs=True, name="Pasillo Cobro")
            area_exh += (w_chk * PROF_CHECK)
            
        elif rot_c == 90: # Frente al Este
            registrar_obj(xc, yc, PROF_CONTRA, w_chk, '#82E0AA', "C.CAJA", rot=90, name="Contracaja")
            registrar_obj(xc + PROF_CONTRA, yc, PROF_CAJERO, w_chk, '#EAEDED', "P. CAJERO", rot=90, name="Pasillo Cajero")
            for i in range(mods_chk): registrar_obj(xc + PROF_CONTRA + PROF_CAJERO, yc + (i*MOD_2FT), PROF_CHECK, MOD_2FT, '#ABEBC6', f"CHK{i+1}", font=5, rot=90, name=f"Modulo CHK{i+1}")
            if conf['t_pasillos']: registrar_obj(xc + PROF_CONTRA + PROF_CAJERO + PROF_CHECK, yc, PASILLO_STD, w_chk, '#D5F5E3', "PASILLO COBRO", rot=90, alpha=0.5, is_obs=True, name="Pasillo Cobro")
            area_exh += (w_chk * PROF_CHECK)
            
        elif rot_c == 180: # Frente al Norte
            if conf['t_pasillos']: registrar_obj(xc, yc, w_chk, PASILLO_STD, '#D5F5E3', "PASILLO COBRO", alpha=0.5, is_obs=True, name="Pasillo Cobro")
            for i in range(mods_chk): registrar_obj(xc + (i*MOD_2FT), yc + PASILLO_STD, MOD_2FT, PROF_CHECK, '#ABEBC6', f"CHK{i+1}", font=5, name=f"Modulo CHK{i+1}")
            registrar_obj(xc, yc + PASILLO_STD + PROF_CHECK, w_chk, PROF_CAJERO, '#EAEDED', "P. CAJERO (1m)", name="Pasillo Cajero")
            registrar_obj(xc, yc + PASILLO_STD + PROF_CHECK + PROF_CAJERO, w_chk, PROF_CONTRA, '#82E0AA', "C.CAJA", name="Contracaja")
            area_exh += (w_chk * PROF_CHECK)

    # ==========================================
    # 4. CUARTO FRÍO (Destino 7ft)
    # ==========================================
    if conf['t_frio']:
        xf, yf = conf['pos_frio_x'], conf['pos_frio_y']
        ptas = conf['cant_frio']
        wfrio = ptas * MOD_2FT
        
        if conf['forma_frio'] == 'Lineal':
            registrar_obj(xf, yf, wfrio, PROF_FRIO, '#AED6F1', "CUARTO FRÍO (7ft)", weight='bold', name="Cuarto Frio")
            for i in range(ptas): registrar_obj(xf + (i*MOD_2FT), yf, MOD_2FT, 0.15, '#2874A6', f"P{i+1}", rot=90, font=4, txt_col='white', name=f"Pta Frio {i+1}")
            if conf['t_pasillos']: registrar_obj(xf, yf - PASILLO_STD, wfrio, PASILLO_STD, '#FCF3CF', "PASILLO FRÍO", alpha=0.6, is_obs=True, name="Pasillo Frio", txt_col='#9A7D0A')
            area_exh += (wfrio * PROF_FRIO)
        else: # Escuadra
            pfondo = int(ptas * 0.6)
            plat = ptas - pfondo
            registrar_obj(xf, yf, pfondo*MOD_2FT, PROF_FRIO, '#AED6F1', "FRÍO FONDO", name="Frio Fondo")
            registrar_obj(xf, yf - (plat*MOD_2FT), PROF_FRIO, plat*MOD_2FT, '#AED6F1', "FRÍO LAT", rot=90, name="Frio Lat")
            area_exh += ((pfondo*MOD_2FT*PROF_FRIO) + (plat*MOD_2FT*PROF_FRIO))

    # ==========================================
    # 5. GÓNDOLAS CENTRALES (4ft - 5ft)
    # ==========================================
    if conf['t_gondolas']:
        xg, yg = conf['pos_gon_x'], conf['pos_gon_y']
        tramos = conf['cant_tramos']
        largo_g = tramos * MOD_3FT
        
        for i in range(conf['cant_trenes']):
            if conf['rot_gon'] == 'Vertical':
                registrar_obj(xg, yg, GONDOLA_PROF, CABECERA_PROF, '#E74C3C', "CAB", font=4, name=f"Cab Sur {i+1}")
                if conf['sep_cab']: registrar_obj(xg, yg + CABECERA_PROF + 0.6, GONDOLA_PROF, largo_g - 1.2, '#ABB2B9', "TRAMOS", name=f"Cuerpo {i+1}")
                else: 
                    for t in range(tramos): registrar_obj(xg, yg + CABECERA_PROF + (t*MOD_3FT), GONDOLA_PROF, MOD_3FT, '#ABB2B9', f"Tr{t+1}", font=5, name=f"Tr{t+1} Tren{i+1}")
                registrar_obj(xg, yg + CABECERA_PROF + largo_g, GONDOLA_PROF, CABECERA_PROF, '#E74C3C', "CAB", font=4, name=f"Cab Norte {i+1}")
                
                if conf['t_pasillos']: registrar_obj(xg + GONDOLA_PROF, yg, conf['pas_gon'], largo_g + CABECERA_PROF*2, '#EBEDEF', "PASILLO GONDOLAS", rot=90, alpha=0.6, is_obs=True, name=f"Pasillo Gon {i+1}")
                xg += GONDOLA_PROF + conf['pas_gon']
            else: # Horizontal
                registrar_obj(xg, yg, CABECERA_PROF, GONDOLA_PROF, '#E74C3C', "CAB", rot=90, font=4, name=f"Cab Oeste {i+1}")
                if conf['sep_cab']: registrar_obj(xg + CABECERA_PROF + 0.6, yg, largo_g - 1.2, GONDOLA_PROF, '#ABB2B9', "TRAMOS", rot=90, name=f"Cuerpo {i+1}")
                else:
                    for t in range(tramos): registrar_obj(xg + CABECERA_PROF + (t*MOD_3FT), yg, MOD_3FT, GONDOLA_PROF, '#ABB2B9', f"Tr{t+1}", rot=90, font=5, name=f"Tr{t+1} Tren{i+1}")
                registrar_obj(xg + CABECERA_PROF + largo_g, yg, CABECERA_PROF, GONDOLA_PROF, '#E74C3C', "CAB", rot=90, font=4, name=f"Cab Este {i+1}")
                
                if conf['t_pasillos']: registrar_obj(xg, yg + GONDOLA_PROF, largo_g + CABECERA_PROF*2, conf['pas_gon'], '#EBEDEF', "PASILLO GONDOLAS", alpha=0.6, is_obs=True, name=f"Pasillo Gon {i+1}")
                yg += GONDOLA_PROF + conf['pas_gon']
            area_exh += GONDOLA_PROF * (largo_g + CABECERA_PROF*2)

    # ==========================================
    # 6. FOODVENIENCE (CAFÉ)
    # ==========================================
    if conf['t_cafe']:
        x_c, y_c = conf['pos_cafe_x'], conf['pos_cafe_y']
        mods = conf['cant_cafe']
        if conf['forma_cafe'] == 'Lineal':
            for i in range(mods): registrar_obj(x_c + (i*MOD_2FT), y_c, MOD_2FT, PROF_CAFE, '#FAD7A0', f"C{i+1}", name=f"Cafe {i+1}")
            if conf['t_pasillos']: registrar_obj(x_c, y_c + PROF_CAFE, mods*MOD_2FT, PASILLO_STD, '#FADBD8', "PASILLO CAFE", alpha=0.5, is_obs=True, name="Pasillo Cafe", txt_col='#E74C3C')
            area_exh += (mods * MOD_2FT * PROF_CAFE)
        else: # Escuadra
            mods_x = int(mods / 2)
            mods_y = mods - mods_x
            registrar_obj(x_c, y_c, mods_x*MOD_2FT, PROF_CAFE, '#FAD7A0', "CAFE H", name="Cafe Horiz")
            registrar_obj(x_c, y_c + PROF_CAFE, PROF_CAFE, mods_y*MOD_2FT, '#FAD7A0', "CAFE V", rot=90, name="Cafe Vert")
            registrar_obj(x_c, y_c, PROF_CAFE, PROF_CAFE, '#E59866', "X", name="Cafe Pivote") # Pivote
            area_exh += (mods * MOD_2FT * PROF_CAFE)

    # ==========================================
    # 7. PERIMETRALES E ISLAS
    # ==========================================
    if conf['t_perimetral']:
        # Algoritmo de auto-relleno simplificado
        for y in range(int(L)):
            if not colisiona(0, y, PROF_PERIMETRO, MOD_1FT, obstaculos)[0]: registrar_obj(0, y, PROF_PERIMETRO, MOD_1FT, '#D5DBDB', "P", font=4, rot=90, name=f"Perim Izq {y}")
            if not colisiona(W - PROF_PERIMETRO, y, PROF_PERIMETRO, MOD_1FT, obstaculos)[0]: registrar_obj(W - PROF_PERIMETRO, y, PROF_PERIMETRO, MOD_1FT, '#D5DBDB', "P", font=4, rot=90, name=f"Perim Der {y}")

    if conf['t_islas']:
        islas_ok = 0
        gx = 2 if conf['grupo_islas'] in ['2x1', '2x2'] else 1
        gy = 2 if conf['grupo_islas'] == '2x2' else 1
        dim_x, dim_y = ISLA_DIM * gx, ISLA_DIM * gy
        
        for yi in range(1, int(L)-1):
            for xi in range(1, int(W)-1):
                if islas_ok >= conf['cant_islas']: break
                if not colisiona(xi, yi, dim_x, dim_y, obstaculos)[0]:
                    registrar_obj(xi, yi, dim_x, dim_y, '#F4D03F', f"ISLA {islas_ok+1}", font=5, name=f"Isla {islas_ok+1}")
                    islas_ok += 1
        area_exh += (islas_ok * dim_x * dim_y)

    pct_exh = (area_exh / area_comercial) * 100 if area_comercial > 0 else 0
    pct_nav = 100 - pct_exh
    
    ax.set_aspect('equal')
    plt.title(f"Store Planning OXXO V20.0 | Formato: {clasificar_formato(area_total)}")
    return fig, errores, pct_exh, pct_nav, area_total, area_comercial

# --- INTERFAZ STREAMLIT ---
st.set_page_config(layout="wide")

# --- DASHBOARD LATERAL ---
with st.sidebar:
    st.title("🏬 Store Planning OXXO V20")
    st.markdown("### 📊 Auditoría Oficial M2")
    
    ancho = st.number_input("Ancho (m)", 5.0, 20.0, 12.0, 0.5)
    largo = st.number_input("Profundidad (m)", 5.0, 20.0, 15.0, 0.5)
    
    a_tot = ancho * largo
    a_op = a_tot * 0.20
    a_com = a_tot * 0.80
    
    st.write(f"**Total:** {a_tot:.1f} m² | `{clasificar_formato(a_tot)}`")
    st.caption(f"80% Comercial ({a_com:.1f} m²) | 20% Operativo ({a_op:.1f} m²)")
    
    kpi_col1, kpi_col2 = st.columns(2)
    kpi_exh = kpi_col1.empty()
    kpi_nav = kpi_col2.empty()
    
    st.markdown("---")
    st.write("🕹️ **Panel de Control Paramétrico**")

col_controles, col_plot = st.columns([1.5, 2.5])

with col_controles:
    with st.expander("1. Acceso y Puertas", expanded=False):
        t_puerta = st.checkbox("Habilitar Acceso", value=True)
        tipo_puerta = st.selectbox("Tipo", ['1 Puerta (90cm)', '2 Puertas (180cm)'], index=1)
        muro_puerta = st.selectbox("Muro", ['Sur', 'Norte', 'Este', 'Oeste'])
        pos_puerta_x = st.number_input("Posición X", 0.0, float(ancho), 5.0, 0.1)
        pos_puerta_y = st.number_input("Posición Y (Si está en Este/Oeste)", 0.0, float(largo), 0.0, 0.1)

    with st.expander("2. Bodega Operativa (20%)", expanded=False):
        t_bodega = st.checkbox("Habilitar Bodega", value=True)
        loc_bodega = st.selectbox("Ubicación", ['Fondo (Norte)', 'Frente (Sur)', 'Lateral Izq (Oeste)', 'Lateral Der (Este)'])

    with st.expander("3. Red de Pasillos (Zonas Seguras)", expanded=False):
        t_pasillos = st.checkbox("Habilitar Pasillos", value=True)
        pas_poder = st.slider("Ancho Pasillo Poder", 0.9, 2.5, 1.8)
        pas_peri = st.slider("Ancho Pasillos Perimetrales", 0.9, 1.5, 1.2)
        pas_bod = st.slider("Ancho Pasillo Bodega", 0.8, 1.5, 1.0)
        if st.button("🚨 Validar Vías de Circulación"): st.warning("Motor de colisión activo: Verifique alertas en rojo bajo el plano.")

    with st.expander("4. Checkout (Control X/Y)", expanded=False):
        t_check = st.checkbox("Habilitar Checkout", value=True)
        cant_check = st.slider("Módulos", 2, 7, 3)
        rot_check = st.selectbox("Rotación (°)", [0, 90, 180, 270])
        pos_chk_x = st.number_input("Check Pos X", 0.0, float(ancho), ancho - (cant_check*MOD_2FT), 0.1)
        pos_chk_y = st.number_input("Check Pos Y", 0.0, float(largo), 0.0, 0.1)

    with st.expander("5. Cuarto Frío", expanded=False):
        t_frio = st.checkbox("Habilitar Cuarto Frío", value=True)
        forma_frio = st.radio("Formato Frío", ['Lineal', 'Escuadra'])
        cant_frio = st.slider("Puertas", 2, 20, 8)
        pos_frio_x = st.number_input("Frío Pos X", 0.0, float(ancho), 0.0, 0.1)
        pos_frio_y = st.number_input("Frío Pos Y", 0.0, float(largo), largo - PROF_FRIO, 0.1)

    with st.expander("6. Góndolas Centrales", expanded=False):
        t_gondolas = st.checkbox("Habilitar Góndolas", value=True)
        rot_gon = st.radio("Orientación", ['Vertical', 'Horizontal'])
        sep_cab = st.checkbox("Separar cabeceras (Dejar hueco)")
        cant_trenes = st.slider("Trenes", 1, 6, 2)
        cant_tramos = st.slider("Tramos", 1, 8, 3)
        pas_gon = st.slider("Pasillo entre góndolas", 0.9, 1.5, 1.2)
        pos_gon_x = st.number_input("Góndola Pos X", 0.0, float(ancho), 4.0, 0.1)
        pos_gon_y = st.number_input("Góndola Pos Y", 0.0, float(largo), 4.0, 0.1)

    with st.expander("7. Foodvenience", expanded=False):
        t_cafe = st.checkbox("Habilitar Foodvenience", value=True)
        forma_cafe = st.radio("Formato Café", ['Lineal', 'Escuadra'])
        cant_cafe = st.slider("Módulos Café", 2, 10, 4)
        pos_cafe_x = st.number_input("Café Pos X", 0.0, float(ancho), 0.0, 0.1)
        pos_cafe_y = st.number_input("Café Pos Y", 0.0, float(largo), 0.0, 0.1)

    with st.expander("8. Góndola Perimetral e Islas", expanded=False):
        t_perimetral = st.checkbox("Habilitar Perimetrales Auto", value=True)
        t_islas = st.checkbox("Habilitar Islas Auto", value=True)
        cant_islas = st.slider("Cantidad de agrupaciones", 1, 20, 4)
        grupo_islas = st.selectbox("Agrupación Islas", ['1x1', '2x1', '2x2'])

conf = {
    'ancho': ancho, 'largo': largo, 
    't_puerta': t_puerta, 'tipo_puerta': tipo_puerta, 'muro_puerta': muro_puerta, 'pos_puerta_x': pos_puerta_x, 'pos_puerta_y': pos_puerta_y,
    't_bodega': t_bodega, 'loc_bodega': loc_bodega, 'pas_bod': pas_bod,
    't_pasillos': t_pasillos, 'pas_poder': pas_poder, 'pas_peri': pas_peri,
    't_check': t_check, 'rot_check': rot_check, 'cant_check': cant_check, 'pos_chk_x': pos_chk_x, 'pos_chk_y': pos_chk_y,
    't_frio': t_frio, 'forma_frio': forma_frio, 'cant_frio': cant_frio, 'pos_frio_x': pos_frio_x, 'pos_frio_y': pos_frio_y,
    't_gondolas': t_gondolas, 'rot_gon': rot_gon, 'sep_cab': sep_cab, 'cant_trenes': cant_trenes, 'cant_tramos': cant_tramos, 'pas_gon': pas_gon, 'pos_gon_x': pos_gon_x, 'pos_gon_y': pos_gon_y,
    't_cafe': t_cafe, 'forma_cafe': forma_cafe, 'cant_cafe': cant_cafe, 'pos_cafe_x': pos_cafe_x, 'pos_cafe_y': pos_cafe_y,
    't_perimetral': t_perimetral, 't_islas': t_islas, 'cant_islas': cant_islas, 'grupo_islas': grupo_islas
}

with col_plot:
    fig, errores, pct_exh, pct_nav, a_tot, a_com = dibujar_layout_oxxo_v20(conf)
    st.pyplot(fig)
    
    if errores:
        st.error("🚨 **Motor de Colisiones Activo:**")
        for err in errores: st.warning(f"• {err}")

# Update Dashboard KPIs
kpi_exh.metric("Rentabilidad (30-40%)", f"{pct_exh:.1f}%", "Aceptado" if 30 <= pct_exh <= 40 else "Revisar")
kpi_nav.metric("Experiencia (60-70%)", f"{pct_nav:.1f}%", "Aceptado" if 60 <= pct_nav <= 70 else "Revisar")