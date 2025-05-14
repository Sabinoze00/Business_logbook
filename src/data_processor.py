import pandas as pd
import numpy as np
from datetime import datetime
import streamlit as st

def process_logbook(df):
    """
    Elabora il dataframe del logbook per garantire formati corretti
    e aggiungere colonne utili.
    
    Args:
        df: DataFrame del logbook
        
    Returns:
        DataFrame elaborato
    """
    # Crea una copia per evitare modifiche all'originale
    processed_df = df.copy() if df is not None else pd.DataFrame()
    
    if processed_df.empty:
        # Restituisce un DataFrame vuoto ma con le colonne necessarie senza mostrare errori
        return pd.DataFrame(columns=['Nome', 'Data', 'Mese', 'Giorno', 'Reparto1', 
                                     'Macro attività', 'Micro attività', 'Cliente', 
                                     'Note', 'Minuti Impiegati'])
    
    # Converte la colonna Data in formato datetime
    try:
        if 'Data' in processed_df.columns:
            processed_df['Data'] = pd.to_datetime(processed_df['Data'], format='%d/%m/%Y', errors='coerce')
            
            # Se ci sono date non valide, prova altri formati - no warning
            if processed_df['Data'].isna().any():
                # Mantieni le date già convertite
                valid_dates = ~processed_df['Data'].isna()
                invalid_dates = processed_df[~valid_dates].copy()
                
                # Prova altri formati di data
                for fmt in ['%Y-%m-%d', '%d-%m-%Y', '%m/%d/%Y', '%Y/%m/%d']:
                    try:
                        date_temp = pd.to_datetime(invalid_dates['Data'], format=fmt, errors='coerce')
                        # Aggiorna solo le date che sono state convertite con successo
                        mask = ~date_temp.isna()
                        if mask.any():
                            processed_df.loc[~valid_dates][mask, 'Data'] = date_temp[mask]
                    except Exception:
                        pass
        else:
            processed_df['Data'] = None
    except Exception:
        processed_df['Data'] = None
    
    # Controlla se le colonne richieste esistono
    required_columns = ['Nome', 'Data', 'Mese', 'Giorno', 'Reparto1', 'Macro attività', 
                        'Micro attività', 'Cliente', 'Note', 'Minuti Impiegati']
    
    for col in required_columns:
        if col not in processed_df.columns:
            processed_df[col] = None
    
    # Assicurati che Minuti Impiegati sia numerico
    try:
        processed_df['Minuti Impiegati'] = pd.to_numeric(processed_df['Minuti Impiegati'], errors='coerce')
        processed_df['Minuti Impiegati'] = processed_df['Minuti Impiegati'].fillna(0)
    except Exception:
        processed_df['Minuti Impiegati'] = 0
    
    # Estrai il mese e il giorno dalla data se non presenti o vuoti
    if 'Data' in processed_df.columns and not processed_df['Data'].isna().all():
        # Aggiungi colonna mese se vuota o mancante
        if 'Mese' not in processed_df.columns or processed_df['Mese'].isnull().any():
            processed_df['Mese'] = processed_df['Data'].dt.strftime('%B').str.lower()
        
        # Aggiungi colonna giorno se vuota o mancante
        if 'Giorno' not in processed_df.columns or processed_df['Giorno'].isnull().any():
            processed_df['Giorno'] = processed_df['Data'].dt.day_name()
    
    # Rimuovi righe con data null o NaT
    processed_df = processed_df[processed_df['Data'].notna()]
    
    return processed_df

def merge_data(logbook_df, clienti_df, compensi_df, mapping_df):
    """
    Combina i dati dai vari fogli per le analisi.
    
    Args:
        logbook_df: DataFrame del logbook
        clienti_df: DataFrame dei clienti mensili
        compensi_df: DataFrame dei compensi collaboratori
        mapping_df: DataFrame di mapping clienti
        
    Returns:
        DataFrame combinato
    """
    # Questo è un punto di partenza per future integrazioni più complesse
    # Per ora ritorniamo il logbook elaborato
    merged_df = logbook_df.copy() if logbook_df is not None else pd.DataFrame()
    
    # TODO: Implementare integrazione dati più avanzata se necessario
    
    return merged_df

def filter_data(df, start_date, end_date, collaborators=None, departments=None, 
               macro_activities=None, micro_activities=None, clients=None):
    """
    Filtra il dataframe in base ai criteri selezionati.
    
    Args:
        df: DataFrame da filtrare
        start_date: Data di inizio periodo
        end_date: Data di fine periodo
        collaborators: Lista di collaboratori da includere
        departments: Lista di reparti da includere
        macro_activities: Lista di macro attività da includere
        micro_activities: Lista di micro attività da includere (non usato)
        clients: Lista di clienti da includere
        
    Returns:
        DataFrame filtrato
    """
    # Verifica che il DataFrame non sia vuoto
    if df is None or df.empty:
        return pd.DataFrame()
    
    # Crea una copia per evitare modifiche all'originale
    filtered_df = df.copy()
    
    # Filtro per data
    if start_date and end_date and 'Data' in filtered_df.columns:
        # Converti le date in timestamp per il confronto
        start_ts = pd.Timestamp(start_date)
        end_ts = pd.Timestamp(end_date)
        
        # Applica il filtro sulle date, gestendo valori nulli
        filtered_df = filtered_df[
            (filtered_df['Data'].notna()) & 
            (filtered_df['Data'] >= start_ts) & 
            (filtered_df['Data'] <= end_ts)
        ]
    
    # Filtro per collaboratori
    if collaborators and len(collaborators) > 0 and 'Nome' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['Nome'].isin(collaborators)]
    
    # Filtro per reparti - controlla prima se esiste 'Reparto', altrimenti usa 'Reparto1'
    if departments and len(departments) > 0:
        if 'Reparto' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['Reparto'].isin(departments)]
        elif 'Reparto1' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['Reparto1'].isin(departments)]
    
    # Filtro per macro attività
    if macro_activities and len(macro_activities) > 0 and 'Macro attività' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['Macro attività'].isin(macro_activities)]
    
    # Filtro per clienti
    if clients and len(clients) > 0 and 'Cliente' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['Cliente'].isin(clients)]
    
    return filtered_df

def aggregate_hours_by_collaborator(df):
    """
    Aggrega le ore per collaboratore.
    
    Args:
        df: DataFrame filtrato
        
    Returns:
        DataFrame aggregato
    """
    if df is None or df.empty or 'Nome' not in df.columns or 'Minuti Impiegati' not in df.columns:
        return pd.DataFrame(columns=['Nome', 'Ore'])
    
    agg_df = df.groupby('Nome')['Minuti Impiegati'].sum().reset_index()
    agg_df['Ore'] = agg_df['Minuti Impiegati'] / 60
    return agg_df[['Nome', 'Ore']]

def aggregate_hours_by_client(df):
    """
    Aggrega le ore per cliente.
    
    Args:
        df: DataFrame filtrato
        
    Returns:
        DataFrame aggregato
    """
    if df is None or df.empty or 'Cliente' not in df.columns or 'Minuti Impiegati' not in df.columns:
        return pd.DataFrame(columns=['Cliente', 'Ore'])
    
    agg_df = df.groupby('Cliente')['Minuti Impiegati'].sum().reset_index()
    agg_df['Ore'] = agg_df['Minuti Impiegati'] / 60
    return agg_df[['Cliente', 'Ore']]