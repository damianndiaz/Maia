import streamlit as st
from assistant import get_assistant_answer  # Importamos la función para interactuar con el asistente
from openai import OpenAI
import os
from dotenv import load_dotenv

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
    proceed = False
    st.set_page_config(page_title="Doc IA", page_icon=":speech_balloon:")

    # Mostrar título y descripción.
    st.title("🤖 Doc IA")
    st.write("Asistente médico especializado en recoger información clínica.")

    # Autenticación
    password = st.text_input("Ingrese la clave de la aplicación", type="password")

    if not password:
        st.info("Por favor, ingrese la clave de la aplicación para continuar.", icon="🗝️")
    else:
        if password != st.secrets["app_password"]:
            st.info("La clave provista es incorrecta.", icon="🗝️")
        else: 
            proceed = True

    if proceed:
        # Verificamos si 'thread_id' está en session_state, si no, lo inicializamos
        if "thread_id" not in st.session_state:
            st.session_state.thread_id = None

        # Inicializamos el historial de mensajes si no está en session_state
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Mensaje inicial del asistente
        if len(st.session_state.messages) == 0:
            initial_message = "Hola, soy el Doc. Vamos a realizar algunas preguntas para poder ayudarte mejor. ¿Listo para comenzar?"
            st.session_state.messages.append({"role": "assistant", "content": initial_message})

        # Muestra los mensajes en la conversación
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Input del usuario
        user_input = st.chat_input("Escribe tu mensaje aquí...")

        # Cuando el usuario envía un mensaje
        if user_input:
            # Añade el mensaje del usuario a la sesión
            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.markdown(user_input)

            # Llamada al asistente para obtener la respuesta
            assistant_response = get_assistant_answer(openai_client, user_input, st.session_state.thread_id)
            answer = assistant_response["assistant_answer_text"]
            st.session_state.thread_id = assistant_response["thread_id"]  # Actualizamos el thread_id

            # Añade la respuesta del asistente a la sesión
            st.session_state.messages.append({"role": "assistant", "content": answer})
            with st.chat_message("assistant"):
                st.markdown(answer)

# Ejecutamos la app
if __name__ == '__main__':
    main()
