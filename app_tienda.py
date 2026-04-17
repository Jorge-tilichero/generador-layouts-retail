class OxxoStorePlanner:
    def __init__(self, m2_totales):
        """
        Inicializa el planificador con el total de metros cuadrados del layout arquitectónico.
        """
        self.m2_totales = m2_totales

    def clasificar_formato(self):
        """
        Clasifica el formato de la tienda basado en la Matriz de Distribución Espacial.
        """
        m2 = self.m2_totales
        if 5 <= m2 <= 15:
            return "BOOTH (Compacto)"
        elif 16 <= m2 <= 36:
            return "MINI (Compacto)"
        elif 37 <= m2 <= 56:
            return "MINI 2 (Compacto)"
        elif 57 <= m2 <= 77:
            return "MEDIA (Reducido)"
        elif 78 <= m2 <= 98:
            return "MEDIA 2 (Reducido)"
        elif 99 <= m2 <= 117:
            return "REGULAR (Ordinario)"
        elif 118 <= m2 <= 135:
            return "MINIMO 2 (Ordinario)"
        elif 136 <= m2 <= 154:
            return "OPTIMO (Ordinario)"
        elif 155 <= m2 <= 170:
            return "OPTIMO 2 (Ordinario)"
        elif 171 <= m2 <= 250:
            return "MAXIMO (Extra Ordinario)"
        elif m2 > 250:
            return "MEGA (Casos Particulares)"
        else:
            return "Formato no clasificado o m2 inválidos"

    def calcular_distribucion_areas(self):
        """
        Calcula el balanceo de m2 (Regla 80/20 y 60/40) para rentabilidad y experiencia.
        """
        # Distribución principal de la tienda (100%)
        area_comercial = self.m2_totales * 0.80
        area_operativa = self.m2_totales * 0.20

        # Sub-distribución del Área Operativa (20% del total)
        # Nota: El manual marca 65%, 15% y 10% explícitamente como guías proporcionales.
        almacenar = area_operativa * 0.65
        operar = area_operativa * 0.15
        habitar = area_operativa * 0.10

        # Sub-distribución del Área Comercial (80% del total) -> Piso de venta
        espacios_exhibicion = area_comercial * 0.40
        espacios_navegacion = area_comercial * 0.60

        return {
            "M2 Totales": round(self.m2_totales, 2),
            "Area Operativa (20%)": {
                "Total": round(area_operativa, 2),
                "Almacenar (~65%)": round(almacenar, 2),
                "Operar (~15%)": round(operar, 2),
                "Habitar (~10%)": round(habitar, 2)
            },
            "Area Comercial (80%)": {
                "Total": round(area_comercial, 2),
                "Espacios de Exhibicion (~40%)": round(espacios_exhibicion, 2),
                "Espacios de Navegacion (~60%)": round(espacios_navegacion, 2)
            }
        }

    def obtener_reglas_4_elementos(self):
        """
        Retorna las directrices de ubicación de los 4 elementos principales del layout.
        """
        return {
            "1. Acceso": "Punto de partida. Ajusta su ubicación conforme el resto se adecúa.",
            "2. Check Out": "Debe estar lo más cercano al ACCESO (punto final/inicio del recorrido).",
            "3. Espacio Operativo": "Fácil acceso hacia el interior, sin generar espacios muertos en piso de venta.",
            "4. Cuarto Frio (CF)": "Ubicación perimetral, buscando estar lo más alejado al ACCESO."
        }

    def obtener_jerarquia_visual(self):
        """
        Retorna las reglas de 'Landscaping' o jerarquía visual del mobiliario.
        """
        return {
            "Regla General": "Primero lo más bajo y al fondo lo más alto.",
            "Acceso/Servicio": "Alturas bajas (3.5 ft - 4.5 ft) cerca de la entrada.",
            "Mobiliario Central": "Alturas medias (3 ft - 4.5 ft). Ej. Rack Tarima, Góndola Central.",
            "Mobiliario Perimetral": "Alturas máximas (6.5 ft - 7 ft) en las paredes alejadas. Ej. Enfriadores, Góndola Alta."
        }

# ==========================================
# EJEMPLO DE USO DEL SCRIPT
# ==========================================
if __name__ == "__main__":
    # Supongamos que tenemos un local de 140 m2
    m2_proyecto = 140
    planificador = OxxoStorePlanner(m2_proyecto)

    print(f"--- PLANEACIÓN DE TIENDA OXXO ({m2_proyecto} m2) ---")
    print(f"Formato Sugerido: {planificador.clasificar_formato()}\n")

    print("--- DISTRIBUCIÓN DE ÁREAS (Balance Rentabilidad/Experiencia) ---")
    distribucion = planificador.calcular_distribucion_areas()
    import json
    print(json.dumps(distribucion, indent=4))
    print("\n")

    print("--- REGLAS DE UBICACIÓN (4 ELEMENTOS) ---")
    elementos = planificador.obtener_reglas_4_elementos()
    for elemento, regla in elementos.items():
        print(f"{elemento}: {regla}")
    print("\n")

    print("--- JERARQUÍA VISUAL (LANDSCAPING) ---")
    jerarquia = planificador.obtener_jerarquia_visual()
    for zona, altura in jerarquia.items():
        print(f"{zona}: {altura}")