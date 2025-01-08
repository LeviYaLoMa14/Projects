import tkinter as tk
import serial
import time

# Configura el puerto serie
puerto = 'COM11'  
baud_rate = 9600 

# Parámetros del cálculo 
E = 10  # Voltaje de entrada
R = 10000  # Resistencia punto de calibracion
E1 = E / 2  # Configuración de E1
b = 12495  # Valor de b para la fórmula de temperatura
m = -99.8  # Pendiente de la fórmula de temperatura
CombinacionBinaria = 255  # Valor máximo de la combinación binaria (8 bits)
Vresolucion = E1 / CombinacionBinaria  # Resolución del voltaje

# Inicializa el puerto serie
ser = serial.Serial(puerto, baud_rate, timeout=1)

# Función para calcular la temperatura
def calcular_temperatura(binario_decimal):
    # Paso 1: Calcular el voltaje de salida
    Vsalida = binario_decimal * Vresolucion

    # Paso 2: Calcular E2
    E2 = E1 - Vsalida

    # Paso 3: Calcular la variación de la resistencia
    DeltaR = R * ((E - (2 * E2)) / (E - E2))

    # Paso 4: Calcular la resistencia del sensor
    Rsensor = R - DeltaR

    # Paso 5: Calcular la temperatura
    Temperatura = (Rsensor - b) / m

    return Temperatura

# Función para actualizar la interfaz con la temperatura
def actualizar():
    if ser.in_waiting > 0:
        datos_binarios = ser.read(ser.in_waiting)

        for byte in datos_binarios:
            # Valor binario recibido (8 bits)
            binario_decimal = byte
            print(f"Valor binario recibido: {binario_decimal} (decimal)")  # Depuración

            # Calcular la temperatura
            temperatura = calcular_temperatura(binario_decimal)
            print(f"Temperatura calculada: {temperatura:.2f}°C")  # Depuración

            # Actualizar la etiqueta de temperatura
            label_temperatura.config(text=f"Temperatura: {temperatura:.2f} °C")
            
            # Cambiar el color del termómetro según la temperatura
            if temperatura < 30:
                color = 'blue'  # Frío
            elif 30 <= temperatura <= 50:
                color = 'yellow'  # Temperatura ambiente
            else:
                color = 'red'  # Calor
            canvas_termo.config(bg=color)
            
            # Actualizar la barra de llenado del termómetro
            # Mapeamos la temperatura de 25 a 1150 grados a la altura del termómetro
            temperatura_normalizada = max(25, min(temperatura, 126))  # Limitar a 25-126 grados
            altura_barra = 270 - (temperatura_normalizada * 2)  # 280 (tamaño del termómetro) menos el tamaño de la barra

            # Usamos coords() para mover la barra de llenado en el lienzo
            canvas_termo.coords(barra_llenado, 55, altura_barra, 95, 280)

    # Llamar nuevamente a la función de actualización después de 100 ms
    root.after(100, actualizar)

# Crear la ventana principal de la interfaz gráfica
root = tk.Tk()
root.title("Visualización de Temperatura")

# Etiqueta para mostrar la temperatura
label_temperatura = tk.Label(root, text="Temperatura: 0.00 °C", font=("Arial", 16))
label_temperatura.pack(pady=20)

# Crear un lienzo para el termómetro
canvas_termo = tk.Canvas(root, width=150, height=300, bg='lightgray')
canvas_termo.pack(pady=20)

# Dibujo del termómetro
canvas_termo.create_rectangle(50, 20, 100, 280, outline="black", width=3)  # Termómetro
canvas_termo.create_line(75, 20, 75, 280, fill="black", width=5)  # Líneas del termómetro

# Barra de llenado para la temperatura (vacío inicialmente)
barra_llenado = canvas_termo.create_rectangle(55, 280, 95, 280, fill="gray", outline="gray")

# Iniciar la actualización de la interfaz
root.after(100, actualizar)

# Ejecutar la interfaz gráfica
root.mainloop()

# Cerrar el puerto serie al terminar
ser.close()
