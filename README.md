# Dashboard Aziendale

Dashboard Streamlit per la visualizzazione e l'analisi dei dati aziendali. L'applicazione si connette a Google Sheets per recuperare i dati in tempo reale e visualizzare metriche come ore lavorate, costo orario, fatturato e margine.

## Struttura del Progetto

```
/dashboard-aziendale/
│
├── .streamlit/
│   └── secrets.toml       # File per le credenziali
│
├── credentials/
│   └── service_account.json   # Credenziali API Google
│
├── src/
│   ├── data_loader.py     # Funzioni per caricare i dati da Google Sheets
│   ├── data_processor.py  # Funzioni per elaborare e trasformare i dati
│   ├── visualizations.py  # Funzioni per creare grafici e visualizzazioni
│   └── utils.py           # Funzioni di utilità generale
│
├── .gitignore             # Per escludere file sensibili dal repository
├── README.md              # Documentazione del progetto
├── requirements.txt       # Dipendenze del progetto
└── app.py                 # File principale dell'applicazione Streamlit
```

## Requisiti

- Python 3.8 o superiore
- Librerie Python elencate in `requirements.txt`
- Account Google con accesso al foglio Google Sheets
- Credenziali Service Account Google per l'API Google Sheets

## Configurazione

1. **Creare un ambiente virtuale Python**:
   ```
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

2. **Installare le dipendenze**:
   ```
   pip install -r requirements.txt
   ```

3. **Configurare le credenziali Google Sheets**:
   
   a. Accedi alla [Google Cloud Console](https://console.cloud.google.com/)
   
   b. Crea un nuovo progetto o seleziona un progetto esistente
   
   c. Abilita l'API Google Sheets e Google Drive
   
   d. Crea un Service Account con le autorizzazioni appropriate
   
   e. Scarica il file JSON delle credenziali
   
   f. Salva il file JSON nella cartella `credentials/` con nome `service_account.json`
   
   g. Condividi il tuo foglio Google Sheets con l'email del Service Account

4. **Configura i secrets di Streamlit**:
   
   a. Crea la cartella `.streamlit` se non esiste
   
   b. Modifica il file `.streamlit/secrets.toml` inserendo l'URL del tuo foglio Google Sheets e le credenziali del Service Account

5. **Concedi le autorizzazioni di lettura al foglio Google Sheets**:
   
   Assicurati di condividere il foglio Google Sheets con l'email del Service Account (visibile nel file JSON delle credenziali).

## Esecuzione

Per avviare l'applicazione, esegui:

```
streamlit run app.py
```

L'applicazione sarà disponibile all'indirizzo `http://localhost:8501`.

## Funzionalità

- **Filtri**: Seleziona intervalli di date, collaboratori, reparti, attività e clienti
- **Metriche**: Visualizza ore lavorate, costo orario, fatturato e margine
- **Grafici**: Analizza la distribuzione del lavoro per collaboratore e cliente
- **Tabelle**: Esamina i dettagli dei dati filtrati

## Note

- Le credenziali sono sensibili e non dovrebbero essere incluse nel repository.
- Il file `.gitignore` è configurato per escludere la cartella `.streamlit` e `credentials/`.
- Se il foglio Google Sheets ha una struttura diversa, sarà necessario modificare le funzioni di caricamento dati.