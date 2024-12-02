import streamlit as st
from assistant import get_assistant_answer  # Importamos la función para interactuar con el asistente
from openai import OpenAI
import os
from dotenv import load_dotenv

st.set_page_config(page_title="Maia AI", page_icon=":speech_balloon:")

# Cargar la clave API de OpenAI desde el archivo .env (o desde Streamlit secrets)
openai_api_key = st.secrets["OPENAI_API_KEY"]

# Obtener la clave secreta
app_password = os.getenv("APP_PASSWORD")

# Inicializamos el cliente de OpenAI
if openai_api_key:
    openai_client = OpenAI(api_key=openai_api_key)
    if openai_client:
        print("Cliente de OpenAI creado correctamente.")
else:
    st.error("Error al cargar la clave de API de OpenAI")
    st.stop()  # Detiene la ejecución si no se encuentra la clave
    
# Inicializamos la app de Streamlit
def main():
    
    # Mostrar título y descripción
    st.title("👩🏼‍⚕️ Maia")
    st.write("Asistente médica especializada en recolectar información clínica.")

    # Autenticación
    password = st.text_input("Ingrese la clave de la aplicación", type="password")

      # Autenticación
    password = st.text_input("Ingrese la clave de la aplicación", type="password")
    if not password:
        st.info("Por favor, ingrese la clave de la aplicación para continuar.", icon="🗝️")
        return

    if password != st.secrets["app_password"]:
        st.info("La clave provista es incorrecta.", icon="🗝️")
        return

    # Verificamos si 'thread_id' está en session_state
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = None

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Mostrar los mensajes en la conversación
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Entrada del usuario
    user_input = st.chat_input("Escribe tu mensaje...")

    if user_input:
        # Añadir el mensaje del usuario
        st.session_state.messages.append({"role": "user", "content": user_input})

        # Llamar al asistente
        assistant_response = get_assistant_answer(openai_client, user_input, st.session_state.thread_id)
        assistant_answer = assistant_response["assistant_answer_text"]
        st.session_state.thread_id = assistant_response["thread_id"]

        # Mostrar la respuesta del asistente
        st.session_state.messages.append({"role": "assistant", "content": assistant_answer})

        with st.chat_message("assistant"):
            st.markdown(assistant_answer)

# Ejecutar la aplicación de Streamlit
if __name__ == "__main__":
    main()
