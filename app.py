import streamlit as st
import json
from assistant import get_assistant_answer  # Importamos la función para interactuar con el asistente
from openai import OpenAI
import os
import subprocess
import logging

# Configurar el logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

st.set_page_config(page_title="Maia AI", page_icon=":speech_balloon:")

# Cargar la clave API de OpenAI desde el archivo .env (o desde Streamlit secrets)
openai_api_key = st.secrets["OPENAI_API_KEY"]

# Inicializamos el cliente de OpenAI
if openai_api_key:
    openai_client = OpenAI(api_key=openai_api_key)
    if openai_client:
        logging.info("Cliente de OpenAI creado correctamente.")
else:
    logging.error("Error al cargar la clave de API de OpenAI")
    st.stop()

# Ruta donde se guardará el archivo JSON localmente
JSON_FILE_PATH = "entrevistas.json"

def save_to_json(data, file_path=JSON_FILE_PATH):
    """
    Guarda los datos en un archivo JSON.
    """
    try:
        with open(file_path, "w", encoding="utf-8") as json_file:
            json.dump(data, json_file, indent=4, ensure_ascii=False)
        st.success(f"Datos guardados correctamente en {file_path}")
    except Exception as e:
        st.error(f"Error al guardar el archivo JSON: {e}")

def push_to_github(file_path):
    """
    Realiza un commit y push del archivo JSON al repositorio remoto de GitHub.
    """
    try:
        # Agregar el archivo al repositorio local
        subprocess.run(["git", "add", file_path], check=True)

        # Realizar el commit
        commit_message = f"Actualización automática de {file_path}"
        subprocess.run(["git", "commit", "-m", commit_message], check=True)

        # Hacer push al repositorio remoto
        subprocess.run(["git", "push"], check=True)

        st.success(f"El archivo {file_path} se subió correctamente al repositorio de GitHub.")
    except subprocess.CalledProcessError as e:
        st.error(f"Error al ejecutar un comando de Git: {e}")
        
def main():
    # Mostrar título y descripción
    st.title("👩🏼‍⚕️ Maia.")
    st.write("Asistente médica especializada en recolectar información clínica.")

    # Autenticación
    proceed = False
    password = st.text_input("App Password", type="password")
    if not password:
        st.info("Por favor, ingrese la clave de la aplicación.", icon="🗝️")
    elif password != st.secrets["app_password"]:
        st.info("La clave provista es incorrecta.", icon="🗝️")
    else:
        proceed = True

    if proceed:
        # Inicializamos los estados de sesión
        if "thread_id" not in st.session_state:
            st.session_state.thread_id = None
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Mensaje inicial del asistente
        if len(st.session_state.messages) == 0:
            initial_message = "Hola, soy Maia, tu asistente médica. Te voy a hacer algunas preguntas para entender mejor tu situación y poder ayudarte, ¿Comenzamos?"
            st.session_state.messages.append({"role": "assistant", "content": initial_message})

        # Mostrar los mensajes de la conversación
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Entrada del usuario
    user_input = st.chat_input("Escribe tu mensaje aquí...")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # Obtener respuesta del asistente
        assistant_response = get_assistant_answer(
            client=openai_client,
            user_msg=user_input,
            thread_id=st.session_state.thread_id
        )

        if assistant_response is None or "assistant_answer_text" not in assistant_response:
            st.error("No se recibió una respuesta válida del asistente.")
            return

        # Guardar la respuesta del asistente
        answer = assistant_response["assistant_answer_text"]
        st.session_state.messages.append({"role": "assistant", "content": answer})
        with st.chat_message("assistant"):
            st.markdown(answer)

        # Simulación de datos de inserción
        insert_data = {
            "género": "masculino",
            "edad": 25,
            "historial_de_salud": "saludable",
            "síntoma_principal": "cefalea",
            "tiempo_de_evolución": "subagudo",
            "notas": ""
        }

        # Guardar los datos en un archivo JSON
        save_to_json(insert_data)

        # Subir el archivo JSON al repositorio de GitHub
        push_to_github(JSON_FILE_PATH)

# Iniciar la app
if __name__ == "__main__":
    main()
