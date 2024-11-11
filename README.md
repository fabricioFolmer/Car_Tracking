# Car Tracking

Este projeto implementa um sistema de contagem de carros utilizando técnicas de visão computacional com OpenCV. A principal funcionalidade é fornecida pela função `contar_carros` no arquivo `main.py`, que processa gravações de vídeo para detectar e contar carros que cruzam uma linha especificada.

## Requerimentos:

- Python 3.XX;
- Bibliotecas cv2 e numpy (pip install numpy opencv-contrib-python);
- Arquivo `'Camera_Footage.mp4'` na pasta do script ([link](https://drive.google.com/file/d/1UiXeEiafLQtdurwEUUKY9O2BhqZ4OJ8s/view?usp=drive_link)). 

## Uso

A função principal `contar_carros` recebe os sequintes parâmetros:
- `video_path` (str): Caminho do arquivo de vídeo;
- `mostrar_na_tela` (bool): Mostrar ou não na tela o vídeo durante o processamento;
- `windows` (str): Modo de exibição. Deve ser 'debug' - para mostrar o passo a passo do processamento de imagem na tela - ou 'final' - para mostrar apenas a imagem final, já processada.

Exemplo de uso:
```python
qtd = contar_carros(video_path='Camera_Footage.mp4', mostrar_na_tela=True, windows='debug')
print(f"Total de carros contados: {qtd}")
```

## Método de Contagem

1. **Processamento de Vídeo**: Cada frame do vídeo é capturado e processado.
1. **Conversão para Escala de Cinza**: O frame atual é convertido para escala de cinza e suavizado para reduzir ruídos, aumentando a performance (essencial em IoT).
1. **Subtração de Fundo**: A diferença entre o frame atual e um fundo atualizado gradualmente é calculada para identificar áreas de movimento.
1. **Limiarização e Operações Morfológicas**: A imagem resultante é binarizada e operações morfológicas são aplicadas para preencher buracos e remover ruídos.
1. **Detecção de Contornos**: Contornos são detectados na imagem binarizada.
1. **Filtragem de Contornos**: Contornos pequenos são filtrados com base na área, e centros dos contornos são calculados.
1. **Verificação de Cruzamento da Linha**: Verifica-se se o centro de um contorno cruzou uma linha vertical específica traçando uma linha entre o centro do veículo no frame atual com o centro do mesmo no frame anterior.
1. **Contagem de Carros**: Se um contorno cruzar a linha, incrementa-se o contador de carros.

## Referências

Computer Vision with OpenCV: Building a Car Counting System. Disponível em 
- [Medium](https://medium.com/@andresberejnoi/computer-vision-with-opencv-building-a-car-counting-system-andres-berejnoi-8bcc29fc256)
- [YouTube](https://www.youtube.com/watch?v=_UGCBud63Eo&ab_channel=Andr%C3%A9sBerejnoi)
- [GitHub Repo](https://github.com/andresberejnoi/OpenCV_Traffic_Counter)