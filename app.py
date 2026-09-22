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

# --- Datenquellen: Vollständiges Wettbewerber-Set inkl. LinkedIn-Suche ---
COMPETITORS = {
    # 1. Klassische Systemhäuser (News + LinkedIn Posts)
    "SKIDATA": '"SKIDATA" (site:linkedin.com/posts OR site:linkedin.com/company OR Parkhaus OR Connect)',
    "Scheidt & Bachmann": '"Scheidt & Bachmann" (site:linkedin.com/posts OR site:linkedin.com/company OR entervo OR mobility)',
    "HUB Parking (FAAC)": '("HUB Parking" OR "FAAC") (site:linkedin.com/posts OR site:linkedin.com/company OR JMS)',
    "Amano McGann": '"Amano McGann" (site:linkedin.com/posts OR site:linkedin.com/company OR Parking)',
    "Flowbird": '"Flowbird" (site:linkedin.com/posts OR site:linkedin.com/company OR Parking)',

    # 2. Kamera & Cloud Disruptoren
    "Peter Park": '"Peter Park" (site:linkedin.com/posts OR site:linkedin.com/company OR Parken OR CityFlow)',
    "Parkdepot": '"Parkdepot" (site:linkedin.com/posts OR site:linkedin.com/company OR Parkplatz)',
    "ARIVO": '"ARIVO" (site:linkedin.com/posts OR site:linkedin.com/company OR Parken)',
    "Smart City System": '("Smart City System" OR "ParkAgent") (site:linkedin.com/posts OR site:linkedin.com/company)',
    "Autopay (Nordics)": '"Autopay" (site:linkedin.com/posts OR site:linkedin.com/company OR Parking)',

    # 3. US Plattformen & Computer Vision
    "Flash (USA)": '("FlashParking" OR "Flash") (site:linkedin.com/posts OR site:linkedin.com/company OR Parking)',
    "Metropolis (USA)": '"Metropolis" (site:linkedin.com/posts OR site:linkedin.com/company OR Parking)',

    # 4. Mobility & Payment
    "EasyPark": '"EasyPark" (site:linkedin.com/posts OR site:linkedin.com/company OR CameraPark)',
    "Parkster": '"Parkster" (site:linkedin.com/posts OR site:linkedin.com/company OR Parken)'
}

# --- Cache-gestützte Datenabfrage mit Browser-Header ---
@st.cache_data(ttl=1800)
def fetch_live_news():
    news_items = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    for comp, query in COMPETITORS.items():
        encoded = urllib.parse.quote(query)
        rss_url = f"https://news.google.com/rss/search?q={encoded}&hl=de&gl=DE&ceid=DE:de"
        feed = feedparser.parse(rss_url, request_headers=headers)

        for entry in feed.entries[:5]:
            title = entry.title
            title_lower = title.lower()

            tags = []
            if "linkedin.com" in entry.link or "linkedin" in title_lower:
                tags.append("LinkedIn")

            if any(k in title_lower for k in ["kooperation", "partner", "allianz", "schließt sich", "vertrag"]):
                tags.append("Kooperation")
            if any(k in title_lower for k in ["kamera", "anpr", "schrankenlos", "free-flow", "kennzeichen"]):
                tags.append("Camera / ANPR")
            if any(k in title_lower for k in ["cloud", "software", "app", "plattform", "api", "jms", "connect"]):
                tags.append("Cloud / Software")
            if any(k in title_lower for k in ["ladesäule", "ev", "charging", "strom", "energie"]):
                tags.append("EV / Energie")
            if any(k in title_lower for k in ["kasse", "automat", "schranke", "terminal", "hardware"]):
                tags.append("Hardware")
            if not tags:
                tags.append("Markt / Allgemein")

            news_items.append({
                "competitor": comp,
                "title": title,
                "link": entry.link,
                "published": entry.get("published", ""),
                "tags": tags
            })

    return news_items

# --- Navigation Tabs ---
tab1, tab2, tab3 = st.tabs(["📡 Live-Radar", "📊 Feature-Matrix (Global)", "📁 PM-Dossiers & Strategie"])

# ==========================================
# TAB 1: LIVE-RADAR
# ==========================================
with tab1:
    st.subheader("Aktuelle Marktbewegungen & LinkedIn-Funde")

    col_btn, col_f1 = st.columns([1, 4])
    with col_btn:
        if st.button("🔄 Feeds jetzt neu laden"):
            st.cache_data.clear()
            st.rerun()
    with col_f1:
        comp_filter = st.selectbox("Wettbewerber filtern", ["Alle"] + list(COMPETITORS.keys()))

    with st.spinner("Lade weltweite Marktdaten..."):
        all_news = fetch_live_news()

    filtered_news = all_news if comp_filter == "Alle" else [n for n in all_news if n["competitor"] == comp_filter]

    if not filtered_news:
        st.info("Keine aktuellen Meldungen für diesen Filter gefunden.")
    else:
        for item in filtered_news:
            with st.container():
                st.markdown(f"#### [{item['competitor']}] {item['title']}")
                tag_str = " ".join([f"`{t}`" for t in item['tags']])
                st.caption(f"Tags: {tag_str} | Datum: {item['published']}")
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
