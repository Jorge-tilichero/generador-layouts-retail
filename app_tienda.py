import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.ticker import MultipleLocator
import io

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

def colisiona(x, y, w, h, lista_obstaculos):
    margen = 0.05
    for (ox, oy, ow, oh, nombre) in lista_obstaculos:
        if not (x + w <= ox + margen or x >= ox + ow - margen or y + h <= oy + margen or y >= oy + oh - margen):
            return True, nombre
    return False, ""

def normalizar_rotacion(r):
    r = r % 360
    if 90 < r < 270: r -= 180
    return r

# --- MOTOR DE TRANSFORMACIÓN ESPACIAL ---
def obtener_transformacion(muro, ancho_orig, largo_orig):
    def transform(x, y, w, h, rot_texto=0):
        if muro == 'Inferior (Frente)': return x, y, w, h, rot_texto
        elif muro == 'Lateral Izquierdo': return y, x, h, w, rot_texto - 90
        elif muro == 'Lateral Derecho': return ancho_orig - y - h, x, h, w, rot_texto + 90
    return transform

def dibujar_layout_oxxo_v22(conf):
    W, L = conf['ancho'], conf['largo']

    fig, ax = plt.subplots(figsize=(12, 12))
    ax.set_xlim(0, W)
    ax.set_ylim(0, L)
    
    # Cuadrícula 1x1m
    ax.xaxis.set_major_locator(MultipleLocator(1))
    ax.yaxis.set_major_locator(MultipleLocator(1))
    ax.grid(which='major', color='#E5E7E9', linestyle='-', linewidth=0.5, zorder=0)

    # DOBLE CAPA DE COLISIÓN
    obs_fisicos = []  
    obs_pasillos = [] 
    errores = []
    area_exh = 0
    
    def registrar_obj(x, y, w, h, color, texto="", rot=0, alpha=1.0, font=6, z=5, tipo="Fisico", name="Objeto", txt_col='black', weight='normal'):
        if rot in [90, 270, -90]: w, h = h, w
        
        choca = False
        obj_chocado = ""
        
        if tipo == "Fisico":
            c1, n1 = colisiona(x, y, w, h, obs_fisicos)
            c2, n2 = colisiona(x, y, w, h, obs_pasillos)
            if c1: choca, obj_chocado = True, n1
            elif c2: choca, obj_chocado = True, n2
        elif tipo == "Pasillo":
            choca, obj_chocado = colisiona(x, y, w, h, obs_fisicos)

        if choca: 
            errores.append(f"{name} colisiona o bloquea a {obj_chocado}.")
            ec, lw = 'red', 2
        else:
            if tipo == "Fisico": obs_fisicos.append((x, y, w, h, name))
            elif tipo == "Pasillo": obs_pasillos.append((x, y, w, h, name))
            ec, lw = ('black', 1) if tipo == "Fisico" else ('none', 0)

        ax.add_patch(patches.Rectangle((x, y), w, h, color=color, ec=ec, lw=lw, alpha=alpha, zorder=z))
        if texto:
            ax.text(x + w/2, y + h/2, texto, ha='center', va='center', rotation=normalizar_rotacion(rot), fontsize=font, color=txt_col, weight=weight, zorder=10)
        return w, h

    # Lienzo Base
    ax.add_patch(patches.Rectangle((0, 0), W, L, fill=False, ec='black', lw=4, zorder=10))
    area_total = W * L

    # ==========================================
    # 1. BODEGA PARAMÉTRICA
    # ==========================================
    a_op = 0
    if conf['t_bodega']:
        w_b, h_b = conf['w_bodega'], conf['h_bodega']
        xb, yb = conf['x_bodega'], conf['y_bodega']
        a_op = w_b * h_b
        
        registrar_obj(xb, yb, w_b, h_b, '#D2B48C', f"BODEGA ({a_op:.1f} m²)", font=8, weight='bold', name="Bodega")
        
        pb = conf['pas_bod']
        registrar_obj(xb + 0.5, yb + 0.5, w_b - 1.0, h_b - 1.0, '#E59866', f"Pasillo Bodega {pb}m\nRacks 50cm", alpha=0.3, tipo="Pasillo", txt_col='white', name="Interior Bodega")
        
        pos_pb = conf['pos_puerta_bod']
        muro_pb = conf['muro_puerta_bod']
        if muro_pb == 'Sur': registrar_obj(xb + pos_pb, yb, 0.9, 0.2, 'brown', name="Pta Bodega")
        elif muro_pb == 'Norte': registrar_obj(xb + pos_pb, yb + h_b - 0.2, 0.9, 0.2, 'brown', name="Pta Bodega")
        elif muro_pb == 'Oeste': registrar_obj(xb, yb + pos_pb, 0.2, 0.9, 'brown', name="Pta Bodega")
        elif muro_pb == 'Este': registrar_obj(xb + w_b - 0.2, yb + pos_pb, 0.2, 0.9, 'brown', name="Pta Bodega")

    area_comercial = area_total - a_op

    # ==========================================
    # 2. ACCESO Y PASILLO DE PODER
    # ==========================================
    if conf['t_puerta']:
        pw = 0.9 if conf['tipo_puerta'] == '1 Puerta (90cm)' else 1.80
        xp, yp = conf['pos_puerta_x'], conf['pos_puerta_y']
        
        w_puerta = pw if conf['muro_puerta'] in ['Sur', 'Norte'] else 0.2
        h_puerta = 0.2 if conf['muro_puerta'] in ['Sur', 'Norte'] else pw
        registrar_obj(xp, yp, w_puerta, h_puerta, 'red', "ACCESO", font=5, txt_col='white', weight='bold', name="Acceso", z=11)
        
        ax.add_patch(patches.Circle((xp + w_puerta/2, yp + h_puerta/2), 2.0, color='#85C1E9', alpha=0.2, zorder=1))

        if conf['t_pasillos']:
            wpod = conf['pas_poder']
            if conf['muro_puerta'] == 'Sur':
                registrar_obj(xp - (wpod-pw)/2, yp, wpod, L - yp, '#EBF5FB', "PASILLO DE PODER", rot=90, alpha=0.6, tipo="Pasillo", txt_col='#154360', weight='bold', name="Pasillo de Poder")
            elif conf['muro_puerta'] == 'Norte':
                registrar_obj(xp - (wpod-pw)/2, 0, wpod, yp, '#EBF5FB', "PASILLO DE PODER", rot=90, alpha=0.6, tipo="Pasillo", txt_col='#154360', weight='bold', name="Pasillo de Poder")
            elif conf['muro_puerta'] == 'Este':
                registrar_obj(0, yp - (wpod-pw)/2, xp, wpod, '#EBF5FB', "PASILLO DE PODER", alpha=0.6, tipo="Pasillo", txt_col='#154360', weight='bold', name="Pasillo de Poder")
            elif conf['muro_puerta'] == 'Oeste':
                registrar_obj(xp, yp - (wpod-pw)/2, W - xp, wpod, '#EBF5FB', "PASILLO DE PODER", alpha=0.6, tipo="Pasillo", txt_col='#154360', weight='bold', name="Pasillo de Poder")

    # ==========================================
    # 3. CHECKOUT
    # ==========================================
    if conf['t_check']:
        mods_chk = conf['cant_check']
        xc, yc = conf['pos_chk_x'], conf['pos_chk_y']
        rot_c = conf['rot_check']
        w_chk = mods_chk * MOD_2FT
        
        if rot_c == 0: 
            registrar_obj(xc, yc, w_chk, PROF_CONTRA, '#82E0AA', "C.CAJA", name="Contracaja")
            registrar_obj(xc, yc + PROF_CONTRA, w_chk, PROF_CAJERO, '#EAEDED', "P. CAJERO", tipo="Pasillo", name="Pasillo Cajero")
            for i in range(mods_chk): registrar_obj(xc + (i*MOD_2FT), yc + PROF_CONTRA + PROF_CAJERO, MOD_2FT, PROF_CHECK, '#ABEBC6', f"CHK{i+1}", font=5, name=f"CHK{i+1}")
            if conf['t_pasillos']: registrar_obj(xc, yc + PROF_CONTRA + PROF_CAJERO + PROF_CHECK, w_chk, PASILLO_STD, '#D5F5E3', "PASILLO COBRO", alpha=0.5, tipo="Pasillo", name="Pasillo Cobro")
            area_exh += (w_chk * PROF_CHECK)
            
        elif rot_c == 90: 
            registrar_obj(xc, yc, PROF_CONTRA, w_chk, '#82E0AA', "C.CAJA", rot=90, name="Contracaja")
            registrar_obj(xc + PROF_CONTRA, yc, PROF_CAJERO, w_chk, '#EAEDED', "P. CAJERO", rot=90, tipo="Pasillo", name="Pasillo Cajero")
            for i in range(mods_chk): registrar_obj(xc + PROF_CONTRA + PROF_CAJERO, yc + (i*MOD_2FT), PROF_CHECK, MOD_2FT, '#ABEBC6', f"CHK{i+1}", font=5, rot=90, name=f"CHK{i+1}")
            if conf['t_pasillos']: registrar_obj(xc + PROF_CONTRA + PROF_CAJERO + PROF_CHECK, yc, PASILLO_STD, w_chk, '#D5F5E3', "PASILLO COBRO", rot=90, alpha=0.5, tipo="Pasillo", name="Pasillo Cobro")
            area_exh += (w_chk * PROF_CHECK)
            
        elif rot_c == 180: 
            if conf['t_pasillos']: registrar_obj(xc, yc, w_chk, PASILLO_STD, '#D5F5E3', "PASILLO COBRO", alpha=0.5, tipo="Pasillo", name="Pasillo Cobro")
            for i in range(mods_chk): registrar_obj(xc + (i*MOD_2FT), yc + PASILLO_STD, MOD_2FT, PROF_CHECK, '#ABEBC6', f"CHK{i+1}", font=5, name=f"CHK{i+1}")
            registrar_obj(xc, yc + PASILLO_STD + PROF_CHECK, w_chk, PROF_CAJERO, '#EAEDED', "P. CAJERO", tipo="Pasillo", name="Pasillo Cajero")
            registrar_obj(xc, yc + PASILLO_STD + PROF_CHECK + PROF_CAJERO, w_chk, PROF_CONTRA, '#82E0AA', "C.CAJA", name="Contracaja")
            area_exh += (w_chk * PROF_CHECK)
            
        elif rot_c == 270: 
            if conf['t_pasillos']: registrar_obj(xc, yc, PASILLO_STD, w_chk, '#D5F5E3', "PASILLO COBRO", rot=90, alpha=0.5, tipo="Pasillo", name="Pasillo Cobro")
            for i in range(mods_chk): registrar_obj(xc + PASILLO_STD, yc + (i*MOD_2FT), PROF_CHECK, MOD_2FT, '#ABEBC6', f"CHK{i+1}", font=5, rot=90, name=f"CHK{i+1}")
            registrar_obj(xc + PASILLO_STD + PROF_CHECK, yc, PROF_CAJERO, w_chk, '#EAEDED', "P. CAJERO", rot=90, tipo="Pasillo", name="Pasillo Cajero")
            registrar_obj(xc + PASILLO_STD + PROF_CHECK + PROF_CAJERO, yc, PROF_CONTRA, w_chk, '#82E0AA', "C.CAJA", rot=90, name="Contracaja")
            area_exh += (w_chk * PROF_CHECK)

    # ==========================================
    # 4. CUARTO FRÍO
    # ==========================================
    if conf['t_frio']:
        xf, yf = conf['pos_frio_x'], conf['pos_frio_y']
        rot_f = conf['rot_frio']
        
        if conf['forma_frio'] == 'Lineal':
            wf = conf['cant_frio'] * MOD_2FT
            if rot_f in [0, 180]:
                registrar_obj(xf, yf, wf, PROF_FRIO, '#AED6F1', "CUARTO FRÍO", weight='bold', name="Frio")
                if conf['t_pasillos']: registrar_obj(xf, yf - PASILLO_STD if rot_f==0 else yf + PROF_FRIO, wf, PASILLO_STD, '#FCF3CF', "PASILLO FRÍO", alpha=0.6, tipo="Pasillo", name="Pasillo Frio", txt_col='#9A7D0A')
            else:
                registrar_obj(xf, yf, PROF_FRIO, wf, '#AED6F1', "CUARTO FRÍO", rot=90, weight='bold', name="Frio")
                if conf['t_pasillos']: registrar_obj(xf - PASILLO_STD if rot_f==90 else xf + PROF_FRIO, yf, PASILLO_STD, wf, '#FCF3CF', "PASILLO FRÍO", rot=90, alpha=0.6, tipo="Pasillo", name="Pasillo Frio", txt_col='#9A7D0A')
            area_exh += (wf * PROF_FRIO)
            
        else: # Escuadra
            w1, w2 = conf['ptas_frio_1'] * MOD_2FT, conf['ptas_frio_2'] * MOD_2FT
            if rot_f == 0: 
                registrar_obj(xf, yf, w1, PROF_FRIO, '#AED6F1', "FRIO L1", name="Frio 1")
                registrar_obj(xf, yf + PROF_FRIO, PROF_FRIO, w2, '#AED6F1', "FRIO L2", rot=90, name="Frio 2")
            elif rot_f == 90:
                registrar_obj(xf, yf, PROF_FRIO, w1, '#AED6F1', "FRIO L1", rot=90, name="Frio 1")
                registrar_obj(xf + PROF_FRIO, yf, w2, PROF_FRIO, '#AED6F1', "FRIO L2", name="Frio 2")
            elif rot_f == 180:
                registrar_obj(xf, yf, w1, PROF_FRIO, '#AED6F1', "FRIO L1", name="Frio 1")
                registrar_obj(xf + w1 - PROF_FRIO, yf - w2, PROF_FRIO, w2, '#AED6F1', "FRIO L2", rot=90, name="Frio 2")
            elif rot_f == 270:
                registrar_obj(xf, yf, PROF_FRIO, w1, '#AED6F1', "FRIO L1", rot=90, name="Frio 1")
                registrar_obj(xf - w2, yf + w1 - PROF_FRIO, w2, PROF_FRIO, '#AED6F1', "FRIO L2", name="Frio 2")
            area_exh += ((w1 * PROF_FRIO) + (w2 * PROF_FRIO))

    # ==========================================
    # 5. FOODVENIENCE
    # ==========================================
    if conf['t_cafe']:
        x_c, y_c = conf['pos_cafe_x'], conf['pos_cafe_y']
        mods = conf['cant_cafe']
        if conf['forma_cafe'] == 'Lineal':
            for i in range(mods): registrar_obj(x_c + (i*MOD_2FT), y_c, MOD_2FT, PROF_CAFE, '#FAD7A0', f"C{i+1}", name=f"Cafe {i+1}")
            if conf['t_pasillos']: registrar_obj(x_c, y_c + PROF_CAFE, mods*MOD_2FT, PASILLO_STD, '#FADBD8', "PASILLO CAFE", alpha=0.5, tipo="Pasillo", name="Pasillo Cafe", txt_col='#E74C3C')
            area_exh += (mods * MOD_2FT * PROF_CAFE)
        else: # Escuadra
            mods_x, mods_y = int(mods / 2), mods - int(mods/2)
            registrar_obj(x_c, y_c, mods_x*MOD_2FT, PROF_CAFE, '#FAD7A0', "CAFE H", name="Cafe Horiz")
            registrar_obj(x_c, y_c + PROF_CAFE, PROF_CAFE, mods_y*MOD_2FT, '#FAD7A0', "CAFE V", rot=90, name="Cafe Vert")
            registrar_obj(x_c, y_c, PROF_CAFE, PROF_CAFE, '#E59866', "X", name="Cafe Pivote")
            area_exh += (mods * MOD_2FT * PROF_CAFE)

    # ==========================================
    # 6. PERIMETRALES
    # ==========================================
    if conf['t_perimetral']:
        w_peri = conf['pas_peri']
        if conf['peri_izq']: 
            for i in range(conf['tramos_izq']): registrar_obj(0, conf['pos_izq_y'] + (i*MOD_1FT), PROF_PERIMETRO, MOD_1FT, '#D5DBDB', "P", rot=90, font=4, name=f"PIzq{i}")
            if conf['t_pasillos']: registrar_obj(PROF_PERIMETRO, 0, w_peri, L, '#FCF3CF', "PASILLO PERIMETRAL", rot=90, alpha=0.3, tipo="Pasillo", name="Pas Peri Izq")
            area_exh += (conf['tramos_izq'] * MOD_1FT * PROF_PERIMETRO)
            
        if conf['peri_der']: 
            for i in range(conf['tramos_der']): registrar_obj(W - PROF_PERIMETRO, conf['pos_der_y'] + (i*MOD_1FT), PROF_PERIMETRO, MOD_1FT, '#D5DBDB', "P", rot=90, font=4, name=f"PDer{i}")
            if conf['t_pasillos']: registrar_obj(W - PROF_PERIMETRO - w_peri, 0, w_peri, L, '#FCF3CF', "PASILLO PERIMETRAL", rot=90, alpha=0.3, tipo="Pasillo", name="Pas Peri Der")
            area_exh += (conf['tramos_der'] * MOD_1FT * PROF_PERIMETRO)
            
        if conf['peri_frente']: 
            for i in range(conf['tramos_frente']): registrar_obj(conf['pos_fre_x'] + (i*MOD_1FT), 0, MOD_1FT, PROF_PERIMETRO, '#D5DBDB', "P", font=4, name=f"PFre{i}")
            if conf['t_pasillos']: registrar_obj(0, PROF_PERIMETRO, W, w_peri, '#FCF3CF', "PASILLO PERIMETRAL", alpha=0.3, tipo="Pasillo", name="Pas Peri Fre")
            area_exh += (conf['tramos_frente'] * MOD_1FT * PROF_PERIMETRO)
            
        if conf['peri_fondo']: 
            for i in range(conf['tramos_fondo']): registrar_obj(conf['pos_fon_x'] + (i*MOD_1FT), L - PROF_PERIMETRO, MOD_1FT, PROF_PERIMETRO, '#D5DBDB', "P", font=4, name=f"PFon{i}")
            if conf['t_pasillos']: registrar_obj(0, L - PROF_PERIMETRO - w_peri, W, w_peri, '#FCF3CF', "PASILLO PERIMETRAL", alpha=0.3, tipo="Pasillo", name="Pas Peri Fon")
            area_exh += (conf['tramos_fondo'] * MOD_1FT * PROF_PERIMETRO)

    # ==========================================
    # 7. GÓNDOLAS CENTRALES
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
                
                if conf['t_pasillos']: registrar_obj(xg + GONDOLA_PROF, yg, conf['pas_gon'], largo_g + CABECERA_PROF*2, '#EBEDEF', "P. GÓNDOLAS", rot=90, alpha=0.6, tipo="Pasillo", name=f"Pasillo Gon {i+1}")
                xg += GONDOLA_PROF + conf['pas_gon']
            else: 
                registrar_obj(xg, yg, CABECERA_PROF, GONDOLA_PROF, '#E74C3C', "CAB", rot=90, font=4, name=f"Cab Oeste {i+1}")
                if conf['sep_cab']: registrar_obj(xg + CABECERA_PROF + 0.6, yg, largo_g - 1.2, GONDOLA_PROF, '#ABB2B9', "TRAMOS", rot=90, name=f"Cuerpo {i+1}")
                else:
                    for t in range(tramos): registrar_obj(xg + CABECERA_PROF + (t*MOD_3FT), yg, MOD_3FT, GONDOLA_PROF, '#ABB2B9', f"Tr{t+1}", rot=90, font=5, name=f"Tr{t+1} Tren{i+1}")
                registrar_obj(xg + CABECERA_PROF + largo_g, yg, CABECERA_PROF, GONDOLA_PROF, '#E74C3C', "CAB", rot=90, font=4, name=f"Cab Este {i+1}")
                
                if conf['t_pasillos']: registrar_obj(xg, yg + GONDOLA_PROF, largo_g + CABECERA_PROF*2, conf['pas_gon'], '#EBEDEF', "P. GÓNDOLAS", alpha=0.6, tipo="Pasillo", name=f"Pasillo Gon {i+1}")
                yg += GONDOLA_PROF + conf['pas_gon']
            area_exh += GONDOLA_PROF * (largo_g + CABECERA_PROF*2)

    # ==========================================
    # 8. ISLAS INDIVIDUALES
    # ==========================================
    if conf['t_islas']:
        for i in range(conf['cant_islas']):
            ix, iy = conf[f'isla_x_{i}'], conf[f'isla_y_{i}']
            registrar_obj(ix, iy, ISLA_DIM, ISLA_DIM, '#F4D03F', f"E{i+1}", font=6, name=f"Isla {i+1}")
            area_exh += (ISLA_DIM * ISLA_DIM)

    pct_exh = (area_exh / area_comercial) * 100 if area_comercial > 0 else 0
    pct_nav = 100 - pct_exh
    
    ax.set_aspect('equal')
    plt.title(f"Store Planning OXXO: {conf['nombre_tienda']} | Formato: {clasificar_formato(area_total)}")
    return fig, errores, pct_exh, pct_nav, area_total, area_comercial, a_op

# --- INTERFAZ STREAMLIT ---
st.set_page_config(layout="wide", page_title="Store Planning OXXO")

# Inicialización de configuración
conf = {}

with st.sidebar:
    st.title("🏬 Store Planning OXXO")
    
    nombre_tienda = st.text_input("Nombre de la Tienda", "OXXO Nueva Creación")
    
    st.markdown("### 📊 Auditoría Oficial M2")
    
    ancho = st.number_input("Ancho (m)", 5.0, 20.0, 12.0, 0.5)
    largo = st.number_input("Profundidad (m)", 5.0, 20.0, 15.0, 0.5)
    
    area_tot = ancho * largo
    st.write(f"**Total:** {area_tot:.1f} m² | `{clasificar_formato(area_tot)}`")
    
    kpi_bod = st.empty()
    kpi_exh = st.empty()
    kpi_nav = st.empty()
    
    st.markdown("---")
    st.write("🕹️ **Panel de Control Paramétrico**")
    st.caption("Activa y posiciona el mobiliario desde cero.")

col_info, col_plot = st.columns([1.5, 2.5])

with col_info:
    with st.expander("ℹ️ Lineamientos Store Planning OXXO", expanded=False):
        st.markdown("""
        **Balanceo de Áreas:** 20% Operativos y 80% Comerciales. Dentro del comercial: 40% exhibición, 60% navegación.
        **Matriz de Formatos:** Clasificación automática de acuerdo al librito oficial (Ej. REGULAR, MEDIA).
        **Blindaje de Pasillos:** Los pasillos de circulación pueden cruzarse entre sí (no generan colisión), pero actúan como barrera para evitar que coloques un mueble encima de ellos.
        """)

    with st.expander("1. Acceso y Puertas", expanded=False):
        t_puerta = st.checkbox("Habilitar Acceso", value=False)
        tipo_puerta = st.selectbox("Tipo", ['1 Puerta (90cm)', '2 Puertas (180cm)'], index=1)
        muro_puerta = st.selectbox("Muro", ['Sur', 'Norte', 'Este', 'Oeste'])
        pos_puerta_x = st.number_input("Posición X", 0.0, float(ancho), 5.0, 0.1)
        pos_puerta_y = st.number_input("Posición Y (Si Este/Oeste)", 0.0, float(largo), 0.0, 0.1)

    with st.expander("2. Bodega Operativa", expanded=False):
        t_bodega = st.checkbox("Habilitar Bodega", value=False)
        loc_bodega = st.selectbox("Ubicación", ['Fondo (Norte)', 'Frente (Sur)', 'Lateral Izq (Oeste)', 'Lateral Der (Este)'])
        col_bx, col_by = st.columns(2)
        x_bodega = col_bx.number_input("Posición Bodega X", 0.0, 20.0, 0.0, 0.1)
        y_bodega = col_by.number_input("Posición Bodega Y", 0.0, 20.0, float(largo) - float((ancho*largo*0.2)/ancho), 0.1)
        col_w, col_h = st.columns(2)
        w_bodega = col_w.number_input("Ancho Bodega", 1.0, 20.0, float(ancho), 0.1)
        h_bodega = col_h.number_input("Largo Bodega", 1.0, 20.0, float((ancho*largo*0.2)/ancho), 0.1)
        muro_puerta_bod = st.selectbox("Muro Puerta Bodega", ['Sur', 'Norte', 'Este', 'Oeste'])
        pos_puerta_bod = st.slider("Posición Puerta Bodega", 0.0, 10.0, 1.0)

    with st.expander("3. Red de Pasillos (Blindaje)", expanded=False):
        t_pasillos = st.checkbox("Habilitar Blindaje de Pasillos", value=False)
        pas_poder = st.slider("Ancho Pasillo Poder", 0.9, 2.5, 1.8)
        pas_peri = st.slider("Ancho Pasillos Perimetrales", 0.9, 1.5, 1.2)
        pas_bod = st.slider("Ancho Pasillo Bodega", 0.8, 1.5, 1.0)

    with st.expander("4. Checkout", expanded=False):
        t_check = st.checkbox("Habilitar Checkout", value=False)
        cant_check = st.slider("Módulos", 2, 7, 3)
        rot_check = st.selectbox("Rotación (°)", [0, 90, 180, 270])
        pos_chk_x = st.number_input("Check Pos X", 0.0, float(ancho), ancho - (cant_check*MOD_2FT), 0.1)
        pos_chk_y = st.number_input("Check Pos Y", 0.0, float(largo), 0.0, 0.1)

    with st.expander("5. Cuarto Frío", expanded=False):
        t_frio = st.checkbox("Habilitar Cuarto Frío", value=False)
        forma_frio = st.radio("Formato Frío", ['Lineal', 'Escuadra'])
        rot_frio = st.selectbox("Rotación Frío (°)", [0, 90, 180, 270])
        pos_frio_x = st.number_input("Frío Pos X", 0.0, float(ancho), 0.0, 0.1)
        pos_frio_y = st.number_input("Frío Pos Y", 0.0, float(largo), largo - PROF_FRIO, 0.1)
        
        if forma_frio == 'Lineal': cant_frio = st.slider("Puertas", 2, 20, 8)
        else:
            col_p1, col_p2 = st.columns(2)
            ptas_frio_1 = col_p1.number_input("Puertas Lado 1", 1, 15, 5)
            ptas_frio_2 = col_p2.number_input("Puertas Lado 2", 1, 15, 3)
            cant_frio = ptas_frio_1 + ptas_frio_2

    with st.expander("6. Góndolas Centrales", expanded=False):
        t_gondolas = st.checkbox("Habilitar Góndolas", value=False)
        rot_gon = st.radio("Orientación", ['Vertical', 'Horizontal'])
        sep_cab = st.checkbox("Separar cabeceras para islas")
        cant_trenes = st.slider("Trenes", 1, 6, 2)
        cant_tramos = st.slider("Tramos por Tren", 1, 8, 3)
        pas_gon = st.slider("Pasillo entre góndolas", 0.9, 1.5, 1.2)
        pos_gon_x = st.number_input("Góndola Pos X", 0.0, float(ancho), 4.0, 0.1)
        pos_gon_y = st.number_input("Góndola Pos Y", 0.0, float(largo), 4.0, 0.1)

    with st.expander("7. Foodvenience", expanded=False):
        t_cafe = st.checkbox("Habilitar Foodvenience", value=False)
        forma_cafe = st.radio("Formato Café", ['Lineal', 'Escuadra'])
        cant_cafe = st.slider("Módulos Café", 2, 10, 4)
        pos_cafe_x = st.number_input("Café Pos X", 0.0, float(ancho), 0.0, 0.1)
        pos_cafe_y = st.number_input("Café Pos Y", 0.0, float(largo), 0.0, 0.1)

    with st.expander("8. Góndola Perimetral", expanded=False):
        t_perimetral = st.checkbox("Habilitar Perimetrales Manual", value=False)
        col_m1, col_m2 = st.columns(2)
        peri_izq = col_m1.checkbox("Muro Izquierdo", value=False)
        tramos_izq = col_m1.number_input("Tramos Izq", 0, 30, 10)
        pos_izq_y = col_m1.number_input("Inicio Y Izq", 0.0, 20.0, 0.0, 0.1)
        
        peri_der = col_m2.checkbox("Muro Derecho", value=False)
        tramos_der = col_m2.number_input("Tramos Der", 0, 30, 10)
        pos_der_y = col_m2.number_input("Inicio Y Der", 0.0, 20.0, 0.0, 0.1)
        
        peri_frente = col_m1.checkbox("Muro Frente", value=False)
        tramos_frente = col_m1.number_input("Tramos Fre", 0, 30, 5)
        pos_fre_x = col_m1.number_input("Inicio X Fre", 0.0, 20.0, 0.0, 0.1)
        
        peri_fondo = col_m2.checkbox("Muro Fondo", value=False)
        tramos_fondo = col_m2.number_input("Tramos Fon", 0, 30, 5)
        pos_fon_x = col_m2.number_input("Inicio X Fon", 0.0, 20.0, 0.0, 0.1)

    with st.expander("9. Islas Individuales", expanded=False):
        t_islas = st.checkbox("Habilitar Islas Libres", value=False)
        cant_islas = st.slider("Cantidad de Islas", 1, 10, 3)
        for i in range(cant_islas):
            c1, c2 = st.columns(2)
            conf[f'isla_x_{i}'] = c1.number_input(f"Isla {i+1} X", 0.0, 20.0, 2.0 + (i*1.0), 0.1)
            conf[f'isla_y_{i}'] = c2.number_input(f"Isla {i+1} Y", 0.0, 20.0, 2.0, 0.1)

# Compilación Final del Diccionario
conf.update({
    'nombre_tienda': nombre_tienda,
    'ancho': ancho, 'largo': largo, 
    't_puerta': t_puerta, 'tipo_puerta': tipo_puerta, 'muro_puerta': muro_puerta, 'pos_puerta_x': pos_puerta_x, 'pos_puerta_y': pos_puerta_y,
    't_bodega': t_bodega, 'loc_bodega': loc_bodega, 'x_bodega': x_bodega if t_bodega else 0, 'y_bodega': y_bodega if t_bodega else 0, 'w_bodega': w_bodega if t_bodega else 0, 'h_bodega': h_bodega if t_bodega else 0, 'pas_bod': pas_bod, 'muro_puerta_bod': muro_puerta_bod, 'pos_puerta_bod': pos_puerta_bod,
    't_pasillos': t_pasillos, 'pas_poder': pas_poder, 'pas_peri': pas_peri,
    't_check': t_check, 'rot_check': rot_check, 'cant_check': cant_check, 'pos_chk_x': pos_chk_x, 'pos_chk_y': pos_chk_y,
    't_frio': t_frio, 'forma_frio': forma_frio, 'rot_frio': rot_frio, 'cant_frio': cant_frio if forma_frio=='Lineal' else 0, 'ptas_frio_1': ptas_frio_1 if forma_frio=='Escuadra' else 0, 'ptas_frio_2': ptas_frio_2 if forma_frio=='Escuadra' else 0, 'pos_frio_x': pos_frio_x, 'pos_frio_y': pos_frio_y,
    't_gondolas': t_gondolas, 'rot_gon': rot_gon, 'sep_cab': sep_cab, 'cant_trenes': cant_trenes, 'cant_tramos': cant_tramos, 'pas_gon': pas_gon, 'pos_gon_x': pos_gon_x, 'pos_gon_y': pos_gon_y,
    't_cafe': t_cafe, 'forma_cafe': forma_cafe, 'cant_cafe': cant_cafe, 'pos_cafe_x': pos_cafe_x, 'pos_cafe_y': pos_cafe_y,
    't_perimetral': t_perimetral, 'peri_izq': peri_izq, 'tramos_izq': tramos_izq, 'pos_izq_y': pos_izq_y, 'peri_der': peri_der, 'tramos_der': tramos_der, 'pos_der_y': pos_der_y, 'peri_frente': peri_frente, 'tramos_frente': tramos_frente, 'pos_fre_x': pos_fre_x, 'peri_fondo': peri_fondo, 'tramos_fondo': tramos_fondo, 'pos_fon_x': pos_fon_x,
    't_islas': t_islas, 'cant_islas': cant_islas
})

with col_plot:
    fig, errores, pct_exh, pct_nav, a_tot, a_com, a_op_real = dibujar_layout_oxxo_v22(conf)
    st.pyplot(fig)
    
    # Exportaciones Vectoriales (CAD/PDF)
    col_pdf, col_svg = st.columns(2)
    
    buf_pdf = io.BytesIO()
    fig.savefig(buf_pdf, format="pdf", bbox_inches='tight')
    col_pdf.download_button(label="📥 Descargar Plano PDF", data=buf_pdf.getvalue(), file_name=f"{nombre_tienda}.pdf", mime="application/pdf", use_container_width=True)
    
    buf_svg = io.BytesIO()
    fig.savefig(buf_svg, format="svg", bbox_inches='tight')
    col_svg.download_button(label="📐 Descargar Plano Vectorial (SVG)", data=buf_svg.getvalue(), file_name=f"{nombre_tienda}.svg", mime="image/svg+xml", use_container_width=True)
    
    if errores:
        st.error("🚨 **Motor de Colisiones Activo:**")
        for err in errores: st.warning(f"• {err}")

# Update Dashboard KPIs
pct_op = (a_op_real / a_tot) * 100 if a_tot > 0 else 0
if 18 <= pct_op <= 22: kpi_bod.success(f"Bodega: {pct_op:.1f}% (Meta 20%)")
else: kpi_bod.error(f"Bodega: {pct_op:.1f}% (Meta 20%)")

kpi_exh.metric("Rentabilidad (30-40%)", f"{pct_exh:.1f}%", "Aceptado" if 30 <= pct_exh <= 40 else "Revisar")
kpi_nav.metric("Experiencia (60-70%)", f"{pct_nav:.1f}%", "Aceptado" if 60 <= pct_nav <= 70 else "Revisar")