import streamlit as st

# ----------- FUNCIONES ------------
def calcular_tmb(peso, altura_cm, edad, genero):
    if genero.lower() == "m":
        return (10 * peso) + (6.25 * altura_cm) - (5 * edad) + 5
    else:
        return (10 * peso) + (6.25 * altura_cm) - (5 * edad) - 161


def calcular_imc(peso, altura_cm):
    altura_m = altura_cm / 100
    return peso / (altura_m ** 2)


def calcular_get(tmb, actividad):
    return tmb * actividad


# ----------- PESTAÑAS ------------
tab1, tab2 = st.tabs(["🧮 Calculadora Nutricional", "💬 WhatsApp Message"])

# ----------- TAB 1: Calculadora Nutricional ------------
with tab1:
    st.title("📊 Calculadora Nutricional")

    # Entrada de datos del usuario
    nombre = st.text_input("Ingrese su nombre:", value=st.session_state.get("nombre", ""))
    edad = st.number_input("Ingrese su edad (años):", min_value=1, max_value=120, step=1,
                           value=st.session_state.get("edad", 25))
    peso = st.number_input("Ingrese su peso (kg):", min_value=1.0, max_value=300.0, step=0.1,
                           value=st.session_state.get("peso", 70.0))
    altura_cm = st.number_input("Ingrese su altura (cm):", min_value=50, max_value=250, step=1,
                                value=st.session_state.get("altura", 170))
    genero = st.radio("Seleccione su género:", ["M", "F"], index=0 if st.session_state.get("genero", "M") == "M" else 1)

    st.session_state["nombre"] = nombre
    st.session_state["edad"] = edad
    st.session_state["peso"] = peso
    st.session_state["altura"] = altura_cm
    st.session_state["genero"] = genero

    # Nivel de actividad física
    actividad_opciones = {
        "Poco o ningún ejercicio": 1.2,
        "Ligero": 1.375,
        "Moderado": 1.55,
        "Fuerte": 1.725,
        "Muy fuerte": 1.9
    }
    actividad = st.selectbox("Seleccione su nivel de actividad física:", list(actividad_opciones.keys()), index=2)
    factor_actividad = actividad_opciones[actividad]

    if st.button("Calcular"):
        tmb = calcular_tmb(peso, altura_cm, edad, genero)
        imc = calcular_imc(peso, altura_cm)
        get = calcular_get(tmb, factor_actividad)

        st.session_state["tmb"] = tmb
        st.session_state["imc"] = imc
        st.session_state["get"] = get

        st.write(f"**{nombre}, aquí están sus resultados:**")
        st.write(f"✅ **IMC:** {imc:.2f}")

        if imc < 18.5:
            st.warning("Clasificación: Bajo peso")
        elif imc < 25:
            st.success("Clasificación: Peso normal")
        elif imc < 30:
            st.warning("Clasificación: Sobrepeso")
        else:
            st.error("Clasificación: Obesidad")

        st.write(f"🔥 **TMB:** {tmb:.2f} kcal")
        st.write(f"⚡ **GET:** {get:.2f} kcal")

    if "get" in st.session_state:
        st.subheader("📌 Distribución calórica de macronutrientes (en %)")

        if "porc_carbs" not in st.session_state:
            st.session_state["porc_carbs"] = 50.0
        if "porc_prot" not in st.session_state:
            st.session_state["porc_prot"] = 25.0
        if "porc_lipidos" not in st.session_state:
            st.session_state["porc_lipidos"] = 25.0

        porc_carbs = st.number_input("Carbohidratos (%):", min_value=0.0, max_value=100.0, step=1.0,
                                     value=st.session_state["porc_carbs"])
        porc_prot = st.number_input("Proteínas (%):", min_value=0.0, max_value=100.0, step=1.0,
                                    value=st.session_state["porc_prot"])
        porc_lipidos = st.number_input("Lípidos (%):", min_value=0.0, max_value=100.0, step=1.0,
                                       value=st.session_state["porc_lipidos"])

        st.session_state["porc_carbs"] = porc_carbs
        st.session_state["porc_prot"] = porc_prot
        st.session_state["porc_lipidos"] = porc_lipidos

        suma_porcentajes = porc_carbs + porc_prot + porc_lipidos

        if suma_porcentajes != 100:
            st.warning("⚠️ Los porcentajes deben sumar exactamente 100%. Ajuste los valores.")
        else:
            cal_carbs = (st.session_state["get"] * porc_carbs) / 100
            cal_prot = (st.session_state["get"] * porc_prot) / 100
            cal_lipidos = (st.session_state["get"] * porc_lipidos) / 100

            g_carbs = cal_carbs / 4
            g_prot = cal_prot / 4
            g_lipidos = cal_lipidos / 9

            st.success("✅ Distribución calórica válida.")
            st.write("### 🍽️ Distribución de macronutrientes")
            st.table({
                "Macronutriente": ["Carbohidratos", "Proteínas", "Lípidos", "Total"],
                "Gramos": [f"{g_carbs:.2f} g", f"{g_prot:.2f} g", f"{g_lipidos:.2f} g",
                           f"{(g_carbs + g_prot + g_lipidos):.2f} g"],
                "Kcal": [f"{cal_carbs:.2f} kcal", f"{cal_prot:.2f} kcal", f"{cal_lipidos:.2f} kcal",
                         f"{st.session_state['get']:.2f} kcal"],
                "Porcentaje": [f"{porc_carbs}%", f"{porc_prot}%", f"{porc_lipidos}%", "100%"],
                "Gramos por kg de peso": [f"{g_carbs / peso:.2f} g/kg", f"{g_prot / peso:.2f} g/kg", f"{g_lipidos / peso:.2f} g/kg", "-"]
            })

# ----------- TAB 2: WhatsApp Message ------------
with tab2:
    st.title("💬 Enviar mensaje por WhatsApp")

    nombre_destinatario = st.text_input("Nombre del destinatario:")
    mensaje = st.text_area("Mensaje a enviar:")
    numero = st.text_input("Número de WhatsApp (con código de país, sin +)", max_chars=15)

    if st.button("Generar enlace de WhatsApp"):
        if numero and mensaje:
            mensaje_codificado = mensaje.replace(" ", "%20")
            enlace = f"https://wa.me/{numero}?text={mensaje_codificado}"

            st.success("✅ Enlace generado:")
            st.markdown(f"[Haz clic aquí para abrir WhatsApp]({enlace})")
        else:
            st.warning("Por favor, completa todos los campos.")
