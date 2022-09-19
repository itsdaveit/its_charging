from urllib import request


from datetime import datetime, timedelta
import requests
from requests.auth import HTTPBasicAuth

class evse_wallbox:

    def __init__(self, url, user, password):
        self.base_url = url
        self.auth = HTTPBasicAuth(user, password)

    def _request(self, endpoint):
        """Perform a GET request to `endpoint` and return the JSON response."""
        url = self.base_url + endpoint
        response = requests.get(url, auth=self.auth)
        response.raise_for_status()
        return response.json()

    def get_parameters(self):
        """Der Aufruf getParameters gibt essentielle Daten zum Status der Wallbox und dem aktuellen
    	Ladevorgang zurück.
        Parameter Beschreibung Datentyp
        vehicleState Fahrzeugstatus (1: bereit | 2: Fahrzeug angeschlossen | 3: Fahrzeug lädt | 5: Fehler) integer
        evseState EVSE Status (true: Ladestation freigeschaltet | false: Ladestation gesperrt) boolean
        maxCurrent Maximal möglicher Ladestrom (abhängig vom PPWiderstand und dem konfigurierten maximalen Ladestrom – je nachdem welcher Wert niedriger ist) integer
        actualCurrent Konfigurierter Ladestrom in A (z.B. 15 -> 15A) integer
        actualCurrentMA* Konfigurierter Ladestrom in hundertstel A (z.B. 1550 -> 15,50A) integer
        actualPower Aktuelle Ladeleistung in kW float
        duration Dauer des Ladevorgangs in ms integer
        alwaysActive Always Active Mode (true/false) boolean
        lastActionUser Name des Benutzers, der die letzte Aktivität durchgeführt hat (Aktivieren/Deaktivieren) string
        lastActionUID UID des Benutzers, der die letzte Aktivität durchgeführt hat (Aktivieren/Deaktivieren) string
        energy Geladene Energie des aktuellen Ladevorgangs in kWh float
        mileage Geladene Energie des aktuellen Ladevorgangs in km (abhängig vom konfigurierten Stromverbrauch des Fahrzeugs) float
        meterReading Zählerstand float
        currentP1 Strom in A (L1) float
        currentP2 Strom in A (L2) float
        currentP3 Strom in A (L3) float
        voltageP1 Spannung in V (L1) float
        voltageP2 Spannung in V (L2) float
        voltageP3 Spannung in V (L3) float
        useMeter Stromzähler konfiguriert (true/false) boolean
        RFIDUID Zuletzt erkannte RFID-UID (kann mit /clearRFID manuell zurückgesetzt werden; wird überschrieben, sobald eine neue RFID-Auslesung erfolgt)  string
        """
        endpoint = "getParameters"
        response = self._request(endpoint)
        return response["list"][0]
    
    def get_log(self):
        """Ausgabe des Logfiles im JSON-Format
        Parameter Beschreibung Datentyp
        uid UID des RFID-Benutzers, der den Ladevorgang initiiert hat. Bei einer Aktivierung, welche nicht per RFID ausgeführt wurde gilt: GUI: GUI | Taster: Button | API: remote | Fahrzeug: vehicle string
        username Vergebener RFID-Benutzername, der den Ladevorgang initiiert hat. Bei einer Aktivierung, welche nicht per RFID ausgeführt wurde gilt: GUI: GUI | Taster: Button | API: remote | Fahrzeug: vehicle string
        timestamp Unix Timestamp zu Beginn des Ladevorgangs integer
        duration Dauer des Ladevogangs in Millisekunden integer
        energy Geladene Energie in kWh float
        price Zum Beginn des Ladevorgangs hinterlegter Energiepreis cffloat
        reading* Zählerstand zu Beginn des Ladevorgangs float """
        endpoint = "getLog"
        response = self._request(endpoint)
        return response["list"]
    
    def get_evse(self):
        """Gibt Netzwerk- und weitere Konfigurationswerte zurück.
        Parameter Beschreibung Datentyp
        ssid Konfigurierte SSID string
        dns Konfigurierter DNS-Server string
        mac MAC-Adresse der Wallbox string
        ip IP-Adresse der Wallbox string
        netmask Konfigurierte Subnetzmaske string
        gateway Konfiguriertes Gateway string
        uptime Betriebszeit seit Einschalten der Wallbox in Sekunden integer
        opMode* Betriebsmodus: normal | alwaysActive | remote string
        firmware* Firmware-Version string
        *ab Firmware v2.2.5
        Hinweis: Ab Firmware v2.2.5 wird dieser API-Aufruf auch beantwortet, wenn in den Einstellungen die
        API grundsätzlich deaktiviert ist."""
        endpoint = "evseHost"
        response = self._request(endpoint)
        return response["list"][0]
