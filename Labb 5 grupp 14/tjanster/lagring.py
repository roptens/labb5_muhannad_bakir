import os
import json
from tjanster.hjalpmetoder import dagens_datumstampel

DATA_MAPP = "data"

def sakerstall_data_mapp():
    #Skapar data mappen om den inte finns
    os.makedirs(DATA_MAPP, exist_ok=True)

def las_json(filvag: str, standard):

    #Läser en JSON fil och returnerar innehållet
    if not os.path.exists(filvag):
        return standard

    with open(filvag, "r", encoding="utf-8") as f:
        return json.load(f)

def skriv_json(filvag: str, data):
    #Skriver data som JSON till fil
    with open(filvag, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def kategorier_filvag() -> str:
    #Returnerar filvägen till categories.json
    sakerstall_data_mapp()
    return os.path.join(DATA_MAPP, "kategorier.json")

def lasa_kategorier():
    #Läser kategorier från fil.
    return las_json(kategorier_filvag(), [])

def spara_kategorier(kategorier):
    #Sparar kategorier till fil
    skriv_json(kategorier_filvag(), kategorier)

def bocker_filvag(kategori_slug: str) -> str:

    #Filnamn för dagens böcker i en kategori
    # data/travel_2026-02-25.json
    sakerstall_data_mapp()
    return os.path.join(DATA_MAPP, f"{kategori_slug}_{dagens_datumstampel()}.json")

def lasa_bocker_fil(kategori_slug: str):
         return las_json(bocker_filvag(kategori_slug), None)

def spara_bocker_fil(kategori_slug: str, innehall):
    #Sparar payload (böcker + metadata) i dagens fil
    skriv_json(bocker_filvag(kategori_slug), innehall)

def hitta_bok_med_id(bocker: list, bok_id: str):
    #Letar efter en bok i listan med ett visst id
    for bok in bocker:
        if bok.get("id") == bok_id:
            return bok
    return None