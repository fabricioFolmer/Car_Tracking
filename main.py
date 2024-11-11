import cv2, time, math, numpy as np
from typing import Literal

# Código por Fabrício Landskren Folmer

# TODO Retornar apenas a quantidade de carros e remover correção de contagem e gabarito
# TODO Remover Chat desse código https://chatgpt.com/c/6730c31c-74a8-8008-9348-8dbac3574b65
# TODO Remover linhas referentes a atualização do background

def contar_carros(video_path: str, mostrar_na_tela: bool = True, windows: str = 'debug') -> tuple[int, dict[int, int]]:
    # Função para contar carros em um vídeo
    # Parâmetros:
    # - video_path: caminho do vídeo
    # - mostrar_na_tela: se True, mostra o vídeo com os contornos e a linha de contagem
    # - windows: 'debug' para mostrar todas as janelas, 'final' para mostrar apenas o vídeo final
    # Retorna:
    # - quantidade de carros contados
    
    def apurar_centro_contornos(lst_contornos: list) -> list:
        # Apura os centros dos contornos
        # Parâmetros:
        # - lst_contornos: lista de contornos
        # Retorna:
        # - lista de tuplas contendo os centros dos contornos
        
        lst = []

        # Loop para cada contorno da lista
        for contour in lst_contornos:
            # Filtra contornos pequenos com base na área
            x, y, w, h = cv2.boundingRect(contour)
            if w >= largura_minima and h >= largura_maxima:
                lst.append((x + w // 2, y + h // 2))

        return lst

    def centro_mais_perto(centro, centros):
        # Determina o centro mais próximo de um centro informado
        # Parâmetros:
        # - centro: tupla contendo as coordenadas (x, y) do centro
        # - centros: lista de tuplas contendo os centros
        # Retorna:
        # - tupla contendo as coordenadas do centro mais próximo
        
        menor_dist = None
        centro_mais_proximo = None

        # Loop para cada centro da lista
        for c in centros:

            # Determina a distância entre c e centro, usando o teorema de Pitágoras
            dist = math.sqrt((c[0] - centro[0])**2 + (c[1] - centro[1])**2)
            
            # Atualiza o centro_mais_proximo se a distância for a menor encontrada até agora
            if menor_dist is None or dist < menor_dist:
                menor_dist = dist
                centro_mais_proximo = c
        
        return centro_mais_proximo

    def passou_pela_linha(centro, dist_maxima, centros_frame_atual, centros_ultimo_frame, tipo_linha: Literal['horizontal', 'vertical'], line_position: int) -> bool:
    # Verifica se o centro de um contorno cruzou a linha de contagem
    # Parâmetros:
    # - centro: tupla contendo as coordenadas (x, y) do centro do contorno
    # - dist_maxima: distância máxima entre o centro informado e o centro do último frame para considerar que é o mesmo contorno
    # - centros_frame_atual: lista de tuplas contendo os centros dos contornos do frame atual
    # - centros_ultimo_frame: lista de tuplas contendo os centros dos contornos do último frame
    # - tipo_linha: tipo de linha de contagem ('horizontal' ou 'vertical')
    # - line_position: posição da linha de contagem
    # Retorna:
    # - True se o contorno cruzou a linha de contagem, False caso contrário
    
        # Determina o centro do último frame mais próximo do centro informado. Variável 'centro_frame_anterior'
        menor_dist = centro_frame_anterior = None
        for c in centros_ultimo_frame:

            # Determina a distância entre c e centro, usando o teorema de Pitágoras
            dist = math.sqrt((c[0] - centro[0])**2 + (c[1] - centro[1])**2)
            
            # Atualiza o centro_frame_anterior se a distância for a menor encontrada até agora. 
            # Desconsiderando casos onde a distância é maior do que a área do contorno atual
            if (menor_dist is None or dist < menor_dist) and dist < dist_maxima:
                
                # Verifica se o centro anterior encontrado possui um outro centro mais próximo no novo frame.
                # Se ele possui, quer dizer que o centro informado é um novo contorno, e não o mesmo que o anterior, e por isso deve ser ignorado
                if centro_mais_perto(c, centros_frame_atual) == centro:
                    menor_dist = dist
                    centro_frame_anterior = c

        # Debug Mostra uma linha entre os centros
        if mostrar_na_tela is True and windows == 'debug':
            cv2.line(dict_frames['frame'], centro, centro_frame_anterior, (0, 255, 255), 2)
            
        # Se não encontrar um centro do último frame próximo ao centro informado, retorna False
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
        
        # Se não cruzar a linha de contagem, retorna False
        return False

    # Verifica se o argumento 'windows' é válido
    if windows not in ['debug', 'final']:
        raise ValueError("Argumento 'windows' deve ser 'debug' ou 'final'")
    else:
        # Define quais frames serão mostrados na tela
        if windows == 'debug':
            frames = ['frame', 'gray_frame', 'background', 'frame_delta', 'fg_mask']
        else:
            frames = ['frame']

    # Define variáveis
    qtd_carros = 0              # Contador de carros
    largura_minima = 40         # Largura mínima do contorno detectado para contar como carro
    largura_maxima = 40         # Altura mínima do contorno detectado para contar como carro
    pos_da_linha = 430          # Posição da linha vertical de contagem (local mais visível da rua)
    centros_ultimo_frame = []   # Lista de centros dos contornos do último frame. Usado para determinar se um carro cruzou a linha de contagem
    dict_resultados = {}        # Dicionário para armazenar os resultados da contagem a cada minuto
    background = None           # Inicializa o background como None
    alpha = 0.01                # Taxa de atualização do background (fator de suavização)

    # Carrega o vídeo
    cap = cv2.VideoCapture(video_path)

    # Loop através de cada frame no vídeo
    while cap.isOpened():
        
        # Mostra na tela apenas após o minuto X TODO Remover
      #  if ((cap.get(cv2.CAP_PROP_POS_MSEC) / 1000 / 60) + 1) >= 5.34:
      #      mostrar_na_tela = True
      #      time.sleep(.2)

        # Erros: TODO Remover
        # 4.17: 2 carros contam como 1
        # Minuto 5: Embora a contagem total está correta, vários carros foram mesclados como um

        # Lê o próximo frame
        ret, frame = cap.read()
        if not ret:
            break
        
        # Converte o frame atual para escala de cinza. 4x para reduzir ruído com maior efetividade
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray_frame = cv2.GaussianBlur(gray_frame, (21, 21), 0)  # Aplica suavização para reduzir ruído
        gray_frame = cv2.GaussianBlur(gray_frame, (21, 21), 0)  # Aplica suavização para reduzir ruído
        gray_frame = cv2.GaussianBlur(gray_frame, (21, 21), 0)  # Aplica suavização para reduzir ruído
        gray_frame = cv2.GaussianBlur(gray_frame, (21, 21), 0)  # Aplica suavização para reduzir ruído

        # Inicializa a imagem de fundo com o primeiro frame
        if background is None:
            background = gray_frame.astype("float")
            continue
        
        # Atualiza o background gradualmente com o frame atual      # TODO Evoluir para desconsiderar áreas de movimento lentas, como background
        # NEW Cria uma máscara binária para áreas de movimento (usada para evitar atualização com áreas móveis)
        #_, movement_mask = cv2.threshold(frame_delta, 25, 1, cv2.THRESH_BINARY)
        #inverse_mask = cv2.bitwise_not(movement_mask)  # Máscara inversa para áreas estáticas (background)
        # cv2.accumulateWeighted(gray_frame, background, alpha) # , mask=inverse_mask)
        
        # Calcula a diferença entre o background atualizado e o frame atual
        frame_delta = cv2.absdiff(gray_frame, cv2.convertScaleAbs(background))
        
        # Aplica limiar para obter uma imagem binária, onde áreas de movimento são destacadas
        _, fg_mask = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)
        
        # Aplica operações morfológicas para preencher buracos e remover ruídos. 4x para remover ruídos com maior efetividade
        fg_mask = cv2.dilate(fg_mask, None)
        fg_mask = cv2.dilate(fg_mask, None)
        fg_mask = cv2.dilate(fg_mask, None)
        fg_mask = cv2.dilate(fg_mask, None)

        # Encontra contornos
        contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Dicionário para armazenar os objeto dos frames para exibição
        dict_frames = {'frame': frame, 'gray_frame': gray_frame, 'background': cv2.convertScaleAbs(background), 'frame_delta': frame_delta, 'fg_mask': fg_mask}

        # Processa cada contorno do frame
        centros_frame_atual = apurar_centro_contornos(contours)
        for contour in contours:

            # Filtra contornos pequenos com base na área
            x, y, w, h = cv2.boundingRect(contour)
            if w >= largura_minima and h >= largura_maxima:

                # Desenha um retângulo em torno dos contornos detectados, e um ponto no centro
                for frm in frames:
                    cv2.rectangle(dict_frames[frm], (x, y), (x + w, y + h), (255, 0, 0), 2)
                    cv2.circle(dict_frames[frm], (x + w // 2, y + h // 2), 5, (0, 255, 0), -1)
                
                # Determina se o carro cruzou a linha vertical
                centro = (x + w // 2, y + h // 2)
                if passou_pela_linha(centro, w, centros_frame_atual, centros_ultimo_frame, 'vertical', pos_da_linha) is True:
                    minuto_atual = int(cap.get(cv2.CAP_PROP_POS_MSEC) / 1000 / 60) + 1 # TODO Remover
                    if minuto_atual not in dict_resultados: # TODO Remover
                        dict_resultados[minuto_atual] = 1 # TODO Remover
                    else: # TODO Remover
                        dict_resultados[minuto_atual] += 1 # TODO Remover
                    qtd_carros += 1
                    # Debug print(f'{qtd_carros}:  {cap.get(cv2.CAP_PROP_POS_MSEC) / 1000 / 60 + 1}') # TODO Remover

        # Atualiza os centros do último frame, para comparar com o próximo frame
        centros_ultimo_frame = centros_frame_atual.copy()

        # Configurações da janela de exibição
        if mostrar_na_tela is True:

            # Exibe a linha de contagem vertical
            cv2.line(frame, (pos_da_linha, 0), (pos_da_linha, frame.shape[0]), (0, 0, 255), 2)

            # Exibe o frame com a contagem de carros
            for frm in frames:
                cv2.putText(dict_frames[frm], f"Carros Contados: {qtd_carros}", (10, 60), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
                cv2.putText(dict_frames[frm], f"Contornos processados no frame: {len(contours)}", (10, 100), cv2.FONT_HERSHEY_COMPLEX, .5, (255, 255, 255), 1)
                cv2.imshow(frm, dict_frames[frm])

            # Encerra o loop se a tecla 'q' for pressionada ou se a janela principal for fechada
            if cv2.waitKey(30) & 0xFF == ord('q') or cv2.getWindowProperty("frame", cv2.WND_PROP_VISIBLE) < 1:
                break

            # Exibe o tempo atual do vídeo se a tecla 't' for pressionada
            if cv2.waitKey(30) & 0xFF == ord('t'):
                print(cap.get(cv2.CAP_PROP_POS_MSEC) / 1000 / 60)
            
    # Libera os recursos
    cap.release()
    cv2.destroyAllWindows()

    return qtd_carros, dict_resultados


# Exemplo de uso
qtd, dict_resultados = contar_carros(video_path='Camera_Footage.mp4', mostrar_na_tela=True, windows='debug')

# TODO Remover a partir daqui
# Exibe o resultado final da contagem
print(f"Total de carros contados: {qtd}. Eram esperados 39.")

# Checagem do gabarito
gabarito = {1: 8, 2: 7, 3: 3, 4: 13, 5: 6}
for minuto, qtd in dict_resultados.items():
    if minuto in gabarito:
        if qtd != gabarito[minuto]:
            print(f"Erro no minuto {minuto}: {qtd} carros. Gabarito: {gabarito[minuto]}")
    else:
        print(f"Erro no minuto {minuto}: {qtd} carros. Gabarito: 0")


#   Gabarito:

# Minuto 1:
#   8 Carros
# Minuto 2:
#   5 Carros
#   1 Caminhão
#   1 Moto
# Minuto 3:
#   1 Bike
#   2 Carro
# Minuto 4:
#   13 Carro
# Minuto 5:
#   6 Carro

# Total: 36 Carros, 1 moto, 1 Bike, 1 Caminhão
# Total: 39