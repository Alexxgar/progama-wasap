import streamlit as st
import pandas as pd
import urllib.parse

# === FUNCIONES DE CÁLCULO ===
def calcular_tmb(peso, altura_cm, edad, genero):
    return (10 * peso) + (6.25 * altura_cm) - (5 * edad) + (5 if genero == "M" else -161)

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

    nombre = st.text_input("Nombre")
    edad = st.number_input("Edad", 1, 120, 25)
    peso = st.number_input("Peso (kg)", 1.0, 300.0, 70.0)
    altura = st.number_input("Altura (cm)", 50, 250, 170)
    genero = st.radio("Género", ["M", "F"])

    actividad_nivel = {
        "Poco o ningún ejercicio": 1.2,
        "Ligero": 1.375,
        "Moderado": 1.55,
        "Fuerte": 1.725,
        "Muy fuerte": 1.9
    }
    actividad = st.selectbox("Nivel de actividad", list(actividad_nivel.keys()))
    factor = actividad_nivel[actividad]

    if st.button("Calcular"):
        tmb = calcular_tmb(peso, altura, edad, genero)
        imc = calcular_imc(peso, altura)
        get = calcular_get(tmb, factor)

        st.write(f"**IMC:** {imc:.2f}")
        st.write(f"**TMB:** {tmb:.2f} kcal")
        st.write(f"**GET:** {get:.2f} kcal")

        if imc < 18.5:
            st.warning("Clasificación: Bajo peso")
        elif imc < 25:
            st.success("Clasificación: Peso normal")
        elif imc < 30:
            st.warning("Clasificación: Sobrepeso")
        else:
            st.error("Clasificación: Obesidad")

        # Distribución calórica
        st.subheader("Distribución calórica de macronutrientes")
        carbs = st.slider("Carbohidratos (%)", 0, 100, 50)
        prot = st.slider("Proteínas (%)", 0, 100, 25)
        lip = st.slider("Lípidos (%)", 0, 100, 25)

        if carbs + prot + lip != 100:
            st.warning("Los porcentajes deben sumar 100%")
        else:
            cal_carbs = get * carbs / 100
            cal_prot = get * prot / 100
            cal_lip = get * lip / 100
            st.table({
                "Macronutriente": ["Carbohidratos", "Proteínas", "Lípidos"],
                "Kcal": [f"{cal_carbs:.1f}", f"{cal_prot:.1f}", f"{cal_lip:.1f}"],
                "Gramos": [f"{cal_carbs/4:.1f} g", f"{cal_prot/4:.1f} g", f"{cal_lip/9:.1f} g"]
            })

# === MENSAJE WHATSAPP MANUAL ===
with tab2:
    st.title("📱 Enviar mensaje por WhatsApp")
    numero = st.text_input("Número (sin +57 ni espacios)")
    mensaje = st.text_area("Mensaje")

    if st.button("Generar enlace"):
        if numero.startswith("+"):
            numero_completo = numero
        else:
            numero_completo = "+57" + numero.strip()
        mensaje_encoded = urllib.parse.quote(mensaje)
        url = f"https://wa.me/{numero_completo.replace('+','')}?text={mensaje_encoded}"
        st.markdown(f"[👉 Abrir WhatsApp]({url})")

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

                # Limpiar y construir los enlaces
                df['numero'] = df['numero'].astype(str).apply(lambda x: "+57" + x.strip() if not x.startswith("+") else x)
                df['link'] = df.apply(
                    lambda row: f"https://wa.me/{row['numero'].replace('+', '')}?text={urllib.parse.quote(str(row['mensaje']))}", axis=1
                )

                st.write("### Vista previa del archivo:")
                st.dataframe(df[["numero", "mensaje"]])

                st.write("### Enlaces para enviar mensaje por WhatsApp:")
                for idx, row in df.iterrows():
                    st.markdown(
                        f"<a href='{row['link']}' target='_blank'>📩 Enviar a {row['numero']}</a>",
                        unsafe_allow_html=True
                    )
        except Exception as e:
            st.error(f"Ocurrió un error al leer el archivo: {e}")


