import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, State, dash_table
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import processing  # Importamos el módulo que acabamos de crear

# --- CARGA DE DATOS ---
# Esto se ejecuta una vez al iniciar la aplicación
df_diario = processing.generar_base_datos()
df_mensual_segmentado = processing.generar_datos_clustering(df_diario)

# Diccionario de meses para el Dropdown
meses_dict = {
    1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril', 5: 'Mayo', 6: 'Junio',
    7: 'Julio', 8: 'Agosto', 9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
}

# --- ESTILOS CSS ---
FILTERS_STYLE = {
    "backgroundColor": "#ecf0f1",
    "padding": "20px",
    "borderRadius": "10px",
    "marginBottom": "20px",
    "boxShadow": "0 4px 8px 0 rgba(0,0,0,0.1)",
    "display": "flex",
    "gap": "20px",
    "alignItems": "flex-end"
}

FILTER_ITEM_STYLE = {
    "flex": 1,
    "minWidth": "200px"
}

SIDEBAR_STYLE = {
    "width": "195px",
    "minWidth": "195px",
    "maxWidth": "195px",
    "minHeight": "100vh",
    "backgroundColor": "#2c3e50",
    "color": "white",
    "padding": "24px 18px",
    "boxShadow": "2px 0 8px rgba(0,0,0,0.1)",
    "position": "sticky",
    "top": 0,
    "flexShrink": 0
}

SIDEBAR_ITEM_STYLE = {
    "padding": "12px 14px",
    "borderRadius": "8px",
    "color": "white",
    "textDecoration": "none",
    "display": "block",
    "fontWeight": "600",
    "marginBottom": "8px",
    "backgroundColor": "#34495e"
}

CONTENT_WRAPPER_STYLE = {
    "flex": 1,
    "padding": "20px",
    "maxWidth": "1400px"
}

# --- DEFINICIÓN DE LA APP ---
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "GoData Financial Dashboard"
server = app.server  # Exponer el server para deployment

# --- LAYOUT ---
app.layout = html.Div([
    dcc.Store(id='selected-segment-store'),

    html.Div([
        # Sidebar
        html.Div([
            html.H2("GoData", style={"textAlign": "center", "marginBottom": "16px"}),
            html.Hr(style={"borderColor": "#bdc3c7"}),
            dcc.Link("Profitability Overview", href="#profitability-overview", style=SIDEBAR_ITEM_STYLE),
        ], style=SIDEBAR_STYLE),

        # Main content
        html.Div([
            html.Div(id='profitability-overview'),
            html.H1("Análisis de Rentabilidad vs Cumplimiento", style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': '30px'}),
            html.P("Visualización interactiva de segmentos de clientes. (Haz click en una burbuja para ver detalle de clientes)", style={'textAlign': 'center', 'marginBottom': '20px', 'color': '#7f8c8d', 'fontSize': '14px'}),
            html.Hr(),

            # Primera fila: Filtros
            html.Div([
                html.Div([
                    html.Label("Seleccionar Año:", style={'fontWeight': 'bold', 'marginBottom': '5px', 'display': 'block'}),
                    dcc.Dropdown(
                        id='year-filter',
                        options=[{'label': str(y), 'value': y} for y in [2024, 2025, 2026]],
                        value=2026,
                        clearable=False,
                        style={'color': 'black'}
                    ),
                ], style=FILTER_ITEM_STYLE),
                
                html.Div([
                    html.Label("Seleccionar Mes:", style={'fontWeight': 'bold', 'marginBottom': '5px', 'display': 'block'}),
                    dcc.Dropdown(
                        id='month-filter',
                        options=[{'label': 'Todos', 'value': 0}] + [{'label': name, 'value': num} for num, name in meses_dict.items()],
                        value=0,
                        clearable=False,
                        style={'color': 'black'}
                    ),
                ], style=FILTER_ITEM_STYLE),
            ], style=FILTERS_STYLE),

            # Segunda fila: Dos columnas con visualizaciones
            html.Div([
                # Columna izquierda: Gráfico de Burbujas
                html.Div([
                    dcc.Graph(
                        id='bubble-chart', 
                        style={'height': '600px'},
                        hoverData={'points': [{'curveNumber': 0, 'customdata': ['Todos']}]}
                    )
                ], style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '10px', 'boxShadow': '0 4px 8px 0 rgba(0,0,0,0.2)', 'flex': 1}),

                # Columna derecha: Gráfico Scatter de Detalle
                html.Div([
                    html.H3(id='drill-title', style={'color': '#2c3e50', 'marginBottom': '15px'}),
                    dcc.Graph(id='drill-chart', style={'height': '560px'})
                ], id='drill-container', style={
                    'backgroundColor': 'white', 
                    'padding': '20px', 
                    'borderRadius': '10px', 
                    'boxShadow': '0 4px 8px 0 rgba(0,0,0,0.2)',
                    'flex': 1,
                    'display': 'block'
                }),
            ], style={'display': 'flex', 'gap': '20px', 'marginBottom': '20px'}),

            # Tercera fila: Tabla resumen de clientes
            html.Div([
                html.H3("Resumen de Clientes", style={'color': '#2c3e50', 'marginBottom': '15px'}),
                
                # Campo de búsqueda
                html.Div([
                    html.Label("Buscar Cliente:", style={'fontWeight': 'bold', 'marginRight': '10px'}),
                    dcc.Input(
                        id='search-input',
                        type='text',
                        placeholder='Escriba el nombre del cliente...',
                        style={
                            'width': '300px',
                            'padding': '8px',
                            'borderRadius': '5px',
                            'border': '1px solid #ccc'
                        }
                    )
                ], style={'marginBottom': '15px'}),
                
                dash_table.DataTable(
                    id='customer-table',
                    columns=[
                        {'name': 'Nombre del Cliente', 'id': 'Name'},
                        {'name': 'Segmento del Cliente', 'id': 'Segmento'},
                        {'name': 'Sum Profit', 'id': 'Profit', 'type': 'numeric', 'format': {'specifier': ',.2f'}}
                    ],
                    data=[],
                    style_table={'overflowX': 'auto'},
                    style_cell={
                        'textAlign': 'left',
                        'padding': '10px',
                        'fontFamily': 'Arial, sans-serif'
                    },
                    style_header={
                        'backgroundColor': '#2c3e50',
                        'color': 'white',
                        'fontWeight': 'bold'
                    },
                    style_data_conditional=[
                        {
                            'if': {'row_index': 'odd'},
                            'backgroundColor': '#f9f9f9'
                        }
                    ],
                    page_size=10,
                    sort_action='native',
                    filter_action='native'
                )
            ], style={
                'backgroundColor': 'white',
                'padding': '20px',
                'borderRadius': '10px',
                'boxShadow': '0 4px 8px 0 rgba(0,0,0,0.2)',
                'marginBottom': '20px'
            }),

            html.Div(id='debug-text', style={'color': 'gray', 'textAlign': 'center'}),
        ], style=CONTENT_WRAPPER_STYLE),
    ], style={'display': 'flex', 'gap': '24px', 'alignItems': 'flex-start'}),
], style={'margin': '0 auto', 'padding': '20px'})

# --- CALLBACKS (Lógica Interactiva) ---
@app.callback(
    [Output('bubble-chart', 'figure'),
     Output('debug-text', 'children'),
     Output('selected-segment-store', 'data')],
    [Input('year-filter', 'value'),
     Input('month-filter', 'value'),
     Input('bubble-chart', 'hoverData')]
)
def update_graph(selected_year, selected_month, hoverData):
    # 1. Filtrar los datos generados por Año y Mes
    if selected_month == 0:  # "Todos" los meses
        filtered_df = df_mensual_segmentado[df_mensual_segmentado['Year'] == selected_year]
    else:
        filtered_df = df_mensual_segmentado[
            (df_mensual_segmentado['Year'] == selected_year) & 
            (df_mensual_segmentado['Month'] == selected_month)
        ]
    
    if filtered_df.empty:
        return px.scatter(title="No hay datos para esta selección"), "Sin datos", "Todos"

    # 2. Agrupar por SEGMENTO para crear las burbujas
    # Primero agregamos a nivel de cliente dentro del período seleccionado
    client_segment_agg = filtered_df.groupby(['CustomerKey', 'Segmento']).agg({
        'Profit': 'sum',
        '% Cumplimiento': 'mean',
    }).reset_index()
    
    # Luego agregamos por segmento
    bubble_data = client_segment_agg.groupby('Segmento').agg({
        'Profit': 'sum',
        '% Cumplimiento': 'mean',
        'CustomerKey': 'count'
    }).rename(columns={
        'Profit': 'Total Profit (X)',
        '% Cumplimiento': 'Avg Cumplimiento (Y)',
        'CustomerKey': 'Num Clientes (Size)'
    }).reset_index()

    # 3. Generar Gráfico
    month_label = "Todos los meses" if selected_month == 0 else meses_dict[selected_month]
    
    # Crear figura con plotly graph_objects para mayor control
    fig = go.Figure()
    
    # Agregar punto invisible "Todos" que cubra el área de fondo
    fig.add_trace(go.Scatter(
        x=[bubble_data["Total Profit (X)"].mean()],
        y=[bubble_data["Avg Cumplimiento (Y)"].mean()],
        mode='markers',
        marker=dict(size=1, color='rgba(0,0,0,0)', opacity=0),
        hoverinfo='skip',
        customdata=[["Todos"]],
        showlegend=False,
        name='Background'
    ))
    
    # Agregar las burbujas de segmentos
    for idx, row in bubble_data.iterrows():
        fig.add_trace(go.Scatter(
            x=[row["Total Profit (X)"]],
            y=[row["Avg Cumplimiento (Y)"]],
            mode='markers+text',
            marker=dict(
                size=min(row["Num Clientes (Size)"] * 8, 80),
                color=idx,
                colorscale='Viridis',
                showscale=False
            ),
            text=row["Segmento"],
            textposition='top center',
            customdata=[[row["Segmento"]]],
            name=row["Segmento"],
            hovertemplate='<b>%{customdata[0]}</b><br>' +
                         'Total Profit: %{x:,.0f}<br>' +
                         'Avg Cumplimiento: %{y:.1f}%<br>' +
                         'Num Clientes: ' + str(row["Num Clientes (Size)"]) + '<extra></extra>'
        ))
    
    fig.update_layout(
        title=f"Segmentación de Clientes - {month_label} {selected_year}",
        xaxis_title="Profit Total del Segmento (USD)",
        yaxis_title="% Cumplimiento Promedio",
        plot_bgcolor='#ecf0f1',
        xaxis=dict(zeroline=True, zerolinecolor='black', showgrid=True),
        yaxis=dict(zeroline=True, zerolinecolor='black', showgrid=True),
        font=dict(family="Arial, sans-serif", size=14),
        hovermode='closest',
        showlegend=False
    )
    
    fig.add_hline(y=100, line_dash="dash", line_color="green", annotation_text="Meta 100%")
    fig.add_vline(x=0, line_dash="dash", line_color="red")

    month_label = "Todos los meses" if selected_month == 0 else meses_dict[selected_month]
    debug_msg = f"Mostrando datos para {month_label} del {selected_year}. Total registros procesados: {len(filtered_df)}"
    
    # Extraer el segmento del hoverData (tendrá valor inicial "Todos" cuando no hay hover)
    selected_segment = "Todos"
    if hoverData and 'points' in hoverData and len(hoverData['points']) > 0:
        selected_segment = hoverData['points'][0]['customdata'][0]
    
    return fig, debug_msg, selected_segment

# Callback para mostrar el gráfico drill-through
@app.callback(
    [Output('drill-chart', 'figure'),
     Output('drill-title', 'children'),
     Output('drill-container', 'style')],
    [Input('selected-segment-store', 'data'),
     Input('year-filter', 'value'),
     Input('month-filter', 'value')]
)
def update_drill_chart(selected_segment, selected_year, selected_month):
    # Filtrar por año y opcionalmente por mes
    if selected_month == 0:  # "Todos" los meses
        filtered_df = df_mensual_segmentado[df_mensual_segmentado['Year'] == selected_year]
    else:
        filtered_df = df_mensual_segmentado[
            (df_mensual_segmentado['Year'] == selected_year) & 
            (df_mensual_segmentado['Month'] == selected_month)
        ]
    
    # Si el segmento es "Todos" o no hay selección, mostrar todos los clientes
    if not selected_segment or selected_segment == "Todos":
        drill_df = filtered_df
        title_segment = "Todos"
    else:
        # Filtrar por segmento específico
        drill_df = filtered_df[filtered_df['Segmento'] == selected_segment]
        title_segment = selected_segment
    
    if drill_df.empty:
        empty_fig = go.Figure()
        empty_fig.update_layout(title="No hay datos para este segmento")
        style = {
            'backgroundColor': 'white', 
            'padding': '20px', 
            'borderRadius': '10px', 
            'boxShadow': '0 4px 8px 0 rgba(0,0,0,0.2)',
            'flex': 1,
            'display': 'block'
        }
        return empty_fig, f"Detalle de Clientes - {title_segment}", style
    
    # Agrupar por cliente
    customer_data = drill_df.groupby(['CustomerKey', 'Name']).agg({
        'Profit': 'sum',
        '% Cumplimiento': 'mean',
        'Income': 'sum',
        'Budget Profit': 'sum'
    }).reset_index()
    
    # Crear gráfico scatter
    fig = px.scatter(
        customer_data,
        x='Profit',
        y='% Cumplimiento',
        hover_name='Name',
        hover_data={
            'Profit': ':,.0f',
            '% Cumplimiento': ':.1f',
            'Income': ':,.0f',
            'Budget Profit': ':,.0f'
        },
        color='Profit',
        color_continuous_scale='RdYlGn',
        title=f"Clientes en {title_segment} - {'Todos los meses' if selected_month == 0 else meses_dict[selected_month]} {selected_year}",
        labels={
            'Profit': 'Profit (USD)',
            '% Cumplimiento': '% Cumplimiento'
        }
    )
    
    fig.update_traces(marker=dict(size=10, line=dict(width=1, color='DarkSlateGrey')))
    fig.update_layout(
        plot_bgcolor='#ecf0f1',
        xaxis=dict(zeroline=True, zerolinecolor='red', showgrid=True),
        yaxis=dict(zeroline=True, zerolinecolor='black', showgrid=True),
        height=560,
        font=dict(family="Arial, sans-serif", size=12)
    )
    
    # Líneas de referencia
    fig.add_hline(y=100, line_dash="dash", line_color="green", annotation_text="Meta 100%")
    fig.add_vline(x=0, line_dash="dash", line_color="red")
    
    title_text = f"Detalle de Clientes - {title_segment}"
    style = {
        'backgroundColor': 'white', 
        'padding': '20px', 
        'borderRadius': '10px', 
        'boxShadow': '0 4px 8px 0 rgba(0,0,0,0.2)',
        'flex': 1,
        'display': 'block'
    }
    
    return fig, title_text, style

# Callback para actualizar la tabla de clientes
@app.callback(
    Output('customer-table', 'data'),
    [Input('selected-segment-store', 'data'),
     Input('year-filter', 'value'),
     Input('month-filter', 'value'),
     Input('search-input', 'value')]
)
def update_customer_table(selected_segment, selected_year, selected_month, search_value):
    # Filtrar por año y opcionalmente por mes
    if selected_month == 0:  # "Todos" los meses
        filtered_df = df_mensual_segmentado[df_mensual_segmentado['Year'] == selected_year]
    else:
        filtered_df = df_mensual_segmentado[
            (df_mensual_segmentado['Year'] == selected_year) & 
            (df_mensual_segmentado['Month'] == selected_month)
        ]
    
    # Si el segmento es "Todos" o no hay selección, mostrar todos los clientes
    if not selected_segment or selected_segment == "Todos":
        table_df = filtered_df
    else:
        # Filtrar por segmento específico
        table_df = filtered_df[filtered_df['Segmento'] == selected_segment]
    
    # Agrupar por cliente
    customer_summary = table_df.groupby(['CustomerKey', 'Name', 'Segmento']).agg({
        'Profit': 'sum'
    }).reset_index()
    
    # Filtrar por búsqueda de nombre
    if search_value and search_value.strip():
        customer_summary = customer_summary[
            customer_summary['Name'].str.contains(search_value, case=False, na=False)
        ]
    
    # Ordenar por Profit descendente
    customer_summary = customer_summary.sort_values('Profit', ascending=False)
    
    # Seleccionar solo las columnas necesarias
    customer_summary = customer_summary[['Name', 'Segmento', 'Profit']]
    
    return customer_summary.to_dict('records')

if __name__ == '__main__':
    # Ejecutar en modo debug para desarrollo local, producción para deploy
    import os
    debug_mode = os.environ.get('DASH_DEBUG', 'True') == 'True'
    port = int(os.environ.get('PORT', 8050))
    app.run(debug=debug_mode, host='0.0.0.0', port=port)