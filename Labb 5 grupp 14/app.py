from flask import Flask, request, jsonify

from tjanster.skrapa import skrapa_och_spara_kategorier, hamta_bocker_for_kategori_idag
from tjanster.lagring import spara_bocker_fil, hitta_bok_med_id

app = Flask(__name__)



# KATEGORIER

@app.post("/api/kategorier/skrapa")
def api_skrapa_kategorier():

    #Skrapar kategorier från books.toscrape.com och sparar i data/kategorier.json

    kategorier = skrapa_och_spara_kategorier()
    return jsonify({"antal": len(kategorier), "kategorier": kategorier}), 200



@app.get("/api/bocker/<string:kategori_slug>")
def api_hamta_bocker(kategori_slug: str):

    #Returnerar böcker i en kategori om dagens fil finns  använd den. Annars  skrapar och skapar en ny fil. 

    try:
        payload = hamta_bocker_for_kategori_idag(kategori_slug, tvinga_uppdatering=False)
        return jsonify(payload), 200
    except ValueError as e:
        return jsonify({"fel": str(e)}), 404
    except Exception as e:
        return jsonify({"fel": "Internt fel", "detaljer": str(e)}), 500


@app.post("/api/bocker/<string:kategori_slug>")
def api_skapa_bok(kategori_slug: str):
    """
    Skapar en bok och sparar i dagens fil.
    
    {
      "titel": "Min bok",
      "pris_gbp": 9.99,
      "pris_sek": 120.0,
      "betyg": "Five",
      "produkt_url": "https://länk.com"
    }
    """
    data = request.get_json(silent=True) or {}

    try:
        payload = hamta_bocker_for_kategori_idag(kategori_slug, tvinga_uppdatering=False)

        if not data.get("id"):
            data["id"] = f"egen-{len(payload['bocker']) + 1}"

        payload["bocker"].append({
            "id": data.get("id"),
            "titel": data.get("titel", ""),
            "pris_gbp": float(data.get("pris_gbp", 0)),
            "pris_sek": float(data.get("pris_sek", 0)),
            "betyg": data.get("betyg", "Okant"),
            "produkt_url": data.get("produkt_url", "")
        })

        spara_bocker_fil(kategori_slug, payload)
        return jsonify(payload), 201

    except ValueError as e:
        return jsonify({"fel": str(e)}), 404
    except Exception as e:
        return jsonify({"fel": "Internt fel", "detaljer": str(e)}), 500


@app.put("/api/bocker/<string:kategori_slug>/<string:bok_id>")
def api_uppdatera_bok(kategori_slug: str, bok_id: str):

   # Uppdaterar en bok 
    # { "pris_gbp": 12.5, "betyg": "Three" }

    data = request.get_json(silent=True) or {}

    try:
        payload = hamta_bocker_for_kategori_idag(kategori_slug, tvinga_uppdatering=False)
        bok = hitta_bok_med_id(payload["bocker"], bok_id)
        if not bok:
            return jsonify({"fel": "Bok hittades inte"}), 404

        if "titel" in data:
            bok["titel"] = data["titel"]
        if "pris_gbp" in data:
            bok["pris_gbp"] = float(data["pris_gbp"])
        if "pris_sek" in data:
            bok["pris_sek"] = float(data["pris_sek"])
        if "betyg" in data:
            bok["betyg"] = data["betyg"]
        if "produkt_url" in data:
            bok["produkt_url"] = data["produkt_url"]

        spara_bocker_fil(kategori_slug, payload)
        return jsonify(bok), 200

    except ValueError as e:
        return jsonify({"fel": str(e)}), 404
    except Exception as e:
        return jsonify({"fel": "Internt fel", "detaljer": str(e)}), 500


@app.delete("/api/bocker/<string:kategori_slug>/<string:bok_id>")
def api_ta_bort_bok(kategori_slug: str, bok_id: str):
    #Tar bort en bok från dagens fil
    try:
        payload = hamta_bocker_for_kategori_idag(kategori_slug, tvinga_uppdatering=False)

        fore = len(payload["bocker"])
        payload["bocker"] = [b for b in payload["bocker"] if b.get("id") != bok_id]
        efter = len(payload["bocker"])

        if fore == efter:
            return jsonify({"fel": "Bok hittades inte"}), 404

        spara_bocker_fil(kategori_slug, payload)
        return jsonify({"borttagen": True, "id": bok_id}), 200

    except ValueError as e:
        return jsonify({"fel": str(e)}), 404
    except Exception as e:
        return jsonify({"fel": "Internt fel", "detaljer": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)