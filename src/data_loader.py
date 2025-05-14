import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import numpy as np
import re

@st.cache_resource(ttl=3600)  # Cache per un'ora con tempo di vita di 1 ora
def get_gsheet_client():
    """
    Crea e restituisce un client autenticato per Google Sheets.
    Utilizza le credenziali del service account dalle secrets di Streamlit.
    """
    scope = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    
    try:
        # Carica credenziali da Streamlit Secrets
        credentials = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=scope
        )
        client = gspread.authorize(credentials)
        return client
    except Exception as e:
        st.error(f"Errore di autenticazione Google Sheets. Verifica le credenziali nel file secrets.toml.")
        return None

def convert_eu_to_number(amount_str):
    """
    Converte un valore monetario dal formato europeo (es. '€ 550,00') a un float.
    
    Args:
        amount_str: Stringa che rappresenta un valore monetario in formato europeo
        
    Returns:
        float: Il valore numerico
    """
    if not isinstance(amount_str, str):
        return 0.0
    
    # Rimuovi il simbolo dell'euro e gli spazi
    clean_str = amount_str.replace('€', '').strip()
    
    # Gestisci formati europei: sostituisci punto come separatore di migliaia e virgola come decimale
    # es. 1.234,56 -> 1234.56
    if ',' in clean_str:
        # Rimuovi punti usati come separatori di migliaia
        clean_str = clean_str.replace('.', '')
        # Sostituisci virgola con punto per il decimale
        clean_str = clean_str.replace(',', '.')
    
    # Converti in float
    try:
        return float(clean_str)
    except ValueError:
        # Se non riesci a convertire, restituisci 0
        return 0.0

@st.cache_data(ttl=1800)  # Cache per 30 minuti
def load_sheets_data(sheet_url):
    """
    Carica i dati dai fogli Google Sheets.
    
    Args:
        sheet_url: URL del foglio Google Sheets
        
    Returns:
        tuple: (logbook_df, clienti_df, compensi_df, mapping_df)
    """
    try:
        client = get_gsheet_client()
        if not client:
            return None, None, None, None
        
        # Aumentiamo il timeout per le connessioni
        import socket
        default_timeout = socket.getdefaulttimeout()
        socket.setdefaulttimeout(30)  # Timeout di 30 secondi
        
        try:
            # Apri il foglio
            sheet = client.open_by_url(sheet_url)
            
            # 1. Carica foglio "Logbook"
            try:
                logbook_worksheet = sheet.worksheet("Logbook")
                logbook_data = logbook_worksheet.get_all_values()
                logbook_headers = logbook_data[0]  # Prima riga come header
                logbook_data = logbook_data[1:]    # Dati senza header
                
                logbook_df = pd.DataFrame(logbook_data, columns=logbook_headers)
            except Exception as e:
                st.error(f"Errore nel caricamento del foglio Logbook. Verifica che esista e sia accessibile.")
                logbook_df = None
            
            # 2. Carica foglio "Clienti"
            try:
                clienti_worksheet = sheet.worksheet("Clienti")
                clienti_data = clienti_worksheet.get_all_values()
                clienti_headers = clienti_data[0]  # Prima riga come header
                clienti_data = clienti_data[1:]    # Dati senza header
                
                clienti_df = pd.DataFrame(clienti_data, columns=clienti_headers)
            except Exception as e:
                st.error(f"Errore nel caricamento del foglio Clienti. Verifica che esista e sia accessibile.")
                clienti_df = None
            
            # 3. Carica foglio "Compensi collaboratori"
            try:
                compensi_worksheet = sheet.worksheet("Compensi collaboratori")
                compensi_data = compensi_worksheet.get_all_values()
                compensi_headers = compensi_data[0]  # Prima riga come header
                compensi_data = compensi_data[1:]    # Dati senza header
                
                compensi_df = pd.DataFrame(compensi_data, columns=compensi_headers)
            except Exception as e:
                st.error(f"Errore nel caricamento del foglio Compensi collaboratori. Verifica che esista e sia accessibile.")
                compensi_df = None
            
            # 4. Carica foglio "Mappa"
            try:
                mapping_worksheet = sheet.worksheet("Mappa")
                mapping_data = mapping_worksheet.get_all_values()
                mapping_headers = mapping_data[0]  # Prima riga come header
                mapping_data = mapping_data[1:]    # Dati senza header
                
                mapping_df = pd.DataFrame(mapping_data, columns=mapping_headers)
            except Exception:
                # Se non trova il foglio Mappa, utilizza un mapping predefinito nel codice
                mapping_data = [
                    ["ACOS MEDICA", "Acos Medica"],
                    ["Bovo Garden Srl", "Flobflower"],
                    ["Business Gates S.r.l.", "Business Gates"],
                    ["CARL ZEISS VISION ITALIA S.P.A.", "Zeiss"],
                    ["CAROVILLA PIERLUIGI (SONIT)", "Sonit"],
                    ["Cisa S.p.a.", "Cisa"],
                    ["CoLibrì System S.p.A.", "Colibrì"],
                    ["CURCAPIL DI CARLUCCI DONATO SNC", "Curcapil"],
                    ["Elettrocasa S.r.l.", "Elettrocasa"],
                    ["FIDELIA - S.R.L.", "Casaviva"],
                    ["FLO.MAR. S.R.L.S.", "Flomar"],
                    ["Fratelli Bonella", "Fratelli Bonella"],
                    ["HOMIT S.R.L.", "Divani Store"],
                    ["NOWAVE", "Nowave"],
                    ["PATRIZIO BRESEGHELLO", "Patrizio Breseghello"],
                    ["POLONORD ADESTE", "Polonord"],
                    ["SAIET", "Saiet"],
                    ["SAN PIETRO LAB", "San Pietro Lab"],
                    ["Sivec Srl", "Passione Fiori"],
                    ["STILMAR DI MARISE RICCARDO (COCCOLE)", "Coccole"],
                    ["TOMAINO SRL", "Tomaino"]
                ]
                mapping_df = pd.DataFrame(mapping_data, columns=["Cliente", "Cliente Map"])
        finally:
            # Ripristina il timeout originale
            socket.setdefaulttimeout(default_timeout)
        
        # Verifica che i dataframe essenziali siano stati caricati correttamente
        if logbook_df is None or clienti_df is None or compensi_df is None:
            st.error("Alcuni fogli essenziali non sono stati caricati correttamente.")
            # Ritorna comunque i dataframe, alcuni potrebbero essere None
            return logbook_df, clienti_df, compensi_df, mapping_df
        
        # Rimuovi righe vuote
        logbook_df = logbook_df.dropna(how='all')
        clienti_df = clienti_df.dropna(how='all')
        compensi_df = compensi_df.dropna(how='all')
        if mapping_df is not None:
            mapping_df = mapping_df.dropna(how='all')
        
        # Prepara il DataFrame Clienti
        # Invece di convertire direttamente i valori, li lasceremo come stringhe
        # e useremo la funzione convert_eu_to_number quando necessario
        
        # Prima di procedere, controlliamo se la colonna 'Actual' esiste
        if 'Actual' in clienti_df.columns:
            # Filtra solo le righe "Actual"
            clienti_df = clienti_df[clienti_df['Actual'] == 'Actual']
            clienti_df = clienti_df.drop('Actual', axis=1)
        
        # Prepara il DataFrame CompensCollaboratori: imposta Collaboratore come indice
        if 'Collaboaratore' in compensi_df.columns:
            compensi_df = compensi_df.rename(columns={'Collaboaratore': 'Collaboratore'})
        
        if 'Collaboratore' in compensi_df.columns:
            compensi_df = compensi_df.set_index('Collaboratore')
            
            # Converti i valori monetari in numeri
            # NOTA: per i compensi, lasciamo la logica originale che funzionava bene
            for col in compensi_df.columns:
                if col not in ['Collaboratore']:
                    try:
                        # Sostituisci stringhe vuote con NaN
                        compensi_df[col] = compensi_df[col].replace('', np.nan)
                        # Rimuovi simboli valuta e spazi
                        compensi_df[col] = compensi_df[col].replace(r'[€.,\s]', '', regex=True)
                        # Converti in float, gestendo i valori non numerici
                        compensi_df[col] = pd.to_numeric(compensi_df[col], errors='coerce')
                        # Sostituisci NaN con 0
                        compensi_df[col] = compensi_df[col].fillna(0)
                    except Exception:
                        # Se non riesce a convertire, imposta tutti i valori a 0
                        compensi_df[col] = 0
        
        return logbook_df, clienti_df, compensi_df, mapping_df
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        # Forniamo un messaggio di errore più specifico
        if "RemoteDisconnected" in str(e) or "ConnectionAbortedError" in str(e):
            st.error("Errore di connessione con Google Sheets. Verifica la tua connessione internet e riprova.")
        elif "not found" in str(e):
            st.error("Foglio o documento Google Sheets non trovato. Verifica l'URL e le autorizzazioni.")
        elif "invalid_grant" in str(e):
            st.error("Errore di autenticazione. Le credenziali del Service Account potrebbero essere scadute o non valide.")
        else:
            st.error(f"Errore nel caricamento dei dati: {str(e)}")
        
        # Salviamo l'errore completo nei log per debugging
        print(f"Dettaglio errore: {error_details}")
        
        return None, None, None, None