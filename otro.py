import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

# Datos de los agentes
data = {
    'IDAGENTE': [144105, 166150, 701200, 701201, 705100, 705101, 705102, 705103, 705104, 801104, 801105, 801116, 801117, 801127, 801130],
    'Ventas Totales': [425.95, 1825.89, 2638.79, 2876.61, 3034.74, 1360.63, 1829.00, 1393.55, 1519.34, 3063.74, 1255.28, 2978.99, 3945.43, 2659.92, 2412.45],
    'Rentabilidad Total': [8.05, 45.73, 57.95, 69.85, 69.70, 26.08, 47.98, 34.71, 34.39, 78.95, 39.13, 67.56, 93.51, 68.00, 67.07],
    'Numero de Establecimientos': [3, 19, 18, 20, 21, 7, 13, 13, 12, 25, 15, 24, 28, 24, 23]
}

# Crear un DataFrame
df = pd.DataFrame(data)

# Crear un gráfico de boxplot para las ventas totales
plt.figure(figsize=(10, 6))
sns.boxplot(data=df[['Ventas Totales']], color='skyblue')
plt.title('Distribución de Ventas Totales por Agente')
plt.ylabel('Ventas Totales (miles)')
plt.show()

# Crear un gráfico de boxplot para la rentabilidad total
plt.figure(figsize=(10, 6))
sns.boxplot(data=df[['Rentabilidad Total']], color='lightgreen')
plt.title('Distribución de Rentabilidad Total por Agente')
plt.ylabel('Rentabilidad Total (miles)')
plt.show()

# Crear un gráfico de boxplot para el número de establecimientos gestionados
plt.figure(figsize=(10, 6))
sns.boxplot(data=df[['Numero de Establecimientos']], color='lightcoral')
plt.title('Distribución del Número de Establecimientos por Agente')
plt.ylabel('Número de Establecimientos')
plt.show()
