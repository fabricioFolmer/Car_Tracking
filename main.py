import cv2, time

# Chat desse código
# https://chatgpt.com/c/6730c31c-74a8-8008-9348-8dbac3574b65

# Projeto avançado, semelhante:
# https://medium.com/@andresberejnoi/computer-vision-with-opencv-building-a-car-counting-system-andres-berejnoi-8bcc29fc256
# https://www.youtube.com/watch?v=_UGCBud63Eo&ab_channel=Andr%C3%A9sBerejnoi
# https://github.com/andresberejnoi/OpenCV_Traffic_Counter


def contar_carros(video_path: str, mostrar_na_tela: bool = True, windows: str = 'debug') -> int:
    
    # Configuração das janelas
    if windows not in ['debug', 'final']:
        raise ValueError("Argumento 'windows' deve ser 'debug' ou 'final'")
    else:
        if windows == 'debug':
            frames = ['frame', 'gray_frame', 'background', 'frame_delta', 'fg_mask']
        else:
            frames = ['frame']

    # Carrega o vídeo
    cap = cv2.VideoCapture(video_path)

    # Define variáveis
    qtd_carros = 0
    min_contour_width = 40  # Largura mínima do contorno detectado para contar como carro
    min_contour_height = 40 # Altura mínima do contorno detectado para contar como carro
    # line_position = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) // 2)  # Posição da linha vertical de contagem (meio da tela)
    line_position = 430  # Posição da linha vertical de contagem (local mais visível da rua)
    cars_crossed_line = set()  # Conjunto para rastrear os carros que já foram contados

    # Inicializa o background (imagem de fundo) como None
    background = None
    alpha = 0.01  # Taxa de atualização do background (fator de suavização)

    # Loop através de cada frame no vídeo
    while cap.isOpened():
        #time.sleep(0.1)
        ret, frame = cap.read()
        if not ret:
            break
        
        # Converte o frame atual para escala de cinza
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray_frame = cv2.GaussianBlur(gray_frame, (21, 21), 0)  # Aplica suavização para reduzir ruído

        # Inicializa a imagem de fundo com o primeiro frame
        if background is None:
            background = gray_frame.astype("float")
            continue
        
        # Atualiza o background gradualmente com o frame atual
        cv2.accumulateWeighted(gray_frame, background, alpha)
        
        # Calcula a diferença entre o background atualizado e o frame atual
        frame_delta = cv2.absdiff(gray_frame, cv2.convertScaleAbs(background))
        
        # Aplica limiar para obter uma imagem binária, onde áreas de movimento são destacadas
        _, fg_mask = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)
        
        # Encontra contornos
        contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Dicionário para armazenar os frames para exibição
        dict_frames = {'frame': frame, 'gray_frame': gray_frame, 'background': cv2.convertScaleAbs(background), 'frame_delta': frame_delta, 'fg_mask': fg_mask}

        # Processa cada contorno
        for contour in contours:
            # Filtra contornos pequenos com base na área
            x, y, w, h = cv2.boundingRect(contour)
            if w >= min_contour_width and h >= min_contour_height:

                # Desenha um retângulo em torno dos carros detectados
                if mostrar_na_tela is True:
                    for frm in frames:
                        cv2.rectangle(dict_frames[frm], (x, y), (x + w, y + h), (255, 0, 0), 2)
#                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                
                # Determina se o carro cruzou a linha vertical
                car_center = (x + w // 2, y + h // 2)
                if car_center[0] > line_position and car_center[0] < line_position + 20:
                    # Usa um ID único para cada evento de passagem do carro
                    car_id = id(contour)
                    
                    if car_id not in cars_crossed_line:
                        cars_crossed_line.add(car_id)
                        qtd_carros += 1
                    else:
                        print('Duplicado')
        
        if mostrar_na_tela is True:
            # Exibe a linha de contagem vertical
            cv2.line(frame, (line_position, 0), (line_position, frame.shape[0]), (0, 0, 255), 2)

            # Exibe o frame com a contagem de carros
            for frm in frames:
                cv2.putText(dict_frames[frm], f"Carros Contados: {qtd_carros}", (10, 60), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
                cv2.putText(dict_frames[frm], f"Contornos: {len(contours)}", (10, 100), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
                cv2.imshow(frm, dict_frames[frm])

            # Encerra o loop se a tecla 'q' for pressionada ou se uma janela for fechada
            if cv2.waitKey(30) & 0xFF == ord('q') or cv2.getWindowProperty("frame", cv2.WND_PROP_VISIBLE) < 1:
                break

            

    # Libera os recursos
    cap.release() 
    if mostrar_na_tela is True:
        cv2.destroyAllWindows()

    return qtd_carros


# qtd = contar_carros(video_path='Camera_Footage.mp4', mostrar_na_tela=False)
qtd = contar_carros(video_path='Camera_Footage.mp4', mostrar_na_tela=True, windows='debug')
#qtd = contar_carros(video_path='Camera_Footage.mp4', mostrar_na_tela=True, windows='final')

# Exibe o resultado final da contagem
print(f"Total de carros contados: {qtd}")

# 24 Caminhao 2x
# 24 bike 3x
# 24:54 carro n contou
# 25:XX carro n contou
# 25:21 carro n contou