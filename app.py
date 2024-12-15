import streamlit as st
import json
from assistant import get_assistant_answer
from openai import OpenAI
import logging

# Configurar logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

st.set_page_config(page_title="Maia AI", page_icon=":speech_balloon:")

# Cargar la clave API de OpenAI
openai_api_key = st.secrets["OPENAI_API_KEY"]
openai_client = OpenAI(api_key=openai_api_key)

# Archivo JSON local
FILE_PATH = "entrevistas.json"

# Guardar datos en JSON
def save_to_json(data):
    try:
        with open(FILE_PATH, "r", encoding="utf-8") as file:
            existing_data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        existing_data = []

    existing_data.append(data)
    with open(FILE_PATH, "w", encoding="utf-8") as file:
        json.dump(existing_data, file, indent=4, ensure_ascii=False)

# Crear un nuevo thread
def create_thread():
    thread = openai_client.beta.threads.create()
    logging.info(f"Nuevo thread creado: {thread.id}")
    return thread.id

# Inicializar estado
if "messages" not in st.session_state:
    st.session_state.messages = []
if "interview_complete" not in st.session_state:
    st.session_state.interview_complete = False
if "thread_id" not in st.session_state:
    st.session_state.thread_id = None

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
    if st.session_state.thread_id is None:  # Crear un nuevo thread por autenticación
        st.session_state.thread_id = create_thread()
        st.session_state.messages = [
            {"role": "assistant", "content": "Hola, soy Maia, tu asistente médica. Te voy a hacer algunas preguntas para entender mejor tu situación y poder ayudarte, ¿Comenzamos?"}
        ]
        logging.info("Thread ID inicializado con éxito.")

if proceed:
    # Mostrar mensajes previos
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Entrada del usuario
    if not st.session_state.interview_complete:
        user_input = st.chat_input("Escribe tu mensaje aquí...")
        if user_input:
            # Agregar mensaje del usuario
            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.markdown(user_input)

            # Enviar mensaje al mismo thread
            run = openai_client.beta.threads.runs.create(
                thread_id=st.session_state.thread_id,
                assistant_id=st.secrets["assistant_id"],  # ID del Assistant
                instructions="Continúa con la conversación y recoge toda la información necesaria."
            )

            # Obtener respuesta del Assistant
            response = openai_client.beta.threads.messages.list(
                thread_id=st.session_state.thread_id
            )

            # Extraer el último mensaje del Assistant
            assistant_response = response.data[0].content[0].text.value
            st.session_state.messages.append({"role": "assistant", "content": assistant_response})
            with st.chat_message("assistant"):
                st.markdown(assistant_response)

            # Manejar funciones si existen
            if "insertar_resultado_entrevista" in assistant_response:
                save_to_json(json.loads(assistant_response))
                st.success("¡Los datos se han registrado correctamente!")
                st.session_state.interview_complete = True
