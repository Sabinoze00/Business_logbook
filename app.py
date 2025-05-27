import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import calendar
import locale
import sys
import os

# Aggiungiamo la directory src al path di Python
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

# Importiamo i moduli personalizzati
from data_loader import load_sheets_data, convert_eu_to_number
from data_processor import process_logbook, merge_data, filter_data
from visualizations import create_hours_chart, create_clients_chart, create_metrics_cards
from utils import months_it_to_num, get_month_range, format_currency

# Configurazione pagina
st.set_page_config(
    page_title="Dashboard Aziendale",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Disabilitiamo i messaggi di debug e avvisi di default
try:
    st.set_option('deprecation.showPyplotGlobalUse', False)
except Exception:
    pass

# Imposta locale italiano per i nomi dei mesi
try:
    locale.setlocale(locale.LC_TIME, 'it_IT.UTF-8')
except Exception:
    try:
        locale.setlocale(locale.LC_TIME, 'it_IT')
    except Exception:
        try:
            locale.setlocale(locale.LC_TIME, 'it_IT.utf8')
        except Exception:
            pass

def find_client_row(clienti_df, client_name):
    """
    Trova la riga corrispondente al cliente nel DataFrame clienti_df.
    """
    if clienti_df is None or clienti_df.empty:
        return None
    
    if 'Cliente' in clienti_df.columns:
        result = clienti_df[clienti_df['Cliente'] == client_name]
        if not result.empty:
            return result
        
        # Cerca corrispondenze parziali se la ricerca esatta fallisce
        result = clienti_df[clienti_df['Cliente'].str.contains(client_name, case=False, na=False)]
        if not result.empty:
            return result
    
    return None

def extract_month_from_date(date):
    """
    Estrae il mese da una data e lo restituisce con l'iniziale maiuscola
    in formato italiano (es. 'Gennaio').
    """
    try:
        if pd.isna(date):
            return None
        
        month_num = date.month
        
        month_map = {
            1: 'Gennaio', 2: 'Febbraio', 3: 'Marzo', 4: 'Aprile',
            5: 'Maggio', 6: 'Giugno', 7: 'Luglio', 8: 'Agosto',
            9: 'Settembre', 10: 'Ottobre', 11: 'Novembre', 12: 'Dicembre'
        }
        
        return month_map.get(month_num)
    except Exception:
        return None

def main():
    st.title("Dashboard Aziendale")
    
    # Aggiungi il pulsante di reboot nell'header
    col1, col2, col3 = st.columns([6, 1, 1])
    with col3:
        if st.button("🔄 Ricarica Dashboard", help="Clicca per ricaricare tutti i dati"):
            st.cache_data.clear()
            st.rerun()
    
    st.markdown("---")
    
    try:
        with st.spinner("Caricamento dati in corso..."):
            if "sheet_url" not in st.secrets:
                st.error("URL del foglio Google non trovato nel file secrets.toml. Controlla la configurazione.")
                st.info("Verifica che il file .streamlit/secrets.toml esista e contenga l'URL del foglio Google.")
                st.stop()
                
            sheet_url = st.secrets["sheet_url"]
            logbook_df, clienti_df, compensi_df, mapping_df = load_sheets_data(sheet_url)
            
            if logbook_df is None or clienti_df is None or compensi_df is None:
                st.error("Errore nel caricamento dei dati. Verifica che i nomi dei fogli Google Sheets siano corretti.")
                st.info("""
                Controlla:
                1. La connessione Internet
                2. Che le credenziali Google siano valide
                3. Che il foglio Google Sheets sia accessibile e condiviso con l'account di servizio
                4. Che i nomi dei fogli siano: "Logbook", "Clienti", "Compensi collaboratori"
                """)
                st.stop()
    except Exception as e:
        st.error(f"Errore durante l'avvio dell'applicazione")
        st.info("""
        Si è verificato un problema di connessione con Google Sheets. Verifica:
        1. La tua connessione Internet
        2. Che le credenziali nel file secrets.toml siano corrette
        3. Che il foglio Google Sheets sia accessibile e condiviso con l'account di servizio
        4. Che non ci siano problemi temporanei con i servizi Google
        
        Riprova tra qualche minuto o contatta l'amministratore se il problema persiste.
        """)
        st.stop()
    
    client_map = {}
    if mapping_df is not None and not mapping_df.empty:
        if 'Cliente' in mapping_df.columns and 'Cliente Map' in mapping_df.columns:
            client_map = dict(zip(mapping_df['Cliente Map'], mapping_df['Cliente']))
    
    logbook_processed = process_logbook(logbook_df)
    
    if 'Data' in logbook_processed.columns:
        logbook_processed['MeseFormattato'] = logbook_processed['Data'].apply(extract_month_from_date)
    
    st.sidebar.title("Filtri")
    
    # Aggiungi pulsante di reboot anche nella sidebar
    if st.sidebar.button("🔄 Ricarica Dati", help="Ricarica tutti i dati da Google Sheets"):
        st.cache_data.clear()
        st.rerun()
    
    st.sidebar.subheader("Periodo")
    
    if logbook_processed.empty:
        st.error("Nessun dato valido nel foglio Logbook.")
        st.stop()
        
    if 'Data' not in logbook_processed.columns or logbook_processed['Data'].isna().all():
        st.error("Colonna 'Data' non trovata o non valida nel foglio Logbook.")
        st.stop()
    
    min_date = logbook_processed['Data'].min()
    max_date = logbook_processed['Data'].max()
    
    default_start = max_date - timedelta(days=30) if not pd.isna(max_date) else datetime.now() - timedelta(days=30)
    default_end = max_date if not pd.isna(max_date) else datetime.now()
    
    start_date = st.sidebar.date_input("Data Inizio", default_start, min_value=min_date, max_value=max_date)
    end_date = st.sidebar.date_input("Data Fine", default_end, min_value=min_date, max_value=max_date)
    
    if start_date > end_date:
        st.sidebar.error("La data di fine deve essere successiva alla data di inizio")
        st.stop()
    
    date_filtered_df = filter_data(
        logbook_processed, start_date, end_date,
        None, None, None, None, None
    )
    
    active_clients = sorted(date_filtered_df['Cliente'].unique()) if not date_filtered_df.empty else []
    
    clients_options = sorted(logbook_processed['Cliente'].unique())
    selected_clients = st.sidebar.multiselect("Clienti", clients_options, default=[])
    
    if 'Reparto' in logbook_processed.columns:
        departments = sorted(logbook_processed['Reparto'].unique())
    else:
        departments = sorted(logbook_processed['Reparto1'].unique())
    selected_departments = st.sidebar.multiselect("Reparti", departments, default=[])
    
    macro_activities = sorted(logbook_processed['Macro attività'].unique())
    selected_macro = st.sidebar.multiselect("Macro Attività", macro_activities, default=[])
    
    pre_filtered_df = filter_data(
        logbook_processed, start_date, end_date, None,
        selected_departments if selected_departments else None,
        selected_macro if selected_macro else None,
        None,
        selected_clients if selected_clients else None
    )
    
    active_collaborators = sorted(pre_filtered_df['Nome'].unique()) if not pre_filtered_df.empty else []
    
    collaborators_options = sorted(logbook_processed['Nome'].unique())
    selected_collaborators = st.sidebar.multiselect(
        "Collaboratori", collaborators_options, default=[]
    )
    
    final_collaborators_filter = selected_collaborators if selected_collaborators else None
    final_clients_filter = selected_clients if selected_clients else None
    
    filtered_df = filter_data(
        logbook_processed, start_date, end_date,
        final_collaborators_filter,
        selected_departments if selected_departments else None,
        selected_macro if selected_macro else None,
        None, # No filtro micro attività
        final_clients_filter
    )
    
    collaborators_for_costs = selected_collaborators if selected_collaborators else active_collaborators
    clients_for_revenue = selected_clients if selected_clients else active_clients
    
    with st.sidebar.container():
        record_info = st.empty()
        record_info.info(f"Record visualizzati: {len(filtered_df)}")
    
    selected_months_for_calc = []
    if not filtered_df.empty and 'MeseFormattato' in filtered_df.columns:
        selected_months_for_calc = filtered_df['MeseFormattato'].dropna().unique().tolist()

    # --- Inizio Sezione KPI (Full-Width) ---
    st.subheader("Metriche Chiave del Periodo Selezionato")

    # Calcolo ore lavorate nel periodo filtrato
    total_hours = filtered_df['Minuti Impiegati'].sum() / 60
    
    # Calcolo costo risorse
    total_period_cost_for_selected_collaborators = 0
    total_company_hours_for_selected_collaborators = 0
    average_hourly_cost_for_selected_collaborators = 0
    
    if collaborators_for_costs and selected_months_for_calc and not compensi_df.empty:
        # Filtra compensi_df per i collaboratori rilevanti
        relevant_compensi_df = compensi_df[compensi_df.index.isin(collaborators_for_costs)]
        
        # Calcola il costo totale dei collaboratori selezionati per i mesi selezionati
        month_costs_sum = 0
        for month_name in selected_months_for_calc:
            if month_name and month_name in relevant_compensi_df.columns:
                try:
                    month_costs_sum += relevant_compensi_df[month_name].sum()
                except Exception:
                    pass # Ignora errori se una colonna mese non è numerica o ha problemi
        total_period_cost_for_selected_collaborators = month_costs_sum
        
        # Calcola le ore totali aziendali per i collaboratori selezionati nel periodo di date
        company_hours_df = filter_data(
            logbook_processed, start_date, end_date,
            collaborators_for_costs, # Solo i collaboratori selezionati (o attivi)
            None, None, None, None # Nessun altro filtro per le ore totali
        )
        total_company_hours_for_selected_collaborators = company_hours_df['Minuti Impiegati'].sum() / 60
        
        if total_company_hours_for_selected_collaborators > 0:
            average_hourly_cost_for_selected_collaborators = total_period_cost_for_selected_collaborators / total_company_hours_for_selected_collaborators
        else:
            average_hourly_cost_for_selected_collaborators = 0
            
    # Costo totale delle ore filtrate (basato sulla media dei collaboratori considerati)
    filtered_hours_cost = total_hours * average_hourly_cost_for_selected_collaborators
    
    # Calcolo fatturato
    total_revenue = 0
    if selected_months_for_calc and clients_for_revenue and not clienti_df.empty:
        mapped_clients_for_revenue = [client_map.get(cl, cl) for cl in clients_for_revenue]
        
        for client_name_mapped in mapped_clients_for_revenue:
            client_row_data = find_client_row(clienti_df, client_name_mapped)
            
            if client_row_data is not None and not client_row_data.empty:
                for month_name in selected_months_for_calc:
                    if month_name and month_name in client_row_data.columns:
                        try:
                            revenue_values = client_row_data[month_name].apply(convert_eu_to_number)
                            total_revenue += revenue_values.sum()
                        except Exception:
                            pass # Ignora errori
                            
    # Calcolo margine
    margin = total_revenue - filtered_hours_cost
    margin_percentage = (margin / total_revenue * 100) if total_revenue != 0 else 0 # Evita divisione per zero

    # Visualizzazione metriche KPI su due righe per maggiore chiarezza
    kpi_row1_col1, kpi_row1_col2, kpi_row1_col3 = st.columns(3)
    with kpi_row1_col1:
        st.metric("Ore Lavorate (Filtrate)", f"{total_hours:.1f} h")
    with kpi_row1_col2:
        st.metric("Costo Orario Medio", format_currency(average_hourly_cost_for_selected_collaborators))
    with kpi_row1_col3:
        st.metric("Costo Ore Filtrate", format_currency(filtered_hours_cost))

    kpi_row2_col1, kpi_row2_col2, kpi_row2_col3 = st.columns(3) # Uso 3 colonne per allineamento, ma la terza potrebbe essere vuota o per un altro KPI
    with kpi_row2_col1:
        st.metric("Fatturato Stimato", format_currency(total_revenue))
    with kpi_row2_col2:
        st.metric("Margine Stimato", f"{format_currency(margin)} ({margin_percentage:.1f}%)")
    # kpi_row2_col3 può essere usata per un'altra metrica se necessario

    st.markdown("---")
    # --- Fine Sezione KPI ---

    # --- Inizio Grafico Ore Lavorate per Collaboratore (Full-Width) ---
    if not filtered_df.empty:
        st.subheader("Ore Lavorate per Collaboratore (nel periodo e filtri applicati)")
        hours_chart = create_hours_chart(filtered_df)
        st.plotly_chart(hours_chart, use_container_width=True)
    else:
        st.info("Nessun dato disponibile per il grafico 'Ore Lavorate per Collaboratore' con i filtri selezionati.")
    st.markdown("---")
    # --- Fine Grafico Ore Lavorate ---

    # --- Inizio Grafico Distribuzione Clienti (Full-Width, Spostato) ---
    if not filtered_df.empty:
        st.subheader("Distribuzione Ore per Cliente (nel periodo e filtri applicati)")
        clients_chart = create_clients_chart(filtered_df)
        st.plotly_chart(clients_chart, use_container_width=True)
    else:
        st.info("Nessun dato disponibile per il grafico 'Distribuzione Clienti' con i filtri selezionati.")
    st.markdown("---")
    # --- Fine Grafico Distribuzione Clienti ---
    
    # --- Inizio Riepilogo Collaboratori (Full-Width) ---
    st.subheader("Riepilogo Collaboratori (basato sui filtri applicati)")
    
    if not filtered_df.empty and not compensi_df.empty:
        collab_summary_list = []
        
        # Ore lavorate filtrate per collaboratore
        collab_filtered_hours = filtered_df.groupby('Nome')['Minuti Impiegati'].sum().reset_index()
        collab_filtered_hours['Ore Lavorate Filtrate'] = collab_filtered_hours['Minuti Impiegati'] / 60
        
        # Clienti unici per collaboratore dai dati filtrati
        collab_filtered_clients = filtered_df.groupby('Nome')['Cliente'].nunique().reset_index()
        collab_filtered_clients.rename(columns={'Cliente': 'Numero Clienti (Filtrati)'}, inplace=True)
        
        # Iteriamo sui collaboratori presenti nei dati filtrati
        for collab_name in sorted(collab_filtered_hours['Nome'].unique()):
            hours_val = collab_filtered_hours[collab_filtered_hours['Nome'] == collab_name]['Ore Lavorate Filtrate'].values[0]
            
            clients_count_val = 0
            if collab_name in collab_filtered_clients['Nome'].values:
                 clients_count_val = collab_filtered_clients[collab_filtered_clients['Nome'] == collab_name]['Numero Clienti (Filtrati)'].values[0]
            
            # Compenso e costo orario basati sui mesi selezionati e ore totali del collaboratore nel periodo
            collab_total_pay_in_selected_months = 0
            collab_total_hours_in_period = 0 # Ore totali del collaboratore nel periodo, non solo quelle filtrate
            collab_hourly_rate_in_period = 0

            if collab_name in compensi_df.index and selected_months_for_calc:
                for month_name in selected_months_for_calc:
                    if month_name in compensi_df.columns:
                         pay_value = compensi_df.loc[collab_name, month_name]
                         collab_total_pay_in_selected_months += pay_value if not pd.isna(pay_value) else 0
            
            # Ore totali del singolo collaboratore nel periodo selezionato (start_date, end_date)
            single_collab_total_hours_df = filter_data(
                logbook_processed, start_date, end_date,
                [collab_name], # Filtro per il singolo collaboratore corrente
                None, None, None, None # Nessun altro filtro
            )
            collab_total_hours_in_period = single_collab_total_hours_df['Minuti Impiegati'].sum() / 60

            if collab_total_hours_in_period > 0:
                collab_hourly_rate_in_period = collab_total_pay_in_selected_months / collab_total_hours_in_period
            
            collab_summary_list.append({
                'Collaboratore': collab_name,
                'Compenso Tot. nei Mesi Sel.': collab_total_pay_in_selected_months,
                'Ore Tot. nel Periodo': collab_total_hours_in_period, # Ore totali del collaboratore nel periodo
                'Costo Orario Effettivo': collab_hourly_rate_in_period, # Basato su ore totali
                'Ore Lavorate (Filtrate)': hours_val, # Ore filtrate per i task/clienti/reparti selezionati
                'Clienti Seguiti (Filtrati)': clients_count_val
            })
        
        if collab_summary_list:
            summary_df = pd.DataFrame(collab_summary_list)
            
            summary_df['Compenso Tot. nei Mesi Sel.'] = summary_df['Compenso Tot. nei Mesi Sel.'].apply(lambda x: format_currency(x))
            summary_df['Costo Orario Effettivo'] = summary_df['Costo Orario Effettivo'].apply(lambda x: format_currency(x))
            summary_df['Ore Tot. nel Periodo'] = summary_df['Ore Tot. nel Periodo'].apply(lambda x: f"{x:.1f} h")
            summary_df['Ore Lavorate (Filtrate)'] = summary_df['Ore Lavorate (Filtrate)'].apply(lambda x: f"{x:.1f} h")
            
            summary_df = summary_df.sort_values('Collaboratore')
            st.dataframe(summary_df, use_container_width=True)
        else:
            st.info("Nessun dato disponibile per il riepilogo collaboratori con i filtri attuali.")
    else:
        st.info("Nessun dato disponibile per il riepilogo collaboratori (dati filtrati o compensi mancanti).")
    # --- Fine Riepilogo Collaboratori ---

if __name__ == "__main__":
    main()
