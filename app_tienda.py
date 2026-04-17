import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import math
import io

# --- CONSTANTES ---
FT_M = 0.3048
IN_M = 0.0254
PUERTA_FRIO = 24 * IN_M
MODULO_2FT = 2 * FT_M
TRAMO_GONDOLA = 3 * FT_M
ISLA = 0.60

def dibujar_layout_esquinas(ancho, largo, pasillo_min, cant_puertas_frio):
    fig, ax = plt.subplots(figsize=(10, 12))
    ax.set_xlim(0, ancho)
    ax.set_ylim(0, largo)
    
    area_total = ancho * largo
    area_exh = 0
    
    # 1. BODEGA (Esquina Superior Derecha - 20% del área)
    area_bodega = area_total * 0.20
    # Asumimos que la bodega toma la mitad del ancho del fondo
    ancho_bodega = ancho * 0.4 
    prof_bodega = area_bodega / ancho_bodega
    ax.add_patch(patches.Rectangle((ancho - ancho_bodega, largo - prof_bodega), ancho_bodega, prof_bodega, color='#D2B48C', alpha=0.8))
    plt.text(ancho - ancho_bodega/2, largo - prof_bodega/2, 'BODEGA', ha='center', va='center')
    
    # Puerta interna de bodega
    ax.add_patch(patches.Rectangle((ancho - ancho_bodega - 0.5, largo - prof_bodega + 0.5), 0.5, 1.0, color='brown'))
    
    # 2. CUARTO FRÍO (Esquina Superior Izquierda y posible Escuadra)
    prof_frio = 2.0
    ancho_frio_disponible_fondo = ancho - ancho_bodega
    puertas_max_fondo = math.floor(ancho_frio_disponible_fondo / PUERTA_FRIO)
    
    if cant_puertas_frio <= puertas_max_fondo:
        # Cabe lineal en el fondo
        ancho_frio_real = cant_puertas_frio * PUERTA_FRIO
        ax.add_patch(patches.Rectangle((0, largo - prof_frio), ancho_frio_real, prof_frio, color='#AED6F1'))
        plt.text(ancho_frio_real/2, largo - prof_frio/2, f'FRÍO ({cant_puertas_frio}P)', ha='center', va='center')
        area_exh += (ancho_frio_real * prof_frio)
        y_fin_gondolas = largo - prof_frio - pasillo_min
        x_inicio_gondolas = pasillo_min
    else:
        # No cabe, hacemos ESCUADRA (L-Shape) bajando por la pared izquierda
        # Parte 1: Fondo
        ax.add_patch(patches.Rectangle((0, largo - prof_frio), ancho_frio_disponible_fondo, prof_frio, color='#AED6F1'))
        area_exh += (ancho_frio_disponible_fondo * prof_frio)
        
        # Parte 2: Lateral Izquierdo
        puertas_restantes = cant_puertas_frio - puertas_max_fondo
        largo_frio_lateral = puertas_restantes * PUERTA_FRIO
        ax.add_patch(patches.Rectangle((0, largo - prof_frio - largo_frio_lateral), prof_frio, largo_frio_lateral, color='#AED6F1'))
        area_exh += (prof_frio * largo_frio_lateral)
        plt.text(prof_frio/2, largo - prof_frio - largo_frio_lateral/2, 'FRÍO\n(L)', ha='center', va='center', rotation=90)
        
        y_fin_gondolas = largo - prof_frio - pasillo_min
        x_inicio_gondolas = prof_frio + pasillo_min # Empujamos las góndolas hacia la derecha por la L

    # 3. CHECKOUT Y ACCESO (Esquina Inferior Derecha)
    modulos_checkout = 4
    ancho_checkout = modulos_checkout * MODULO_2FT
    prof_checkout = 2.0
    x_checkout = ancho - ancho_checkout
    ax.add_patch(patches.Rectangle((x_checkout, 0), ancho_checkout, prof_checkout, color='#ABEBC6'))
    plt.text(x_checkout + ancho_checkout/2, prof_checkout/2, 'CHECKOUT', ha='center', va='center')
    area_exh += (ancho_checkout * prof_checkout)
    
    # El Acceso se dibuja justo a la izquierda del Checkout (Flexible)
    ancho_acceso = 2.0
    plt.plot([x_checkout - ancho_acceso, x_checkout], [0, 0], color='red', linewidth=8, label="Puerta")
    
    # 4. CAFÉ / GRAB & GO (Esquina Inferior Izquierda)
    modulos_cafe = 4
    ancho_cafe = modulos_cafe * MODULO_2FT
    prof_cafe = 1.5
    ax.add_patch(patches.Rectangle((0, 0), ancho_cafe, prof_cafe, color='#FAD7A0'))
    plt.text(ancho_cafe/2, prof_cafe/2, 'CAFÉ', ha='center', va='center')
    area_exh += (ancho_cafe * prof_cafe)

    # 5. GÓNDOLAS CENTRALES
    y_inicio_gondolas = max(prof_checkout, prof_cafe) + pasillo_min + ISLA + pasillo_min
    largo_disponible = y_fin_gondolas - y_inicio_gondolas
    
    ancho_gondola = 1.0
    x_actual = x_inicio_gondolas
    
    while x_actual + ancho_gondola <= ancho - pasillo_min:
        ax.add_patch(patches.Rectangle((x_actual, y_inicio_gondolas), ancho_gondola, largo_disponible, color='#ABB2B9'))
        area_exh += (ancho_gondola * largo_disponible)
        x_actual += ancho_gondola + pasillo_min

    # 6. EXHIBIDORES DE PISO (Islas en espacios restantes)
    # Colocamos una fila de islas entre el Café/Checkout y las Góndolas
    y_islas = max(prof_checkout, prof_cafe) + pasillo_min
    x_isla = x_inicio_gondolas
    while x_isla + ISLA <= x_checkout: # Hasta llegar a la zona del checkout
        ax.add_patch(patches.Rectangle((x_isla, y_islas), ISLA, ISLA, color='#F4D03F'))
        area_exh += (ISLA**2)
        x_isla += ISLA + pasillo_min

    # KPIs
    area_piso = area_total - area_bodega
    pct_exh = (area_exh / area_piso) * 100

    ax.set_aspect('equal')
    plt.title(f"Configuración 4 Esquinas | Exhibición: {pct_exh:.1f}%")
    plt.legend(loc='upper right')
    return fig, pct_exh, area_total

# --- UI STREAMLIT ---
st.title("🏗️ Diseñador Inteligente - Sistema de Esquinas")

col_params, col_img = st.columns([1, 2])

with col_params:
    st.header("Medidas y Requerimientos")
    ancho = st.number_input("Ancho del local (mts)", 8.0, 30.0, 12.0)
    largo = st.number_input("Largo del local (mts)", 10.0, 50.0, 20.0)
    pasillo = st.slider("Pasillo mínimo (mts)", 1.2, 2.0, 1.2)
    puertas_frio = st.number_input("Cantidad de Puertas de Frío (24\")", 4, 30, 12)
    
    st.info("💡 **Lógica activa:** Bodega/Frío atrás, Checkout/Café al frente. Escuadra automática para Frío.")

with col_img:
    fig, p_exh, a_tot = dibujar_layout_esquinas(ancho, largo, pasillo, puertas_frio)
    st.pyplot(fig)
    
    if 30 <= p_exh <= 40:
        st.success(f"Métricas en rango: {p_exh:.1f}% Muebles vs Navegación")
    else:
        st.warning(f"Fuera de rango (30-40%): {p_exh:.1f}%")