import cv2
import numpy as np
import os
from skimage import measure
from skimage.filters import threshold_otsu
import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk
from scipy import ndimage
from skimage.feature import peak_local_max
from skimage.segmentation import watershed

class CellDetectorApp:
    def __init__(self, root):
        # Preparamos la ventana principal donde vamos a trabajar
        self.root = root
        self.root.title("Detector de Células")
        
        # Hacemos que la interfaz se adapte al tamaño de la ventana
        # es útil cuando queremos hacer la ventana más grande o pequeña, aunque aun noo funciona del todo bn
        self.root.columnconfigure(0, weight=10)
        self.root.rowconfigure(0, weight=10)
        
        # Aquí guardamos las diferentes versiones de la imagen mientras la procesamos
        # Es como tener diferentes capas de la misma foto
        self.current_images = {}
        self.current_image_path = None
        
        # Estos son los valores iniciales para nuestros controles
        # Los podemos ajustar después según necesitemos
        # gaussian_kernel: Controla el suavizado de la imagen
        #   - Valores bajos (1-3): Mantiene más detalles pero también más ruido
        #   - Valores altos (7-11): Elimina ruido pero puede perder células pequeñas
        self.gaussian_kernel = tk.IntVar(value=1)    # Para suavizar bordes

        # morph_kernel: Tamaño del kernel para operaciones morfológicas
        #   - Valores bajos (3-5): Limpieza suave, mantiene detalles finos
        #   - Valores altos (7-11): Limpieza más agresiva, puede unir células cercanas
        self.morph_kernel = tk.IntVar(value=3)       # Para limpiar ruido

        # morph_iterations: Número de veces que se aplica la operación morfológica
        #   - Valores bajos (1-2): Limpieza ligera
        #   - Valores altos (4-5): Limpieza intensa, puede eliminar células pequeñas
        self.morph_iterations = tk.IntVar(value=2)   # Cantidad de limpieza

        # min_cell_size: Tamaño mínimo para considerar una región como célula
        #   - Valores bajos (5-15): Detecta células más pequeñas pero puede incluir ruido
        #   - Valores altos (30-50): Ignora células pequeñas pero más confiable
        self.min_cell_size = tk.IntVar(value=10)     # Células más pequeñas que esto se ignoran

        # max_cell_size: Tamaño máximo para considerar una región como célula
        #   - Valores bajos (100-300): Puede dividir células grandes
        #   - Valores altos (600-1000): Permite detectar células más grandes o agrupadas
        self.max_cell_size = tk.IntVar(value=600)    # Células más grandes que esto se ignoran

        # min_distance: Distancia mínima entre centros de células
        #   - Valores bajos (1-5): Permite detectar células muy juntas
        #   - Valores altos (10-20): Evita detecciones múltiples pero puede perder células cercanas
        self.min_distance = tk.IntVar(value=1)       # Qué tan juntas pueden estar las células
        
        # Crear el marco principal
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar el grid del marco principal
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(1, weight=1)
        
        # Botones de control
        self.create_control_buttons()
        
        # Área de visualización
        self.create_image_display()
        
        # Etiqueta para mostrar información
        self.info_label = ttk.Label(self.main_frame, text="")
        self.info_label.grid(row=2, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        
        # Crear el panel de control de parámetros
        self.create_parameter_controls()

    def create_control_buttons(self):
        control_frame = ttk.Frame(self.main_frame)
        control_frame.grid(row=0, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Button(control_frame, text="Abrir Imagen", command=self.open_image).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Procesar Directorio", command=self.process_directory).pack(side=tk.LEFT, padx=5)
        
        # Combobox para seleccionar la vista
        self.view_var = tk.StringVar()
        self.view_combo = ttk.Combobox(control_frame, textvariable=self.view_var)
        # Vistas disponibles:
        # - Original: Imagen sin procesar
        # - Escala de Grises: Conversión a grises para mejor procesamiento
        # - Filtro Gaussiano: Imagen suavizada para reducir ruido
        # - Binaria (Otsu): Separación entre células y fondo
        # - Morfología: Resultado después de limpiar ruiz|do
        # - Watershed: Visualización de la segmentación de células
        # - Resultado: Imagen final con células marcadas y numeradas
        self.view_combo['values'] = ['Original', 'Escala de Grises', 'Filtro Gaussiano', 
                                   'Binaria (Otsu)', 'Morfología', 'Watershed', 'Resultado']
        self.view_combo.pack(side=tk.LEFT, padx=5)
        self.view_combo.set('Original')
        self.view_combo.bind('<<ComboboxSelected>>', self.update_image_display)

    def create_image_display(self):
        self.canvas = tk.Canvas(self.main_frame)
        self.canvas.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.main_frame.rowconfigure(1, weight=1)  # Asegúrate de que el canvas se expanda

        # Bind mouse wheel event for zooming
        self.canvas.bind("<MouseWheel>", self.zoom_image)

    def zoom_image(self, event):
        if not self.current_images:
            return

        # Get the current view
        selected_view = self.view_var.get()
        if selected_view not in self.current_images:
            return

        # Get the current image
        image = self.current_images[selected_view]

        # Determine the zoom factor
        scale = 1.1 if event.delta > 0 else 0.9

        # Resize the image
        width, height = image.shape[1], image.shape[0]
        new_width = int(width * scale)
        new_height = int(height * scale)
        resized_image = cv2.resize(image, (new_width, new_height))

        # Convert to PIL and then to PhotoImage
        image_pil = Image.fromarray(resized_image)
        self.photo = ImageTk.PhotoImage(image=image_pil)

        # Update canvas
        self.canvas.config(width=new_width, height=new_height)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)

    def open_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.tif *.tiff")])
        if file_path:
            self.process_single_image(file_path)

    def process_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            image_files = [f for f in os.listdir(directory) 
                         if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff'))]
            total_cells = 0
            
            for image_file in image_files:
                file_path = os.path.join(directory, image_file)
                num_cells = self.process_single_image(file_path)
                total_cells += num_cells
                
            self.info_label.config(text=f"Procesamiento completado. Total de células: {total_cells}")

    def process_single_image(self, image_path):
        """
        Aquí procesamos la imagen paso a paso para encontrar las células.
        """
        self.current_image_path = image_path
        img = cv2.imread(image_path)
        
        # Primero pasamos la imagen a escala de grises
        # Esto nos ayuda a ver mejor los bordes y formas
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Suavizamos la imagen para quitar el ruido
        # Un valor más alto hace la imagen más borrosa, lo que puede ayudar con imágenes muy ruidosas
        # pero también puede hacer que perdamos células pequeñas
        gaussian_size = self.ensure_odd(self.gaussian_kernel.get())
        blurred = cv2.GaussianBlur(gray, (gaussian_size, gaussian_size), 0)
        
        # Otsu nos ayuda a separar las células del fondo
        # Es bastante bueno encontrando el punto medio entre lo que es célula y lo que no
        thresh = threshold_otsu(blurred)
        binary = (blurred > thresh).astype(np.uint8) * 255
        
        # Limpiamos la imagen de manchas y ruido
        # Más iteraciones = más limpieza, pero podemos perder detalles importantes
        morph_size = self.ensure_odd(self.morph_kernel.get())
        kernel = np.ones((morph_size, morph_size), np.uint8)
        opening = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, 
                                 iterations=self.morph_iterations.get())
        
        dist_transform = ndimage.distance_transform_edt(opening)
        
        # Asegurar que el kernel sea impar para el suavizado Gaussiano
        kernel_size = 7  # Cambiamos a un valor impar fijo
        dist_transform = cv2.GaussianBlur(dist_transform, (kernel_size, kernel_size), 0)
        
        local_max = peak_local_max(
            dist_transform, 
            min_distance=self.min_distance.get(),
            exclude_border=False,
            num_peaks=np.inf,
            footprint=np.ones((3, 3)),
            labels=opening
        )
        
        # Crear marcadores para watershed
        markers = np.zeros_like(dist_transform, dtype=int)
        markers[tuple(local_max.T)] = range(1, len(local_max) + 1)
        
        # Aplicar watershed
        labels = watershed(-dist_transform, markers, mask=opening)
        
        # Ahora sí podemos usar labels para regionprops
        props = measure.regionprops(labels)
        valid_cells = [prop for prop in props 
                      if self.min_cell_size.get() < prop.area < self.max_cell_size.get()]
        
        # Visualización de resultados
        # Dibuja círculos verdes en los centros y números para identificar cada célula
        result = img.copy()
        for i, cell in enumerate(valid_cells, start=1):
            y, x = cell.centroid
            cv2.circle(result, (int(x), int(y)), 5, (0, 255, 0), -1)
            cv2.putText(result, str(i), (int(x), int(y)), cv2.FONT_HERSHEY_SIMPLEX, 
                        0.5, (255, 0, 0), 1, cv2.LINE_AA)
            
        # Guardar imágenes procesadas
        self.current_images = {
            'Original': cv2.cvtColor(img, cv2.COLOR_BGR2RGB),
            'Escala de Grises': cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB),
            'Filtro Gaussiano': cv2.cvtColor(blurred, cv2.COLOR_GRAY2RGB),
            'Binaria (Otsu)': cv2.cvtColor(binary, cv2.COLOR_GRAY2RGB),
            'Morfología': cv2.cvtColor(opening, cv2.COLOR_GRAY2RGB),
            'Watershed': cv2.cvtColor((labels * 50).astype(np.uint8), cv2.COLOR_GRAY2RGB),
            'Resultado': cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
        }
        
        # Actualizar el combobox con la nueva vista
        self.view_combo['values'] = list(self.current_images.keys())
        
        # Guardar resultado
        output_path = f'detected_{os.path.basename(image_path)}'
        cv2.imwrite(output_path, result)
        
        # Actualizar display
        self.update_image_display()
        
        num_cells = len(valid_cells)
        self.info_label.config(text=f"Células detectadas: {num_cells}")
        return num_cells

    def update_image_display(self, event=None):
        """
        Actualiza lo que vemos en pantalla cuando cambiamos entre diferentes
        vistas o ajustamos los parámetros.
        """
        if not self.current_images:
            return
            
        selected_view = self.view_var.get()
        if selected_view in self.current_images:
            image = self.current_images[selected_view]
            # Ajustamos el tamaño si la imagen es muy grande
            # 800 píxeles es un buen tamaño para ver detalles sin que ocupe toda la pantalla
            height, width = image.shape[:2]
            max_size = 800
            if width > max_size or height > max_size:
                scale = max_size / max(width, height)
                new_width = int(width * scale)
                new_height = int(height * scale)
                image = cv2.resize(image, (new_width, new_height))
            
            # Convertir a formato PIL y luego a PhotoImage
            image_pil = Image.fromarray(image)
            self.photo = ImageTk.PhotoImage(image=image_pil)
            
            # Actualizar canvas
            self.canvas.config(width=image.shape[1], height=image.shape[0])
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)

    def create_parameter_controls(self):
        """
        Creamos los controles que nos permiten ajustar cómo se procesa la imagen.
        Cada control afecta una parte diferente del proceso.
        """
        param_frame = ttk.LabelFrame(self.main_frame, 
                                   text="Controles de Procesamiento", 
                                   padding="5")
        param_frame.grid(row=0, column=2, rowspan=2, 
                        sticky=(tk.N, tk.S, tk.E, tk.W), padx=5)
        
        # Función para actualizar las etiquetas de valor
        def create_slider_with_value(parent, text, variable, from_, to):
            frame = ttk.Frame(parent)
            frame.pack(fill=tk.X, padx=5, pady=2)
            
            label = ttk.Label(frame, text=text)
            label.pack(anchor=tk.W)
            
            value_label = ttk.Label(frame, text=str(variable.get()))
            value_label.pack(side=tk.RIGHT)
            
            def update_value(*args):
                value_label.config(text=str(variable.get()))
                
            slider = ttk.Scale(frame, from_=from_, to=to, 
                              orient=tk.HORIZONTAL,
                              variable=variable,
                              command=update_value)
            slider.pack(fill=tk.X, expand=True, padx=(0, 5))
            
            return slider
        
        # Crear sliders con sus etiquetas de valor
        create_slider_with_value(param_frame, 
                               "Nivel de suavizado:", 
                               self.gaussian_kernel, 1, 11)
        
        create_slider_with_value(param_frame, 
                               "Kernel Morfológico:", 
                               self.morph_kernel, 3, 11)
        
        create_slider_with_value(param_frame, 
                               "Iteraciones Morfológicas:", 
                               self.morph_iterations, 1, 5)
        
        create_slider_with_value(param_frame, 
                               "Tamaño Mínimo Célula:", 
                               self.min_cell_size, 5, 500)
        
        create_slider_with_value(param_frame, 
                               "Tamaño Máximo Célula:", 
                               self.max_cell_size, 100, 1000)
        
        create_slider_with_value(param_frame, 
                               "Distancia Mínima Entre Células:", 
                               self.min_distance, 1, 20)
        
        # Botón para reprocesar
        ttk.Button(param_frame, text="Reprocesar Imagen",
                  command=self.reprocess_current_image).pack(pady=10)

    def reprocess_current_image(self):
        """Reprocesa la imagen actual con los nuevos parámetros"""
        if self.current_image_path:
            self.process_single_image(self.current_image_path)

    def ensure_odd(self, n):
        """
        OpenCV necesita números impares para sus filtros, así que nos aseguramos
        de que el número sea siempre impar sumándole 1 si es necesario.
        """
        return n + 1 if n % 2 == 0 else n

def main():
    root = tk.Tk()
    app = CellDetectorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()