import streamlit as st
import feedparser
import urllib.parse

# --- Seitenkonfiguration ---
st.set_page_config(
    page_title="Global Parking Competitor Hub | PM",
    page_icon="🚗",
    layout="wide"
)

st.title("🚗 Global Parking Competitor Hub")
st.caption("Echtzeit-Marktüberblick, Technologie-Trends & PM-Dossiers für die Parkraum- und Mobilitätsbranche")

# --- Datenquellen: Vollständiges PM-Fachvokabular (DE + EN) ---
COMPETITORS = {
    # 1. Klassische globale Systemhäuser
    "SKIDATA": '"SKIDATA" (Parking OR ticketless OR "free-flow" OR Connect OR barrier OR airport) when:90d',
    "Scheidt & Bachmann": '"Scheidt & Bachmann" (Parking OR entervo OR "mobility CONNECT" OR ticketless OR gateless) when:90d',
    "HUB Parking (FAAC)": '("HUB Parking" OR "FAAC Parking") (JMS OR ticketless OR "free flow" OR barrier) when:90d',
    "Amano McGann": '("Amano McGann" OR "Amano Parking") ("Amano ONE" OR ticketless OR gateless) when:90d',
    "Flowbird": '"Flowbird" (Parking OR "pay-by-plate" OR ticketless OR "open payment" OR enforcement) when:90d',

    # 2. Kamera- & Cloud-Disruptoren
    "Peter Park": '"Peter Park" (Parken OR Parking OR ticketless OR "free-flow" OR ANPR OR CityFlow OR enforcement) when:90d',
    "Parkdepot": '"Parkdepot" (Parkplatz OR Parking OR enforcement OR "free-flow" OR camera OR Kamera) when:90d',
    "ARIVO": '"ARIVO" (Parken OR Parking OR ticketless OR "free-flow" OR ANPR OR Schrankenlos) when:90d',
    "Smart City System": '("Smart City System" OR "ParkAgent") (Parken OR occupancy OR sensor OR ANPR) when:90d',
    "Autopay (Nordics)": '"Autopay" (Parking OR ticketless OR "free-flow" OR ANPR OR frictionless) when:90d',

    # 3. US / Globale Plattformen
    "Flash (USA)": '("FlashParking" OR "Flash Parking") (cloud OR EV OR "dynamic pricing" OR ticketless) when:90d',
    "Metropolis (USA)": '"Metropolis" (Parking OR "drive-through" OR "checkout-free" OR "computer vision") when:90d',

    # 4. Mobility & Payment Aggregatoren
    "EasyPark": '"EasyPark" (Parking OR "CameraPark" OR ticketless OR acquisition OR partnership) when:90d',
    "Parkster": '"Parkster" (Parking OR Parken OR ticketless OR partnership) when:90d'
}

import email.utils
from datetime import datetime

# --- Cache-gestützte Datenabfrage mit echtem Datums-Parsing ---
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

                # Detailliertes PM-Tagging
                tags = []
                if "linkedin.com" in link or "linkedin" in title_lower:
                    tags.append("LinkedIn")

                if any(k in title_lower for k in ["ticketless", "free-flow", "free flow", "frictionless", "gateless", "schrankenlos", "anpr", "lpr", "kennzeichen"]):
                    tags.append("Free-Flow / Ticketless")

                if any(k in title_lower for k in ["cloud", "software", "app", "platform", "plattform", "api", "dynamic pricing"]):
                    tags.append("Cloud / Software")

                if any(k in title_lower for k in ["enforcement", "falschparker", "violation", "compliance", "validation"]):
                    tags.append("Enforcement / Überwachung")

                if any(k in title_lower for k in ["kooperation", "partner", "partnership", "allianz", "acquisition", "deal", "contract"]):
                    tags.append("Kooperation")

                if any(k in title_lower for k in ["kasse", "automat", "schranke", "barrier", "gate", "kiosk", "terminal", "pay-by-plate", "hardware"]):
                    tags.append("Hardware / POS")

                if any(k in title_lower for k in ["ev", "charging", "ladesäule", "strom", "energy"]):
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
    
# --- Navigation Tabs ---
tab1, tab2, tab3 = st.tabs(["📡 Live-Radar", "📊 Feature-Matrix (Global)", "📁 PM-Dossiers & Strategie"])

# ==========================================
# TAB 1: LIVE-RADAR (MIT FILTERN & SORTIERUNG)
# ==========================================
with tab1:
    st.subheader("Aktuelle Marktbewegungen & LinkedIn-Funde")

    # Alle vorhandenen Tags dynamisch sammeln für das Dropdown
    all_tags = [
        "Alle",
        "Free-Flow / Ticketless",
        "Cloud / Software",
        "Kooperation",
        "Hardware / POS",
        "Enforcement / Überwachung",
        "EV / Energie",
        "LinkedIn"
    ]

    # Filter-Leiste
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

    # Freitext-Suche
    search_query = st.text_input("🔍 Suchbegriff im Titel eingeben (optional):", "").lower().strip()

    with st.spinner("Lade Marktdaten..."):
        all_news = fetch_live_news()

    # 1. Filter anwenden
    filtered_news = []
    for item in all_news:
        if comp_filter != "Alle" and item["competitor"] != comp_filter:
            continue
        if tag_filter != "Alle" and tag_filter not in item["tags"]:
            continue
        if search_query and search_query not in item["title"].lower():
            continue
        filtered_news.append(item)

    # 2. Sortierung nach echtem Datum
    reverse_sort = True if sort_order == "Neueste zuerst" else False
    filtered_news = sorted(filtered_news, key=lambda x: x["dt"], reverse=reverse_sort)

    st.markdown(f"**Gefundene Treffer:** `{len(filtered_news)}`")
    st.divider()

    # Ausgabe der Meldungen
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
# TAB 2: FEATURE-MATRIX
# ==========================================
with tab2:
    st.subheader("Markt-Segmentierung: Systemhäuser vs. Cloud- & Mobility-Player")

    matrix_data = [
        {
            "Wettbewerber": "SKIDATA",
            "Segment": "Klassisches Systemhaus (Global)",
            "Schrankenlos (ANPR)": "Hybrid via SKIDATA Connect",
            "Architektur": "Hybrid / Enterprise Cloud",
            "Hardware-Fokus": "High-End Schranken, Kassen, Säulen",
            "Kern-Zielgruppe": "Flughäfen, Shopping-Center, Großbetreiber"
        },
        {
            "Wettbewerber": "Scheidt & Bachmann",
            "Segment": "Klassisches Systemhaus (Global)",
            "Schrankenlos (ANPR)": "Hybrid via mobility CONNECT",
            "Architektur": "Hybrid / entervo Cloud Services",
            "Hardware-Fokus": "Kassenautomaten, Gates, Bezahlsäulen",
            "Kern-Zielgruppe": "Städte, Großgaragen, Bahnen, Mobility-Hubs"
        },
        {
            "Wettbewerber": "HUB Parking (FAAC)",
            "Segment": "Klassisches Systemhaus (Global)",
            "Schrankenlos (ANPR)": "Hybrid via JMS (Janus Management)",
            "Architektur": "JMS Cloud / On-Premise",
            "Hardware-Fokus": "Jupiter-Serie, Barcode/Ticket-Kassen",
            "Kern-Zielgruppe": "Kommunen, Krankenhäuser, Universitäten"
        },
        {
            "Wettbewerber": "Amano McGann",
            "Segment": "Klassisches Systemhaus (US/Asien)",
            "Schrankenlos (ANPR)": "Hybrid / Ticketless Optionen",
            "Architektur": "Amano ONE (Cloud Platform)",
            "Hardware-Fokus": "Robuste Terminals, Schranken, Kassen",
            "Kern-Zielgruppe": "Nordamerika & Asien, Großgaragen"
        },
        {
            "Wettbewerber": "Flowbird",
            "Segment": "On-Street & Off-Street Mix",
            "Schrankenlos (ANPR)": "Ja / Kombiniert mit Parkscheinautomaten",
            "Architektur": "Flowbird Hub / Open Payment",
            "Hardware-Fokus": "Solar-Parkscheinautomaten, Terminals",
            "Kern-Zielgruppe": "Kommunaler Straßenraum, P&R-Flächen"
        },
        {
            "Wettbewerber": "Peter Park",
            "Segment": "Camera-Only / SaaS Disruptor",
            "Schrankenlos (ANPR)": "100% Core Focus (CityFlow)",
            "Architektur": "Rein Cloud-native SaaS",
            "Hardware-Fokus": "Keine Schranken/Kassen (Partner-Kameras)",
            "Kern-Zielgruppe": "Einzelhandel, Kommunen, Parkplatzbetreiber"
        },
        {
            "Wettbewerber": "Parkdepot",
            "Segment": "Camera-Only / Full-Service",
            "Schrankenlos (ANPR)": "100% Core Focus",
            "Architektur": "Cloud-native + Eigene KI-Kameras",
            "Hardware-Fokus": "Eigene Kamerasäulen (keine Kassen)",
            "Kern-Zielgruppe": "Supermärkte, Kundenparkplätze, Retail"
        },
        {
            "Wettbewerber": "Autopay",
            "Segment": "Skandinavischer Free-Flow Pionier",
            "Schrankenlos (ANPR)": "100% Core Focus",
            "Architektur": "Cloud-basiertes ANPR-Netzwerk",
            "Hardware-Fokus": "Reine ANPR-Portallösungen",
            "Kern-Zielgruppe": "Nordeuropa, Shopping-Center, Flughäfen"
        },
        {
            "Wettbewerber": "Flash (USA)",
            "Segment": "US Cloud-OS & EV",
            "Schrankenlos (ANPR)": "Ja / Hybrid",
            "Architektur": "Cloud-native Operating System",
            "Hardware-Fokus": "Schlanke Kioske + EV-Ladeintegration",
            "Kern-Zielgruppe": "US-Großbetreiber, Commercial Real Estate"
        },
        {
            "Wettbewerber": "Metropolis (USA)",
            "Segment": "Computer-Vision Plattform",
            "Schrankenlos (ANPR)": "100% Drive-in / Drive-out",
            "Architektur": "Proprietäre Computer Vision",
            "Hardware-Fokus": "Eliminiert (reines Checkout-Free)",
            "Kern-Zielgruppe": "Off-Street Parkhäuser (ex SP+ Netz)"
        },
        {
            "Wettbewerber": "EasyPark / Parkster",
            "Segment": "Mobility- & Payment-Aggregator",
            "Schrankenlos (ANPR)": "Integration in Schrankenlos-Partner",
            "Architektur": "Endkunden-App + Betreiber-Schnittstellen",
            "Hardware-Fokus": "Reine Software / Apps",
            "Kern-Zielgruppe": "Endverbraucher, Städte, Flotten"
        }
    ]
    st.dataframe(matrix_data, use_container_width=True)

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
        * **Treiber:** Wachstumskapital (Great Hill Partners), schnelle Expansion in DACH und UK.
        * **Ökosystem:** Tief verknüpft mit App-Bezahldiensten (EasyPark CameraPark, Parkster).
        * 💡 **PM-Schlussfolgerung:** Verdrängt Schranken und Kassen im Retail- und Kommunalbereich durch geringe Vorab-Investitionen (CapEx).
        """,
        "Parkdepot": """
        * **Modell:** Full-Service-Parkraumüberwachung für den Einzelhandel mit eigener modularer KI-Kamerahardware.
        * **Stärken:** Hohe Standardisierung bei Supermärkten (Rewe, Lidl, Aldi) und automatisierte Fallbearbeitung von Falschparkern.
        * 💡 **PM-Schlussfolgerung:** Im reinen Discounter- und Filialumfeld kaum mit Kassenhardware zu schlagen. Klassische Systeme müssen sich auf Multi-Use-Flächen mit komplexeren Tarifen konzentrieren.
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
