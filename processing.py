import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
import datetime

def generar_base_datos():
    print("Generando datos simulados (ETL)... Por favor espere.")
    np.random.seed(42)

    # --- 1. CONFIGURACIÓN INICIAL ---
    start_date = datetime.date(2024, 1, 1)
    end_date = datetime.date(2025, 12, 31)
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    
    n_customers = 300
    n_stores = 8
    
    customers = [f"CLT-{i:03d}" for i in range(1, n_customers + 1)]
    customer_names = [f"Cliente {i}" for i in range(1, n_customers + 1)]
    stores = [f"STR-{i:02d}" for i in range(1, n_stores + 1)]
    store_desc = [f"Almacén {i} - Zona {np.random.choice(['Norte', 'Sur', 'Centro'])}" for i in range(1, n_stores + 1)]

    records = []

    # --- 2. GENERACIÓN FILA A FILA (Diaria) ---
    # Para cumplir 1.3.1 (combinación única), iteramos por fechas y seleccionamos un subset de clientes
    
    for single_date in date_range:
        year = single_date.year
        month = single_date.month
        day = single_date.day
        date_key = int(single_date.strftime('%Y%m%d'))

        # Escenario 2.1: Manipulación de tendencias por mes para forzar positivos/negativos
        # Meses Positivos: 12 (Diciembre), 6 (Junio)
        # Meses Negativos: 1 (Enero), 2 (Febrero)
        # Meses Mixtos: Resto
        
        bias_profit = 0
        if month in [12, 6]: 
            bias_profit = 8000  # Tendencia muy positiva
            volatility = 1000
        elif month in [1, 2]:
            bias_profit = -5000 # Tendencia negativa
            volatility = 2000
        else:
            bias_profit = 1000  # Mixto / levemente positivo
            volatility = 6000   # Alta volatilidad para tener pos y neg

        # Seleccionamos aleatoriamente 40% de clientes activos por día para no hacer la base pesada innecesariamente
        daily_active_customers = np.random.choice(range(n_customers), size=int(n_customers * 0.4), replace=False)

        for idx in daily_active_customers:
            cust_key = customers[idx]
            cust_name = customer_names[idx]
            
            store_idx = np.random.randint(0, n_stores)
            store_key = stores[store_idx]
            store_d = store_desc[store_idx]

            # Generación de métricas base
            sales_qty = np.random.randint(1, 50)
            unit_cost = np.random.uniform(10, 100)
            
            # El precio unitario debe permitir el profit bias
            # Base price + margen aleatorio + bias distribuido en la cantidad
            target_margin_per_unit = (np.random.normal(bias_profit, volatility) / sales_qty) 
            # Aseguramos que el UnitPrice tenga sentido matematico (Cost + Margin)
            unit_price = unit_cost + target_margin_per_unit
            
            # Ajuste: UnitPrice no puede ser negativo en la vida real (aunque el profit sí)
            # Para simplificar el modelo matemático del profit negativo, permitiremos que el Costo supere al Precio
            if unit_price < 0: unit_price = 1 # Precio simbólico bajo si la perdida es extrema

            income = unit_price * sales_qty
            expense = unit_cost * sales_qty
            profit = income - expense

            # Budget Profit: Simulamos que el presupuesto era optimista
            # Si el profit es negativo, el budget probablemente era positivo
            budget_profit = profit * np.random.uniform(0.9, 1.2) if profit > 0 else abs(profit) * 0.5 
            
            # % Cumplimiento distribuido aleatoriamente entre 0 y 100
            if budget_profit == 0:
                perc_cumplimiento = np.random.uniform(0, 100)
            elif profit >= 0:
                # Cuando hay ganancia, cumplimiento entre 50 y 100
                perc_cumplimiento = np.random.uniform(50, 100)
            else:
                # Cuando hay pérdida, cumplimiento entre 0 y 50
                perc_cumplimiento = np.random.uniform(0, 50)

            records.append([
                date_key, single_date, year, month, day, 
                cust_key, cust_name, store_key, store_d,
                unit_cost, unit_price, sales_qty, income, expense, profit, budget_profit, perc_cumplimiento
            ])

    # Crear DataFrame
    columns = [
        'DateKey', 'Date', 'Year', 'Month', 'Day',
        'CustomerKey', 'Name', 'StoreKey', 'Store Description',
        'UnitCost', 'UnitPrice', 'SalesQuantity', 'Income', 'Expense', 'Profit', 'Budget Profit', '% Cumplimiento'
    ]
    df = pd.DataFrame(records, columns=columns)

    # --- 3. CÁLCULOS ACUMULADOS (YTD) ---
    # Ordenamos por Cliente y Fecha
    df = df.sort_values(by=['CustomerKey', 'Date'])
    
    # Agrupamos por Año y Cliente para calcular acumulados reiniciando cada año
    df['Profit Acumulado'] = df.groupby(['Year', 'CustomerKey'])['Profit'].cumsum()
    df['Budget Profit Acumulado'] = df.groupby(['Year', 'CustomerKey'])['Budget Profit'].cumsum()

    print("Datos diarios generados. Procediendo al Clustering...")
    return df

def generar_datos_clustering(df_diario):
    """
    Genera la tabla resumida con segmentos (Burbujas).
    El clustering se hace a nivel de CLIENTE (único segmento por cliente)
    basado en su comportamiento agregado.
    """
    
    # Agrupar datos por Cliente para obtener métricas globales
    df_customer_total = df_diario.groupby(['CustomerKey']).agg({
        'Profit': 'sum',
        'Budget Profit': 'sum',
        'Income': 'sum',
        'Name': 'first'
    }).reset_index()

    # Calcular Cumplimiento Global del Cliente
    df_customer_total['% Cumplimiento'] = np.maximum(
        np.where(
            df_customer_total['Budget Profit'] == 0, 0, 
            (df_customer_total['Profit'] / df_customer_total['Budget Profit']) * 100
        ), 0
    )

    # --- CLUSTERING GLOBAL (Un segmento por cliente) ---
    X = df_customer_total[['Profit', '% Cumplimiento']]
    
    kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
    df_customer_total['Cluster_Label'] = kmeans.fit_predict(X)
    
    # Renombrar Clusters basado en Profit (0 = Peor, 3 = Mejor)
    cluster_centers = df_customer_total.groupby('Cluster_Label')['Profit'].mean().sort_values()
    cluster_map = {
        old_label: f"Segmento {new_rank+1}" 
        for new_rank, old_label in enumerate(cluster_centers.index)
    }
    df_customer_total['Segmento'] = df_customer_total['Cluster_Label'].map(cluster_map)
    
    # Crear mapeo de CustomerKey -> Segmento
    customer_segment_map = df_customer_total[['CustomerKey', 'Segmento']].copy()
    
    # Agrupar datos mensuales para el dashboard
    df_monthly = df_diario.groupby(['Year', 'Month', 'CustomerKey']).agg({
        'Profit': 'sum',
        'Budget Profit': 'sum',
        'Income': 'sum',
        'Name': 'first',
        '% Cumplimiento': 'mean'  # Usar el promedio del cumplimiento ya calculado aleatoriamente
    }).reset_index()

    # No recalcular el cumplimiento, ya lo tenemos desde df_diario
    
    # Asignar el segmento único a cada cliente
    df_segmented = df_monthly.merge(customer_segment_map, on='CustomerKey', how='left')
    
    print("Clustering completado. Cada cliente tiene un único segmento asignado.")
    return df_segmented

# Ejecución de prueba si se corre este archivo solo
if __name__ == "__main__":
    df = generar_base_datos()
    df_seg = generar_datos_clustering(df)
    print(df_seg.head())