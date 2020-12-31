import paho.mqtt.publish as publish
import face_recognition as fr
import cv2 as cv
import numpy as np
import time


# abre webcam com index padrão
webcam = cv.VideoCapture(0)

# carrega a imagem e aprende a fazer o reconhecimento
obama_image = fr.load_image_file("conhecidos/obama.jpg")
obama_face_encoding = fr.face_encodings(obama_image)[0]

# carrega a segunda imagem
biden_image = fr.load_image_file("conhecidos/biden.jpg")
biden_face_encoding = fr.face_encodings(biden_image)[0]

# carrega a terceira imagem
welly_image = fr.load_image_file("conhecidos/welly.jpg")
welly_face_encoding = fr.face_encodings(welly_image)[0]

# cria as matrizes dos rostos e seus respectivos nomes
known_face_encodings = [
    obama_face_encoding,
    biden_face_encoding,
    welly_face_encoding
]
known_face_names = [
    "Barack Obama",
    "Joe Biden",
    "Wellington"
]

# inicializa algumas variáveis necessárias
face_locations = []
face_encodings = []
face_names = []
process_this_frame = True

# nome do topico mqtt
topic = "wtesttopic"
# mensagem a ser publicada
msg = "desconhecido"


while True:
    # obtem um frame unico do video
    ret, frame = webcam.read()

    # reduz o tamanho do frame para 1/4 para maior velocidade de reconhecimento
    small_frame = cv.resize(frame, (0, 0), fx=0.25, fy=0.25)

    # converte a imagem de BGR (utilizado pelo OpenCV) para RGB
    rgb_small_frame = cv.cvtColor(small_frame, cv.COLOR_BGR2RGB)

    if process_this_frame:
        # procura todos os rosto no frame atual
        face_locations = fr.face_locations(rgb_small_frame)
        face_encodings = fr.face_encodings(rgb_small_frame, face_locations)

        face_names = []
        for face_encoding in face_encodings:
            # verifica se o rosto pertence aos conhecidos
            matches = fr.compare_faces(
                known_face_encodings, face_encoding)
            name = "Desconhecido"
            
            # verifica se existe algum rosto conhecido, caso não seja encontrado publica a mensagem no topico
            if True not in matches:
                publish.single(topic, msg, hostname="broker.mqttdashboard.com")
            
            # procura pela imagem mais precisa
            face_distances = fr.face_distance(
                known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = known_face_names[best_match_index]

            face_names.append(name)

    process_this_frame = not process_this_frame

    # mostra os resultados
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        # reescala o frame que foi reduzido
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        # desenha um quadrado em torno do rosto
        cv.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

        # escreve o nome da pessoa
        cv.rectangle(frame, (left, bottom - 35),
                      (right, bottom), (0, 255, 0), cv.FILLED)
        font = cv.FONT_HERSHEY_DUPLEX
        cv.putText(frame, name, (left + 6, bottom - 6),
                    font, 1.0, (0, 0, 0), 2)

    # mostra um preview do resultado
    cv.imshow("Preview", frame)

    # finaliza o loop se a tecla 'Q' for precionada
    if cv.waitKey(1) & 0xFF == ord("q"):
        break

# libera a webcam e fecha todas janelas
webcam.release()
cv.destroyAllWindows()
