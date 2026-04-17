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

def dibujar_layout_v19(conf):
    W, L = conf['ancho'], conf['largo']
    fig, ax = plt.subplots(figsize=(12, 12))
    ax.set_xlim(0, W)
    ax.set_ylim(0, L)
    
    obstaculos, errores = [], []
    area_exhibicion = 0 
    
    # Lienzo
    ax.add_patch(patches.Rectangle((0, 0), W, L, fill=False, ec='black', lw=3))
    area_total = W * L
    area_operativa = area_total * 0.20 
    area_comercial = area_total - area_operativa

    # ==========================================
    # 1. BODEGA OPERATIVA (Fondo)
    # ==========================================
    prof_bodega = area_operativa / W
    y_bodega = L - prof_bodega
    ax.add_patch(patches.Rectangle((0, y_bodega), W, prof_bodega, color='#D2B48C', ec='black'))
    ax.text(W/2, y_bodega + prof_bodega/2, 'ZONA OPERATIVA (20%)', ha='center', weight='bold')
    obstaculos.append((0, y_bodega, W, prof_bodega))

    # ==========================================
    # 2. ACCESO Y PASILLO DE PODER
    # ==========================================
    pos_p = 0
    if conf['t_puerta']:
        pos_p = conf['pos_puerta']
        ax.add_patch(patches.Rectangle((pos_p, 0), PUERTA_ANCHO, 0.2, color='red', lw=2))
        ax.text(pos_p + PUERTA_ANCHO/2, 0.5, 'ACCESO', ha='center', fontsize=7, weight='bold', color='red')
        
        # Pasillo de Poder Principal
        ax.add_patch(patches.Rectangle((pos_p, 0), PUERTA_ANCHO, y_bodega, color='#EBF5FB', alpha=0.6))
        ax.text(pos_p + PUERTA_ANCHO/2, y_bodega/2, 'PASILLO DE PODER', rotation=90, ha='center', va='center', color='#21618C', weight='bold')
        obstaculos.append((pos_p, 0, PUERTA_ANCHO, y_bodega)) 

    # ==========================================
    # 3. CHECKOUT PARAMÉTRICO (Rotación)
    # ==========================================
    if conf['t_check'] and conf['t_puerta']:
        mods = conf['cant_check']
        largo_chk = mods * MOD_2FT
        muro_chk = conf['muro_check']
        
        if muro_chk == 'Inferior (Frente)':
            x_chk = W - largo_chk if pos_p < W/2 else 0
            y_chk = 0
            if not colisiona(x_chk, y_chk, largo_chk, PROF_CONTRA + PROF_CAJERO + PROF_CHECK, obstaculos):
                ax.add_patch(patches.Rectangle((x_chk, y_chk), largo_chk, PROF_CONTRA, color='#82E0AA', ec='black'))
                ax.add_patch(patches.Rectangle((x_chk, y_chk + PROF_CONTRA), largo_chk, PROF_CAJERO, color='#EAEDED'))
                for i in range(mods): ax.add_patch(patches.Rectangle((x_chk + (i*MOD_2FT), y_chk + PROF_CONTRA + PROF_CAJERO), MOD_2FT, PROF_CHECK, color='#ABEBC6', ec='black'))
                ax.add_patch(patches.Rectangle((x_chk, y_chk + PROF_CONTRA + PROF_CAJERO + PROF_CHECK), largo_chk, PASILLO_STD, color='#D5F5E3', alpha=0.5))
                ax.text(x_chk + largo_chk/2, y_chk + PROF_CONTRA + PROF_CAJERO + PROF_CHECK + PASILLO_STD/2, 'PASILLO COBRO', ha='center', fontsize=6)
                obstaculos.append((x_chk, 0, largo_chk, PROF_CONTRA + PROF_CAJERO + PROF_CHECK + PASILLO_STD))
                area_exhibicion += (largo_chk * PROF_CHECK)
            else: errores.append("Checkout colisiona con el acceso.")
            
        elif muro_chk == 'Lateral Izquierdo':
            x_chk, y_chk = 0, 1.0
            if not colisiona(x_chk, y_chk, PROF_CONTRA + PROF_CAJERO + PROF_CHECK, largo_chk, obstaculos):
                ax.add_patch(patches.Rectangle((x_chk, y_chk), PROF_CONTRA, largo_chk, color='#82E0AA', ec='black'))
                ax.add_patch(patches.Rectangle((x_chk + PROF_CONTRA, y_chk), PROF_CAJERO, largo_chk, color='#EAEDED'))
                for i in range(mods): ax.add_patch(patches.Rectangle((x_chk + PROF_CONTRA + PROF_CAJERO, y_chk + (i*MOD_2FT)), PROF_CHECK, MOD_2FT, color='#ABEBC6', ec='black'))
                ax.add_patch(patches.Rectangle((x_chk + PROF_CONTRA + PROF_CAJERO + PROF_CHECK, y_chk), PASILLO_STD, largo_chk, color='#D5F5E3', alpha=0.5))
                obstaculos.append((x_chk, y_chk, PROF_CONTRA + PROF_CAJERO + PROF_CHECK + PASILLO_STD, largo_chk))
                area_exhibicion += (largo_chk * PROF_CHECK)
            else: errores.append("Checkout Izquierdo colisiona.")
            
        elif muro_chk == 'Lateral Derecho':
            x_chk = W - (PROF_CONTRA + PROF_CAJERO + PROF_CHECK)
            y_chk = 1.0
            if not colisiona(x_chk - PASILLO_STD, y_chk, PROF_CONTRA + PROF_CAJERO + PROF_CHECK + PASILLO_STD, largo_chk, obstaculos):
                ax.add_patch(patches.Rectangle((W - PROF_CONTRA, y_chk), PROF_CONTRA, largo_chk, color='#82E0AA', ec='black'))
                ax.add_patch(patches.Rectangle((W - PROF_CONTRA - PROF_CAJERO, y_chk), PROF_CAJERO, largo_chk, color='#EAEDED'))
                for i in range(mods): ax.add_patch(patches.Rectangle((W - PROF_CONTRA - PROF_CAJERO - PROF_CHECK, y_chk + (i*MOD_2FT)), PROF_CHECK, MOD_2FT, color='#ABEBC6', ec='black'))
                ax.add_patch(patches.Rectangle((W - PROF_CONTRA - PROF_CAJERO - PROF_CHECK - PASILLO_STD, y_chk), PASILLO_STD, largo_chk, color='#D5F5E3', alpha=0.5))
                obstaculos.append((W - PROF_CONTRA - PROF_CAJERO - PROF_CHECK - PASILLO_STD, y_chk, PROF_CONTRA + PROF_CAJERO + PROF_CHECK + PASILLO_STD, largo_chk))
                area_exhibicion += (largo_chk * PROF_CHECK)
            else: errores.append("Checkout Derecho colisiona.")

    # ==========================================
    # 4. CUARTO FRÍO MODULAR (Escuadra Manual)
    # ==========================================
    if conf['t_frio'] and conf['t_check']:
        esq = conf['loc_frio']
        ptas_A = conf['cant_frio_A']
        ptas_B = conf['cant_frio_B'] if conf['forma_frio'] == 'Escuadra' else 0
        
        y_f_base = y_bodega - PROF_FRIO
        
        # Lado A (Fondo Horizontal)
        w_frio_A = ptas_A * MOD_2FT
        x_f_A = 0 if esq == 'Fondo Izquierda' else W - w_frio_A
        
        if not colisiona(x_f_A, y_f_base - PASILLO_STD, w_frio_A, PROF_FRIO + PASILLO_STD, obstaculos):
            ax.add_patch(patches.Rectangle((x_f_A, y_f_base), w_frio_A, PROF_FRIO, color='#AED6F1', ec='black'))
            for i in range(ptas_A): ax.add_patch(patches.Rectangle((x_f_A + (i*MOD_2FT), y_f_base), MOD_2FT, 0.15, color='#2874A6', ec='white'))
            ax.add_patch(patches.Rectangle((x_f_A, y_f_base - PASILLO_STD), w_frio_A, PASILLO_STD, color='#FCF3CF', alpha=0.6))
            obstaculos.append((x_f_A, y_f_base - PASILLO_STD, w_frio_A, PROF_FRIO + PASILLO_STD))
            area_exhibicion += (w_frio_A * PROF_FRIO)
        else: errores.append("Frío (Fondo) colisiona.")

        # Lado B (Lateral Vertical)
        if ptas_B > 0:
            h_frio_B = ptas_B * MOD_2FT
            x_f_B = 0 if esq == 'Fondo Izquierda' else W - PROF_FRIO
            y_f_B = y_f_base - h_frio_B
            
            if not colisiona(0 if esq == 'Fondo Izquierda' else W - PROF_FRIO - PASILLO_STD, y_f_B, PROF_FRIO + PASILLO_STD, h_frio_B, obstaculos):
                ax.add_patch(patches.Rectangle((x_f_B, y_f_B), PROF_FRIO, h_frio_B, color='#AED6F1', ec='black'))
                ax.add_patch(patches.Rectangle((PROF_FRIO if esq == 'Fondo Izquierda' else W - PROF_FRIO - PASILLO_STD, y_f_B), PASILLO_STD, h_frio_B, color='#FCF3CF', alpha=0.6))
                obstaculos.append((0 if esq == 'Fondo Izquierda' else W - PROF_FRIO - PASILLO_STD, y_f_B, PROF_FRIO + PASILLO_STD, h_frio_B))
                area_exhibicion += (h_frio_B * PROF_FRIO)
            else: errores.append("Frío (Lateral) colisiona.")

    # ==========================================
    # 5. CAFÉ MODULAR (Escuadra Manual)
    # ==========================================
    if conf['t_cafe'] and conf['t_frio']:
        esq_c = conf['loc_cafe']
        mods_cA = conf['cant_cafe_A']
        mods_cB = conf['cant_cafe_B'] if conf['forma_cafe'] == 'Escuadra' else 0
        
        # Lado A (Frente Horizontal)
        w_cafe_A = mods_cA * MOD_2FT
        x_cA = 0 if esq_c == 'Frente Izquierda' else W - w_cafe_A
        y_cA = 0
        
        if not colisiona(x_cA, y_cA, w_cafe_A, PROF_CAFE + PASILLO_STD, obstaculos):
            for i in range(mods_cA): ax.add_patch(patches.Rectangle((x_cA + (i*MOD_2FT), y_cA), MOD_2FT, PROF_CAFE, color='#FAD7A0', ec='black'))
            ax.add_patch(patches.Rectangle((x_cA, PROF_CAFE), w_cafe_A, PASILLO_STD, color='#FADBD8', alpha=0.5))
            obstaculos.append((x_cA, y_cA, w_cafe_A, PROF_CAFE + PASILLO_STD))
            area_exhibicion += (w_cafe_A * PROF_CAFE)
            
        # Lado B (Lateral Vertical)
        if mods_cB > 0:
            h_cafe_B = mods_cB * MOD_2FT
            x_cB = 0 if esq_c == 'Frente Izquierda' else W - PROF_CAFE
            y_cB = PROF_CAFE
            if not colisiona(0 if esq_c == 'Frente Izquierda' else W - PROF_CAFE - PASILLO_STD, y_cB, PROF_CAFE + PASILLO_STD, h_cafe_B, obstaculos):
                for i in range(mods_cB): ax.add_patch(patches.Rectangle((x_cB, y_cB + (i*MOD_2FT)), PROF_CAFE, MOD_2FT, color='#FAD7A0', ec='black'))
                ax.add_patch(patches.Rectangle((PROF_CAFE if esq_c == 'Frente Izquierda' else W - PROF_CAFE - PASILLO_STD, y_cB), PASILLO_STD, h_cafe_B, color='#FADBD8', alpha=0.5))
                obstaculos.append((0 if esq_c == 'Frente Izquierda' else W - PROF_CAFE - PASILLO_STD, y_cB, PROF_CAFE + PASILLO_STD, h_cafe_B))
                area_exhibicion += (h_cafe_B * PROF_CAFE)

    # ==========================================
    # 6. PERIMETRALES MULTI-MURO
    # ==========================================
    if conf['t_perimetral']:
        def trazar_peri(muro_str, is_vert, base_x, base_y, tramos_solicitados):
            colocados = 0
            for i in range(tramos_solicitados):
                cx = base_x if is_vert else base_x + (i*MOD_1FT)
                cy = base_y + (i*MOD_1FT) if is_vert else base_y
                cw = PROF_PERIMETRO if is_vert else MOD_1FT
                ch = MOD_1FT if is_vert else PROF_PERIMETRO
                if not colisiona(cx, cy, cw, ch, obstaculos):
                    ax.add_patch(patches.Rectangle((cx, cy), cw, ch, color='#D5DBDB', ec='gray'))
                    ax.text(cx + cw/2, cy + ch/2, 'P', ha='center', va='center', fontsize=4, rotation=0 if is_vert else 90)
                    colocados += 1
            return colocados * (MOD_1FT * PROF_PERIMETRO)

        if conf['t_peri_izq']: area_exhibicion += trazar_peri('Izquierdo', True, 0, 0, conf['tramos_izq'])
        if conf['t_peri_der']: area_exhibicion += trazar_peri('Derecho', True, W - PROF_PERIMETRO, 0, conf['tramos_der'])
        if conf['t_peri_fon']: area_exhibicion += trazar_peri('Fondo', False, 0, y_bodega - PROF_PERIMETRO, conf['tramos_fon'])

    # ==========================================
    # 7. GÓNDOLAS CENTRALES (Esquiva todo)
    # ==========================================
    if conf['t_gondolas']:
        y_inicio_g = 2.0 
        x_g = PASILLO_STD + PROF_PERIMETRO
        trenes_ok = 0
        for i in range(conf['cant_trenes']):
            largo_g = conf['cant_tramos'] * MOD_3FT
            colocado = False
            while x_g + GONDOLA_PROF < W:
                # Buscar en Y si hay choque
                y_test = y_inicio_g
                while y_test + largo_g + CABECERA_PROF*2 < y_bodega:
                    if not colisiona(x_g - PASILLO_STD/2, y_test - CABECERA_PROF - PASILLO_STD/2, GONDOLA_PROF + PASILLO_STD, largo_g + CABECERA_PROF*2 + PASILLO_STD, obstaculos):
                        ax.add_patch(patches.Rectangle((x_g, y_test), GONDOLA_PROF, CABECERA_PROF, color='#E74C3C', ec='black'))
                        for t in range(conf['cant_tramos']): ax.add_patch(patches.Rectangle((x_g, y_test + CABECERA_PROF + (t*MOD_3FT)), GONDOLA_PROF, MOD_3FT, color='#ABB2B9', ec='black'))
                        ax.add_patch(patches.Rectangle((x_g, y_test + CABECERA_PROF + largo_g), GONDOLA_PROF, CABECERA_PROF, color='#E74C3C', ec='black'))
                        
                        ax.add_patch(patches.Rectangle((x_g - PASILLO_STD if x_g < pos_p else x_g + GONDOLA_PROF, y_test), PASILLO_STD, largo_g + CABECERA_PROF*2, color='#EBEDEF', alpha=0.6))
                        
                        obstaculos.append((x_g - PASILLO_STD/2, y_test - CABECERA_PROF - PASILLO_STD/2, GONDOLA_PROF + PASILLO_STD, largo_g + CABECERA_PROF*2 + PASILLO_STD))
                        area_exhibicion += GONDOLA_PROF * (largo_g + CABECERA_PROF*2)
                        colocado = True
                        trenes_ok += 1
                        break
                    y_test += 0.5
                if colocado: break
                x_g += 0.5
            if colocado: x_g += GONDOLA_PROF + PASILLO_STD
        if trenes_ok < conf['cant_trenes']: errores.append(f"Solo caben {trenes_ok} trenes centrales libres.")

    # ==========================================
    # 8. ISLAS AGRUPADAS
    # ==========================================
    if conf['t_islas']:
        grupos_ok = 0
        w_grupo = ISLA_DIM * conf['isla_cols']
        h_grupo = ISLA_DIM * conf['isla_filas']
        
        for y_isla in range(2, int(L)-2): 
            for x_isla in range(1, int(W)-1):
                if grupos_ok >= conf['cant_grupos']: break
                # Verificar grupo completo + pasillo perimetral de la isla
                if not colisiona(x_isla - PASILLO_STD/2, y_isla - PASILLO_STD/2, w_grupo + PASILLO_STD, h_grupo + PASILLO_STD, obstaculos):
                    ax.add_patch(patches.Rectangle((x_isla, y_isla), w_grupo, h_grupo, color='#F4D03F', ec='black'))
                    ax.text(x_isla + w_grupo/2, y_isla + h_grupo/2, f'GRUPO\n{conf["isla_cols"]}x{conf["isla_filas"]}', ha='center', va='center', fontsize=6)
                    obstaculos.append((x_isla - PASILLO_STD/2, y_isla - PASILLO_STD/2, w_grupo + PASILLO_STD, h_grupo + PASILLO_STD))
                    grupos_ok += 1
                    area_exhibicion += (w_grupo * h_grupo)

    pct_exh = (area_exhibicion / area_comercial) * 100 if area_comercial > 0 else 0
    pct_nav = 100 - pct_exh

    ax.set_aspect('equal')
    plt.title("Store Planning Paramétrico V19")
    return fig, errores, pct_exh, pct_nav

# --- INTERFAZ STREAMLIT ---
st.set_page_config(layout="wide")
st.title("🏬 Store Planning Paramétrico V19.0")

col_params, col_plot = st.columns([1.3, 2.7])

with col_params:
    ancho = st.number_input("Ancho Local (m)", 5.0, 25.0, 15.0, 0.5)
    largo = st.number_input("Profundidad Local (m)", 5.0, 30.0, 20.0, 0.5)
    
    st.write("🔧 **Constructor Manual (Paramétrico)**")
    
    t_puerta = st.toggle("1. Activar Acceso (Muro Frontal)")
    pos_puerta = st.slider("Posición X de la puerta", 0.0, float(ancho-PUERTA_ANCHO), float(ancho/2 - PUERTA_ANCHO/2)) if t_puerta else 0.0
    
    t_check = st.toggle("2. Activar Checkout")
    muro_check, cant_check = 'Inferior (Frente)', 0
    if t_check:
        muro_check = st.selectbox("Muro de Contracaja", ['Inferior (Frente)', 'Lateral Izquierdo', 'Lateral Derecho'])
        cant_check = st.slider("Módulos Checkout", 1, 6, 3)

    t_frio = st.toggle("3. Activar Cuarto Frío")
    loc_frio, forma_frio, cant_frio_A, cant_frio_B = 'Fondo Derecha', 'Lineal', 0, 0
    if t_frio:
        loc_frio = st.selectbox("Esquina Destino (Frío)", ['Fondo Derecha', 'Fondo Izquierda'])
        forma_frio = st.radio("Formato Frío", ['Lineal', 'Escuadra'], horizontal=True)
        cant_frio_A = st.slider("Puertas Lado A (Fondo)", 2, 20, 8)
        if forma_frio == 'Escuadra':
            cant_frio_B = st.slider("Puertas Lado B (Lateral)", 1, 15, 4)

    t_cafe = st.toggle("4. Activar Área de Café")
    loc_cafe, forma_cafe, cant_cafe_A, cant_cafe_B = 'Frente Izquierda', 'Lineal', 0, 0
    if t_cafe:
        loc_cafe = st.selectbox("Esquina Destino (Café)", ['Frente Izquierda', 'Frente Derecha'])
        forma_cafe = st.radio("Formato Café", ['Lineal', 'Escuadra'], horizontal=True)
        cant_cafe_A = st.slider("Módulos Lado A (Frente)", 2, 10, 4)
        if forma_cafe == 'Escuadra':
            cant_cafe_B = st.slider("Módulos Lado B (Lateral)", 1, 8, 3)

    t_perimetral = st.toggle("5. Activar Perimetrales (Manual)")
    t_peri_izq, tramos_izq = False, 0
    t_peri_der, tramos_der = False, 0
    t_peri_fon, tramos_fon = False, 0
    if t_perimetral:
        colA, colB, colC = st.columns(3)
        with colA: 
            t_peri_izq = st.checkbox("Muro Izq")
            if t_peri_izq: tramos_izq = st.number_input("Tramos Izq", 1, 50, 10)
        with colB:
            t_peri_der = st.checkbox("Muro Der")
            if t_peri_der: tramos_der = st.number_input("Tramos Der", 1, 50, 10)
        with colC:
            t_peri_fon = st.checkbox("Muro Fondo")
            if t_peri_fon: tramos_fon = st.number_input("Tramos Fon", 1, 50, 10)

    t_gondolas = st.toggle("6. Activar Góndolas Centrales")
    cant_trenes, cant_tramos = 0, 0
    if t_gondolas:
        cant_trenes = st.slider("Cantidad de Trenes", 1, 6, 2)
        cant_tramos = st.slider("Tramos por tren", 1, 8, 3)

    t_islas = st.toggle("7. Activar Exhibidores de Piso (Islas)")
    cant_grupos, isla_cols, isla_filas = 0, 1, 1
    if t_islas:
        cant_grupos = st.slider("Cantidad de Grupos", 1, 10, 2)
        colX, colY = st.columns(2)
        with colX: isla_cols = st.number_input("Módulos de Ancho", 1, 4, 2)
        with colY: isla_filas = st.number_input("Módulos de Fondo", 1, 4, 1)

conf = {
    'ancho': ancho, 'largo': largo,
    't_puerta': t_puerta, 'pos_puerta': pos_puerta,
    't_check': t_check, 'muro_check': muro_check, 'cant_check': cant_check,
    't_frio': t_frio, 'loc_frio': loc_frio, 'forma_frio': forma_frio, 'cant_frio_A': cant_frio_A, 'cant_frio_B': cant_frio_B,
    't_cafe': t_cafe, 'loc_cafe': loc_cafe, 'forma_cafe': forma_cafe, 'cant_cafe_A': cant_cafe_A, 'cant_cafe_B': cant_cafe_B,
    't_perimetral': t_perimetral, 't_peri_izq': t_peri_izq, 'tramos_izq': tramos_izq, 't_peri_der': t_peri_der, 'tramos_der': tramos_der, 't_peri_fon': t_peri_fon, 'tramos_fon': tramos_fon,
    't_gondolas': t_gondolas, 'cant_trenes': cant_trenes, 'cant_tramos': cant_tramos,
    't_islas': t_islas, 'cant_grupos': cant_grupos, 'isla_cols': isla_cols, 'isla_filas': isla_filas
}

with col_plot:
    fig, errores, pct_exh, pct_nav = dibujar_layout_v19(conf)
    st.pyplot(fig)
    
    if errores:
        st.error("🚨 **Advertencias de Colisión Espacial:**")
        for err in errores: st.warning(f"• {err}")
    
    if t_puerta:
        st.markdown("---")
        st.subheader("📊 Auditoría de Rentabilidad OXXO")
        col_kpi1, col_kpi2 = st.columns(2)
        with col_kpi1:
            st.metric("Rentabilidad (Exhibición)", f"{pct_exh:.1f}%")
            if 30 <= pct_exh <= 40: st.success("✅ ACEPTADO (30-40%)")
            elif pct_exh < 30: st.info("📉 OPORTUNIDAD")
            else: st.error("❌ SATURADO")
        with col_kpi2:
            st.metric("Experiencia (Navegación)", f"{pct_nav:.1f}%")
            if 60 <= pct_nav <= 70: st.success("✅ ACEPTADO (60-70%)")
            elif pct_nav > 70: st.info("📉 OPORTUNIDAD")
            else: st.error("❌ RECHAZADO")