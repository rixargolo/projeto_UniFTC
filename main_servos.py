import time
import math
import cv2  # importando biblioteca OpneCV
import mediapipe as mp  # importando framework MediaPipe
from Arduino import Arduino  # importanto classe Arduino do módulo Arduino

#variáveis auxiliares para desenho e estilos dos pontos de tracking das mãos
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

#captura o vídeo da webcam
cap = cv2.VideoCapture(0)

#configura a placa arduino e os servos motores
board = Arduino("9600", port="COM4")  
servo = board.Servos

servo.attach(3)
servo.attach(5)

#reseta as portas do arduino
servo.write(3, 0)
servo.write(5, 0)


with mp_hands.Hands( #abre o arquivo-fonte do vídeo para manipulação
    #parâmentos de tracking e detecção das mãos
    model_complexity=0,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5) as hands:
    
    #enquanto o arquivo estiver aberto, leia a fonte
    while cap.isOpened():
        sucess, image = cap.read()

        if not sucess:
            print ("Fonte de câmera sem stream - ignorando...")
            continue

        #marca a imagem como 'not writeable' para melhoria de performance, 
        # quando não há uma mão detectada na tela
        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = hands.process(image)

        #desenha os pontos de tracking quando há uma mão na tela
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        #coleta dados de altura e largura da janela do vídeo 
        image_hight, image_width, _ = image.shape

        #inicia traking da mão
        if results.multi_hand_landmarks:

            #desenha pontos e ligações na mão
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    image,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style()
            )

            for hand_landmarks in results.multi_hand_landmarks:
                #função para calcular ditancia entre 2 pontos na mão
                def dist_pontos(ponto1, ponto2):
                    p1x = ponto1.x * image_hight
                    p2x = ponto2.x * image_hight

                    p1y = ponto1.y * image_width
                    p2y = ponto2.y * image_width

                    p1 = pow((ponto1.x - ponto2.x), 2) 
                    p2 = pow((ponto1.y - ponto2.y), 2)
                    
                    dist = (pow((p1x  - p2x), 2)) + pow((p1y - p2y ), 2)
                    
                    return int(pow(dist, 1/2))


                indicador = dist_pontos(hand_landmarks.landmark[8], hand_landmarks.landmark[5])
                servo.write(3, indicador)

                medio = dist_pontos(hand_landmarks.landmark[12], hand_landmarks.landmark[9])
                servo.write(5, medio)
                
                print("== Monitor de distancias ==")
                print("Indicado: ", indicador)
                print("Medio: ", medio)
                print(" ")
                print(" ")


        #gera a janela de saída com o resultado do traking
        cv2.imshow("UniTFC - Inteligencia Artificial", cv2.flip(image, 1))

        #adiciona condicional de execução da janela até que a tecla 'esc' seja pressionada
        if cv2.waitKey(5) & 0xFF == 27:
            break
    
    #finaliza a captura vídeo e libera a webcam
    cap.release()

#resetas portas do arduino
servo.write(3, 0)
servo.write(5, 0)
