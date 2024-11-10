# Car Tracking

This project implements a car counting system using computer vision techniques with OpenCV. The main functionality is provided by the `contar_carros` function in the 

main.py

 file, which processes video footage to detect and count cars crossing a specified line.

## Features

- **Video Processing**: Loads and processes video frames to detect moving objects.
- **Background Subtraction**: Uses background subtraction to identify moving objects in the video.
- **Contour Detection**: Detects contours of moving objects and filters them based on size to identify cars.
- **Car Counting**: Counts cars that cross a specified vertical line in the video.
- **Display Options**: Provides options to display various stages of the processing pipeline for debugging purposes.

## Usage

The main function `contar_carros` takes the following parameters:
- `video_path` (str): Path to the video file.
- `mostrar_na_tela` (bool): Whether to display the video frames during processing.
- `windows` (str): Display mode, either 'debug' to show intermediate processing steps or 'final' to show only the final output.

Example usage:
```python
qtd = contar_carros(video_path='Camera_Footage.mp4', mostrar_na_tela=True, windows='debug')
print(f"Total de carros contados: {qtd}")
```

## References

- [Computer Vision with OpenCV: Building a Car Counting System](https://medium.com/@andresberejnoi/computer-vision-with-opencv-building-a-car-counting-system-andres-berejnoi-8bcc29fc256)
- [YouTube Video](https://www.youtube.com/watch?v=_UGCBud63Eo&ab_channel=Andr%C3%A9sBerejnoi)
- [GitHub Repository](https://github.com/andresberejnoi/OpenCV_Traffic_Counter)