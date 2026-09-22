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

# --- Datenquellen: Vollständiges PM-Fachvokabular (DE + EN) ---
COMPETITORS = {
    # --- 1. Global & DACH Enterprise Systemhäuser ---
    "SKIDATA": '"SKIDATA" (Parking OR ticketless OR "free-flow" OR Connect OR barrier) when:90d',
    "Scheidt & Bachmann": '"Scheidt & Bachmann" (Parking OR entervo OR "mobility CONNECT" OR ticketless) when:90d',
    "HUB Parking (FAAC)": '("HUB Parking" OR "FAAC Parking") (JMS OR ticketless OR barrier) when:90d',
    "Amano McGann": '("Amano McGann" OR "Amano Parking") ("Amano ONE" OR ticketless) when:90d',
    "Flowbird": '"Flowbird" (Parking OR "pay-by-plate" OR ticketless OR "open payment") when:90d',
    "WPS Parking": '("WPS Parking" OR "WPS ParkAdvance") (ticketless OR barrier OR cloud) when:90d',
    "IP Parking": '"IP Parking" (ParkBase OR ticketless OR barrier OR cloud) when:90d',
    "ICA Traffic": '("ICA Traffic" OR "ICA Parking") (Kassenautomat OR ticketless OR Schranke) when:90d',
    "Orbility": '"Orbility" (Parking OR ticketless OR barrier OR airport) when:90d',
    "Meypar": '"Meypar" (Parking OR ticketless OR barrier) when:90d',
    "Equinsa": '"Equinsa" (Parking OR aparcamiento OR ticketless) when:90d',

    # --- 2. Free-Flow, ANPR & Retail-Disruptoren ---
    "Peter Park": '"Peter Park" (Parken OR Parking OR ticketless OR "free-flow" OR ANPR OR CityFlow) when:90d',
    "WEMOLO (Parkdepot)": '("WEMOLO" OR "Parkdepot") (Parkplatz OR Parking OR enforcement OR "free-flow") when:90d',
    "fair parken": '"fair parken" (Parkplatz OR schrankenlos OR Kennzeichen OR ANPR) when:90d',
    "ARIVO": '"ARIVO" (Parken OR Parking OR ticketless OR "free-flow" OR ANPR) when:90d',
    "AVANTPARK": '"AVANTPARK" (Parken OR Parking OR ANPR OR schrankenlos) when:90d',
    "Autopay": '("Autopay" OR "Autopay.de") (Parking OR ticketless OR "free-flow" OR ANPR) when:90d',
    "JJames": '"JJames" (Parken OR Parking OR Schranken OR Kennzeichenerkennung) when:90d',
    "DigiPark": '"DigiPark" (Parken OR Kennzeichen OR schrankenlos) when:90d',
    "Smart City System": '("Smart City System" OR "ParkAgent") (Parken OR occupancy OR sensor) when:90d',

    # --- 3. Corporate Parking & Mobility Software ---
    "ParkHere": '"ParkHere" (Parkplatz OR Parken OR Corporate OR Schranke OR IoT) when:90d',
    "ParkEfficient": '"ParkEfficient" (Parkplatz OR Corporate OR Parkraummanagement) when:90d',
    "BeParking (AU)": '("BeParking" OR "Becas") (Parking OR ticketless OR retrofit) when:90d',

    # --- 4. US Tech-Plattformen & CV ---
    "Flash (USA)": '("FlashParking" OR "Flash Parking") (cloud OR EV OR ticketless) when:90d',
    "Metropolis (USA)": '"Metropolis" (Parking OR "drive-through" OR "checkout-free") when:90d',

    # --- 5. Mobility & Payment Aggregatoren ---
    "EasyPark": '"EasyPark" (Parking OR "CameraPark" OR ticketless OR acquisition) when:90d',
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

                # Control Center / Leitstand
                if any(k in title_lower for k in [
                    "control center", "leitstand", "leitwarte", "remote", "intercom", 
                    "voip", "monitoring", "dispatch", "operator", "jms", "command"
                ]):
                    tags.append("Control Center / Leitstand")

                # APIs & Marktplatz / Schnittstellen
                if any(k in title_lower for k in [
                    "api", "webhook", "sdk", "marketplace", "marktplatz", 
                    "schnittstelle", "integrat", "open platform", "ecosystem"
                ]):
                    tags.append("APIs / Marktplatz")

                # Dynamic Pricing
                if any(k in title_lower for k in [
                    "dynamic pricing", "tarifierung", "yield", "flexible tarife", 
                    "surge pricing", "variable rates", "pricing"
                ]):
                    tags.append("Dynamic Pricing")

                # Signage & Displays
                if any(k in title_lower for k in [
                    "signage", "display", "anzeige", "led", "vms", 
                    "wayfinding", "screen", "stelen", "information display"
                ]):
                    tags.append("Signage / Displays")

                # Free-Flow / Ticketless
                if any(k in title_lower for k in [
                    "ticketless", "free-flow", "free flow", "frictionless", 
                    "gateless", "schrankenlos", "anpr", "lpr", "kennzeichen"
                ]):
                    tags.append("Free-Flow / Ticketless")

                # Shared Parking
                if any(k in title_lower for k in [
                    "shared parking", "quartier", "mixed-use", "mehrfachnutzung", "anwohner"
                ]):
                    tags.append("Shared Parking")

                # Enforcement & Validierung
                if any(k in title_lower for k in [
                    "enforcement", "falschparker", "violation", "compliance", "validation"
                ]):
                    tags.append("Enforcement / Überwachung")

                # Kooperationen & Verträge
                if any(k in title_lower for k in [
                    "kooperation", "partner", "partnership", "allianz", "acquisition", "deal", "contract"
                ]):
                    tags.append("Kooperation")

                # Hardware & Kassen
                if any(k in title_lower for k in [
                    "kasse", "automat", "schranke", "barrier", "gate", "kiosk", "terminal", "pay-by-plate", "hardware"
                ]):
                    tags.append("Hardware / POS")

                # EV & Ladeinfrastruktur
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
        # --- 1. Klassische Enterprise-Systemhäuser ---
        {
            "Wettbewerber": "SKIDATA",
            "Segment": "Enterprise Systemhaus",
            "Control Center / Leitstand": "Zentrales Monitoring & Control: Multi-Site-Leitstand, SIP/VoIP-Routing, Video-Streaming, Remote-Kennzeichenprüfung bei ANPR-Fehlern, Schrankenfernöffnung.",
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

        # --- 2. Kamera- & Cloud-Disruptoren ---
        {
            "Wettbewerber": "Peter Park",
            "Segment": "Cloud Disruptor (ANPR)",
            "Control Center / Leitstand": "CityFlow Operations Web-App: Reines SaaS-Dashboard für Belegung & Falschparker; kein klassischer Intercom-/Hardware-Leitstand.",
            "APIs & Ökosystem": "CityFlow API: Native Integration von EasyPark (CameraPark), Parkster, Twint, Whitelabel-Web-Payment.",
            "Dynamic Pricing": "Zonenabhängige Preisanpassung über Cloud-Backend; Fokus auf Retail & Mischquartiere.",
            "Signage & Displays": "Partner-Integration für Begrüßungsanzeigen an der Zufahrt (Kennzeichen-Spiegelung, Hinweise)."
        },
        {
            "Wettbewerber": "Parkdepot",
            "Segment": "Cloud Disruptor (ANPR)",
            "Control Center / Leitstand": "Parkdepot Backoffice: Fokus auf Falschparker-Evidenz und Verwarnungsprozesse; kein Operator-Leitstand für Schranken/Sprechanlagen.",
            "APIs & Ökosystem": "Schnittstellen zu Supermarkt-Filialsystemen und Inkasso; eher geschlossenes Ökosystem.",
            "Dynamic Pricing": "Fokus auf Freiparkdauern und Überschreitungstarife (Vertragsstrafen), kein dynamisches Yield-Management.",
            "Signage & Displays": "Eigene Kamerasäulen mit integrierter Kennzeichen-Visualisierung zur Transparenz für Autofahrer."
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
            "Wettbewerber": "Smart City System",
            "Segment": "Sensor- & ANPR-Disruptor",
            "Control Center / Leitstand": "ParkAgent Platform: Visualisierung von Einzelflächen-Sensorik und ANPR-Kameras, Eskalations-Dashboard für Parkverstöße.",
            "APIs & Ökosystem": "ParkAgent REST-API: Datenweitergabe an städtische Parkleitsysteme, Navigationsdienste und Betreiber.",
            "Dynamic Pricing": "Eher statische Zeitzonenüberwachung (z. B. Kurzzeitparken 2h), keine Yield-Engine.",
            "Signage & Displays": "Kopplung an digitale Hinweisschilder und dynamische Zonenwegweiser."
        },
        {
            "Wettbewerber": "Autopay (Nordics)",
            "Segment": "Skandinavischer Free-Flow Pionier",
            "Control Center / Leitstand": "Autopay Operator Suite: Vollautomatisierter 24/7-Cloud-Betrieb, automatische ANPR-Abgleichung, minimale manuelle Eingriffe.",
            "APIs & Ökosystem": "Umfassende API für nahtloses Auto-Debit (automatische Kreditkartenbelastung), Integration in EV-Ladenetzwerke.",
            "Dynamic Pricing": "Vollständige Differenzierung nach Fahrzeugtyp, Uhrzeit, Mitgliedschaften und Auslastung.",
            "Signage & Displays": "Zulauf-Displays mit Kennzeichen-Check und Hinweisen auf 48-Stunden-Zahlungsfristen im Web."
        },

        # --- 3. US Plattformen ---
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

        # --- 4. Mobility & Payment Aggregatoren ---
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
            * **Klassische Systemhäuser (SKIDATA, Scheidt & Bachmann, HUB):**
              * Bieten echte **24/7-Leitwarten-Architekturen** für Großbetreiber.
              * SIP/VoIP-Intercom-Routing, Video-Zuschaltung, direkte Schrankenfernsteuerung, Kassenstörungs-Handling.
              * Unverzichtbar für Betreiber mit Sicherheitsauflagen (z. B. Flughäfen, Spitäler, städtische Großgaragen).
            * **Reine ANPR-Disruptoren (Peter Park, Parkdepot):**
              * Besitzen **keinen physischen Hardware-Leitstand**, da Schranken und Intercoms entfallen.
              * Das 'Control Center' beschränkt sich auf Belegungsanzeige, ANPR-Nachverifikation bei unleserlichen Schildern und Falschparker-Listen.
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
        * 💡 **PM-Schlussfolgerung:** Verdrängt Schranken und Kassen im Retail- und Kommunalbereich durch geringe Vorab-Investitionen (CapEx).
        """,
        "Parkdepot": """
        * **Modell:** Full-Service-Parkraumüberwachung für den Einzelhandel mit eigener modularer KI-Kamerahardware.
        * **Stärken:** Hohe Standardisierung bei Supermärkten (Rewe, Lidl, Aldi) und automatisierte Fallbearbeitung von Falschparkern.
        * 💡 **PM-Schlussfolgerung:** Im Discounter-Umfeld kaum mit Kassenhardware zu schlagen. Klassische Systeme müssen sich auf Multi-Use-Flächen mit komplexeren Tarifen konzentrieren.
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
        "Autopay (Nordics)": """
        * **Modell:** Vorreiter für schrankenlose Kennzeichenerfassung in Skandinavien; fast 100% Marktdurchdringung in einigen Regionen.
        * 💡 **PM-Schlussfolgerung:** Blaupause dafür, wie schnell schrankenlose Systeme klassische Schranken in technikaffinen Ländern verdrängen können.
        """,
        "Smart City System": """
        * **Modell:** Sensor- und ANPR-basierte Parkraumerfassung mit der Management-Plattform *ParkAgent*.
        * 💡 **PM-Schlussfolgerung:** Bietet schlanke digitale Lösungen zur Überwachung von Mischflächen und Falschparkern.
        """,
        "EasyPark": """
        * **Modell:** Größter Park-App-Aggregator Europas.
        * 💡 **PM-Schlussfolgerung:** Greift über *CameraPark* das Transaktionsgeschäft an: Der Autofahrer nutzt die App statt den Kassenautomaten.
        """,
        "Parkster": """
        * **Modell:** Stark wachsende gebührenfreie Park-App in DACH und Skandinavien.
        * 💡 **PM-Schlussfolgerung:** Wichtiger Partner für schrankenlose Betreiber zur Abwicklung mobiler Zahlungen.
        """,
        "ARIVO": """
        * **Modell:** Österreichischer Anbieter modularer ANPR-Lösungen (mit oder ohne Schranke).
        * 💡 **PM-Schlussfolgerung:** Zeigt, dass auch kleinere Anbieter mit hoher Schnittstellen-Flexibilität und fairen Preisen punkten können.
        """
    }

    st.markdown(dossiers.get(selected_comp, "Kein Dossier hinterlegt."))
