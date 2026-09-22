import streamlit as st
import feedparser
import urllib.parse
import email.utils
from datetime import datetime

# --- Seitenkonfiguration ---
st.set_page_config(
    page_title="Global Parking Competitor Hub | PM",
    page_icon="🚗",
    layout="wide"
)

st.title("🚗 Global Parking Competitor Hub")
st.caption("Echtzeit-Marktüberblick, Leitstand-Architektur & PM-Strategie für moderne Park- & Mobilitätssysteme")

# --- Datenquellen: Vollständiges PM-Fachvokabular (27 Wettbewerber weltweit) ---
COMPETITORS = {
    # 1. Globale & DACH Enterprise Systemhäuser
    "SKIDATA": '"SKIDATA" (Parking OR ticketless OR "free-flow" OR Connect OR barrier OR airport) when:90d',
    "Scheidt & Bachmann": '"Scheidt & Bachmann" (Parking OR entervo OR "mobility CONNECT" OR ticketless OR gateless) when:90d',
    "HUB Parking (FAAC)": '("HUB Parking" OR "FAAC Parking") (JMS OR ticketless OR "free flow" OR barrier) when:90d',
    "Amano McGann": '("Amano McGann" OR "Amano Parking") ("Amano ONE" OR ticketless OR gateless) when:90d',
    "Flowbird": '"Flowbird" (Parking OR "pay-by-plate" OR ticketless OR "open payment" OR enforcement) when:90d',
    "WPS Parking": '("WPS Parking" OR "WPS ParkAdvance") (ticketless OR barrier OR cloud) when:90d',
    "IP Parking": '"IP Parking" (ParkBase OR ticketless OR barrier OR cloud) when:90d',
    "ICA Traffic": '("ICA Traffic" OR "ICA Parking") (Kassenautomat OR ticketless OR Schranke) when:90d',
    "Orbility": '"Orbility" (Parking OR ticketless OR barrier OR airport) when:90d',
    "Meypar": '"Meypar" (Parking OR ticketless OR barrier OR "control de accesos") when:90d',
    "Equinsa": '"Equinsa" (Parking OR aparcamiento OR ticketless OR barrera) when:90d',

    # 2. Free-Flow, ANPR & Retail-Disruptoren
    "Peter Park": '"Peter Park" (Parken OR Parking OR ticketless OR "free-flow" OR ANPR OR CityFlow OR enforcement) when:90d',
    "WEMOLO (Parkdepot)": '("WEMOLO" OR "Parkdepot") (Parkplatz OR Parking OR enforcement OR "free-flow" OR camera) when:90d',
    "fair parken": '"fair parken" (Parkplatz OR schrankenlos OR Kennzeichen OR ANPR OR Überwachung) when:90d',
    "ARIVO": '"ARIVO" (Parken OR Parking OR ticketless OR "free-flow" OR ANPR OR Schrankenlos) when:90d',
    "AVANTPARK": '"AVANTPARK" (Parken OR Parking OR ANPR OR schrankenlos OR Kennzeichen) when:90d',
    "Autopay": '("Autopay" OR "Autopay.de") (Parking OR ticketless OR "free-flow" OR ANPR OR frictionless) when:90d',
    "JJames": '"JJames" (Parken OR Parking OR Schranken OR Kennzeichenerkennung OR ANPR) when:90d',
    "DigiPark": '"DigiPark" (Parken OR Kennzeichen OR schrankenlos OR Parkraumüberwachung) when:90d',
    "Smart City System": '("Smart City System" OR "ParkAgent") (Parken OR occupancy OR sensor OR ANPR) when:90d',

    # 3. Corporate & Shared Parking Software
    "ParkHere": '"ParkHere" (Parkplatz OR Parken OR Corporate OR Schranke OR IoT) when:90d',
    "ParkEfficient": '"ParkEfficient" (Parkplatz OR Corporate OR Parkraummanagement OR Kontingent) when:90d',
    "BeParking (AU)": '("BeParking" OR "Becas") (Parking OR ticketless OR retrofit OR "barrier integration") when:90d',

    # 4. US Plattformen & Computer Vision
    "Flash (USA)": '("FlashParking" OR "Flash Parking") (cloud OR EV OR "dynamic pricing" OR ticketless) when:90d',
    "Metropolis (USA)": '"Metropolis" (Parking OR "drive-through" OR "checkout-free" OR "computer vision") when:90d',

    # 5. Mobility & Payment Aggregatoren
    "EasyPark": '"EasyPark" (Parking OR "CameraPark" OR ticketless OR acquisition OR partnership) when:90d',
    "Parkster": '"Parkster" (Parking OR Parken OR ticketless OR partnership) when:90d'
}

# --- Cache-gestützte Datenabfrage mit strategischem PM-Tagging ---
@st.cache_data(ttl=1800)
def fetch_live_news():
    news_items = []
    seen_links = set()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    feed_locales = [
        "hl=de&gl=DE&ceid=DE:de",
        "hl=en-US&gl=US&ceid=US:en"
    ]

    for comp, query in COMPETITORS.items():
        encoded = urllib.parse.quote(query)

        for locale in feed_locales:
            rss_url = f"https://news.google.com/rss/search?q={encoded}&{locale}"
            feed = feedparser.parse(rss_url, request_headers=headers)

            for entry in feed.entries[:5]:
                link = entry.link
                if link in seen_links:
                    continue

                title = entry.title
                title_lower = title.lower()

                # Spam-, Profil- und Stellenanzeigen-Filter
                if any(junk in title_lower for junk in ["lebenslauf", "head of", "cv", "recruiting", "stellenanzeige", "obituary", "karriere"]):
                    continue
                if "linkedin.com/in/" in link:
                    continue

                seen_links.add(link)

                # Datum parsen für exakte Sortierung
                pub_date_str = entry.get("published", "")
                dt_obj = datetime.min
                if pub_date_str:
                    try:
                        dt_obj = email.utils.parsedate_to_datetime(pub_date_str)
                    except Exception:
                        dt_obj = datetime.min

                # --- Strategische Tag-Erkennung ---
                tags = []
                if "linkedin.com" in link or "linkedin" in title_lower:
                    tags.append("LinkedIn")

                if any(k in title_lower for k in [
                    "control center", "leitstand", "leitwarte", "remote", "intercom", 
                    "voip", "monitoring", "dispatch", "operator", "jms", "command"
                ]):
                    tags.append("Control Center / Leitstand")

                if any(k in title_lower for k in [
                    "api", "webhook", "sdk", "marketplace", "marktplatz", 
                    "schnittstelle", "integrat", "open platform", "ecosystem"
                ]):
                    tags.append("APIs / Marktplatz")

                if any(k in title_lower for k in [
                    "dynamic pricing", "tarifierung", "yield", "flexible tarife", 
                    "surge pricing", "variable rates", "pricing"
                ]):
                    tags.append("Dynamic Pricing")

                if any(k in title_lower for k in [
                    "signage", "display", "anzeige", "led", "vms", 
                    "wayfinding", "screen", "stelen", "information display"
                ]):
                    tags.append("Signage / Displays")

                if any(k in title_lower for k in [
                    "ticketless", "free-flow", "free flow", "frictionless", 
                    "gateless", "schrankenlos", "anpr", "lpr", "kennzeichen"
                ]):
                    tags.append("Free-Flow / Ticketless")

                if any(k in title_lower for k in [
                    "shared parking", "quartier", "mixed-use", "mehrfachnutzung", "anwohner", "corporate"
                ]):
                    tags.append("Shared Parking")

                if any(k in title_lower for k in [
                    "enforcement", "falschparker", "violation", "compliance", "validation"
                ]):
                    tags.append("Enforcement / Überwachung")

                if any(k in title_lower for k in [
                    "kooperation", "partner", "partnership", "allianz", "acquisition", "deal", "contract"
                ]):
                    tags.append("Kooperation")

                if any(k in title_lower for k in [
                    "kasse", "automat", "schranke", "barrier", "gate", "kiosk", "terminal", "pay-by-plate", "hardware"
                ]):
                    tags.append("Hardware / POS")

                if any(k in title_lower for k in [
                    "ev", "charging", "ladesäule", "strom", "energy", "ocpi"
                ]):
                    tags.append("EV / Energie")

                if not tags:
                    tags.append("Projekt / News")

                news_items.append({
                    "competitor": comp,
                    "title": title,
                    "link": link,
                    "published": pub_date_str,
                    "dt": dt_obj,
                    "tags": tags
                })

    return news_items


# --- Tabs definieren ---
tab1, tab2, tab3 = st.tabs([
    "📡 Live-Radar", 
    "📊 Architektur & Feature-Matrix", 
    "📁 PM-Dossiers & Strategie"
])

# ==========================================
# TAB 1: LIVE-RADAR
# ==========================================
with tab1:
    st.subheader("Aktuelle Marktbewegungen & Fach-Trends")

    all_tags = [
        "Alle",
        "Control Center / Leitstand",
        "APIs / Marktplatz",
        "Dynamic Pricing",
        "Signage / Displays",
        "Free-Flow / Ticketless",
        "Shared Parking",
        "Enforcement / Überwachung",
        "Kooperation",
        "Hardware / POS",
        "EV / Energie",
        "LinkedIn"
    ]

    col_btn, col_comp, col_tag, col_sort = st.columns([1, 2, 2, 2])
    with col_btn:
        st.write("")
        st.write("")
        if st.button("🔄 Aktualisieren"):
            st.cache_data.clear()
            st.rerun()

    with col_comp:
        comp_filter = st.selectbox("Wettbewerber", ["Alle"] + list(COMPETITORS.keys()))

    with col_tag:
        tag_filter = st.selectbox("Thema / Tag", all_tags)

    with col_sort:
        sort_order = st.selectbox("Sortierung", ["Neueste zuerst", "Älteste zuerst"])

    search_query = st.text_input("🔍 Suchbegriff im Titel eingeben (optional):", "").lower().strip()

    with st.spinner("Lade Marktdaten..."):
        all_news = fetch_live_news()

    filtered_news = []
    for item in all_news:
        if comp_filter != "Alle" and item["competitor"] != comp_filter:
            continue
        if tag_filter != "Alle" and tag_filter not in item["tags"]:
            continue
        if search_query and search_query not in item["title"].lower():
            continue
        filtered_news.append(item)

    reverse_sort = True if sort_order == "Neueste zuerst" else False
    filtered_news = sorted(filtered_news, key=lambda x: x["dt"], reverse=reverse_sort)

    st.markdown(f"**Gefundene Treffer:** `{len(filtered_news)}`")
    st.divider()

    if not filtered_news:
        st.info("Keine Meldungen gefunden, die diesen Filterkriterien entsprechen.")
    else:
        for item in filtered_news:
            with st.container():
                st.markdown(f"#### [{item['competitor']}] {item['title']}")
                tag_str = " ".join([f"`{t}`" for t in item['tags']])
                st.caption(f"Tags: {tag_str} | Veröffentlicht: **{item['published']}**")
                st.markdown(f"👉 [Originalmeldung öffnen]({item['link']})")
                st.divider()

# ==========================================
# TAB 2: STRATEGISCHE ARCHITEKTUR- & FEATURE-MATRIX
# ==========================================
with tab2:
    st.subheader("Strategischer Architektur- & Feature-Vergleich")
    st.caption("Detaillierte Analyse zu Leitstand (Control Center), offenen APIs, Dynamic Pricing & digitaler Kundenansprache (Signage).")

    detailed_matrix = [
        # --- 1. Enterprise Systemhäuser ---
        {
            "Wettbewerber": "SKIDATA",
            "Segment": "Enterprise Systemhaus",
            "Control Center / Leitstand": "Zentrales Monitoring & Control: Multi-Site-Leitstand für Großbetreiber, Intercom/VoIP-Routing, Video-Streaming, Remote-Kennzeichenprüfung bei ANPR-Fehlern, Schrankenfernöffnung.",
            "APIs & Ökosystem": "SKIDATA Connect Plattform: Offene REST-APIs für Mobility-Partner, Parkplatz-Marktplätze, EV-Roaming und Vorbuchungsplattformen.",
            "Dynamic Pricing": "Regelbasierte Tarif-Engine (zeit-, event- und auslastungsabhängig); Synchronisation mit Kassen und Buchungsportalen.",
            "Signage & Displays": "Proprietäre und Standard-VMS-Ansteuerung (Zulauf, Restplätze, Echtzeit-Kennzeigenspiegelung an Ein-/Ausfahrt)."
        },
        {
            "Wettbewerber": "Scheidt & Bachmann",
            "Segment": "Enterprise Systemhaus",
            "Control Center / Leitstand": "entervo Leitstand + 'smart control' App: Vollständige Überwachung aller Feldgeräte, mobile Entstörung vor Ort, Intercom-Weiterleitung auf Mobilgeräte.",
            "APIs & Ökosystem": "mobility CONNECT: Offener API-Hub für MaaS-Anbieter, Buchungsplattformen, Payment-Provider, Flottenkarten & Ladedienste.",
            "Dynamic Pricing": "entervo Tarifserver mit flexiblen Staffelmodellen, Kalender-/Event-Steuerung.",
            "Signage & Displays": "Anbindung von Wechselverkehrszeichen (VMS), städtischen Parkleitrechnern (Datex II) & Multimedia-Bildschirmen an Terminals."
        },
        {
            "Wettbewerber": "HUB Parking (FAAC)",
            "Segment": "Enterprise Systemhaus",
            "Control Center / Leitstand": "JMS (Janus Management System): Webbasierte Leitstandkonsole für Multi-Standorte, CCTV-Streaming, Alarm- und Aufgabenrouting.",
            "APIs & Ökosystem": "JMS Open APIs: Schnittstellen für Vorbuchungssysteme, Payment-Gateways und Dritt-Geschäftslogik.",
            "Dynamic Pricing": "Tarifkonfigurator für gestaffelte und eventspezifische Abrechnung.",
            "Signage & Displays": "JDS (Janus Digital Signage): Integriertes CMS zur Steuerung dynamischer Werbe- und Infobildschirme an Automaten/Säulen."
        },
        {
            "Wettbewerber": "WPS Parking",
            "Segment": "Enterprise Systemhaus",
            "Control Center / Leitstand": "ParkAdvance Control Room: Webbasiertes Leitstand-Cockpit, SIP-Intercom-Zentralisierung, visuelle Schranken- und Terminalüberwachung.",
            "APIs & Ökosystem": "WPS Marketplace & APIs: Modulare Anbindung von Bezahl-Apps, ANPR-Systemen und Flottendiensten.",
            "Dynamic Pricing": "Tarifmodelle für variable Zeiten und Event-Zuschläge.",
            "Signage & Displays": "Vollfarb-Touchscreens an Terminals sowie LED-Hinweistafeln zur Fahrerführung."
        },
        {
            "Wettbewerber": "IP Parking",
            "Segment": "Enterprise Systemhaus (Cloud)",
            "Control Center / Leitstand": "ParkBase Cloud Management: Webbasierte Zentrale für Hardware-Überwachung, SIP-Audio über WebRTC, Fernöffnung per Mausklick.",
            "APIs & Ökosystem": "Starkes Open-API-Konzept: Schnittstellen zu Ticketing, Hotel-PMS, Dritt-Kassen und Kennzeichenerfassern.",
            "Dynamic Pricing": "Auslastungs- und zeitabhängige Tarifierung über Cloud-Tarifmodul.",
            "Signage & Displays": "Ansteuerung von Zulauf-Displays, Kennzeichen-Welcome-Displays und Touchscreens."
        },
        {
            "Wettbewerber": "ICA Traffic",
            "Segment": "Systemhaus (ÖPNV/Off-Street)",
            "Control Center / Leitstand": "ICA Central System: Fokus auf Geräteüberwachung (Geldstatus, Papiervorrat, Alarmierung), klassische Fernwartung.",
            "APIs & Ökosystem": "Schnittstellen zu kommunalen Verkehrsleitrechnern, ÖPNV-Ticketingsystemen und Barzahler-Infrastruktur.",
            "Dynamic Pricing": "Klassische städtische Tarifzonen und Zeittarife; weniger agiles Yield-Pricing.",
            "Signage & Displays": "Großdisplays an Kassenautomaten, Anbindung an städtische Parkleitsysteme."
        },
        {
            "Wettbewerber": "Orbility",
            "Segment": "Enterprise Systemhaus (Global)",
            "Control Center / Leitstand": "Orbility e-Connect: Zentrale Leitwarte für Großanlagen (Flughäfen, Spitäler), Intercom-Integration, Kameraüberwachung.",
            "APIs & Ökosystem": "Umfangreiche Schnittstellen für Drittanbieter-Validierungen, Airline-Systeme und Payment-Gateways.",
            "Dynamic Pricing": "Fortschrittliche Tarifmodelle für Vorbuchungen und Yield-Management im Flughafen-Umfeld.",
            "Signage & Displays": "Integration dynamischer VMS-Schilder, Terminal-Displays und Restplatzanzeigen."
        },
        {
            "Wettbewerber": "Meypar",
            "Segment": "Systemhaus (Südeuropa/LatAm)",
            "Control Center / Leitstand": "Nexus Parking Management: Zentrale Leitstellensoftware für Alarmmanagement, Intercom und Kassenstati.",
            "APIs & Ökosystem": "REST-Schnittstellen für Dritt-Payment, E-Commerce-Validierung und Kennzeichenabgleich.",
            "Dynamic Pricing": "Konfigurierbare Zeittarife und Event-Staffelungen.",
            "Signage & Displays": "LED-Zufahrtstafeln und Displayanzeigen an Einfahrtsterminals."
        },
        {
            "Wettbewerber": "Equinsa",
            "Segment": "Systemhaus (Spanien)",
            "Control Center / Leitstand": "Equinsa Control Hub: Standard-Leitstand für Geräteüberwachung, Schrankenstatus und Gegensprechanbindung.",
            "APIs & Ökosystem": "Schnittstellen für spanische Bezahl-Apps, Via-T (Telepass) und Kennzeichendatenbanken.",
            "Dynamic Pricing": "Regelbasierte Standardtarife nach Dauer und Wochentag.",
            "Signage & Displays": "LED-Restplatz- und Wegweiseranzeigen."
        },
        {
            "Wettbewerber": "Amano McGann",
            "Segment": "Enterprise Systemhaus (US/Asien)",
            "Control Center / Leitstand": "Amano ONE Command Center: Cloud-basierte Fernüberwachung für Schranken & Kassen, integrierter Call-Center-Support.",
            "APIs & Ökosystem": "Amano ONE API: Offene Cloud-Schnittstellen für Drittanbieter-Validierungen, Reservierungen und Zahlungsanbieter.",
            "Dynamic Pricing": "Integrierte dynamische Ratenanpassung für Events und Spitzenzeiten in Parkhäusern.",
            "Signage & Displays": "Direkte Ansteuerung von Ein-/Ausfahrts-Displays und Kassen-Touchscreens."
        },
        {
            "Wettbewerber": "Flowbird",
            "Segment": "On-Street & Off-Street Mix",
            "Control Center / Leitstand": "Flowbird Hub: Flottenmanagement für Automaten, Live-Monitoring, Kassen-Füllstände; schlanker Leitstand für Kommunen.",
            "APIs & Ökosystem": "Offene Schnittstellen für kommunale Mobilitätsplattformen, Open Payment & Handyparken.",
            "Dynamic Pricing": "Starke kommunale Tarifregeln (Bewohner, Pendler, Zeitzonen), weniger flexibles Yield-Pricing.",
            "Signage & Displays": "Fokus auf integrierte Display-Terminals und Parkleitsystem-Schnittstellen."
        },

        # --- 2. Kamera- & Free-Flow Disruptoren ---
        {
            "Wettbewerber": "Peter Park",
            "Segment": "Cloud Disruptor (ANPR)",
            "Control Center / Leitstand": "CityFlow Operations Web-App: Reines SaaS-Dashboard für Belegung & Falschparker; kein klassischer Intercom-/Hardware-Leitstand.",
            "APIs & Ökosystem": "CityFlow API: Native Integration von EasyPark (CameraPark), Parkster, Twint, Whitelabel-Web-Payment.",
            "Dynamic Pricing": "Zonenabhängige Preisanpassung über Cloud-Backend; Fokus auf Retail & Mischquartiere.",
            "Signage & Displays": "Partner-Integration für Begrüßungsanzeigen an der Zufahrt (Kennzeichen-Spiegelung, Hinweise)."
        },
        {
            "Wettbewerber": "WEMOLO (Parkdepot)",
            "Segment": "Cloud Disruptor (ANPR/Retail)",
            "Control Center / Leitstand": "WEMOLO Dashboard: Fokus auf automatisierte Fallbearbeitung, Beweisführung und Falschparker-Validierung; kein Operator-Leitstand für Schranken.",
            "APIs & Ökosystem": "Schnittstellen zu Supermarkt-Filialsystemen (z. B. Kassenbon-Scan zur Rabattierung) und Inkassodiensten.",
            "Dynamic Pricing": "Freiparkdauern mit progressiver Vertragsstrafe bei Überschreitung, kein klassisches Yield-Pricing.",
            "Signage & Displays": "Eigene Kamerasäulen mit Front-Display zur Kennzeichen-Visualisierung und Transparenz."
        },
        {
            "Wettbewerber": "fair parken",
            "Segment": "Operator & ANPR-Disruptor",
            "Control Center / Leitstand": "fair parken Leitwarte: Betreiber-Dashboard für Vertragsstrafen, Kunden-Kulanzanträge und Parkscheibenüberwachung per Sensor/ANPR.",
            "APIs & Ökosystem": "Schnittstellen zu Einzelhandels-Partnern (Guthaben) und Bezahl-Apps (EasyPark).",
            "Dynamic Pricing": "Fokus auf Freiparkdauern und Nachverfolgung, z. T. Bezahlparken auf Supermarktflächen nachts.",
            "Signage & Displays": "Großflächige juristische Beschilderung vor Ort, zunehmend digitale Infotafeln."
        },
        {
            "Wettbewerber": "ARIVO",
            "Segment": "Cloud Disruptor (Hybrid/ANPR)",
            "Control Center / Leitstand": "ARIVO Cloud Control: Webbasierter Leitstand für hybride Anlagen (mit/ohne Schranke), Fernöffnung, Belegungsampeln.",
            "APIs & Ökosystem": "ARIVO Open API: REST-Schnittstellen für Hotel-PMS, Zutrittskontrollsysteme und externe Bezahl-Apps.",
            "Dynamic Pricing": "Flexible Tarifengine für Mischparker (Mitarbeiter frei, Externe gebührenpflichtig je Tageszeit).",
            "Signage & Displays": "Unterstützung von LED-Restplatzanzeigen und Kennzeichenanzeigen an der Zufahrt."
        },
        {
            "Wettbewerber": "AVANTPARK",
            "Segment": "Free-Flow / Enforcement",
            "Control Center / Leitstand": "AVANTPARK Cloud Portal: Fokus auf ANPR-Nachprüfung, Datenschutz-konforme Bildverarbeitung und Halterabfragen.",
            "APIs & Ökosystem": "Anbindung von Web-Pay-Portalen (Zahlen bis 48h danach) und App-Zahlungsdiensten.",
            "Dynamic Pricing": "Standard-Stundentarife und Überziehungspauschalen.",
            "Signage & Displays": "Welcome-Displays mit Kennzeichenerkennungs-Feedback an der Einfahrt."
        },
        {
            "Wettbewerber": "Autopay",
            "Segment": "Skandinavischer Free-Flow Pionier",
            "Control Center / Leitstand": "Autopay Operator Suite: Vollautomatisierter 24/7-Cloud-Betrieb, automatische ANPR-Abgleichung, minimale manuelle Eingriffe.",
            "APIs & Ökosystem": "Umfassende API für nahtloses Auto-Debit (automatische Kreditkartenbelastung), Integration in EV-Ladenetzwerke.",
            "Dynamic Pricing": "Vollständige Differenzierung nach Fahrzeugtyp, Uhrzeit, Mitgliedschaften und Auslastung.",
            "Signage & Displays": "Zulauf-Displays mit Kennzeichen-Check und Hinweisen auf 48-Stunden-Zahlungsfristen im Web."
        },
        {
            "Wettbewerber": "JJames",
            "Segment": "ANPR & Ticketless (Österreich)",
            "Control Center / Leitstand": "JJames Dashboard: Übersicht über Ein-/Ausfahrten, Kennzeichen-Validierung und manuelle Korrekturen.",
            "APIs & Ökosystem": "Schnittstellen zu Schrankensteuerungen für Retrofit-Installationen und Web-Payment.",
            "Dynamic Pricing": "Staffeltarife nach Kundenkategorie (Kurzparker vs. Mitarbeiter).",
            "Signage & Displays": "Ansteuerung von Hinweistafeln zur Zahlungsaufforderung und Kennzeichenanzeige."
        },
        {
            "Wettbewerber": "DigiPark",
            "Segment": "ANPR & Enforcement (DACH)",
            "Control Center / Leitstand": "DigiPark Backoffice: Web-Portal zur Erfassung von Parkverstößen und Freigabe von Dauerparkern.",
            "APIs & Ökosystem": "Schnittstellen für White-Label-Bezahlung und Kundenfreischaltung.",
            "Dynamic Pricing": "Feste Höchstparkdauern und Überschreitungstarife.",
            "Signage & Displays": "Juristische Schildersätze und digitale Eingangsstelen."
        },
        {
            "Wettbewerber": "Smart City System",
            "Segment": "Sensor- & ANPR-Disruptor",
            "Control Center / Leitstand": "ParkAgent Platform: Visualisierung von Einzelflächen-Sensorik und ANPR-Kameras, Eskalations-Dashboard für Parkverstöße.",
            "APIs & Ökosystem": "ParkAgent REST-API: Datenweitergabe an städtische Parkleitsysteme, Navigationsdienste und Betreiber.",
            "Dynamic Pricing": "Eher statische Zeitzonenüberwachung (z. B. Kurzzeitparken 2h), keine Yield-Engine.",
            "Signage & Displays": "Kopplung an digitale Hinweisschilder und dynamische Zonenwegweiser."
        },

        # --- 3. Corporate & Shared Parking Software ---
        {
            "Wettbewerber": "ParkHere",
            "Segment": "Corporate & IoT Parking",
            "Control Center / Leitstand": "ParkHere Corporate Admin: Buchungskalender für Mitarbeiter, Zuteilungs-Logik, Schrankenfreigabe per Kennzeichen/App.",
            "APIs & Ökosystem": "Integration in Microsoft Teams, Outlook, Workday, SAP und Gebäudeleittechnik.",
            "Dynamic Pricing": "Mitarbeiter-Guthabenmodelle, Ladeabrechnung und Firmenkontingentierung.",
            "Signage & Displays": "Display-Stelen an Werkstoren mit Namens-/Kennzeichen-Begrüßung und Parkplatz-Zuweisung."
        },
        {
            "Wettbewerber": "ParkEfficient",
            "Segment": "Corporate Parking Software",
            "Control Center / Leitstand": "ParkEfficient Portal: Kein Leitstand für Schrankenstörungen; Fokus auf Belegungsoptimierung und Parkplatz-Sharing im Unternehmen.",
            "APIs & Ökosystem": "HR- und Kalender-Schnittstellen (MS Exchange, Azure AD) zur Mitarbeiter-Identifikation.",
            "Dynamic Pricing": "Interne Verrechnungssätze und Mobilitätsbudgets.",
            "Signage & Displays": "Digitale Zonenanzeigen auf Firmenparkplätzen."
        },
        {
            "Wettbewerber": "BeParking (AU)",
            "Segment": "Retrofit & Ticketless Platform",
            "Control Center / Leitstand": "BeParking Cloud Hub: Gateway-Lösung zur Fernsteuerung bestehender Schrankenanlagen fremder Hersteller.",
            "APIs & Ökosystem": "Edge-Controller-APIs für Fremdhardware, Anbindung von Payment-Gateways und QR-Codes.",
            "Dynamic Pricing": "Webbasierte Preisregeln nach Tageszeit und Wochentag.",
            "Signage & Displays": "Unterstützung externer LED-Displays zur Schrankenstatus-Anzeige."
        },

        # --- 4. US Tech-Plattformen & CV ---
        {
            "Wettbewerber": "Flash (USA)",
            "Segment": "US Cloud Platform",
            "Control Center / Leitstand": "FlashOS Cloud Command: Voll virtueller 24/7-Leitstand mit 2-Wege-Video an Kiosken, Remote-Gatesteuerung.",
            "APIs & Ökosystem": "Flash API Ecosystem: Tiefe Koppelung von Valet-Software, EV-Chargern, Aggregatoren und Flotten.",
            "Dynamic Pricing": "Voll dynamisches Yield-Pricing nach Hotel-/Airline-Vorbild (nachfrageabhängige Preisanpassung).",
            "Signage & Displays": "Dynamische Preisanzeige an Zufahrts-Stelen in Echtzeit synchronisiert mit der App."
        },
        {
            "Wettbewerber": "Metropolis (USA)",
            "Segment": "Computer-Vision Plattform",
            "Control Center / Leitstand": "Metropolis Vision OS: Keine Hardware-Leitwarte; KI-Erfassung wickelt den Vorgang ohne Schranke oder Kasse ab.",
            "APIs & Ökosystem": "Checkout-Free API: Nahtlose Wallet-Abrechnung ohne Kassen-Schnittstellen.",
            "Dynamic Pricing": "Vollständig algorithmisch gesteuerte Preise je nach Standort und Fahrzeugfrequenz.",
            "Signage & Displays": "Fokus auf Smartphone-Benachrichtigung statt physischer Vor-Ort-Displays."
        },

        # --- 5. Mobility & Payment Aggregatoren ---
        {
            "Wettbewerber": "EasyPark",
            "Segment": "Mobility & Payment Aggregator",
            "Control Center / Leitstand": "EasyPark Operator Portal: Kein Leitstand für Feldgeräte; Management von Transaktionen, Zonen und App-Nutzern.",
            "APIs & Ökosystem": "CameraPark API & Standard-Konnektoren: Ermöglicht Kassen-/Schranken-Herstellern die Anbindung von App-Zahlung.",
            "Dynamic Pricing": "Ermöglicht Kommunen und Betreibern das Ausspielen flexibler App-Tarife.",
            "Signage & Displays": "Hinweisbeschilderung vor Ort ('Hier parken mit EasyPark') und In-App-Navigation."
        },
        {
            "Wettbewerber": "Parkster",
            "Segment": "Mobility & Payment Aggregator",
            "Control Center / Leitstand": "Parkster Betreiberportal: Abrechnungs- und Transaktionsübersicht ohne Vor-Ort-Hardware-Steuerung.",
            "APIs & Ökosystem": "Offene Schnittstellen für Schrankenlos-Partner (z. B. Peter Park) zur Zahlungsabwicklung.",
            "Dynamic Pricing": "Unterstützung zonenspezifischer Betreibertarife ohne Zusatzgebühren für Endkunden.",
            "Signage & Displays": "Klassische Zonenschilder vor Ort, Tarif- und Restzeitanzeige in der mobilen App."
        }
    ]

    # Fokus-Filter
    view_mode = st.radio(
        "Fokus-Ansicht wählen:",
        ["Gesamtübersicht", "Control Center & Leitstand", "APIs & Ökosystem", "Dynamic Pricing & Signage"],
        horizontal=True
    )

    if view_mode == "Gesamtübersicht":
        display_data = detailed_matrix
    elif view_mode == "Control Center & Leitstand":
        cols = ["Wettbewerber", "Segment", "Control Center / Leitstand"]
        display_data = [{k: row[k] for k in cols} for row in detailed_matrix]
    elif view_mode == "APIs & Ökosystem":
        cols = ["Wettbewerber", "Segment", "APIs & Ökosystem"]
        display_data = [{k: row[k] for k in cols} for row in detailed_matrix]
    elif view_mode == "Dynamic Pricing & Signage":
        cols = ["Wettbewerber", "Segment", "Dynamic Pricing", "Signage & Displays"]
        display_data = [{k: row[k] for k in cols} for row in detailed_matrix]

    # Umschalter: Lesemodus (Karten) vs. Tabelle
    lesemodus = st.toggle("📖 Lesemodus aktivieren (Strukturierte Karten statt Tabelle)", value=True)

    if lesemodus:
        for item in display_data:
            with st.container():
                st.markdown(f"### {item['Wettbewerber']} <span style='font-size: 0.85em; color: gray;'>({item.get('Segment', '')})</span>", unsafe_allow_html=True)
                cols_to_show = [k for k in item.keys() if k not in ["Wettbewerber", "Segment"]]
                for key in cols_to_show:
                    st.markdown(f"**{key}:**")
                    st.info(item[key])
                st.divider()
    else:
        col_config = {
            "Wettbewerber": st.column_config.TextColumn("Wettbewerber", width="medium"),
            "Segment": st.column_config.TextColumn("Segment", width="small"),
            "Control Center / Leitstand": st.column_config.TextColumn("Control Center / Leitstand", width="large"),
            "APIs & Ökosystem": st.column_config.TextColumn("APIs & Ökosystem", width="large"),
            "Dynamic Pricing": st.column_config.TextColumn("Dynamic Pricing", width="medium"),
            "Signage & Displays": st.column_config.TextColumn("Signage & Displays", width="medium"),
        }
        st.dataframe(
            display_data,
            column_config=col_config,
            use_container_width=True,
            hide_index=True
        )

    st.markdown("---")
    st.subheader("Architektur-Differenzierung für Produktmanager")

    c1, c2 = st.columns(2)
    with c1:
        with st.expander("🏢 Leitstand-Vergleich: Systemhaus vs. Cloud-Disruptor"):
            st.markdown("""
            * **Klassische Systemhäuser (SKIDATA, Scheidt & Bachmann, HUB, WPS, Orbility):**
              * Bieten echte **24/7-Leitwarten-Architekturen** für Großbetreiber.
              * SIP/VoIP-Intercom-Routing, Video-Zuschaltung, direkte Schrankenfernsteuerung, Kassenstörungs-Handling.
              * Unverzichtbar für Betreiber mit Sicherheitsauflagen (Flughäfen, Spitäler, städtische Großgaragen).
            * **Reine ANPR-Disruptoren (Peter Park, WEMOLO, fair parken):**
              * Besitzen **keinen physischen Hardware-Leitstand**, da Schranken und Intercoms entfallen.
              * Das 'Control Center' beschränkt sich auf Belegungsanzeige, ANPR-Nachverifikation und Falschparker-Listen.
              * *Verkaufsargument:* Großbetreiber können mit reinen Disruptoren bestehende Schranken- und Sprechanlagen-Workflows nicht abbilden.
            """)

    with c2:
        with st.expander("🔌 Schnittstellen & Signage: Das neue Schlachtfeld"):
            st.markdown("""
            * **Open APIs (Plattform statt Monolith):**
              * Reine Kassen- und Schrankenverkäufe genügen Betreibern nicht mehr.
              * Entscheidend ist die Geschwindigkeit, mit der externe Vertriebskanäle (Parketplace, Vorbucher, Flottenkarten) per Webhook angebunden werden können.
            * **Signage als Enabler für Ticketless:**
              * Ohne Schranke ist das Display das einzige Feedback für den Fahrer.
              * Wer Signage (Begrüßung, Kennzeigenspiegelung, Bezahlstatus) in Echtzeit (< 500 ms) aus dem Leitstand bedient, gewinnt die User Experience bei Ticketless-Projekten.
            """)

# ==========================================
# TAB 3: PM-DOSSIERS & STRATEGIE
# ==========================================
with tab3:
    st.subheader("Strategische PM-Dossiers")
    selected_comp = st.selectbox(
        "Unternehmen für Deep-Dive wählen:",
        list(COMPETITORS.keys())
    )

    dossiers = {
        "Peter Park": """
        * **Modell:** Schrankenlose Bewirtschaftung via Kennzeichenerkennung (ANPR) mit Cloud-Backend (*CityFlow*).
        * **Treiber:** Starkes Wachstumskapital, aggressive Expansion im DACH-Raum und UK.
        * **Ökosystem:** Tief verknüpft mit App-Bezahldiensten (EasyPark CameraPark, Parkster).
        * 💡 **PM-Schlussfolgerung:** Verdrängt Schranken und Kassen im Retail- und Kommunalbereich durch minimale Vorab-Investitionen (CapEx).
        """,
        "WEMOLO (Parkdepot)": """
        * **Modell:** Full-Service-Parkraumüberwachung für den Einzelhandel (Ex-Parkdepot). Eigene modulare KI-Kamerahardware.
        * **Stärken:** Hohe Marktdurchdringung bei Supermärkten (Rewe, Aldi, Lidl, Kaufland) und automatisierte Fallbearbeitung von Falschparkern.
        * 💡 **PM-Schlussfolgerung:** Im reinen Discounter-Umfeld kaum mit Kassenhardware zu schlagen. Etablierte Systemhäuser müssen sich auf Multi-Use-Flächen mit komplexeren Tarifen konzentrieren.
        """,
        "fair parken": """
        * **Modell:** Größter deutscher Bewirtschafter von Kunden- und Klinikparkplätzen. Starke Umrüstung von Parkscheibe auf Free-Flow-Kameras.
        * 💡 **PM-Schlussfolgerung:** Bietet Komplettpakete inkl. Parkraumservice vor Ort und Zahlungsnachverfolgung.
        """,
        "SKIDATA": """
        * **Modell:** Ganzheitliche Zutritts- und Abrechnungssysteme unter ASSA ABLOY. Transformation via *SKIDATA Connect*.
        * **Ökosystem:** Schnittstellen zu Mikromobilität, Ladesäulen, Paketboxen und Dritt-Apps.
        * 💡 **PM-Schlussfolgerung:** SKIDATA macht aus Parkhäusern multimodale Mobility-Hubs, um Großbetreiber an die Plattform zu binden.
        """,
        "Scheidt & Bachmann": """
        * **Modell:** Flaggschiff-System *entervo* und Integrationsplattform *mobility CONNECT*.
        * **Stärken:** Tiefe Verzahnung mit Tankstellen, ÖPNV-Verbünden und Bahn-Infrastrukturen.
        * 💡 **PM-Schlussfolgerung:** Konzentriert sich auf ganzheitliche Mobilitätsketten (MaaS) und vernetzte Flottenabrechnung.
        """,
        "HUB Parking (FAAC)": """
        * **Modell:** Modulare Systemhaus-Lösungen rund um die *Jupiter*-Serie und das *JMS (Janus Management System)*.
        * **Stärken:** Starkes weltweites Distributionsnetzwerk über die FAAC-Muttergesellschaft.
        * 💡 **PM-Schlussfolgerung:** Robuster Konkurrent bei traditionellen Ausschreibungen (Flughäfen, Spitäler, Universitäten).
        """,
        "WPS Parking": """
        * **Modell:** Niederländischer Systemhaus-Pionier mit *ParkAdvance* und Cloud-Ausrichtung.
        * 💡 **PM-Schlussfolgerung:** Starker europäischer Wettbewerber bei Betreibern, die auf Barcode-Tickets und schrankenlose Hybridsysteme setzen.
        """,
        "IP Parking": """
        * **Modell:** Niederländischer Cloud-Challenger mit *ParkBase*. Wachsende Präsenz in Westeuropa und den USA.
        * 💡 **PM-Schlussfolgerung:** Nutzt offene Webstandards und APIs, um klassische Anbieter über modernere Software-Architektur herauszufordern.
        """,
        "ICA Traffic": """
        * **Modell:** Deutscher Spezialist für Ticketing, Kassenautomaten und Schrankensysteme im kommunalen und Bahn-Umfeld.
        * 💡 **PM-Schlussfolgerung:** Extrem stark bei Ausschreibungen von Kommunen und Verkehrsverbünden, wo hohe Standards für Bargeld und ÖPNV gefordert sind.
        """,
        "Orbility": """
        * **Modell:** Französischer Marktführer mit globaler Präsenz (Ex-ACS/Ascom).
        * 💡 **PM-Schlussfolgerung:** Hauptkonkurrent bei weltweiten Großausschreibungen für Flughäfen und zentrale Innenstadtgaragen.
        """,
        "Meypar": """
        * **Modell:** Traditioneller spanischer Hersteller robuster Hard- und Software für Garagen.
        * 💡 **PM-Schlussfolgerung:** Stark in Südeuropa und Lateinamerika verankert.
        """,
        "Equinsa": """
        * **Modell:** Spanischer Systemanbieter für Parkschranken, Kassen und Kontrollsysteme.
        * 💡 **PM-Schlussfolgerung:** Fokussiert auf den iberischen Markt mit budgetfreundlichen Komplettlösungen.
        """,
        "Flowbird": """
        * **Modell:** Weltmarktführer bei Straßen-Parkscheinautomaten, der zunehmend in Off-Street-Parken und Open-Payment drängt.
        * **Stärken:** Riesige installierte Basis bei Kommunen und Städten weltweit.
        * 💡 **PM-Schlussfolgerung:** Bedroht klassische Systeme über die kommunale Schnittstelle (On-Street und Off-Street aus einer Hand).
        """,
        "Amano McGann": """
        * **Modell:** Traditionelles Schwergewicht in Nordamerika und Asien; Modernisierung über *Amano ONE*.
        * 💡 **PM-Schlussfolgerung:** Sehr starke lokale Präsenz in den USA; reagiert auf Disruptoren wie Flash durch eigene Cloud-Modelle.
        """,
        "Flash (USA)": """
        * **Modell:** Cloud-native Parkhaus-Plattform, die Parkmanagement und Ladeinfrastruktur (EV) vereint.
        * 💡 **PM-Schlussfolgerung:** Definiert das Parkhaus neu als Energie- und Mobilitäts-Hub mit dynamischer Preisfindung.
        """,
        "Metropolis (USA)": """
        * **Modell:** Radikales Computer-Vision-System ("Drive in, Drive out"). Durch Kauf von SP+ einer der größten US-Betreiber.
        * 💡 **PM-Schlussfolgerung:** Zeigt das Extrem: Kassenhardware wird komplett überflüssig, Software und KI übernehmen alles.
        """,
        "Autopay": """
        * **Modell:** Vorreiter für schrankenlose Kennzeichenerfassung in Skandinavien; expandiert über Autopay.de stark in DACH.
        * 💡 **PM-Schlussfolgerung:** Blaupause für maximale Automatisierung ohne Vor-Ort-Personal.
        """,
        "ARIVO": """
        * **Modell:** Österreichischer Anbieter modularer ANPR-Lösungen (mit oder ohne Schranke).
        * 💡 **PM-Schlussfolgerung:** Zeigt, dass auch kleinere Anbieter mit hoher Schnittstellen-Flexibilität und fairen Preisen punkten können.
        """,
        "AVANTPARK": """
        * **Modell:** Free-Flow ANPR-Überwachung für Parkplätze in Deutschland und Nordeuropa.
        * 💡 **PM-Schlussfolgerung:** Drängt bei Einzelhandel und Fachmärkten auf den Markt mit 48h-Zahlungsmodellen.
        """,
        "JJames": """
        * **Modell:** Österreichischer Spezialist für Schranken- und Kennzeichentechnik (Retrofit).
        * 💡 **PM-Schlussfolgerung:** Bietet unkomplizierte Nachrüstungen für bestehende Betreiber ohne Gesamttausch.
        """,
        "DigiPark": """
        * **Modell:** Digitale Parkplatzüberwachung und Kennzeichenerkennung für Gewerbe- und Kundenflächen.
        * 💡 **PM-Schlussfolgerung:** Konzentriert sich auf automatisierte Fallbearbeitung für Eigentümer.
        """,
        "Smart City System": """
        * **Modell:** Sensor- und ANPR-basierte Parkraumerfassung mit der Management-Plattform *ParkAgent*.
        * 💡 **PM-Schlussfolgerung:** Schlanke digitale Lösungen zur Überwachung von Mischflächen und Falschparkern.
        """,
        "ParkHere": """
        * **Modell:** Münchner Spezialist für betriebliches Parkraummanagement (Corporate Mobility).
        * 💡 **PM-Schlussfolgerung:** Zeigt, wie B2B-Kunden Parkplätze an Mitarbeiter zuteilen und Ladesäulen integrieren.
        """,
        "ParkEfficient": """
        * **Modell:** Software-Plattform zur internen Parkplatzkontingentierung bei Großkonzernen.
        * 💡 **PM-Schlussfolgerung:** Rein softwaregetriebenes Shared-Parking-Modell ohne Fokus auf Kassenautomaten.
        """,
        "BeParking (AU)": """
        * **Modell:** Australischer Plattform-Anbieter für ticketlose Schranken-Nachrüstungen via Edge-Controller.
        * 💡 **PM-Schlussfolgerung:** Spannender Ansatz zur Verlängerung der Lebensdauer alter Hardware.
        """,
        "EasyPark": """
        * **Modell:** Größter Park-App-Aggregator Europas.
        * 💡 **PM-Schlussfolgerung:** Greift über *CameraPark* das Transaktionsgeschäft an: Autofahrer zahlen per App statt am Kassenautomaten.
        """,
        "Parkster": """
        * **Modell:** Stark wachsende gebührenfreie Park-App in DACH und Skandinavien.
        * 💡 **PM-Schlussfolgerung:** Wichtiger Partner für schrankenlose Betreiber zur Abwicklung mobiler Zahlungen.
        """
    }

    st.markdown(dossiers.get(selected_comp, "Kein Dossier hinterlegt."))
