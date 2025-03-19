from flask import Flask, request
from pymessenger.bot import Bot
import openai
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)

# Configuración de Facebook Messenger (cargada desde .env)
ACCESS_TOKEN = os.getenv("FACEBOOK_ACCESS_TOKEN")
VERIFY_TOKEN = os.getenv("FACEBOOK_VERIFY_TOKEN")
bot = Bot(ACCESS_TOKEN)

# Configuración de OpenAI (ChatGPT) desde variables de entorno
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=OPENAI_API_KEY)

@app.route('/', methods=['GET'])
def home():
    return "🟢 Kai con ChatGPT está activo en Messenger!"

# Webhook para Facebook Messenger
@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        token_sent = request.args.get("hub.verify_token")
        return verify_fb_token(token_sent)
    else:
        output = request.get_json()
        for event in output['entry']:
            messaging = event['messaging']
            for message in messaging:
                if message.get('message'):
                    recipient_id = message['sender']['id']
                    user_message = message['message'].get('text', '')

                    # Enviar el mensaje del usuario a ChatGPT
                    response_sent_text = get_ai_response(user_message)

                    # Responder en Messenger
                    send_message(recipient_id, response_sent_text)
        return "Mensaje procesado"

def verify_fb_token(token_sent):
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return 'Token de verificación incorrecto.'

def get_ai_response(user_message):
    """Envía la consulta a ChatGPT y obtiene la respuesta."""
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": user_message}]
    )
    return response.choices[0].message.content

def send_message(recipient_id, response):
    """Envía la respuesta a Messenger."""
    bot.send_text_message(recipient_id, response)

if __name__ == '__main__':
    app.run(debug=True)
