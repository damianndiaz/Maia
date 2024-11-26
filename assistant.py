import json

def get_assistant_answer(
    client,
    user_msg:str=None,
    thread_id:str=None,
    assistant_id:str="asst_5LOtpCJ117xkaOpCxr0MhPNA"
):

    # Si no se recibe un thread_id, generamos uno nuevo
    if not thread_id:
        print("No se proporciona un thread_id, creando uno nuevo...")

        thread = client.beta.threads.create(
            messages=[
                {
                    "role": "assistant",
                    "content": "Soy tu asistente médico. Estoy aquí para ayudarte a comprender tu situación. ¿Cómo te encontrás hoy?",
                },
            ]
        )
        thread_id = thread.id

        if thread_id:
            print(f"Nuevo thread creado con ID: {thread_id}")
    else:
        print(f"Se utiliza el thread_id proporcionado: {thread_id}")
    
    # Obtener los mensajes existentes en el hilo
    messages = client.beta.threads.messages.list(thread_id=thread_id)
    if messages:
        print(f"El hilo tiene mensajes previos.")

    # Si el mensaje del usuario está vacío, el asistente proporciona un mensaje por defecto
    if not user_msg or user_msg == '':
        message = client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content="Por favor, ¿me podrías explicar cómo puedo ayudarte?"
        )
        print("Mensaje vacío recibido, agregando un mensaje predeterminado.")
    else:
        message = client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=user_msg
        )
        print(f"Mensaje del usuario: '{user_msg}' agregado al hilo.")
    
    # Ejecutar el asistente
    if message.id and assistant_id:
        run = client.beta.threads.runs.create_and_poll(
            thread_id=thread_id,
            assistant_id=assistant_id,
        )
        print("Ejecutando asistente...")

    # Comprobar si la corrida fue completada o requiere acción
    if run.status == 'completed':
        print("Corrida completada. Obteniendo respuesta del asistente...")

        # Extraemos la respuesta del asistente y la devolvemos
        messages = client.beta.threads.messages.list(thread_id=thread_id)
        answer = messages.data[-1].content  # Última respuesta del asistente

        return {
            "thread_id": thread_id,
            "assistant_answer_text": answer,
            "tool_output_details": None  # Datos de la herramienta (si corresponde)
        }
    else:
        print("La corrida del asistente requiere acciones.")
        return {"error": "Asistente requiere acciones adicionales."}
