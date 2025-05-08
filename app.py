import streamlit as st
import pandas as pd
import urllib.parse

# === FUNCIONES DE CÁLCULO ===
def calcular_tmb(peso, altura_cm, edad, genero):
    return (10 * peso) + (6.25 * altura_cm) - (5 * edad) + (5 if genero.lower() == "m" else -161)

def calcular_imc(peso, altura_cm):
    altura_m = altura_cm / 100
    return peso / (altura_m ** 2)

def calcular_get(tmb, actividad):
    return tmb * actividad

# === PESTAÑAS ===
tab1, tab2, tab3 = st.tabs(["Calculadora Nutricional", "Mensaje WhatsApp Manual", "Enlaces desde Archivo"])

# === CALCULADORA NUTRICIONAL ===
with tab1:
    st.title("📊 Calculadora Nutricional")

    nombre = st.text_input("Ingrese su nombre:", value=st.session_state.get("nombre", ""))
    edad = st.number_input("Edad:", 1, 120, value=st.session_state.get("edad", 25))
    peso = st.number_input("Peso (kg):", 1.0, 300.0, value=st.session_state.get("peso", 70.0))
    altura = st.number_input("Altura (cm):", 50, 250, value=st.session_state.get("altura", 170))
    genero = st.radio("Género:", ["M", "F"], index=0 if st.session_state.get("genero", "M") == "M" else 1)

    st.session_state["nombre"] = nombre
    st.session_state["edad"] = edad
    st.session_state["peso"] = peso
    st.session_state["altura"] = altura
    st.session_state["genero"] = genero

    actividad_nivel = {
        "Poco o ningún ejercicio": 1.2,
        "Ligero": 1.375,
        "Moderado": 1.55,
        "Fuerte": 1.725,
        "Muy fuerte": 1.9
    }
    actividad = st.selectbox("Nivel de actividad:", list(actividad_nivel.keys()), index=2)
    factor = actividad_nivel[actividad]

    if st.button("Calcular"):
        tmb = calcular_tmb(peso, altura, edad, genero)
        imc = calcular_imc(peso, altura)
        get = calcular_get(tmb, factor)

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

        porc_carbs = st.number_input("Carbohidratos (%):", 0.0, 100.0, step=1.0, value=st.session_state["porc_carbs"])
        porc_prot = st.number_input("Proteínas (%):", 0.0, 100.0, step=1.0, value=st.session_state["porc_prot"])
        porc_lipidos = st.number_input("Lípidos (%):", 0.0, 100.0, step=1.0, value=st.session_state["porc_lipidos"])

        st.session_state["porc_carbs"] = porc_carbs
        st.session_state["porc_prot"] = porc_prot
        st.session_state["porc_lipidos"] = porc_lipidos

        total = porc_carbs + porc_prot + porc_lipidos
        if total != 100:
            st.warning("⚠️ Los porcentajes deben sumar exactamente 100%.")
        else:
            get = st.session_state["get"]
            cal_carbs = get * porc_carbs / 100
            cal_prot = get * porc_prot / 100
            cal_lipidos = get * porc_lipidos / 100

            st.success("✅ Distribución calórica válida.")

            st.write("### 🍽️ Distribución de macronutrientes")
            st.table({
                "Macronutriente": ["Carbohidratos", "Proteínas", "Lípidos", "Total"],
                "Gramos": [f"{cal_carbs/4:.2f} g", f"{cal_prot/4:.2f} g", f"{cal_lipidos/9:.2f} g", f"{(cal_carbs/4 + cal_prot/4 + cal_lipidos/9):.2f} g"],
                "Kcal": [f"{cal_carbs:.2f} kcal", f"{cal_prot:.2f} kcal", f"{cal_lipidos:.2f} kcal", f"{get:.2f} kcal"],
                "Porcentaje": [f"{porc_carbs}%", f"{porc_prot}%", f"{porc_lipidos}%", "100%"],
                "Gramos por kg de peso": [f"{cal_carbs/4/peso:.2f} g/kg", f"{cal_prot/4/peso:.2f} g/kg", f"{cal_lipidos/9/peso:.2f} g/kg", "-"]
            })

# === MENSAJE WHATSAPP MANUAL ===
with tab2:
    st.title("📱 Enviar mensaje por WhatsApp")
    numero = st.text_input("Número (sin +57 ni espacios)")
    mensaje = st.text_area("Mensaje")

    if st.button("Generar enlace"):
        numero_completo = "+57" + numero.strip() if not numero.startswith("+") else numero
        mensaje_encoded = urllib.parse.quote(mensaje)
        url = f"https://wa.me/{numero_completo.replace('+','')}?text={mensaje_encoded}"
        st.markdown(f"[👉 Abrir WhatsApp]({url})", unsafe_allow_html=True)

# === ENLACES DESDE ARCHIVO ===
with tab3:
    st.title("📂 Generador de Enlaces WhatsApp desde Archivo")

    archivo = st.file_uploader("Sube archivo Excel o CSV con columnas 'numero' y 'mensaje'", type=["xlsx", "csv"])

    if archivo:
        try:
            if archivo.name.endswith(".csv"):
                df = pd.read_csv(archivo)
            else:
                df = pd.read_excel(archivo)

            if 'numero' not in df.columns or 'mensaje' not in df.columns:
                st.error("El archivo debe tener columnas llamadas 'numero' y 'mensaje'")
            else:
                st.success("Archivo cargado correctamente.")
                df['numero'] = df['numero'].astype(str).apply(lambda x: "+57" + x.strip() if not x.startswith("+") else x)
                df['link'] = df.apply(lambda row: f"https://wa.me/{row['numero'].replace('+', '')}?text={urllib.parse.quote(str(row['mensaje']))}", axis=1)

                st.write("### Enlaces para enviar mensaje:")
                for idx, row in df.iterrows():
                    st.markdown(f"[📩 Enviar a {row['numero']}]({row['link']})", unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Ocurrió un error al leer el archivo: {e}")
