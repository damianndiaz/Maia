import json

def get_assistant_answer(
    client,
    user_msg: str = None,
    thread_id: str = None,
    assistant_id: str = "asst_5LOtpCJ117xkaOpCxr0MhPNA"
):

    # Si no hay thread_id, generamos uno nuevo
    if not thread_id:
        print("Generando nuevo thread...")

        # Crear un nuevo hilo con un mensaje inicial
        thread = client.beta.threads.create(
            messages=[
                {
                    "role": "assistant",
                    "content": "Soy un asistente médico especializado en recolectar información clínica. ¿Cómo puedo ayudarte hoy?",
                }
            ]
        )
        thread_id = thread.id  # Asignamos el nuevo thread_id

        print(f"Nuevo thread creado. ID: {thread_id}")

    else:
        print(f"Usando thread_id existente: {thread_id}")

    # Crear el mensaje del usuario en el hilo
    message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=user_msg
    )
    message_id = message.id
    print(f"Mensaje del usuario: '{user_msg}' agregado al thread.")

    # Ejecutar el modelo con la información del hilo
    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread_id,
        assistant_id=assistant_id
    )

    if run.status == 'completed':
        print(f"Assistant Run completado.")

        # Obtener la respuesta del asistente
        messages = client.beta.threads.messages.list(thread_id=thread_id)
        assistant_answer = messages.data[-1].content  # Tomamos el último mensaje como respuesta

        print(f"Respuesta del asistente: {assistant_answer}")

        return {
            "thread_id": thread_id,
            "assistant_answer_text": assistant_answer,
            "tool_output_details": None
        }
    else:
        print("La corrida del asistente requiere acciones.")
        return {"error": "Asistente requiere acciones adicionales."}
