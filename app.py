import streamlit as st
import pandas as pd
import urllib.parse

st.set_page_config(page_title="Mensajes WhatsApp", layout="centered")

st.title("📲 Generador de Enlaces de WhatsApp Personalizados")

st.write("Sube un archivo **Excel o CSV** con dos columnas: `numero` y `mensaje`.")

archivo = st.file_uploader("Selecciona el archivo", type=["xlsx", "csv"])

if archivo:
    try:
        if archivo.name.endswith(".csv"):
            df = pd.read_csv(archivo)
        else:
            df = pd.read_excel(archivo)

        if "numero" not in df.columns or "mensaje" not in df.columns:
            st.error("❌ El archivo debe contener las columnas 'numero' y 'mensaje'.")
        else:
            st.success("✅ Archivo cargado correctamente.")

            for i, fila in df.iterrows():
                numero = str(fila["numero"]).replace(" ", "").replace("+", "")
                mensaje = str(fila["mensaje"])
                mensaje_codificado = urllib.parse.quote(mensaje)
                enlace = f"https://wa.me/{numero}?text={mensaje_codificado}"

                st.markdown(f"📤 **[{numero}]**: {mensaje}")
                st.markdown(f"[🔗 Enviar mensaje por WhatsApp]({enlace})\n")
    except Exception as e:
        st.error(f"Error al procesar el archivo: {e}")
