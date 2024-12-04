import json
import os

def get_assistant_answer(client, user_msg, thread_id=None, assistant_id="asst_5LOtpCJ117xkaOpCxr0MhPNA"):
    print("Se inicia la función get_assistant_answer")
    
    # Si no se recibe thread_id, generamos uno nuevo
    if not thread_id:
        print("Generando nuevo thread...")
        thread = client.beta.threads.create(
            messages=[]  # No se enviará mensaje inicial aquí, lo manejamos en app.py
        )
        thread_id = thread.id
        print(f"Nuevo thread creado. ID: {thread_id}")

    # Verificación de que el mensaje del usuario no esté vacío
    if user_msg:
        # Si el mensaje es válido, creamos el mensaje en el hilo
        message = client.beta.threads.messages.create(thread_id=thread_id, role="user", content=user_msg)
        message_id = message.id
        print(f"Mensaje del usuario: '{user_msg}' agregado al thread.")
    else:
        print("El mensaje del usuario está vacío. No se procesará.")

    # Ejecutar el modelo con la información del hilo
    try:
        run = client.beta.threads.runs.create_and_poll(thread_id=thread_id, assistant_id=assistant_id)
        tool_outputs = []
        tool_output_details = {}

        if run.status == 'requires_action':
            print(f"Assistant Run requiere acciones por parte del servidor.")
            for tool_call in run.required_action.submit_tool_outputs.tool_calls:
                if tool_call.type == 'function':
                    function_name = tool_call.function.name
                    function_arguments = json.loads(tool_call.function.arguments)
                    print(f"Función llamada: {function_name}")

                    if function_name == 'insertar_resultado_entrevista':
                        # Extraer los parámetros para la función
                        genero = function_arguments.get('género')
                        edad = function_arguments.get('edad')
                        historial_de_salud = function_arguments.get('historial_de_salud')
                        sintoma_principal = function_arguments.get('síntoma_principal')
                        tiempo_de_evolución = function_arguments.get('tiempo_de_evolución')
                        notas = function_arguments.get('notas')

                        # Guardar los datos en un archivo JSON
                        save_to_json(genero, edad, historial_de_salud, sintoma_principal, tiempo_de_evolución, notas)
                        
                        # Resultado de la función
                        output_str = "Resultado insertado exitosamente."
                        tool_outputs.append({"tool_call_id": tool_call.id, "output": output_str})

                        # Detalles de la salida
                        tool_output_details['insertar_resultado_entrevista'] = {
                            'genero': genero,
                            'edad': edad,
                            'historial_de_salud': historial_de_salud,
                            'sintoma_principal': sintoma_principal,
                            'tiempo_de_evolución': tiempo_de_evolución,
                            'notas': notas
                        }

        if run.status == 'completed':
            print("Assistant Run completado.")
            messages = client.beta.threads.messages.list(thread_id=thread_id)
            if messages.data:
                assistant_answer = messages.data[-1].content
                print(f"Respuesta del asistente: {assistant_answer}")
                return {
                    "thread_id": thread_id,
                    "assistant_answer_text": assistant_answer,
                    "tool_output_details": tool_output_details
                }
            else:
                print("No se recibieron mensajes en el hilo.")
                return {
                    "thread_id": thread_id,
                    "assistant_answer_text": "No se recibió una respuesta válida del asistente.",
                    "tool_output_details": tool_output_details
                }
    except Exception as e:
        print(f"Error en la ejecución del Assistant Run: {e}")
        return {
            "thread_id": thread_id,
            "assistant_answer_text": "Hubo un error al procesar la solicitud. Por favor, intenta nuevamente.",
            "tool_output_details": {}
        }

def save_to_json(genero, edad, historial_de_salud, sintoma_principal, tiempo_de_evolución, notas):
    # Guardamos los datos en un archivo JSON sin sobrescribir los datos previos
    file_path = "entrevistas.json"
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            data = json.load(file)
    else:
        data = []

    # Añadimos los nuevos datos
    data.append({
        "genero": genero,
        "edad": edad,
        "historial_de_salud": historial_de_salud,
        "sintoma_principal": sintoma_principal,
        "tiempo_de_evolución": tiempo_de_evolución,
        "notas": notas
    })

    # Guardamos los datos actualizados
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)
    print("Datos guardados en entrevistas.json")
