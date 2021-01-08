import paho.mqtt.publish as publish
import face_recognition as fr
import cv2 as cv
import numpy as np
import time
import datetime
import subprocess
import gtts
import vlc


# carrega webcam
cam = cv.VideoCapture(0)

# carrega uma imagem e aprende a fazer o reconhecimento
carl_img = fr.load_image_file("data/carl_sagan.jpg")
carl_face_encoding = fr.face_encodings(carl_img)[0]

# carrega a segunda imagem
gal_img = fr.load_image_file("data/gal_gadot.jpg")
gal_face_encoding = fr.face_encodings(gal_img)[0]

# carrega a terceira
welly_img = fr.load_image_file("data/welly.jpg")
welly_face_encoding = fr.face_encodings(welly_img)[0]

# carrega a quarta
keanu_img = fr.load_image_file("data/keanu_reeves2.jpg")
keanu_face_encoding = fr.face_encodings(keanu_img)[0]


# array de rostos conhecidos
known_face_encodings = [
    carl_face_encoding,
    gal_face_encoding,
    welly_face_encoding,
    keanu_face_encoding
]
# array com nome dos rostos conhecidos
known_face_names = [
    "Carl Sagan",
    "Gal Gadot",
    "Wellington",
    "Keanu Reeves"
]

# inicializa algumas variáveis necessárias
face_locations = []
face_encodings = []
face_names = []
process_this_frame = True

# variaveis mqtt
topic = "mytopic"
host = "127.0.0.1"
# contador de desconhecidos
cont1 = 0
# contador conhecidos
cont2 = 0

while True:
    # obtem um frame unico do video
    ret, frame = cam.read()

    # reduz o tamanho do frame para 1/4 para maior velocidade de reconhecimento
    small_frame = cv.resize(frame, (0, 0), fx=0.25, fy=0.25)

    if process_this_frame:
        # procura todos os rosto no frame atual
        face_locations = fr.face_locations(small_frame)
        face_encodings = fr.face_encodings(small_frame, face_locations)

        face_names = []
        for face_encoding in face_encodings:
            # verifica se o rosto pertence aos conhecidos
            matches = fr.compare_faces(
                known_face_encodings, face_encoding)
            name = "Desconhecido"

            # procura pela imagem mais precisa
            face_distances = fr.face_distance(
                known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = known_face_names[best_match_index]

            current_date = datetime.datetime.now()
            pub_date = str(
                f"{current_date.hour}:{current_date.minute}:{current_date.second}")

            # publica em um broker mqtt o nome da pessoa ou se ela é desconhecida
            if True not in matches:
                pub_msg = (f"{name} - {pub_date}")
                publish.single(topic, pub_msg, hostname=host)
                cont1 = (cont1 + 1)
                # se o contador atingir o valor executa o bot
                if cont1 == 30:
                    #gambiarra para excutar o bot, precisa de modificações para funcionar como um modulo
                    subprocess.check_output("/usr/bin/python ./bot.py ", shell=True)
                    cont1 = 0
                time.sleep(1)
            elif True in matches:
                pub_msg = (f"{name} - {pub_date}")
                publish.single(topic, pub_msg, hostname=host)
                cont2 = (cont2 + 1)
                if cont2 == 10:
                    publish.single(topic,f"{name}, está na porta.", hostname=host)
                    tss = gtts.gTTS(f"{name}, está na porta.", lang="pt-br")
                    tss.save("buffer.mp3")
                    p = vlc.MediaPlayer('./buffer.mp3')
                    p.play()
                    time.sleep(3)
                    cont2 = 0
                time.sleep(1)
            else:
                pass

            face_names.append(name)

    process_this_frame = not process_this_frame

# libera a webcam
cam.release()