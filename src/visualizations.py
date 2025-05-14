import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from data_processor import aggregate_hours_by_collaborator, aggregate_hours_by_client

def create_hours_chart(df):
    """
    Crea un grafico a barre orizzontale per visualizzare le ore lavorate per collaboratore.
    
    Args:
        df: DataFrame filtrato
        
    Returns:
        Figura Plotly
    """
    if df.empty:
        # Ritorna un grafico vuoto se non ci sono dati
        fig = go.Figure()
        fig.update_layout(
            title="Nessun dato disponibile",
            xaxis_title="Ore",
            yaxis_title="Collaboratore"
        )
        return fig
    
    # Calcola le ore per collaboratore
    hours_by_collaborator = aggregate_hours_by_collaborator(df)
    
    # Ordina per ore in ordine decrescente
    hours_by_collaborator = hours_by_collaborator.sort_values(by='Ore', ascending=True)
    
    # Crea grafico a barre orizzontale
    fig = px.bar(
        hours_by_collaborator,
        x='Ore',
        y='Nome',
        orientation='h',
        text='Ore',
        color='Ore',
        color_continuous_scale='Viridis',
    )
    
    # Personalizza il layout
    fig.update_layout(
        title="Ore Lavorate per Collaboratore",
        xaxis_title="Ore",
        yaxis_title="",
        coloraxis_showscale=False,
        height=max(250, len(hours_by_collaborator) * 30),  # Altezza adattiva
    )
    
    # Formatta i valori di testo delle barre
    fig.update_traces(
        texttemplate='%{text:.1f} h',
        textposition='outside',
    )
    
    return fig

def create_clients_chart(df):
    """
    Crea un grafico a torta per visualizzare la distribuzione dei clienti.
    
    Args:
        df: DataFrame filtrato
        
    Returns:
        Figura Plotly
    """
    if df.empty:
        # Ritorna un grafico vuoto se non ci sono dati
        fig = go.Figure()
        fig.update_layout(
            title="Nessun dato disponibile"
        )
        return fig
    
    # Calcola le ore per cliente
    hours_by_client = aggregate_hours_by_client(df)
    
    # Ordina per ore in ordine decrescente
    hours_by_client = hours_by_client.sort_values(by='Ore', ascending=False)
    
    # Se ci sono più di 10 clienti, raggruppa i meno significativi in "Altri"
    if len(hours_by_client) > 10:
        top_clients = hours_by_client.head(9)
        others = pd.DataFrame({
            'Cliente': ['Altri'],
            'Ore': [hours_by_client.iloc[9:]['Ore'].sum()]
        })
        hours_by_client = pd.concat([top_clients, others])
    
    # Crea grafico a torta
    fig = px.pie(
        hours_by_client,
        values='Ore',
        names='Cliente',
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Prism
    )
    
    # Personalizza il layout
    fig.update_layout(
        title="Distribuzione Ore per Cliente",
        legend=dict(orientation="h", yanchor="bottom", y=-0.3),
    )
    
    # Formatta i valori percentuali
    fig.update_traces(
        textinfo='percent+label',
        textposition='inside',
        insidetextorientation='radial'
    )
    
    return fig

def create_metrics_cards(total_hours, cost_per_hour, total_revenue, margin, margin_percentage):
    """
    Crea le cards delle metriche principali.
    
    Args:
        total_hours: Totale ore lavorate
        cost_per_hour: Costo orario
        total_revenue: Fatturato totale
        margin: Margine
        margin_percentage: Percentuale di margine
        
    Returns:
        Tuple di colonne Streamlit con le metriche
    """
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Ore Lavorate", f"{total_hours:.1f} h")
    
    with col2:
        st.metric("Costo Orario", f"{cost_per_hour:.2f} €")
    
    with col3:
        st.metric("Fatturato", f"{total_revenue:.2f} €")
    
    with col4:
        st.metric("Margine", f"{margin:.2f} € ({margin_percentage:.1f}%)")
    
    return col1, col2, col3, col4

def create_activity_timeline(df):
    """
    Crea un grafico timeline delle attività.
    
    Args:
        df: DataFrame filtrato
        
    Returns:
        Figura Plotly
    """
    if df.empty:
        # Ritorna un grafico vuoto se non ci sono dati
        fig = go.Figure()
        fig.update_layout(
            title="Nessun dato disponibile"
        )
        return fig
    
    # Aggrega i dati per data e attività
    timeline_df = df.groupby(['Data', 'Macro attività'])['Minuti Impiegati'].sum().reset_index()
    timeline_df['Ore'] = timeline_df['Minuti Impiegati'] / 60
    
    # Crea un grafico a linee
    fig = px.line(
        timeline_df,
        x='Data',
        y='Ore',
        color='Macro attività',
        markers=True,
        line_shape='linear'
    )
    
    # Personalizza il layout
    fig.update_layout(
        title="Timeline delle Attività",
        xaxis_title="Data",
        yaxis_title="Ore",
        legend_title="Macro Attività",
    )
    
    return fig

def create_department_chart(df):
    """
    Crea un grafico a barre per visualizzare le ore per reparto.
    
    Args:
        df: DataFrame filtrato
        
    Returns:
        Figura Plotly
    """
    if df.empty:
        # Ritorna un grafico vuoto se non ci sono dati
        fig = go.Figure()
        fig.update_layout(
            title="Nessun dato disponibile"
        )
        return fig
    
    # Calcola le ore per reparto
    hours_by_dept = df.groupby('Reparto1')['Minuti Impiegati'].sum().reset_index()
    hours_by_dept['Ore'] = hours_by_dept['Minuti Impiegati'] / 60
    
    # Ordina per ore in ordine decrescente
    hours_by_dept = hours_by_dept.sort_values(by='Ore', ascending=False)
    
    # Crea grafico a barre
    fig = px.bar(
        hours_by_dept,
        x='Reparto1',
        y='Ore',
        text='Ore',
        color='Reparto1',
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    
    # Personalizza il layout
    fig.update_layout(
        title="Ore per Reparto",
        xaxis_title="Reparto",
        yaxis_title="Ore",
        legend_title="Reparto",
        showlegend=False
    )
    
    # Formatta i valori di testo delle barre
    fig.update_traces(
        texttemplate='%{text:.1f} h',
        textposition='outside',
    )
    
    return fig

def create_efficiency_chart(filtered_df, clienti_df, compensi_df, selected_months, selected_collaborators):
    """
    Crea un grafico di efficienza che confronta fatturato, costi e margine per mese.
    
    Args:
        filtered_df: DataFrame filtrato con i dati del logbook
        clienti_df: DataFrame con i dati del fatturato mensile
        compensi_df: DataFrame con i dati dei compensi collaboratori
        selected_months: Lista dei mesi selezionati
        selected_collaborators: Lista dei collaboratori selezionati
        
    Returns:
        Figura Plotly
    """
    if filtered_df.empty or not selected_months:
        # Ritorna un grafico vuoto se non ci sono dati
        fig = go.Figure()
        fig.update_layout(
            title="Nessun dato disponibile"
        )
        return fig
    
    months_data = []
    
    # Per ogni mese selezionato calcola fatturato, costi e margine
    for month in selected_months:
        # Fatturato del mese (somma di tutti i clienti)
        month_revenue = clienti_df[month].sum() if month in clienti_df.columns else 0
        
        # Costi del mese (somma dei compensi dei collaboratori selezionati)
        month_costs = 0
        if selected_collaborators:
            costs_df = compensi_df[compensi_df.index.isin(selected_collaborators)]
            month_costs = costs_df[month].sum() if month in costs_df.columns else 0
        
        # Margine
        month_margin = month_revenue - month_costs
        
        # Aggiungi i dati alla lista
        months_data.append({
            'Mese': month,
            'Metrica': 'Fatturato',
            'Valore': month_revenue
        })
        months_data.append({
            'Mese': month,
            'Metrica': 'Costi',
            'Valore': month_costs
        })
        months_data.append({
            'Mese': month,
            'Metrica': 'Margine',
            'Valore': month_margin
        })
    
    # Crea DataFrame con i dati aggregati
    efficiency_df = pd.DataFrame(months_data)
    
    # Crea grafico a barre raggruppate
    fig = px.bar(
        efficiency_df,
        x='Mese',
        y='Valore',
        color='Metrica',
        barmode='group',
        text='Valore',
        color_discrete_map={
            'Fatturato': '#36A2EB',
            'Costi': '#FF6384',
            'Margine': '#4BC0C0'
        }
    )
    
    # Personalizza il layout
    fig.update_layout(
        title="Confronto Fatturato, Costi e Margine per Mese",
        xaxis_title="Mese",
        yaxis_title="Valore (€)",
        legend_title="Metrica",
    )
    
    # Formatta i valori di testo delle barre
    fig.update_traces(
        texttemplate='%{text:.0f} €',
        textposition='outside',
    )
    
    return fig