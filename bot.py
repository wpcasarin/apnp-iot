from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, JobQueue
import telegram
import logging
import time
import multiprocessing

# token to bot
token = '1550877121:AAFrs14q7Usj9fm9EH6GxXRXuFFzK6Ks6TY'
# id do chat da pessoa que vai receber a mensagem
chat_id = '1281004814'

# mensagem a ser enviada
msg = "ALERTA!! DESCONHECIDO!"


# habilita um logger
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    level=logging.INFO)

logger = logging.getLogger(__name__)


# função para enviar msg
def tele_msg(context):
    context.bot.send_message(chat_id=chat_id,  text=msg)

# função principal


def main(token, msg):
    updater = Updater(token, use_context=True)
    job = updater.job_queue

    try:
        job.run_once(tele_msg, 2)
        updater.start_polling()
        updater.idle()

    except KeyboardInterrupt:
        updater.stop()
        print("DONE")


if __name__ == "__main__":
    # cria um processo que vai enviar a mensagem apenas uma vez e vai ser finalizado depois de 5 segundos
    p = multiprocessing.Process(target=main, name="Foo", args=(token, msg))
    p.start()
    time.sleep(5)
    if p.is_alive():
        p.terminate()
    p.join()
