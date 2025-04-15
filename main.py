from telegram import Bot
import requests
import time
from keep_alive import keep_alive

keep_alive()

API_KEY = "e5fa93f1664a311c5f4ee2b034a92d38"
TELEGRAM_TOKEN = "7143753192:AAGPbxttFiwIRRHV1TgwTGXK0Qt6tenb1wo"
CHAT_ID = "212424067"
MIN_VARIATION = 10.0

LEAGUES = [
    "soccer_italy_serie_a",
    "soccer_epl",
    "soccer_spain_la_liga",
    "soccer_germany_bundesliga",
    "soccer_france_ligue_one"
]

bot = Bot(token=TELEGRAM_TOKEN)
storico_quote = {}

def controlla_partite():
    print("Controllo partite in corso...")

    for league in LEAGUES:
        url = f"https://api.the-odds-api.com/v4/sports/{league}/odds?regions=eu&markets=h2h&apiKey={API_KEY}"
        response = requests.get(url)

        if response.status_code != 200:
            print(f"[{league}] Errore nella richiesta API:", response.text)
            continue

        partite = response.json()

        for match in partite:
            match_id = match["id"]
            home = match["home_team"]
            away = match["away_team"]
            bookmakers = match.get("bookmakers", [])

            if not bookmakers:
                continue

            outcomes = bookmakers[0]["markets"][0]["outcomes"]

            for outcome in outcomes:
                esito = outcome["name"]
                quota = float(outcome["price"])
                chiave = f"{match_id}-{esito}"

                if chiave in storico_quote:
                    quota_prec = storico_quote[chiave]
                    variazione = ((quota - quota_prec) / quota_prec) * 100

                    if variazione <= -MIN_VARIATION:
                        messaggio = (
                            f"**Quota in CALO ({esito})**
"
                            f"{home} vs {away}
"
                            f"Da {quota_prec:.2f} a {quota:.2f} ({variazione:.1f}%)"
                        )
                        print(messaggio)
                        bot.send_message(chat_id=CHAT_ID, text=messaggio)

                    elif variazione >= MIN_VARIATION:
                        messaggio = (
                            f"**Quota in SALITA ({esito})**
"
                            f"{home} vs {away}
"
                            f"Da {quota_prec:.2f} a {quota:.2f} (+{variazione:.1f}%)"
                        )
                        print(messaggio)
                        bot.send_message(chat_id=CHAT_ID, text=messaggio)

                storico_quote[chiave] = quota

while True:
    try:
        controlla_partite()
    except Exception as e:
        print("Errore:", e)
    time.sleep(300)
