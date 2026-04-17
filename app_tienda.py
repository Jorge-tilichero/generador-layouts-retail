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

def dibujar_layout_v16(conf):
    W, L = conf['ancho'], conf['largo']
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_xlim(0, W)
    ax.set_ylim(0, L)
    
    obstaculos = [] 
    errores = [] # Lista para capturar errores de ejecución
    area_exhibicion = 0 # Acumulador para el cálculo del balance
    
    # Lienzo
    ax.add_patch(patches.Rectangle((0, 0), W, L, fill=False, ec='black', lw=3))

    # Áreas Base
    area_total = W * L
    area_operativa = area_total * 0.20 # 20% fijo de bodega operativa
    area_comercial = area_total - area_operativa

    # ==========================================
    # 1. ACCESO Y PASILLO DE PODER
    # ==========================================
    if conf['t_puerta']:
        pos_p = conf['pos_puerta']
        ax.add_patch(patches.Rectangle((pos_p, 0), PUERTA_ANCHO, 0.2, color='red', lw=2))
        ax.text(pos_p + PUERTA_ANCHO/2, 0.5, 'ACCESO', ha='center', fontsize=7, weight='bold', color='red')
        
        ax.add_patch(patches.Circle((pos_p + PUERTA_ANCHO/2, 0), 2.0, color='#85C1E9', alpha=0.3))
        ax.add_patch(patches.Rectangle((pos_p, 0), PUERTA_ANCHO, L, color='#EBF5FB', alpha=0.6))
        ax.text(pos_p + PUERTA_ANCHO/2, L/2, 'PASILLO DE PODER', rotation=90, ha='center', va='center', color='#21618C', weight='bold')
        
        obstaculos.append((pos_p - 0.2, 0, PUERTA_ANCHO + 0.4, L)) 

    # ==========================================
    # 2. CHECKOUT EN ESQUINA
    # ==========================================
    if conf['t_check'] and conf['t_puerta']:
        ancho_check = conf['cant_check'] * MOD_2FT
        if ancho_check > W - PUERTA_ANCHO:
            errores.append(f"El checkout de {conf['cant_check']} módulos es más ancho que el espacio disponible.")
            ancho_check = (W - PUERTA_ANCHO) - 1.0 # Ajuste forzado
            
        x_chk = W - ancho_check if conf['loc_check'] == 'Esquina Inferior Derecha' else 0
        y_chk = 0
        
        if colisiona(x_chk, y_chk, ancho_check, PROF_CONTRA + PROF_CAJERO + PROF_CHECK, obstaculos):
            errores.append("No se pudo colocar el Checkout porque colisiona con el acceso.")
        else:
            ax.add_patch(patches.Rectangle((x_chk, y_chk), ancho_check, PROF_CONTRA, color='#82E0AA', ec='black'))
            ax.text(x_chk + ancho_check/2, y_chk + PROF_CONTRA/2, 'C.CAJA', ha='center', fontsize=5)
            ax.add_patch(patches.Rectangle((x_chk, y_chk + PROF_CONTRA), ancho_check, PROF_CAJERO, color='#EAEDED'))
            ax.text(x_chk + ancho_check/2, y_chk + PROF_CONTRA + PROF_CAJERO/2, 'PASILLO CAJERO (1m)', ha='center', fontsize=6, color='gray')
            
            y_mods = y_chk + PROF_CONTRA + PROF_CAJERO
            for i in range(conf['cant_check']):
                ax.add_patch(patches.Rectangle((x_chk + (i*MOD_2FT), y_mods), MOD_2FT, PROF_CHECK, color='#ABEBC6', ec='black'))
                ax.text(x_chk + (i*MOD_2FT) + MOD_2FT/2, y_mods + PROF_CHECK/2, f'CHK{i+1}', ha='center', fontsize=6)
            
            y_fila = y_mods + PROF_CHECK
            ax.add_patch(patches.Rectangle((x_chk, y_fila), ancho_check, PASILLO_STD, color='#D5F5E3', alpha=0.5))
            ax.text(x_chk + ancho_check/2, y_fila + PASILLO_STD/2, 'PASILLO COBRO (Fila)', ha='center', fontsize=7, color='#186A3B')
            
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
            
            if ancho_frio > W:
                errores.append(f"El cuarto frío lineal de {ptas} puertas excede el ancho del local ({W}m).")
            else:
                ax.add_patch(patches.Rectangle((x_frio, y_frio), ancho_frio, PROF_FRIO, color='#AED6F1', ec='black'))
                for i in range(ptas):
                    ax.add_patch(patches.Rectangle((x_frio + (i*MOD_2FT), y_frio), MOD_2FT, 0.15, color='#2874A6', ec='white'))
                
                ax.add_patch(patches.Rectangle((x_frio, y_frio - PASILLO_STD), ancho_frio, PASILLO_STD, color='#FCF3CF', alpha=0.6))
                ax.text(x_frio + ancho_frio/2, y_frio - PASILLO_STD/2, 'PASILLO FRÍO', ha='center', fontsize=7, color='#9A7D0A')
                obstaculos.append((x_frio, y_frio - PASILLO_STD, ancho_frio, PROF_FRIO + PASILLO_STD))
                area_exhibicion += (ancho_frio * PROF_FRIO)
                
        else: # Escuadra
            ptas_fondo = int(ptas * 0.6)
            ptas_lat = ptas - ptas_fondo
            ancho_fondo = ptas_fondo * MOD_2FT
            largo_lat = ptas_lat * MOD_2FT
            
            if ancho_fondo > W or largo_lat > L:
                 errores.append("El cuarto frío en escuadra excede los límites físicos del local.")
            else:
                if conf['loc_frio'] == 'Fondo Izquierda':
                    ax.add_patch(patches.Rectangle((0, y_frio), ancho_fondo, PROF_FRIO, color='#AED6F1', ec='black'))
                    ax.add_patch(patches.Rectangle((0, y_frio - largo_lat), PROF_FRIO, largo_lat, color='#AED6F1', ec='black'))
                    ax.add_patch(patches.Rectangle((0, y_frio - PASILLO_STD), ancho_fondo, PASILLO_STD, color='#FCF3CF', alpha=0.6))
                    ax.add_patch(patches.Rectangle((PROF_FRIO, y_frio - largo_lat), PASILLO_STD, largo_lat, color='#FCF3CF', alpha=0.6))
                    obstaculos.append((0, y_frio - largo_lat - PASILLO_STD, max(ancho_fondo, PROF_FRIO + PASILLO_STD), PROF_FRIO + largo_lat + PASILLO_STD))
                else:
                    x_f = W - ancho_fondo
                    ax.add_patch(patches.Rectangle((x_f, y_frio), ancho_fondo, PROF_FRIO, color='#AED6F1', ec='black'))
                    ax.add_patch(patches.Rectangle((W - PROF_FRIO, y_frio - largo_lat), PROF_FRIO, largo_lat, color='#AED6F1', ec='black'))
                    obstaculos.append((W - max(ancho_fondo, PROF_FRIO + PASILLO_STD), y_frio - largo_lat - PASILLO_STD, max(ancho_fondo, PROF_FRIO + PASILLO_STD), PROF_FRIO + largo_lat + PASILLO_STD))
                area_exhibicion += ((ancho_fondo * PROF_FRIO) + (PROF_FRIO * largo_lat))

    # ==========================================
    # 4. GÓNDOLAS CENTRALES
    # ==========================================
    if conf['t_gondolas'] and conf['t_frio']:
        y_inicio_g = 4.0 
        x_g = PASILLO_STD + PROF_PERIMETRO
        trenes_colocados = 0
        
        for i in range(conf['cant_trenes']):
            largo_g = conf['cant_tramos'] * MOD_3FT
            colocado = False
            
            while x_g + GONDOLA_PROF < W:
                if not colisiona(x_g, y_inicio_g, GONDOLA_PROF, largo_g + CABECERA_PROF*2, obstaculos):
                    ax.add_patch(patches.Rectangle((x_g, y_inicio_g), GONDOLA_PROF, CABECERA_PROF, color='#E74C3C', ec='black'))
                    for t in range(conf['cant_tramos']):
                        y_t = y_inicio_g + CABECERA_PROF + (t*MOD_3FT)
                        ax.add_patch(patches.Rectangle((x_g, y_t), GONDOLA_PROF, MOD_3FT, color='#ABB2B9', ec='black'))
                        ax.text(x_g + GONDOLA_PROF/2, y_t + MOD_3FT/2, f'Tr{t+1}', ha='center', fontsize=6)
                    ax.add_patch(patches.Rectangle((x_g, y_inicio_g + CABECERA_PROF + largo_g), GONDOLA_PROF, CABECERA_PROF, color='#E74C3C', ec='black'))
                    
                    pas_x = x_g - PASILLO_STD if x_g < conf['pos_puerta'] else x_g + GONDOLA_PROF
                    ax.add_patch(patches.Rectangle((pas_x, y_inicio_g), PASILLO_STD, largo_g + CABECERA_PROF*2, color='#EBEDEF', alpha=0.6))
                    
                    obstaculos.append((x_g - PASILLO_STD, y_inicio_g - CABECERA_PROF, GONDOLA_PROF + PASILLO_STD*2, largo_g + CABECERA_PROF*2))
                    area_exhibicion += GONDOLA_PROF * (largo_g + CABECERA_PROF*2)
                    colocado = True
                    trenes_colocados += 1
                    break
                x_g += 0.5 
            if colocado: x_g += GONDOLA_PROF + PASILLO_STD
            
        if trenes_colocados < conf['cant_trenes']:
            errores.append(f"Solo se pudieron colocar {trenes_colocados} de {conf['cant_trenes']} trenes de góndola por falta de espacio.")

    # ==========================================
    # 5. MÓDULOS DE CAFÉ
    # ==========================================
    if conf['t_cafe'] and conf['t_gondolas']:
        ancho_cafe = conf['cant_cafe'] * MOD_2FT
        x_cafe = 0 if conf['loc_check'] == 'Esquina Inferior Derecha' else W - ancho_cafe
        y_cafe = 0
        
        if colisiona(x_cafe, y_cafe, ancho_cafe, PROF_CAFE + PASILLO_STD, obstaculos):
            errores.append("No se pudo colocar el área de café porque colisiona con el acceso u otro mobiliario.")
        else:
            for i in range(conf['cant_cafe']):
                ax.add_patch(patches.Rectangle((x_cafe + (i*MOD_2FT), y_cafe), MOD_2FT, PROF_CAFE, color='#FAD7A0', ec='black'))
                ax.text(x_cafe + (i*MOD_2FT) + MOD_2FT/2, y_cafe + PROF_CAFE/2, f'C{i+1}', ha='center', fontsize=6)
            ax.add_patch(patches.Rectangle((x_cafe, PROF_CAFE), ancho_cafe, PASILLO_STD, color='#FADBD8', alpha=0.5))
            obstaculos.append((x_cafe, y_cafe, ancho_cafe, PROF_CAFE + PASILLO_STD))
            area_exhibicion += (ancho_cafe * PROF_CAFE)

    # ==========================================
    # 6. PERIMETRALES Y 7. ISLAS
    # ==========================================
    if conf['t_perimetral'] and conf['t_cafe']:
        tramos_peri = 0
        def colocar_muro(x_base, y_base, largo_muro, vertical=True):
            nonlocal tramos_peri
            tramos = int(largo_muro / MOD_1FT)
            for i in range(tramos):
                cx = x_base if vertical else x_base + (i*MOD_1FT)
                cy = y_base + (i*MOD_1FT) if vertical else y_base
                cw = PROF_PERIMETRO if vertical else MOD_1FT
                ch = MOD_1FT if vertical else PROF_PERIMETRO
                
                if not colisiona(cx, cy, cw, ch, obstaculos):
                    ax.add_patch(patches.Rectangle((cx, cy), cw, ch, color='#D5DBDB', ec='gray'))
                    tramos_peri += 1

        colocar_muro(0, 0, L, vertical=True) 
        colocar_muro(W - PROF_PERIMETRO, 0, L, vertical=True) 
        colocar_muro(0, L - PROF_PERIMETRO, W, vertical=False)
        area_exhibicion += (tramos_peri * MOD_1FT * PROF_PERIMETRO)

    if conf['t_islas'] and conf['t_perimetral']:
        islas_ok = 0
        for y_isla in range(2, int(L)-2): 
            for x_isla in range(1, int(W)-1):
                if islas_ok >= conf['cant_islas']: break
                if not colisiona(x_isla, y_isla, ISLA_DIM, ISLA_DIM, obstaculos):
                    ax.add_patch(patches.Rectangle((x_isla, y_isla), ISLA_DIM, ISLA_DIM, color='#F4D03F', ec='black'))
                    ax.text(x_isla + ISLA_DIM/2, y_isla + ISLA_DIM/2, f'E{islas_ok+1}', ha='center', va='center', fontsize=6)
                    obstaculos.append((x_isla - 0.2, y_isla - 0.2, ISLA_DIM + 0.4, ISLA_DIM + 0.4))
                    islas_ok += 1
        
        area_exhibicion += (islas_ok * ISLA_DIM * ISLA_DIM)
        if islas_ok < conf['cant_islas']:
            errores.append(f"Solo se colocaron {islas_ok} de {conf['cant_islas']} islas para proteger los pasillos.")

    # Cálculos Finales
    pct_exh = (area_exhibicion / area_comercial) * 100 if area_comercial > 0 else 0
    pct_nav = 100 - pct_exh

    ax.set_aspect('equal')
    plt.title(f"Planograma Secuencial V16.0")
    return fig, errores, pct_exh, pct_nav

# --- INTERFAZ STREAMLIT ---
st.set_page_config(layout="wide")
st.title("🏗️ Planogramador Arquitectónico V16.0")

col_params, col_plot = st.columns([1.2, 2.8])

with col_params:
    st.header("Propiedades del Local")
    ancho = st.number_input("Ancho (m)", min_value=5.0, max_value=20.0, value=12.0, step=0.5)
    largo = st.number_input("Profundidad (m)", min_value=5.0, max_value=20.0, value=15.0, step=0.5)
    
    st.markdown("---")
    st.write("🔧 **Constructor de Flujos**")
    
    t_puerta = st.toggle("1. Activar Acceso")
    pos_puerta = st.slider("Separación desde pared izq.", 0.0, float(ancho-PUERTA_ANCHO), float(ancho/2 - PUERTA_ANCHO/2)) if t_puerta else 0.0
    
    t_check, loc_check, cant_check = False, "", 0
    if t_puerta:
        t_check = st.toggle("2. Activar Checkout")
        if t_check:
            loc_check = st.selectbox("Esquina (Anclaje a Muro)", ['Esquina Inferior Derecha', 'Esquina Inferior Izquierda'])
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
    'ancho': ancho, 'largo': largo,
    't_puerta': t_puerta, 'pos_puerta': pos_puerta,
    't_check': t_check, 'loc_check': loc_check, 'cant_check': cant_check,
    't_frio': t_frio, 'loc_frio': loc_frio, 'forma_frio': forma_frio, 'cant_frio': cant_frio,
    't_gondolas': t_gondolas, 'cant_trenes': cant_trenes, 'cant_tramos': cant_tramos,
    't_cafe': t_cafe, 'cant_cafe': cant_cafe,
    't_perimetral': t_perimetral,
    't_islas': t_islas, 'cant_islas': cant_islas
}

with col_plot:
    fig, errores, pct_exh, pct_nav = dibujar_layout_v16(conf)
    st.pyplot(fig)
    
    # --- MENSAJES DE ERROR ---
    if errores:
        st.error("🚨 **Advertencias de Diseño Espacial:**")
        for err in errores:
            st.warning(f"• {err}")
    
    # --- DASHBOARD DE KPIS ---
    if t_puerta: # Solo mostrar si hay tienda activa
        st.markdown("---")
        st.subheader("📊 Balance de Layout (Criterios Oficiales)")
        st.write("El balance ideal que garantiza la rentabilidad y una experiencia memorable es **30-40% de exhibición** y **60-70% de navegación**.")
        
        col_kpi1, col_kpi2 = st.columns(2)
        
        # Evaluación Exhibición
        with col_kpi1:
            st.metric("Área de Exhibición", f"{pct_exh:.1f}%", help="Suma de m2 de todos los muebles comerciales.")
            if 30 <= pct_exh <= 40:
                st.success("✅ ACEPTADO (Rentabilidad Óptima)")
            elif pct_exh < 30:
                st.info("📉 OPORTUNIDAD (Falta mobiliario para rentabilizar)")
            else:
                st.error("❌ RECHAZADO (Piso saturado)")
                
        # Evaluación Navegación
        with col_kpi2:
            st.metric("Área de Navegación", f"{pct_nav:.1f}%", help="Espacio libre para pasillos y circulación.")
            if 60 <= pct_nav <= 70:
                st.success("✅ ACEPTADO (Experiencia Óptima)")
            elif pct_nav > 70:
                st.info("📉 OPORTUNIDAD (Demasiado espacio libre)")
            else:
                st.error("❌ RECHAZADO (Pasillos bloqueados / mala experiencia)")