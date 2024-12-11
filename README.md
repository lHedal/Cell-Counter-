# Cell-Counter-

# Detector de Células

## Descripción
Este proyecto implementa una aplicación de escritorio para el análisis y conteo automático (o no) de células en imágenes microscópicas. Utiliza técnicas avanzadas de procesamiento de imágenes y segmentación watershed para identificar y contar células de manera precisa.

## Características Principales
- 🖼️ Interfaz gráfica intuitiva
- 📁 Procesamiento individual o por lotes de imágenes
- 🔍 Zoom interactivo en las imágenes
- 📊 Múltiples vistas del proceso de análisis:
  - Imagen original
  - Escala de grises
  - Filtro gaussiano
  - Binarización (Otsu)
  - Morfología
  - Watershed
  - Resultado final
- ⚙️ Controles ajustables en tiempo real:
  - Nivel de suavizado
  - Kernel morfológico
  - Iteraciones morfológicas
  - Tamaños mínimo y máximo de células
  - Distancia mínima entre células

## Requisitos del Sistema
- Python 3.7 o superior
- Sistema operativo: Windows/Linux/MacOS

## Dependencias
bash
opencv-python>=4.5.0
numpy>=1.19.0
scikit-image>=0.18.0
pillow>=8.0.0
scipy>=1.6.0
tkinter (incluido en Python)


## Instalación
1. Clonar el repositorio:
    bash
    git clone https://github.com/tu-usuario/detector-celulas.git
    cd detector-celulas


2. Crear un entorno virtual (opcional pero recomendado):
    bash
    python -m venv venv
    source venv/bin/activate # En Linux/MacOS
    venv\Scripts\activate # En Windows


3. Instalar dependencias:


## Uso
1. Ejecutar la aplicación: 

    bash
    python CellCounter.py


2. Para analizar imágenes:
   - Click en "Abrir Imagen" para procesar una imagen individual
   - Click en "Procesar Directorio" para analizar múltiples imágenes
   - Ajustar los parámetros según sea necesario
   - Usar el menú desplegable para ver las diferentes etapas del procesamiento

## Parámetros Ajustables

### Nivel de Suavizado (1-11)
- Controla el kernel gaussiano para suavizar la imagen
- Valores bajos: Mantiene más detalles pero más ruido
- Valores altos: Elimina ruido pero puede perder células pequeñas

### Kernel Morfológico (3-11)
- Define el tamaño del kernel para operaciones morfológicas
- Valores bajos: Limpieza suave, mantiene detalles finos
- Valores altos: Limpieza más agresiva, puede unir células cercanas

### Iteraciones Morfológicas (1-5)
- Número de veces que se aplica la operación morfológica
- Valores bajos: Limpieza ligera
- Valores altos: Limpieza intensa

### Tamaño Mínimo de Célula (5-500)
- Define el área mínima para considerar una región como célula
- Ayuda a filtrar ruido y artefactos pequeños

### Tamaño Máximo de Célula (100-1000)
- Define el área máxima para una célula individual
- Ayuda a identificar grupos de células

### Distancia Mínima Entre Células (1-20)
- Define la separación mínima entre centros de células
- Ayuda a evitar detecciones duplicadas

## Salida
- Genera una imagen con células numeradas y marcadas
- Muestra el conteo total de células
- Guarda automáticamente los resultados con el prefijo "detected_"

## Contribuciones
Las contribuciones son bienvenidas. Por favor, sigue estos pasos:
1. Fork el repositorio
2. Crea una rama para tu característica (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## Licencia
Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## Autor
HedaAllows

## Contacto
- GitHub: [@HedaAllows](https://github.com/HedaAllows)


