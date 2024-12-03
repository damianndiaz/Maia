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
    
def main():
    # Show title and description.
    st.title("👩🏼‍⚕️ Maia.")
    st.write(
        "Asistente médica especializada en recolectar información clínica."
    )

    # Authentication
    proceed = False
    password = st.text_input("App Password", type="password")

    if not password:
        st.info("Por favor, ingrese la clave de la aplicación.", icon="🗝️")
    else:
        if password != st.secrets["app_password"]:
            st.info("La clave provista es incorrecta.", icon="🗝️")
        else: 
            proceed = True
    #################
    #proceed = True
    if proceed == True:
        # Verificamos si 'thread_id' está en session_state, si no, lo inicializamos
        if "thread_id" not in st.session_state:
            st.session_state.thread_id = None

        # Inicializamos el historial de mensajes si no está en session_state
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Mensaje inicial del asistente
        if len(st.session_state.messages) == 0:
            initial_message = "Hola, soy Maia, tu asistente médica. Te voy a hacer algunas preguntas para entender mejor tu situación y poder ayudarte, ¿Comenzamos?"
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

            # Envía el mensaje al modelo de OpenAI
            assistant_response = get_assistant_answer(openai_client, user_input, st.session_state.thread_id)
            answer = assistant_response["assistant_answer_text"]
            st.session_state.thread_id = assistant_response["thread_id"]  # Actualizamos el thread_id
            print(f"thread id de la conversación: {st.session_state.thread_id}")

            # Añade la respuesta del asistente a la sesión
            st.session_state.messages.append({"role": "assistant", "content": answer})
            with st.chat_message("assistant"):
                st.markdown(answer)

# Run the Streamlit app
if __name__ == '__main__':
    main()
