import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# --- CONSTANTES DE MODULACIÓN EXACTA ---
MOD_1FT = 0.30        # Tramos perimetrales
MOD_2FT = 0.61        # Checkout, Café, Puertas Frío
MOD_3FT = 0.91        # Tramos de góndola
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
    """Verifica si un rectángulo choca con las zonas prohibidas (muebles o pasillos)"""
    margen = 0.05 # 5cm de tolerancia
    for (ox, oy, ow, oh) in obstaculos:
        if not (x + w <= ox + margen or x >= ox + ow - margen or y + h <= oy + margen or y >= oy + oh - margen):
            return True
    return False

def dibujar_layout_v15(conf):
    W, L = conf['ancho'], conf['largo']
    fig, ax = plt.subplots(figsize=(12, 12))
    ax.set_xlim(0, W)
    ax.set_ylim(0, L)
    
    obstaculos = [] # Aquí guardaremos Muebles + Pasillos para que nada se encime
    
    # Lienzo
    ax.add_patch(patches.Rectangle((0, 0), W, L, fill=False, ec='black', lw=3))

    # ==========================================
    # 1. ACCESO Y PASILLO DE PODER
    # ==========================================
    if conf['t_puerta']:
        pos_p = conf['pos_puerta']
        
        # Puerta Física
        ax.add_patch(patches.Rectangle((pos_p, 0), PUERTA_ANCHO, 0.2, color='red', lw=2))
        ax.text(pos_p + PUERTA_ANCHO/2, 0.5, 'ACCESO', ha='center', fontsize=7, weight='bold', color='red')
        
        # Descompresión (Semi-círculo)
        ax.add_patch(patches.Circle((pos_p + PUERTA_ANCHO/2, 0), 2.0, color='#85C1E9', alpha=0.3))
        
        # Pasillo de Poder
        ax.add_patch(patches.Rectangle((pos_p, 0), PUERTA_ANCHO, L, color='#EBF5FB', alpha=0.6))
        ax.text(pos_p + PUERTA_ANCHO/2, L/2, 'PASILLO DE PODER', rotation=90, ha='center', va='center', color='#21618C', weight='bold')
        
        # Bloquear el Pasillo de Poder para que no se pongan muebles encima
        obstaculos.append((pos_p - 0.2, 0, PUERTA_ANCHO + 0.4, L)) 

    # ==========================================
    # 2. CHECKOUT EN ESQUINA
    # ==========================================
    if conf['t_check'] and conf['t_puerta']:
        ancho_check = conf['cant_check'] * MOD_2FT
        x_chk = W - ancho_check if conf['loc_check'] == 'Esquina Inferior Derecha' else 0
        y_chk = 0
        
        # Bloques de Checkout
        ax.add_patch(patches.Rectangle((x_chk, y_chk), ancho_check, PROF_CONTRA, color='#82E0AA', ec='black'))
        ax.text(x_chk + ancho_check/2, y_chk + PROF_CONTRA/2, 'C.CAJA', ha='center', fontsize=5)
        
        ax.add_patch(patches.Rectangle((x_chk, y_chk + PROF_CONTRA), ancho_check, PROF_CAJERO, color='#EAEDED'))
        ax.text(x_chk + ancho_check/2, y_chk + PROF_CONTRA + PROF_CAJERO/2, 'PASILLO CAJERO (1m)', ha='center', fontsize=6, color='gray')
        
        # Módulos individuales CHK
        y_mods = y_chk + PROF_CONTRA + PROF_CAJERO
        for i in range(conf['cant_check']):
            ax.add_patch(patches.Rectangle((x_chk + (i*MOD_2FT), y_mods), MOD_2FT, PROF_CHECK, color='#ABEBC6', ec='black'))
            ax.text(x_chk + (i*MOD_2FT) + MOD_2FT/2, y_mods + PROF_CHECK/2, f'CHK{i+1}', ha='center', fontsize=6)
        
        # Pasillo de Cobro (Fila)
        y_fila = y_mods + PROF_CHECK
        ax.add_patch(patches.Rectangle((x_chk, y_fila), ancho_check, PASILLO_STD, color='#D5F5E3', alpha=0.5))
        ax.text(x_chk + ancho_check/2, y_fila + PASILLO_STD/2, 'PASILLO COBRO (Fila)', ha='center', fontsize=7, color='#186A3B')
        
        obstaculos.append((x_chk, 0, ancho_check, y_fila + PASILLO_STD))

    # ==========================================
    # 3. CUARTO FRÍO
    # ==========================================
    if conf['t_frio'] and conf['t_check']:
        ptas = conf['cant_frio']
        y_frio = L - PROF_FRIO
        
        if conf['forma_frio'] == 'Lineal':
            ancho_frio = ptas * MOD_2FT
            x_frio = 0 if conf['loc_frio'] == 'Fondo Izquierda' else W - ancho_frio
            
            # Dibujar Caja Frio
            ax.add_patch(patches.Rectangle((x_frio, y_frio), ancho_frio, PROF_FRIO, color='#AED6F1', ec='black'))
            ax.text(x_frio + ancho_frio/2, y_frio + PROF_FRIO/2, 'CUARTO FRÍO', ha='center', weight='bold')
            
            # Puertas Individuales
            for i in range(ptas):
                ax.add_patch(patches.Rectangle((x_frio + (i*MOD_2FT), y_frio), MOD_2FT, 0.15, color='#2874A6', ec='white'))
                ax.text(x_frio + (i*MOD_2FT) + MOD_2FT/2, y_frio + 0.3, f'P{i+1}', ha='center', fontsize=5, color='white', rotation=90)
                
            # Pasillo Frio
            ax.add_patch(patches.Rectangle((x_frio, y_frio - PASILLO_STD), ancho_frio, PASILLO_STD, color='#FCF3CF', alpha=0.6))
            ax.text(x_frio + ancho_frio/2, y_frio - PASILLO_STD/2, 'PASILLO FRÍO', ha='center', fontsize=7, color='#9A7D0A')
            
            obstaculos.append((x_frio, y_frio - PASILLO_STD, ancho_frio, PROF_FRIO + PASILLO_STD))
            
        else: # Escuadra
            ptas_fondo = int(ptas * 0.6)
            ptas_lat = ptas - ptas_fondo
            ancho_fondo = ptas_fondo * MOD_2FT
            largo_lat = ptas_lat * MOD_2FT
            
            if conf['loc_frio'] == 'Fondo Izquierda':
                ax.add_patch(patches.Rectangle((0, y_frio), ancho_fondo, PROF_FRIO, color='#AED6F1', ec='black')) # Fondo
                ax.add_patch(patches.Rectangle((0, y_frio - largo_lat), PROF_FRIO, largo_lat, color='#AED6F1', ec='black')) # Lat
                # Pasillos L
                ax.add_patch(patches.Rectangle((0, y_frio - PASILLO_STD), ancho_fondo, PASILLO_STD, color='#FCF3CF', alpha=0.6))
                ax.add_patch(patches.Rectangle((PROF_FRIO, y_frio - largo_lat), PASILLO_STD, largo_lat, color='#FCF3CF', alpha=0.6))
                obstaculos.append((0, y_frio - largo_lat - PASILLO_STD, max(ancho_fondo, PROF_FRIO + PASILLO_STD), PROF_FRIO + largo_lat + PASILLO_STD))
            else:
                x_f = W - ancho_fondo
                ax.add_patch(patches.Rectangle((x_f, y_frio), ancho_fondo, PROF_FRIO, color='#AED6F1', ec='black'))
                ax.add_patch(patches.Rectangle((W - PROF_FRIO, y_frio - largo_lat), PROF_FRIO, largo_lat, color='#AED6F1', ec='black'))
                obstaculos.append((W - max(ancho_fondo, PROF_FRIO + PASILLO_STD), y_frio - largo_lat - PASILLO_STD, max(ancho_fondo, PROF_FRIO + PASILLO_STD), PROF_FRIO + largo_lat + PASILLO_STD))

    # ==========================================
    # 4. GÓNDOLAS CENTRALES
    # ==========================================
    if conf['t_gondolas'] and conf['t_frio']:
        y_inicio_g = 4.0 # Respeto frontal
        x_g = PASILLO_STD + PROF_PERIMETRO
        
        for i in range(conf['cant_trenes']):
            largo_g = conf['cant_tramos'] * MOD_3FT
            colocado = False
            
            # Buscar en X un espacio libre
            while x_g + GONDOLA_PROF < W:
                if not colisiona(x_g, y_inicio_g, GONDOLA_PROF, largo_g + CABECERA_PROF*2, obstaculos):
                    # Cabecera Sur
                    ax.add_patch(patches.Rectangle((x_g, y_inicio_g), GONDOLA_PROF, CABECERA_PROF, color='#E74C3C', ec='black'))
                    ax.text(x_g + GONDOLA_PROF/2, y_inicio_g + CABECERA_PROF/2, 'CAB', ha='center', fontsize=5)
                    
                    # Tramos (Cuerpo)
                    for t in range(conf['cant_tramos']):
                        y_t = y_inicio_g + CABECERA_PROF + (t*MOD_3FT)
                        ax.add_patch(patches.Rectangle((x_g, y_t), GONDOLA_PROF, MOD_3FT, color='#ABB2B9', ec='black'))
                        ax.text(x_g + GONDOLA_PROF/2, y_t + MOD_3FT/2, f'Tr{t+1}', ha='center', fontsize=6)
                    
                    # Cabecera Norte
                    ax.add_patch(patches.Rectangle((x_g, y_inicio_g + CABECERA_PROF + largo_g), GONDOLA_PROF, CABECERA_PROF, color='#E74C3C', ec='black'))
                    
                    # Pasillo de Góndola
                    pas_x = x_g - PASILLO_STD if x_g < conf['pos_puerta'] else x_g + GONDOLA_PROF
                    ax.add_patch(patches.Rectangle((pas_x, y_inicio_g), PASILLO_STD, largo_g + CABECERA_PROF*2, color='#EBEDEF', alpha=0.6))
                    ax.text(pas_x + PASILLO_STD/2, y_inicio_g + largo_g/2, 'PASILLO GÓNDOLAS', rotation=90, ha='center', va='center', fontsize=6, color='gray')
                    
                    obstaculos.append((x_g - PASILLO_STD, y_inicio_g - CABECERA_PROF, GONDOLA_PROF + PASILLO_STD*2, largo_g + CABECERA_PROF*2))
                    colocado = True
                    break
                x_g += 0.5 
            if colocado: x_g += GONDOLA_PROF + PASILLO_STD

    # ==========================================
    # 5. CAFÉ
    # ==========================================
    if conf['t_cafe'] and conf['t_gondolas']:
        ancho_cafe = conf['cant_cafe'] * MOD_2FT
        x_cafe = 0 if conf['loc_check'] == 'Esquina Inferior Derecha' else W - ancho_cafe
        y_cafe = 0
        
        if not colisiona(x_cafe, y_cafe, ancho_cafe, PROF_CAFE, obstaculos):
            for i in range(conf['cant_cafe']):
                ax.add_patch(patches.Rectangle((x_cafe + (i*MOD_2FT), y_cafe), MOD_2FT, PROF_CAFE, color='#FAD7A0', ec='black'))
                ax.text(x_cafe + (i*MOD_2FT) + MOD_2FT/2, y_cafe + PROF_CAFE/2, f'C{i+1}', ha='center', fontsize=6)
                
            # Pasillo Café
            ax.add_patch(patches.Rectangle((x_cafe, PROF_CAFE), ancho_cafe, PASILLO_STD, color='#FADBD8', alpha=0.5))
            ax.text(x_cafe + ancho_cafe/2, PROF_CAFE + PASILLO_STD/2, 'PASILLO CAFÉ', ha='center', fontsize=7, color='#E74C3C')
            
            obstaculos.append((x_cafe, y_cafe, ancho_cafe, PROF_CAFE + PASILLO_STD))

    # ==========================================
    # 6. GÓNDOLAS PERIMETRALES (Tramos 1ft)
    # ==========================================
    if conf['t_perimetral'] and conf['t_cafe']:
        def colocar_muro(x_base, y_base, largo_muro, vertical=True):
            tramos = int(largo_muro / MOD_1FT)
            for i in range(tramos):
                cx = x_base if vertical else x_base + (i*MOD_1FT)
                cy = y_base + (i*MOD_1FT) if vertical else y_base
                cw = PROF_PERIMETRO if vertical else MOD_1FT
                ch = MOD_1FT if vertical else PROF_PERIMETRO
                
                if not colisiona(cx, cy, cw, ch, obstaculos):
                    ax.add_patch(patches.Rectangle((cx, cy), cw, ch, color='#D5DBDB', ec='gray'))
                    ax.text(cx + cw/2, cy + ch/2, 'P', ha='center', va='center', fontsize=4, rotation=0 if vertical else 90)

        colocar_muro(0, 0, L, vertical=True) # Muro Izq
        colocar_muro(W - PROF_PERIMETRO, 0, L, vertical=True) # Muro Der
        colocar_muro(0, L - PROF_PERIMETRO, W, vertical=False) # Muro Fondo

    # ==========================================
    # 7. EXHIBIDORES DE PISO (ISLAS 60x60)
    # ==========================================
    if conf['t_islas'] and conf['t_perimetral']:
        islas_ok = 0
        for y_isla in range(2, int(L)-2): # Evitar bordes extremos
            for x_isla in range(1, int(W)-1):
                if islas_ok >= conf['cant_islas']: break
                
                # Probar si el espacio de 60x60cm está libre de muebles y pasillos
                if not colisiona(x_isla, y_isla, ISLA_DIM, ISLA_DIM, obstaculos):
                    ax.add_patch(patches.Rectangle((x_isla, y_isla), ISLA_DIM, ISLA_DIM, color='#F4D03F', ec='black'))
                    ax.text(x_isla + ISLA_DIM/2, y_isla + ISLA_DIM/2, f'E{islas_ok+1}', ha='center', va='center', fontsize=6)
                    obstaculos.append((x_isla - 0.2, y_isla - 0.2, ISLA_DIM + 0.4, ISLA_DIM + 0.4))
                    islas_ok += 1

    ax.set_aspect('equal')
    plt.title(f"Layout Secuencial V15.0 - Dimensiones: {W}m x {L}m")
    return fig

# --- INTERFAZ STREAMLIT ---
st.set_page_config(layout="wide")
st.title("🏗️ Diseñador Secuencial y Arquitectónico V15.0")

col_params, col_plot = st.columns([1.2, 2.8])

with col_params:
    st.header("Propiedades del Local")
    ancho = st.number_input("Ancho (m)", min_value=5.0, max_value=20.0, value=12.0, step=0.5)
    largo = st.number_input("Profundidad (m)", min_value=5.0, max_value=20.0, value=15.0, step=0.5)
    
    st.markdown("---")
    st.write("🔧 **Constructor de Flujos (Paso a Paso)**")
    
    # 1. PUERTA
    t_puerta = st.toggle("1. Activar Acceso y Pasillo de Poder")
    pos_puerta = 0.0
    if t_puerta:
        pos_puerta = st.slider("Separación desde pared izq.", 0.0, float(ancho-PUERTA_ANCHO), float(ancho/2 - PUERTA_ANCHO/2))
    
    # 2. CHECKOUT
    t_check, loc_check, cant_check = False, "", 0
    if t_puerta:
        t_check = st.toggle("2. Activar Checkout")
        if t_check:
            loc_check = st.selectbox("Esquina (Anclaje a Muro)", ['Esquina Inferior Derecha', 'Esquina Inferior Izquierda'])
            cant_check = st.slider("Módulos Checkout", min_value=1, max_value=5, value=3)

    # 3. CUARTO FRÍO
    t_frio, loc_frio, forma_frio, cant_frio = False, "", "", 0
    if t_check:
        t_frio = st.toggle("3. Activar Cuarto Frío")
        if t_frio:
            loc_frio = st.selectbox("Esquina Destino", ['Fondo Derecha', 'Fondo Izquierda'])
            forma_frio = st.radio("Formato", ['Lineal', 'Escuadra'], horizontal=True)
            cant_frio = st.slider("Puertas Frío", min_value=2, max_value=20, value=8)

    # 4. GÓNDOLAS
    t_gondolas, cant_trenes, cant_tramos = False, 0, 0
    if t_frio:
        t_gondolas = st.toggle("4. Activar Góndolas Centrales")
        if t_gondolas:
            cant_trenes = st.slider("Trenes Centrales", min_value=1, max_value=4, value=2)
            cant_tramos = st.slider("Tramos por tren", min_value=1, max_value=6, value=3)

    # 5. CAFÉ
    t_cafe, cant_cafe = False, 0
    if t_gondolas:
        t_cafe = st.toggle("5. Activar Área de Café")
        if t_cafe:
            cant_cafe = st.slider("Módulos Café", min_value=2, max_value=10, value=4)

    # 6. PERIMETRALES
    t_perimetral = False
    if t_cafe:
        t_perimetral = st.toggle("6. Activar Góndola Perimetral")
        if t_perimetral:
            st.caption("Tramos de 1ft etiquetados con 'P' en paredes libres.")

    # 7. ISLAS
    t_islas, cant_islas = False, 0
    if t_perimetral:
        t_islas = st.toggle("7. Activar Exhibidores de Piso")
        if t_islas:
            cant_islas = st.slider("Islas (60x60cm)", min_value=1, max_value=20, value=4)

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
    st.pyplot(dibujar_layout_v15(conf))
    
    st.info("""
    **Reglas Restablecidas (V15):**
    * **Dimensiones Oficiales:** Local ajustable de 5m a 20m. Módulos y límites restaurados (ej. hasta 20 puertas de frío, 10 de café).
    * **Identificación Visual:** Pasillos nombrados y cruzados (Poder, Cobro, Frío, etc.). Tramos de góndola (Tr1), Checkout (CHK1) y perimetrales (P) marcados individualmente.
    * **Anti-Colisión Total:** Las islas y perimetrales jamás invadirán los pasillos coloreados ni el área de descompresión.
    """)