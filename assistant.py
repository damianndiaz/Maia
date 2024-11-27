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
                    "content": "Hola, soy el Doc. Me gustaría hacerte unas preguntas para entender un poco mejor tu situación. ¿Te parece?",
                }
            ]
        )
        thread_id=thread.id # Obtiene un nuevo thread_id y lo asigna para ser reutilizado.

        if thread_id: # checkpoint
            print(f"Nuevo thread iniciado. ID: {thread_id}")
        
    else:
        thread_id=thread_id
        print(f"El cliente proporciona thread_id y se utiliza. ID:{thread_id}")
    
    # messages.list hace un retrieve de todos los mensajes almacenados en el hilo de la conversación.
    messages = client.beta.threads.messages.list(
        thread_id=thread_id
    )
    if messages:
        print(f"El thread posee mensajes") # messages es un objeto de clase SyncCursorPage[Message]

    # Si el usuario envía por error un mensaje con una cadena vacía en su mensaje inicial, el agente se presentará con más detalle.
    if (not user_msg or user_msg == '') and len(messages)==1:  # len(messages) == 1 especifa que es el mensaje inical del thread.
        message = client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=f"Hola, me explicarías de qué forma puedes ayudarme?"
            )
        print(f"El usuario envía mensaje inicial vacío. Se agrega uno por default")

    # Si el usuario envía por error un mensaje con una cadena vacía en un mensaje NO inicial, el agente recibirá el mensaje vacío.
    elif not user_msg and len(messages)>2:
        message = client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=f""
            )
        print(f"El usuario envía mensaje vacío.")
    
    # Si el usuario envía efectivamente un mensaje con contenido, ese mensaje se agrega al hilo.
    else:
        message = client.beta.threads.messages.create(
            thread_id=thread_id,
                role="user",
                content=user_msg
                )
        # Se obtiene un id del mensaje para identificarlo
        message_id=message.id
        print(f"Mensaje del usuario: '{user_msg}' agregado al thread.")


    ### INICIO DE LA CORRIDA DEL ASISTENTE ###
    # Una vez que el mensaje fue insertado en el hilo conversacional, correr el asistente.
    # Se envía el thread_id al assistant_id; el thread ya contiene el nuevo mensaje. El asistente recibe la conversación completa.
    if message_id and assistant_id:
        run = client.beta.threads.runs.create_and_poll(
            thread_id=thread_id,
            assistant_id=assistant_id,
            )
        print(f"Se inicia Assistant Run...")
    
    else:
        print("No se encuentra mensaje y/o asistente para realizar una corrida")

    if run.status == 'requires_action':
        print(f"Assistant Run requiere acciones por parte del servidor.")

    if run.status == 'completed':
        print(f"Assistant Run finalizado.")

        # Una vez agregado el mensaje, se actualza la lista de mensajes y se captura el anteúltimo
        messages = client.beta.threads.messages.list(thread_id=thread_id)
        answer = messages.data[0].content[0].text.value

        print(f"Respuesta: {answer}")

        return {
            "thread_id":thread_id,
            "assistant_answer_text":answer,
            "tool_output_details": None  # En caso de no haber funciones llamadas, se devuelve el diccionario vacío.
            }
