from datetime import datetime
import pytz

def format_utc_to_local(utc_dt: datetime) -> str:
    if not utc_dt:
        return "N/A"
    colombia_tz = pytz.timezone("America/Bogota")
    aware_utc_dt = utc_dt.replace(tzinfo=pytz.utc)
    local_dt = aware_utc_dt.astimezone(colombia_tz)
    return local_dt.strftime('%d-%m-%Y %I:%M %p')
