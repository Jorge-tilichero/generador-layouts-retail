import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import math

# --- CONSTANTES ---
FT_M = 0.3048
IN_M = 0.0254
MOD_2FT = 2 * FT_M    
MOD_3FT = 3 * FT_M    
GONDOLA_PROF = 0.90   
CABECERA_PROF = 0.45  
PUERTA_ANCHO = 1.80   
PUERTA_FRIO = 24 * IN_M
ISLA_DIM = 0.60

def dibujar_layout_v6(conf):
    ancho = conf['ancho']
    largo = conf['largo']
    
    fig, ax = plt.subplots(figsize=(10, 12))
    ax.set_xlim(0, ancho)
    ax.set_ylim(0, largo)
    
    # === 1. ZONAS DE FLUJO Y PASILLO DE PODER (Intocables) ===
    # Definir posición de puerta
    if conf['puerta_loc'] == 'Centro':
        x_puerta_centro = ancho / 2
    elif conf['puerta_loc'] == 'Izquierda':
        x_puerta_centro = PUERTA_ANCHO / 2 + 1.0 # 1m de separación de la pared
    else: # Derecha
        x_puerta_centro = ancho - (PUERTA_ANCHO / 2) - 1.0

    x_inicio_pasillo = x_puerta_centro - PUERTA_ANCHO/2
    
    # Dibujar Pasillo de Poder (Libre de obstáculos)
    ax.add_patch(patches.Rectangle((x_inicio_pasillo, 0), PUERTA_ANCHO, largo, color='#EBF5FB', alpha=0.6, label='Pasillo Poder'))
    # Zona de Descompresión (2m)
    ax.add_patch(patches.Circle((x_puerta_centro, 0), 2.0, color='#85C1E9', alpha=0.3))

    # === 2. BODEGA ===
    area_bodega = (ancho * largo) * 0.20
    if conf['bodega_loc'] == 'Fondo Completo':
        prof_bodega = area_bodega / ancho
        rect_bodega = (0, largo - prof_bodega, ancho, prof_bodega)
    elif conf['bodega_loc'] == 'Fondo Izquierda':
        ancho_bodega = ancho / 2
        prof_bodega = area_bodega / ancho_bodega
        rect_bodega = (0, largo - prof_bodega, ancho_bodega, prof_bodega)
    else: # Fondo Derecha
        ancho_bodega = ancho / 2
        prof_bodega = area_bodega / ancho_bodega
        rect_bodega = (ancho - ancho_bodega, largo - prof_bodega, ancho_bodega, prof_bodega)

    ax.add_patch(patches.Rectangle((rect_bodega[0], rect_bodega[1]), rect_bodega[2], rect_bodega[3], color='#D2B48C'))
    plt.text(rect_bodega[0] + rect_bodega[2]/2, rect_bodega[1] + rect_bodega[3]/2, 'BODEGA', ha='center', va='center', fontsize=9)

    # === 3. CUARTO FRÍO ===
    ancho_frio = conf['cant_frio'] * PUERTA_FRIO
    y_frio = rect_bodega[1] - 2.0 # Se coloca justo delante de la línea de bodega
    
    if conf['bodega_loc'] == 'Fondo Derecha':
        x_frio = 0 # Frio a la izquierda
    elif conf['bodega_loc'] == 'Fondo Izquierda':
        x_frio = ancho - ancho_frio # Frio a la derecha
    else:
        x_frio = (ancho - ancho_frio) / 2 # Centro
        
    ax.add_patch(patches.Rectangle((x_frio, y_frio), ancho_frio, 2.0, color='#AED6F1'))
    plt.text(x_frio + ancho_frio/2, y_frio + 1.0, f'FRÍO ({conf["cant_frio"]}P)', ha='center', va='center')
    
    # Pasillo Frío (1.20m libre)
    y_limite_frio = y_frio - 1.20
    ax.add_patch(patches.Rectangle((0, y_limite_frio), ancho, 1.20, color='#FCF3CF', alpha=0.3))

    # === 4. CHECKOUT Y CAFÉ ===
    # Checkout
    ancho_check = 3 * MOD_2FT # Fijo a 3 modulos para simplificar
    x_check = ancho - ancho_check
    ax.add_patch(patches.Rectangle((x_check, 2.5), ancho_check, 0.60, color='#ABEBC6'))
    ax.add_patch(patches.Rectangle((x_check, 2.5 - 1.20), ancho_check, 1.20, color='#FADBD8', alpha=0.4)) # Fila Libre
    
    # Café
    ancho_cafe = conf['cant_cafe'] * MOD_2FT
    ax.add_patch(patches.Rectangle((0, 0), ancho_cafe, 1.5, color='#FAD7A0'))
    plt.text(ancho_cafe/2, 0.75, f'CAFÉ ({conf["cant_cafe"]} mod)', ha='center', va='center', fontsize=8)

    # === 5. TRENES DE GÓNDOLAS ===
    largo_tren = CABECERA_PROF*2 + (conf['cant_tramos'] * MOD_3FT)
    y_inicio_gondolas = 4.0
    
    # Posicionamiento seguro de góndolas (evitando pasillo de poder)
    x_actual_izq = x_inicio_pasillo - 1.20 - GONDOLA_PROF # 1.20m de pasillo
    x_actual_der = x_inicio_pasillo + PUERTA_ANCHO + 1.20
    
    trenes_dibujados = 0
    zonas_seguras_islas = [] # Guardaremos coordenadas donde podemos poner exhibidores
    
    # Intentar colocar trenes a la izquierda
    while trenes_dibujados < conf['cant_trenes'] / 2 and x_actual_izq > 0:
        ax.add_patch(patches.Rectangle((x_actual_izq, y_inicio_gondolas), GONDOLA_PROF, largo_tren, color='#ABB2B9'))
        ax.add_patch(patches.Rectangle((x_actual_izq, y_inicio_gondolas), GONDOLA_PROF, CABECERA_PROF, color='#E74C3C'))
        ax.add_patch(patches.Rectangle((x_actual_izq, y_inicio_gondolas + largo_tren - CABECERA_PROF), GONDOLA_PROF, CABECERA_PROF, color='#E74C3C'))
        
        # Guardar zona frente a cabecera para posibles islas
        zonas_seguras_islas.append((x_actual_izq, y_inicio_gondolas - 1.0))
        
        x_actual_izq -= (GONDOLA_PROF + 1.20)
        trenes_dibujados += 1

    # Intentar colocar trenes a la derecha
    while trenes_dibujados < conf['cant_trenes'] and x_actual_der + GONDOLA_PROF < ancho:
        ax.add_patch(patches.Rectangle((x_actual_der, y_inicio_gondolas), GONDOLA_PROF, largo_tren, color='#ABB2B9'))
        ax.add_patch(patches.Rectangle((x_actual_der, y_inicio_gondolas), GONDOLA_PROF, CABECERA_PROF, color='#E74C3C'))
        ax.add_patch(patches.Rectangle((x_actual_der, y_inicio_gondolas + largo_tren - CABECERA_PROF), GONDOLA_PROF, CABECERA_PROF, color='#E74C3C'))
        
        # Guardar zona frente a cabecera para posibles islas
        zonas_seguras_islas.append((x_actual_der, y_inicio_gondolas - 1.0))
        
        x_actual_der += (GONDOLA_PROF + 1.20)
        trenes_dibujados += 1

    # === 6. EXHIBIDORES (Islas Promocionales en Zonas Seguras) ===
    # En lugar de ponerlas en el pasillo central, las agrupamos cerca de la descompresión/café/checkout, fuera del flujo
    islas_colocadas = 0
    x_promo