# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

# from typing import Any, Text, Dict, List
#
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []


from typing import Any, Text, Dict, List
import requests
import cx_Oracle
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet


class ActionMarcarVisitaAoMedico(Action):
    def name(self) -> Text:
        return "action_marcar_visita_ao_medico"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Obter informações da visita ao médico dos slots
        user_input = tracker.latest_message['text']
        entities = tracker.latest_message['entities']
        print(user_input)
        print(entities)

        data = tracker.get_slot("data")
        hora = tracker.get_slot("hora")
        medico = tracker.get_slot("medico")
        paciente = tracker.get_slot("paciente")

        # Conectar ao banco de dados Oracle
        connection = cx_Oracle.connect("system/009966@NITRO5-TON:1522/xe")

        # Executar a inserção na tabela de visitas ao médico
        cursor = connection.cursor()
        cursor.execute("INSERT INTO visitas_medico (data_consulta, hora, medico, paciente) VALUES (:data, :hora, :medico, :paciente)",
                       data=data, hora=hora, medico=medico, paciente=paciente)
        connection.commit()

        # Fechar a conexão com o banco de dados
        cursor.close()
        connection.close()

        # Enviar mensagem de confirmação ao usuário
        message = f"Data: {data}, Hora: {hora}, Médico: {medico}, Paciente: {paciente}"
        dispatcher.utter_message(message)
        dispatcher.utter_message("Visita ao médico marcada com sucesso!")

        return [
            SlotSet("data", data),
            SlotSet("hora", hora),
            SlotSet("paciente", paciente),
            SlotSet("medico", medico)
        ]


class ActionConsultarVisitasAoMedico(Action):
    def name(self) -> Text:
        return "action_consultar_visitas_ao_medico"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Conectar ao banco de dados Oracle
        connection = cx_Oracle.connect("system/009966@NITRO5-TON:1522/xe")

        # Executar a consulta na tabela de visitas ao médico
        cursor = connection.cursor()
        cursor.execute(
            "SELECT data, hora, medico, paciente FROM visitas_medico")

        # Recuperar as informações das visitas ao médico
        visitas = cursor.fetchall()

        # Enviar as informações de volta ao usuário
        for visita in visitas:
            data, hora, medico, paciente = visita
            message = f"Data: {data}, Hora: {hora}, Médico: {medico}, Paciente: {paciente}"
            dispatcher.utter_message(message)

        # Fechar a conexão com o banco de dados
        cursor.close()
        connection.close()

        return []
