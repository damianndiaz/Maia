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

    # Validamos la clave
    if not password:
        st.info("Por favor, ingrese la clave de la aplicación para continuar.", icon="🗝️")
        return

    if password != st.secrets["app_password"]:
        st.info("La clave provista es incorrecta.", icon="🗝️")
        return

    # Mostrar mensaje de bienvenida
    st.success("¡Clave correcta! Bienvenido al sistema de atención médica.")
  

    # Verificamos si 'thread_id' está en session_state
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = None

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Agregar el mensaje de bienvenida al historial de mensajes
    st.session_state.messages.append({"role": "assistant", "content": "Hola, soy Maia, tu asistente médica. Te voy a hacer algunas preguntas para entender mejor tu situación y poder ayudarte, ¿te parece?."})

    # Mostrar los mensajes en la conversación
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Obtener la entrada del usuario desde la interfaz de chat
    user_input = st.chat_input("Escribe tu mensaje...")

    # Verificar si el usuario escribió algo antes de procesarlo
    if user_input:
        # Llamar a la función get_assistant_answer
        assistant_response = get_assistant_answer(openai_client, user_input, st.session_state.thread_id)

        # Verificar si la respuesta es válida y asignar la respuesta
        if assistant_response:
            assistant_answer = assistant_response.get("assistant_answer_text", "No se pudo obtener la respuesta.")
            st.session_state.thread_id = assistant_response.get("thread_id", st.session_state.thread_id)  # Actualizar thread_id
        else:
            assistant_answer = "Hubo un error al procesar la solicitud."

        # Agregar el mensaje del asistente al estado de la sesión y mostrarlo en la interfaz
        st.session_state.messages.append({"role": "assistant", "content": assistant_answer})
        with st.chat_message("assistant"):
            st.markdown(assistant_answer)

# Ejecutar la aplicación de Streamlit
if __name__ == "__main__":
    main()
