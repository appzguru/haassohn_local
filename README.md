# Haas+Sohn pelletkachel (lokaal)

Home Assistant-integratie voor Haas+Sohn pelletkachels met de **eigen Haas+Sohn wifimodule** (niet de Fumis WiRCU-module; daarvoor is er de officiële Fumis-integratie). Werkt volledig lokaal via `http://<ip>/status.cgi`, zonder cloud.

Getest met: HSP-6, firmware V6.02, wifimodule V2.2.4. De kachel accepteert alleen hele graden.

## Installatie

1. HACS → ⋮ → Custom repositories → deze repo toevoegen als *Integration*.
2. Installeren, Home Assistant herstarten.
3. Instellingen → Apparaten & diensten → Integratie toevoegen → *Haas+Sohn pelletkachel (lokaal)*.
4. IP-adres en app-PIN invullen (staan op de kachel onder *WLAN status PIN*).

## Entiteiten

| Entiteit | Wat |
|---|---|
| `climate` Kachel | Thermostaat: doeltemperatuur + aan/uit (zie hieronder) |
| Kamertemperatuur, Doeltemperatuur, Status, Foutcode | Actuele toestand |
| Pelletverbruik (kg), Onderhoud over (kg), Schoonmaken over | Onderhoud |
| Ontstekingen, Branduren | Diagnostiek |
| Storing, Weekprogramma kachel | Binaire sensoren |
| Hoofdschakelaar, Eco-modus | Schakelaars |

## "Uit" = spaarstand

Standaard zet **uit** op de thermostaat de kachel niet echt uit, maar verlaagt de doeltemperatuur naar de spaartemperatuur (standaard 17 °C). De kachel dooft vanzelf en ontsteekt pas weer onder die temperatuur. Dat spaart ontstekingen. **Aan** zet de laatst gebruikte comforttemperatuur terug. Echt uitschakelen gaat met de schakelaar *Hoofdschakelaar*. Dit is aan te passen via *Configureren* op de integratie.

## Protocol

- `GET /status.cgi` → volledige status in JSON (geen authenticatie).
- `POST /status.cgi` met bijvoorbeeld `{"sp_temp": 19}`, header `X-HS-PIN = md5(nonce + md5(pin))`; `nonce` komt uit `meta.nonce` van de laatste status en wisselt na elke opdracht.

Gebaseerd op het werk van [ioBroker.haassohn](https://github.com/marvingrieger/ioBroker.haassohn) en de openHAB-binding.
