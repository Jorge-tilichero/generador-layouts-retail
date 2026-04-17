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
    for (ox, oy, ow, oh) in obstaculos:
        if not (x + w <= ox or x >= ox + ow or y + h <= oy or y >= oy + oh):
            return True
    return False

def dibujar_layout_secuencial(conf):
    W, L = conf['ancho'], conf['largo']
    fig, ax = plt.subplots(figsize=(12, 12))
    ax.set_xlim(0, W)
    ax.set_ylim(0, L)
    
    obstaculos = []
    
    # Dibujar Muros Base
    ax.add_patch(patches.Rectangle((0, 0), W, L, fill=False, ec='black', lw=2))

    # ==========================================
    # 1. PUERTA Y PASILLO DE PODER
    # ==========================================
    if conf['t_puerta']:
        pos_p = conf['pos_puerta']
        # Puerta
        ax.add_patch(patches.Rectangle((pos_p, 0), PUERTA_ANCHO, 0.2, color='red'))
        ax.text(pos_p + PUERTA_ANCHO/2, 0.5, 'ACCESO', ha='center', fontsize=7, weight='bold', color='red')
        
        # Descompresión y Pasillo de Poder
        ax.add_patch(patches.Circle((pos_p + PUERTA_ANCHO/2, 0), 2.0, color='#85C1E9', alpha=0.3))
        ax.add_patch(patches.Rectangle((pos_p, 0), PUERTA_ANCHO, L, color='#EBF5FB', alpha=0.5))
        ax.text(pos_p + PUERTA_ANCHO/2, L/2, 'PASILLO DE PODER', rotation=90, ha='center', va='center', color='#21618C', weight='bold')
        
        obstaculos.append((pos_p - 0.5, 0, PUERTA_ANCHO + 1.0, L)) # Evitar bloquear el pasillo

    # ==========================================
    # 2. CHECKOUT EN ESQUINA
    # ==========================================
    if conf['t_check'] and conf['t_puerta']:
        ancho_check = conf['cant_check'] * MOD_2FT
        
        if conf['loc_check'] == 'Esquina Inferior Derecha':
            x_chk = W - ancho_check
            y_chk = 0
            # Contracaja pegada al muro inferior (Y=0), lateral derecho pegado a pared (X=W)
            ax.add_patch(patches.Rectangle((x_chk, y_chk), ancho_check, PROF_CONTRA, color='#82E0AA'))
            ax.add_patch(patches.Rectangle((x_chk, y_chk + PROF_CONTRA), ancho_check, PROF_CAJERO, color='#EAEDED'))
            ax.add_patch(patches.Rectangle((x_chk, y_chk + PROF_CONTRA + PROF_CAJERO), ancho_check, PROF_CHECK, color='#ABEBC6', ec='black'))
            ax.text(x_chk + ancho_check/2, y_chk + PROF_CONTRA + PROF_CAJERO + PROF_CHECK/2, 'CHECKOUT', ha='center', fontsize=7)
            
            # Pasillo Fila
            y_fila = y_chk + PROF_CONTRA + PROF_CAJERO + PROF_CHECK
            ax.add_patch(patches.Rectangle((x_chk, y_fila), ancho_check, PASILLO_STD, color='#D5F5E3', alpha=0.5))
            obstaculos.append((x_chk, 0, ancho_check, y_fila + PASILLO_STD))

        elif conf['loc_check'] == 'Esquina Inferior Izquierda':
            x_chk = 0
            y_chk = 0
            ax.add_patch(patches.Rectangle((x_chk, y_chk), ancho_check, PROF_CONTRA, color='#82E0AA'))
            ax.add_patch(patches.Rectangle((x_chk, y_chk + PROF_CONTRA), ancho_check, PROF_CAJERO, color='#EAEDED'))
            ax.add_patch(patches.Rectangle((x_chk, y_chk + PROF_CONTRA + PROF_CAJERO), ancho_check, PROF_CHECK, color='#ABEBC6', ec='black'))
            ax.text(x_chk + ancho_check/2, y_chk + PROF_CONTRA + PROF_CAJERO + PROF_CHECK/2, 'CHECKOUT', ha='center', fontsize=7)
            
            y_fila = y_chk + PROF_CONTRA + PROF_CAJERO + PROF_CHECK
            ax.add_patch(patches.Rectangle((x_chk, y_fila), ancho_check, PASILLO_STD, color='#D5F5E3', alpha=0.5))
            obstaculos.append((x_chk, 0, ancho_check, y_fila + PASILLO_STD))

    # ==========================================
    # 3. CUARTO FRÍO
    # ==========================================
    if conf['t_frio'] and conf['t_check']:
        ptas = conf['cant_frio']
        loc_frio = conf['loc_frio']
        forma_frio = conf['forma_frio']
        
        y_frio = L - PROF_FRIO
        x_frio = 0 if loc_frio == 'Fondo Izquierda' else W - (ptas * MOD_2FT)
        
        if forma_frio == 'Lineal':
            ancho_frio = ptas * MOD_2FT
            ax.add_patch(patches.Rectangle((x_frio, y_frio), ancho_frio, PROF_FRIO, color='#AED6F1', ec='black'))
            ax.text(x_frio + ancho_frio/2, y_frio + PROF_FRIO/2, f'FRÍO ({ptas}P)', ha='center', va='center')
            obstaculos.append((x_frio, y_frio - PASILLO_STD, ancho_frio, PROF_FRIO + PASILLO_STD))
            
        else: # Escuadra
            ptas_fondo = int(ptas * 0.6) # 60% al fondo, 40% lateral
            ptas_lat = ptas - ptas_fondo
            ancho_fondo = ptas_fondo * MOD_2FT
            largo_lat = ptas_lat * MOD_2FT
            
            if loc_frio == 'Fondo Izquierda':
                # Fondo
                ax.add_patch(patches.Rectangle((0, y_frio), ancho_fondo, PROF_FRIO, color='#AED6F1', ec='black'))
                # Lateral
                ax.add_patch(patches.Rectangle((0, y_frio - largo_lat), PROF_FRIO, largo_lat, color='#AED6F1', ec='black'))
                obstaculos.append((0, y_frio - largo_lat - PASILLO_STD, max(ancho_fondo, PROF_FRIO + PASILLO_STD), PROF_FRIO + largo_lat + PASILLO_STD))
            else: # Fondo Derecha
                x_f = W - ancho_fondo
                ax.add_patch(patches.Rectangle((x_f, y_frio), ancho_fondo, PROF_FRIO, color='#AED6F1', ec='black'))
                ax.add_patch(patches.Rectangle((W - PROF_FRIO, y_frio - largo_lat), PROF_FRIO, largo_lat, color='#AED6F1', ec='black'))
                obstaculos.append((W - max(ancho_fondo, PROF_FRIO + PASILLO_STD), y_frio - largo_lat - PASILLO_STD, max(ancho_fondo, PROF_FRIO + PASILLO_STD), PROF_FRIO + largo_lat + PASILLO_STD))

    # ==========================================
    # 4. GÓNDOLAS CENTRALES
    # ==========================================
    if conf['t_gondolas'] and conf['t_frio']:
        y_inicio_g = 4.0 # Respetar checkout/accesos
        x_g = PASILLO_STD + PROF_PERIMETRO
        
        for i in range(conf['cant_trenes']):
            largo_g = conf['cant_tramos'] * MOD_3FT
            # Buscar espacio que no colisione
            while x_g + GONDOLA_PROF < W:
                if not colisiona(x_g, y_inicio_g, GONDOLA_PROF, largo_g + CABECERA_PROF*2, obstaculos):
                    ax.add_patch(patches.Rectangle((x_g, y_inicio_g), GONDOLA_PROF, largo_g, color='#ABB2B9', ec='black'))
                    ax.add_patch(patches.Rectangle((x_g, y_inicio_g - CABECERA_PROF), GONDOLA_PROF, CABECERA_PROF, color='#E74C3C'))
                    ax.add_patch(patches.Rectangle((x_g, y_inicio_g + largo_g), GONDOLA_PROF, CABECERA_PROF, color='#E74C3C'))
                    obstaculos.append((x_g - PASILLO_STD/2, y_inicio_g - CABECERA_PROF, GONDOLA_PROF + PASILLO_STD, largo_g + CABECERA_PROF*2))
                    break
                x_g += 0.5 # Mover a la derecha y reintentar
            x_g += GONDOLA_PROF + PASILLO_STD

    # ==========================================
    # 5. MÓDULOS DE CAFÉ
    # ==========================================
    if conf['t_cafe'] and conf['t_gondolas']:
        ancho_cafe = conf['cant_cafe'] * MOD_2FT
        # Buscar esquina disponible (opuesta al checkout si es posible)
        x_cafe = 0 if conf['loc_check'] == 'Esquina Inferior Derecha' else W - ancho_cafe
        y_cafe = 0
        
        if not colisiona(x_cafe, y_cafe, ancho_cafe, PROF_CAFE, obstaculos):
            for i in range(conf['cant_cafe']):
                ax.add_patch(patches.Rectangle((x_cafe + (i*MOD_2FT), y_cafe), MOD_2FT, PROF_CAFE, color='#FAD7A0', ec='black'))
            ax.text(x_cafe + ancho_cafe/2, y_cafe + PROF_CAFE/2, 'CAFÉ', ha='center', fontsize=7)
            obstaculos.append((x_cafe, y_cafe, ancho_cafe, PROF_CAFE + PASILLO_STD))

    # ==========================================
    # 6. GÓNDOLAS PERIMETRALES
    # ==========================================
    if conf['t_perimetral'] and conf['t_cafe']:
        # Muro Izquierdo
        for i in range(int(L/MOD_1FT)):
            y_per = i * MOD_1FT
            if not colisiona(0, y_per, PROF_PERIMETRO, MOD_1FT, obstaculos):
                ax.add_patch(patches.Rectangle((0, y_per), PROF_PERIMETRO, MOD_1FT, color='#D5DBDB', ec='gray'))
        
        # Muro Derecho
        for i in range(int(L/MOD_1FT)):
            y_per = i * MOD_1FT
            if not colisiona(W - PROF_PERIMETRO, y_per, PROF_PERIMETRO, MOD_1FT, obstaculos):
                ax.add_patch(patches.Rectangle((W - PROF_PERIMETRO, y_per), PROF_PERIMETRO, MOD_1FT, color='#D5DBDB', ec='gray'))

    # ==========================================
    # 7. EXHIBIDORES DE PISO (ISLAS)
    # ==========================================
    if conf['t_islas'] and conf['t_perimetral']:
        islas_colocadas = 0
        for y_isla in range(int(L)):
            for x_isla in range(int(W)):
                if islas_colocadas >= conf['cant_islas']: break
                
                # Probar colocar isla en zonas centrales
                if not colisiona(x_isla, y_isla, ISLA_DIM, ISLA_DIM, obstaculos) and (PASILLO_STD < x_isla < W-PASILLO_STD):
                    ax.add_patch(patches.Rectangle((x_isla, y_isla), ISLA_DIM, ISLA_DIM, color='#F4D03F', ec='black'))
                    ax.text(x_isla + ISLA_DIM/2, y_isla + ISLA_DIM/2, f'E{islas_colocadas+1}', ha='center', va='center', fontsize=6)
                    obstaculos.append((x_isla - 0.3, y_isla - 0.3, ISLA_DIM + 0.6, ISLA_DIM + 0.6))
                    islas_colocadas += 1

    ax.set_aspect('equal')
    plt.title("Layout Secuencial Activo")
    return fig

# --- INTERFAZ STREAMLIT ---
st.set_page_config(layout="wide")
st.title("🏗️ Diseñador Secuencial V14.0")

col_params, col_plot = st.columns([1, 2.5])

with col_params:
    st.header("Propiedades del Local")
    ancho = st.number_input("Ancho (m)", 10.0, 25.0, 15.0)
    largo = st.number_input("Profundidad (m)", 15.0, 30.0, 20.0)
    
    st.markdown("---")
    st.write("🔧 **Constructor de Flujos**")
    
    # 1. PUERTA
    t_puerta = st.toggle("1. Activar Acceso y Pasillo de Poder")
    pos_puerta = 0.0
    if t_puerta:
        pos_puerta = st.slider("Separación desde pared izq.", 0.0, ancho-PUERTA_ANCHO, ancho/2 - PUERTA_ANCHO/2)
    
    # 2. CHECKOUT
    t_check, loc_check, cant_check = False, "", 0
    if t_puerta:
        t_check = st.toggle("2. Activar Checkout")
        if t_check:
            loc_check = st.selectbox("Ubicación (Pegado a pared)", ['Esquina Inferior Derecha', 'Esquina Inferior Izquierda'])
            cant_check = st.slider("Módulos de cobro", 1, 4, 3)
            st.caption("Contracaja y lateral se anclarán a los muros automáticamente.")

    # 3. CUARTO FRÍO
    t_frio, loc_frio, forma_frio, cant_frio = False, "", "", 0
    if t_check:
        t_frio = st.toggle("3. Activar Cuarto Frío")
        if t_frio:
            loc_frio = st.selectbox("Esquina Destino", ['Fondo Izquierda', 'Fondo Derecha'])
            forma_frio = st.radio("Formato de instalación", ['Lineal', 'Escuadra'])
            cant_frio = st.slider("Total de Puertas", 4, 15, 8)

    # 4. GÓNDOLAS
    t_gondolas, cant_trenes, cant_tramos = False, 0, 0
    if t_frio:
        t_gondolas = st.toggle("4. Activar Góndolas Centrales")
        if t_gondolas:
            cant_trenes = st.number_input("Trenes Centrales", 1, 5, 2)
            cant_tramos = st.number_input("Tramos por tren", 1, 8, 3)

    # 5. CAFÉ
    t_cafe, cant_cafe = False, 0
    if t_gondolas:
        t_cafe = st.toggle("5. Activar Área de Café")
        if t_cafe:
            cant_cafe = st.slider("Módulos de Café", 2, 8, 4)
            st.caption("Se posicionará en la esquina frontal libre.")

    # 6. PERIMETRALES
    t_perimetral = False
    if t_cafe:
        t_perimetral = st.toggle("6. Activar Góndola Perimetral")
        if t_perimetral:
            st.caption("Tramos de 1ft colocados en espacios de pared disponibles.")

    # 7. ISLAS
    t_islas, cant_islas = False, 0
    if t_perimetral:
        t_islas = st.toggle("7. Activar Exhibidores (Islas 60x60)")
        if t_islas:
            cant_islas = st.number_input("Cantidad", 1, 10, 4)

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
    st.pyplot(dibujar_layout_secuencial(conf))