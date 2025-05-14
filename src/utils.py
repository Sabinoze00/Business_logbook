import calendar
import locale
from datetime import datetime, timedelta

def months_it_to_num(month_name):
    """
    Converte il nome del mese in italiano alla forma con iniziale maiuscola.
    
    Args:
        month_name: Nome del mese in italiano (es. 'gennaio')
        
    Returns:
        Nome del mese con iniziale maiuscola (es. 'Gennaio') o None se non trovato
    """
    # Mapping italiano-Iniziale maiuscola
    month_map = {
        'gennaio': 'Gennaio',
        'febbraio': 'Febbraio',
        'marzo': 'Marzo',
        'aprile': 'Aprile',
        'maggio': 'Maggio',
        'giugno': 'Giugno',
        'luglio': 'Luglio',
        'agosto': 'Agosto',
        'settembre': 'Settembre',
        'ottobre': 'Ottobre',
        'novembre': 'Novembre',
        'dicembre': 'Dicembre'
    }
    
    # Normalizza il mese (minuscolo)
    month_name_lower = month_name.lower() if isinstance(month_name, str) else ""
    
    # Controlla se il mese è nel mapping
    if month_name_lower in month_map:
        return month_map[month_name_lower]
    
    # Gestisce anche i mesi in inglese o varianti
    english_map = {
        'january': 'Gennaio',
        'february': 'Febbraio',
        'march': 'Marzo',
        'april': 'Aprile',
        'may': 'Maggio',
        'june': 'Giugno',
        'july': 'Luglio',
        'august': 'Agosto',
        'september': 'Settembre',
        'october': 'Ottobre',
        'november': 'Novembre',
        'december': 'Dicembre'
    }
    
    if month_name_lower in english_map:
        return english_map[month_name_lower]
    
    # Se la stringa ha già l'iniziale maiuscola e il resto minuscolo
    if month_name and month_name[0].isupper() and month_name[1:].islower():
        return month_name
    
    # Se non troviamo corrispondenze
    return None

def get_month_range(year, month):
    """
    Restituisce il primo e l'ultimo giorno del mese specificato.
    
    Args:
        year: Anno
        month: Mese (1-12)
        
    Returns:
        Tuple (primo_giorno, ultimo_giorno) come oggetti datetime
    """
    # Primo giorno del mese
    first_day = datetime(year, month, 1)
    
    # Ultimo giorno del mese
    # Prendiamo il primo giorno del mese successivo e sottraiamo un giorno
    if month == 12:
        last_day = datetime(year + 1, 1, 1) - timedelta(days=1)
    else:
        last_day = datetime(year, month + 1, 1) - timedelta(days=1)
    
    return first_day, last_day

def format_currency(value):
    """
    Formatta un valore come valuta in euro.
    
    Args:
        value: Valore numerico
        
    Returns:
        Stringa formattata (es. "1.234,56 €")
    """
    try:
        return f"{value:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return f"0,00 €"

def quarter_from_month(month):
    """
    Restituisce il trimestre corrispondente al mese.
    
    Args:
        month: Nome del mese o numero (1-12)
        
    Returns:
        Numero del trimestre (1-4)
    """
    # Se è una stringa, converti in numero
    if isinstance(month, str):
        month_num = None
        month_lower = month.lower()
        
        # Mapping italiano
        it_months = {
            'gennaio': 1, 'febbraio': 2, 'marzo': 3,
            'aprile': 4, 'maggio': 5, 'giugno': 6,
            'luglio': 7, 'agosto': 8, 'settembre': 9,
            'ottobre': 10, 'novembre': 11, 'dicembre': 12
        }
        
        # Mapping inglese
        en_months = {
            'january': 1, 'february': 2, 'march': 3,
            'april': 4, 'may': 5, 'june': 6,
            'july': 7, 'august': 8, 'september': 9,
            'october': 10, 'november': 11, 'december': 12
        }
        
        if month_lower in it_months:
            month_num = it_months[month_lower]
        elif month_lower in en_months:
            month_num = en_months[month_lower]
        else:
            # Prova a convertire direttamente
            try:
                month_num = int(month)
            except:
                return None
    else:
        month_num = month
    
    # Determina il trimestre
    if 1 <= month_num <= 3:
        return 1
    elif 4 <= month_num <= 6:
        return 2
    elif 7 <= month_num <= 9:
        return 3
    elif 10 <= month_num <= 12:
        return 4
    else:
        return None

def get_days_in_month(year, month):
    """
    Restituisce il numero di giorni in un mese.
    
    Args:
        year: Anno
        month: Mese (1-12)
        
    Returns:
        Numero di giorni nel mese
    """
    return calendar.monthrange(year, month)[1]

def get_working_days_in_month(year, month):
    """
    Restituisce il numero di giorni lavorativi (Lun-Ven) in un mese.
    
    Args:
        year: Anno
        month: Mese (1-12)
        
    Returns:
        Numero di giorni lavorativi nel mese
    """
    first_day, last_day = get_month_range(year, month)
    
    # Converte gli oggetti datetime in date
    first_date = first_day.date()
    last_date = last_day.date()
    
    # Conta i giorni lavorativi
    working_days = 0
    current_date = first_date
    
    while current_date <= last_date:
        # 0 = lunedì, 6 = domenica
        if current_date.weekday() < 5:  # 0-4 sono giorni lavorativi (Lun-Ven)
            working_days += 1
        
        current_date += timedelta(days=1)
    
    return working_days