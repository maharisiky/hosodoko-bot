import os
from dotenv import load_dotenv
from django.http import response, HttpResponse, JsonResponse
from rest_framework import viewsets, status
from rest_framework.views import APIView
from app.serializers import *
from app.models import *
import requests
from rest_framework.response import Response
from bs4 import BeautifulSoup
import time
from app.views.IA import IA


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class WebhookView(APIView):
    def __init__(self):
        load_dotenv()
        # getting verify token from .env
        self.verify_token = os.getenv("VERIFY_TOKEN")
        self.page_access_token = os.getenv("PAGE_ACCESS_TOKEN")
        self.messaging_endpoint = os.getenv('MESSAGING_ENDPOINT')
        self.page_url = f"{self.messaging_endpoint}?access_token={self.page_access_token}"

        self.ia = IA()

    def get(self, request):
        if request.query_params.get('hub.verify_token') == self.verify_token:
            return Response(int(request.query_params.get('hub.challenge')), status=status.HTTP_200_OK)
        else:
            return Response("Erreur de vérification", status=status.HTTP_403_FORBIDDEN)

    def post(self, request):
        data = request.data
        messaging = data['entry'][0]['messaging'][0]
        sender_id = messaging['sender']['id']

        message = messaging['message']
        self.actions(sender_id, 'mark_seen')
        self.actions(sender_id, 'typing_on')

        # if the message is not a text message
        if 'text' not in message:
            message = """
                Je suis désolé, je ne peux pas traiter ce type de message pour le moment. \nMerci d'envoyer un message texte.
            """
            self.actions(sender_id, 'typing_off')
            self.send_message(sender_id, message)
            return Response("ok", status=status.HTTP_200_OK)

        # manage payload
        # if not quick reply : generate response with IA
        if 'quick_reply' not in message:
            print("Sending response message")
            print("Generating response message")
            response_message = self.ia.ask_gemini(sender_id, message)
            print(f"Response message: {response_message}")
        else:
            payload = message['quick_reply']['payload']
            print(f"Payload: {payload}")
            
            # Récupérer la réponse depuis la base de données
            try:
                from app.models import QuickReply
                quick_reply = QuickReply.objects.get(payload=payload, is_active=True)
                response_message = quick_reply.response_text
            except QuickReply.DoesNotExist:
                response_message = "Désolé, je n'ai pas compris votre demande. Veuillez réessayer."
            except Exception as e:
                print(f"Erreur lors de la récupération de la quick reply: {e}")
                response_message = "Désolé, une erreur est survenue. Veuillez réessayer plus tard."

        self.send_message(sender_id, response_message)
        self.actions(sender_id, 'typing_off')
        return Response("ok", status=status.HTTP_200_OK)



    def send_message(self, recipient_id, message_text):
        params = {
            "access_token": self.page_access_token
        }
        headers = {
            "Content-Type": "application/json"
        }

        # Récupérer les quick replies depuis la base de données
        quick_replies = []
        try:
            from app.models import QuickReply
            qr_objects = QuickReply.objects.filter(is_active=True)
            quick_replies = [
                {"content_type": "text", "title": qr.title, "payload": qr.payload}
                for qr in qr_objects
            ]
        except Exception as e:
            # Fallback vers les quick replies codées en dur en cas d'erreur
            print(f"Erreur lors de la récupération des quick replies: {e}")
            quick_replies = [
                {"content_type": "text", "title": "À propos", "payload": "ABOUT"},
                {"content_type": "text", "title": "Savoir-faire", "payload": "SKILLS"},
                {"content_type": "text", "title": "Événements", "payload": "EVENTS"},
                {"content_type": "text", "title": "Challenges", "payload": "CHALLENGES"},
                {"content_type": "text", "title": "Quizz", "payload": "QUIZ"}
            ]


        data = {
            "recipient": {
                "id": recipient_id
            },
            "message": {
                "text": message_text, 
                "quick_replies": quick_replies
            }
        }

        requests.post(
            self.messaging_endpoint,
            params=params,
            headers=headers,
            json=data
        )


    def actions(self,recipient_id, action):
        payload = {
            'recipient': {'id': recipient_id},
            'sender_action': action,
        }
        headers = {'Content-Type': 'application/json'}
        requests.post(self.page_url, headers=headers, json=payload)


def healthView(request):
    return JsonResponse({"status": "ok"})