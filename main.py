import cv2, time, math, numpy as np
from typing import Literal

# Chat desse código
# https://chatgpt.com/c/6730c31c-74a8-8008-9348-8dbac3574b65

# Projeto avançado, semelhante:
# https://medium.com/@andresberejnoi/computer-vision-with-opencv-building-a-car-counting-system-andres-berejnoi-8bcc29fc256
# https://www.youtube.com/watch?v=_UGCBud63Eo&ab_channel=Andr%C3%A9sBerejnoi
# https://github.com/andresberejnoi/OpenCV_Traffic_Counter

def contar_carros(video_path: str, mostrar_na_tela: bool = True, windows: str = 'debug') -> tuple[int, dict[int, int]]:
    

    def passou_pela_linha(centro, area, centros_ultimo_frame, tipo_linha: Literal['horizontal', 'vertical'], line_position: int) -> bool:
    # Verifica se o centro de um contorno cruzou a linha de contagem
    # Parâmetros:
    # - centro: tupla contendo as coordenadas (x, y) do centro do contorno
    # - area: área do contorno
    # - centros_ultimo_frame: lista de tuplas contendo os centros dos contornos do último frame
    # - tipo_linha: tipo de linha de contagem ('horizontal' ou 'vertical')
    # - line_position: posição da linha de contagem


        # Determina o centro do último frame mais próximo do centro informado. Variável 'centro_frame_anterior'
        menor_dist = centro_frame_anterior = None
        for c in centros_ultimo_frame:
            # Determina a distância entre c e centro
            dist = math.sqrt((c[0] - centro[0])**2 + (c[1] - centro[1])**2)
            
            # Atualiza o centro_frame_anterior se a distância for a menor encontrada até agora. 
            # Desconsiderando casos onde a distância é maior do que a área do contorno atual
            if (menor_dist is None or dist < menor_dist) and dist < area:
                menor_dist = dist
                centro_frame_anterior = c

        if centro_frame_anterior is None:
            return False

        # Se a linha entre o centro informado e o centro do último frame cruzar a linha de contagem, retorna True
        if tipo_linha == 'horizontal':
            if (centro[1] > line_position and centro_frame_anterior[1] < line_position) or (
                centro[1] < line_position and centro_frame_anterior[1] > line_position) or (
                centro[1] == line_position):
                return True
        elif tipo_linha == 'vertical':
            if (centro[0] > line_position and centro_frame_anterior[0] < line_position) or (
                centro[0] < line_position and centro_frame_anterior[0] > line_position) or (
                centro[0] == line_position):
                return True
        return False

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
    centros_ultimo_frame = [] # Lista de centros dos contornos do último frame. Usado para determinar se um carro cruzou a linha de contagem
    dict_resultados = {}  # Dicionário para armazenar os resultados da contagem a cada minuto

 #    LARGE_OBJECT_THRESHOLD = 5000  # Adjust this value based on your specific case


    # Inicializa o background (imagem de fundo) como None
    background = None
    alpha = 0.01  # Taxa de atualização do background (fator de suavização)

    # Loop através de cada frame no vídeo
    while cap.isOpened():
        
        # Mostra na tela apenas após o minuto X
        if ((cap.get(cv2.CAP_PROP_POS_MSEC) / 1000 / 60) + 1) >= 2.9:
            #mostrar_na_tela = True
            time.sleep(0)

        # ERROS: (não são todos)
        # 2.90 Caminhão conta 2x
        # 4.15 2 Carros contam como 3. # TODO Para corrigir, considerar a direção de movimento do carro na def de passou_pela_linha, para buscar apenas contornos 'atras' do carro
        
        ret, frame = cap.read()
        if not ret:
            break
        
        # Converte o frame atual para escala de cinza
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray_frame = cv2.GaussianBlur(gray_frame, (21, 21), 0)  # Aplica suavização para reduzir ruído
        gray_frame = cv2.GaussianBlur(gray_frame, (21, 21), 0)  # Aplica suavização para reduzir ruído
        gray_frame = cv2.GaussianBlur(gray_frame, (21, 21), 0)  # Aplica suavização para reduzir ruído
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
        
        # Aplica operações morfológicas para preencher buracos e remover ruídos
        fg_mask = cv2.dilate(fg_mask, None)
        fg_mask = cv2.dilate(fg_mask, None)
        fg_mask = cv2.dilate(fg_mask, None)
        fg_mask = cv2.dilate(fg_mask, None)

        # Encontra contornos
        contours, _ = cv2.findContours(fg_mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Dicionário para armazenar os frames para exibição
        dict_frames = {'frame': frame, 'gray_frame': gray_frame, 'background': cv2.convertScaleAbs(background), 'frame_delta': frame_delta, 'fg_mask': fg_mask}

        # Processa cada contorno
        centros_frame_atual = []
        for contour in contours:
            # Filtra contornos pequenos com base na área
            x, y, w, h = cv2.boundingRect(contour)
            if w >= min_contour_width and h >= min_contour_height:

                # Desenha um retângulo em torno dos contornos detectados, e um ponto no centro
                for frm in frames:
                    cv2.rectangle(dict_frames[frm], (x, y), (x + w, y + h), (255, 0, 0), 2)
                    cv2.circle(dict_frames[frm], (x + w // 2, y + h // 2), 5, (0, 255, 0), -1)
                
                # Determina se o carro cruzou a linha vertical
                centro = (x + w // 2, y + h // 2)
                
                if passou_pela_linha(centro, w*h, centros_ultimo_frame, 'vertical', line_position) is True:
                    minuto_atual = int(cap.get(cv2.CAP_PROP_POS_MSEC) / 1000 / 60) + 1
                    if minuto_atual not in dict_resultados:
                        dict_resultados[minuto_atual] = 1
                    else:
                        dict_resultados[minuto_atual] += 1
                    qtd_carros += 1
                centros_frame_atual.append(centro)

        centros_ultimo_frame = centros_frame_atual.copy()

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
            
            if cv2.waitKey(30) & 0xFF == ord('t'):
                print(cap.get(cv2.CAP_PROP_POS_MSEC) / 1000 / 60) + 1
            
    # Libera os recursos
    cap.release()
    cv2.destroyAllWindows()

    return qtd_carros, dict_resultados

# Exemplos de uso
# qtd = contar_carros(video_path='Camera_Footage.mp4', mostrar_na_tela=False)
qtd, dict_resultados = contar_carros(video_path='Camera_Footage.mp4', mostrar_na_tela=False, windows='debug')
#qtd = contar_carros(video_path='Camera_Footage.mp4', mostrar_na_tela=True, windows='final')

# Exibe o resultado final da contagem
print(f"Total de carros contados: {qtd}. Eram esperados 38.\n")

# Checagem do gabarito
gabarito = {1: 8, 2: 6, 3: 3, 4: 13, 5: 6}
for minuto, qtd in dict_resultados.items():
    if minuto in gabarito:
        if qtd != gabarito[minuto]:
            print(f"Erro no minuto {minuto}: {qtd} carros. Gabarito: {gabarito[minuto]}")
    else:
        print(f"Erro no minuto {minuto}: {qtd} carros. Gabarito: 0")


# Erros:
# 24:10 Caminhao 3x
# 25:20 VARIOS ERROS


# Minuto 1:
#   8 Carros
# Minuto 2:
#   5 Carros
#   1 Caminhão
# Minuto 3:
#   1 Bike
#   2 Carro
# Minuto 4:
#   13 Carro
# Minuto 5:
#   6 Carro

# Total: 36 Carros, 1 Bike, 1 Caminhão
# Total: 38