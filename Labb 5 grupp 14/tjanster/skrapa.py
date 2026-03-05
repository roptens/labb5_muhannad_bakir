import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re

from tjanster.hjalpmetoder import gor_slug, pris_text_till_float, dagens_datumstampel
from tjanster.lagring import lasa_kategorier, spara_kategorier, lasa_bocker_fil, spara_bocker_fil

BAS_URL = "https://books.toscrape.com/"

def skrapa_och_spara_kategorier():
    """
    1) Hämtar startsidan
    2) Letar upp alla kategorilänkar
    3) Sparar dem i data/kategorier.json
    """
    svar = requests.get(BAS_URL, timeout=20)  # gör en HTTP GET
    svar.raise_for_status()                   # om fel (t.ex. 404) -> kasta exception

    soppa = BeautifulSoup(svar.text, "lxml")  

    #-----------------------------------------------






    lankar = soppa.select("div.side_categories ul li ul li a") # VAR FINNS NAMN PÅ ALLA KATOGIER div.side_categories ul li ul li a SEN LÄNKEN 

    kategorier = [] # tom lista som ska fyllas med alla kategorier som man hittar i sidan 
    for a in lankar: # Loopar igenom alla länkar
        namn = a.get_text(strip=True)     # den hämtar texten som finns mellan <a> Mystery </a> asså i strip=True tar bort alla melanslag
        href = a.get("href", "")          # tar bort herf och behåler den riktiga länken 
        #Från <a href="catalogue/category/books/mystery_3/index.html">
        # till "catalogue/category/books/mystery_3/index.html"

        kategorier.append({ #skapar ett objekt och lägger i namn slug och länken. append gör att den skriver objektet sist ner
            "namn": namn,
            "slug": gor_slug(namn),
            "url": urljoin(BAS_URL, href)  # den ligger herf och base url asså sidans länk https://books.toscrape.com/
        })

    spara_kategorier(kategorier)     #spara kategorier spara listan
    return kategorier
   #----------------------------------------------- #etar upp en kategori i din sparade fil baserat på slug
def hamta_kategori_via_slug(kategori_slug: str): #kategori_slug är texten från din api länken 

    kategorier = lasa_kategorier()  #Läser alla kategorier från fil
    for kategori in kategorier: # Loopar igenom alla kategorier 
        if kategori["slug"] == kategori_slug: # Jämför slug om det finns en match mellan båda då returnerar man kategori
            return kategori
    return None # om det finns inte 
   #-----------------------------------------------
def skrapa_gbp_till_sek_kurs() -> float:

    #Skrapar växelkurs GBP till SEK från x-rates
    try:
        url = "https://www.x-rates.com/calculator/?from=GBP&to=SEK&amount=1" # sidan man skrapar för att växla
        svar = requests.get(url, timeout=20)
        svar.raise_for_status() # kolla om sidan laddas up eleer inte

        soppa = BeautifulSoup(svar.text, "lxml")

        element = soppa.select_one(".ccOutputRslt")  # elementet som innehåller "13.45 SEK"
        if not element: 
            return 0.0 #om ingen element finns med namnet .ccOutputRslt så returnerar 0.0 istället

        text = element.get_text(" ", strip=True)     # som ovan man hämtar texten och  tar bort alla melanslag 
        nummer = re.sub(r"[^0-9.]", "", text)       # behåll bara siffror 
        return float(nummer) if nummer else 0.0     # Gör om till float 

    except Exception:
        # PythonAnywhere kan blocka x-rates krascha inte hela API
        return 13.0   

   #-----------------------------------------------

def skrapa_bocker_i_kategori(kategori_url: str, max_sidor: int = 50): # max_sidor för att koden ska inte fastna 

    kurs = skrapa_gbp_till_sek_kurs() #hämta pris 

    bocker = []      # tom lista för böcker
    sida_url = kategori_url        # sidans länk 
    antal_sidor = 0                    # räkna sidor börja från 0

    while sida_url and antal_sidor < max_sidor: # en while loop 
        antal_sidor += 1                         # lägga till en sida varanan varv

        svar = requests.get(sida_url, timeout=20)     # laddar ner html sidan  
        svar.raise_for_status()                       # kolla status om sidan laddas upp eller inte 
        soppa = BeautifulSoup(svar.text, "lxml")

        for artikel in soppa.select("article.product_pod"):
            titel = artikel.select_one("h3 a").get("title", "").strip() #hittar <a>  i h3 för att hitta title 

            pris_text = artikel.select_one(".price_color").get_text(strip=True)  # gör pris till text
            pris_gbp = pris_text_till_float(pris_text) # tar bort £ tillexempel gör priset 50

            pris_sek = round(pris_gbp * kurs, 2) if kurs else 0.0      # Räkna pris i sek från pound

            # rating sitter i class="star-rating Three"
            betyg = "Okant"              #lägger ne okant värde från början 
            betyg_p = artikel.select_one("p.star-rating") # elementet som innehåller betyget 
            if betyg_p:                    #om elementet hittades fortsätt
                klasser = betyg_p.get("class", []) # Hämta class
                if len(klasser) >= 2:      # kontrolera att i listan finns det mer än 2 
                    betyg = klasser[1]  # Ta själva betyget 

            rel_produkt = artikel.select_one("h3 a").get("href", "") # hittar länken inne i rubriken
            # den ser ut så har <h3><a href="../../../a-light-in-the-attic_1000/index.html" title="...">...</a></h3> på google 
            # den blir så "../../../a-light-in-the-attic_1000/index.html"
            produkt_url = urljoin(sida_url, rel_produkt) # gör länken till en länk du kan klicka på derickt 

            bok_id = f"bok-{len(bocker) + 1}"  # göra en id gör boken 

            bocker.append({              # Lägg in boken i listan bocker är namnet på listan append för att skriva sist ner
                "id": bok_id,
                "titel": titel,
                "pris_gbp": pris_gbp,
                "pris_sek": pris_sek,
                "betyg": betyg,
                "produkt_url": produkt_url
            })
 

        nasta_a = soppa.select_one("li.next a") # Leta efter nästa sida om det finns  så ser den ut på google <li class="next"><a href="page-2.html">next</a></li>
        if nasta_a:
            sida_url = urljoin(sida_url, nasta_a.get("href", ""))
        else:
            sida_url = None

    return {
        "skrapat_datum": dagens_datumstampel(), # sickar till json filen dagens datum
        "gbp_till_sek": kurs,        #hur mycket är sek
        "kalla_kategori_url": kategori_url, #kategori länken
        "bocker": bocker     #istan med alla böcker som är samlat
    }
   #-----------------------------------------------
def hamta_bocker_for_kategori_idag(kategori_slug: str, tvinga_uppdatering: bool = False):
 
    #Om dagens fil finns använd den.
    #Annars skrapa och spara.
    #tvinga_uppdatering=True -> skrapa om även om filen finns.

    kategori = hamta_kategori_via_slug(kategori_slug)
    if not kategori:
        raise ValueError("Kategori hittades inte. Kör POST /api/kategorier/skrapa först.") # Om kategorin inte finns

    if not tvinga_uppdatering:
        befintlig = lasa_bocker_fil(kategori_slug) #läsa från filen somm finns 
        if befintlig is not None:
            return befintlig

    payload = skrapa_bocker_i_kategori(kategori["url"])
    spara_bocker_fil(kategori_slug, payload)
    return payload