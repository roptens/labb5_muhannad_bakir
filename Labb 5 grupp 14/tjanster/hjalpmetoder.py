import datetime
import re

def dagens_datumstampel() -> str:
    #Returnerar dagens datum som text i formatet YYYY-MM-DD
    return datetime.date.today().isoformat()

def gor_slug(text: str) -> str:

    #Gör om en text till en slug (ett url vänligt ).
    # tillexempel "Science Fiction"  "science-fiction"

    text = (text or "").strip().lower()   # ta bort mellanslag + gör små bokstäver
    text = re.sub(r"[^a-z0-9]+", "-", text)  # byt allt som inte är a-z/0-9 till '-'
    text = re.sub(r"-+", "-", text).strip("-")  # ta bort flera '-' i rad och '-' i början/slut
    return text

def pris_text_till_float(pris_text: str) -> float:

    #Tar bort valutasymboler och text och gör om till float.
    # tillexempel  "£50" till 50

    rensad = re.sub(r"[^0-9.]", "", pris_text or "")  # behåll bara siffror och punkt
    return float(rensad) if rensad else 0.0