"""
LK20 Curriculum Data - Emnebibliotek og kompetansemål for norsk matematikk.
Basert på Kunnskapsløftet 2020 (LK20).
"""

# Emnebibliotek organisert etter klassetrinn
TOPIC_LIBRARY = {
    "1.-4. trinn": {
        "Tall og tallforståelse": [
            "Tallene 0-100",
            "Tallene 0-1000",
            "Tiervenner",
            "Partall og oddetall",
            "Plassverdisystemet",
        ],
        "Regning": [
            "Addisjon",
            "Subtraksjon",
            "Multiplikasjon (gangetabellen)",
            "Enkel divisjon",
            "Hoderegning",
        ],
        "Brøk": [
            "Halve og hele",
            "Enkle brøker (1/2, 1/4, 1/3)",
        ],
        "Måling": [
            "Lengde (cm, m)",
            "Vekt (gram, kg)",
            "Volum (liter)",
            "Tid og klokka",
            "Penger og kroner",
        ],
        "Geometri": [
            "Geometriske figurer",
            "Symmetri",
            "Mønster og rekkefølge",
        ],
    },
    "5.-7. trinn": {
        "Tall og algebra": [
            "Store tall og desimaltall",
            "Negative tall",
            "Primtall og faktorisering",
            "Potenser",
            "Regning med parenteser",
            "Enkle likninger",
        ],
        "Brøk, desimaltall og prosent": [
            "Brøkregning",
            "Desimaltall",
            "Prosent",
            "Omgjøring mellom brøk, desimal og prosent",
        ],
        "Forhold og proporsjonalitet": [
            "Forholdstall",
            "Skala og målestokk",
        ],
        "Geometri": [
            "Vinkler",
            "Areal av trekanter og firkanter",
            "Omkrets",
            "Volum av prisme",
            "Koordinatsystemet",
        ],
        "Statistikk": [
            "Gjennomsnitt, median og typetall",
            "Diagrammer og tabeller",
        ],
    },
    "8. trinn": {
        "Tall og algebra": [
            "Regning med potenser",
            "Kvadratrot",
            "Bokstavregning",
            "Faktorisering av uttrykk",
            "Likninger med én ukjent",
        ],
        "Brøk, desimaltall og prosent": [
            "Brøkregning alle regnearter",
            "Prosentregning",
            "Promille",
            "Vekstfaktor",
        ],
        "Geometri": [
            "Pytagoras' setning",
            "Areal og omkrets",
            "Volum og overflate",
            "Formlikhet",
        ],
        "Funksjoner": [
            "Koordinatsystemet",
            "Lineære sammenhenger",
            "Tabell, graf og formel",
        ],
        "Statistikk og sannsynlighet": [
            "Sentralmål",
            "Spredningsmål",
            "Enkel sannsynlighetsregning",
        ],
    },
    "9. trinn": {
        "Tall og algebra": [
            "Potenser med negative eksponenter",
            "Standardform",
            "Faktorisering",
            "Likninger og ulikheter",
            "Ligningssett (to ukjente)",
        ],
        "Økonomi": [
            "Renter og lån",
            "Budsjett",
            "Prosentvis endring",
            "Vekstfaktor og eksponentiell vekst",
        ],
        "Geometri": [
            "Pytagoras anvendelser",
            "Areal av sammensatte figurer",
            "Setninger om trekanter",
            "Konstruksjon",
        ],
        "Funksjoner": [
            "Lineære funksjoner",
            "Stigningstall og konstantledd",
            "Skjæringspunkt mellom linjer",
            "Praktiske problemer med funksjoner",
        ],
        "Statistikk og sannsynlighet": [
            "Statistisk analyse",
            "Kombinatorikk",
            "Sannsynlighetsberegning",
        ],
    },
    "10. trinn": {
        "Tall og algebra": [
            "Rasjonale og irrasjonale tall",
            "Potensregler",
            "Faktorisering av andregradsuttrykk",
            "Andregradslikninger",
            "Formler og formelregning",
        ],
        "Funksjoner": [
            "Lineære funksjoner",
            "Andregradsfunksjoner (parabler)",
            "Eksponentialfunksjoner",
            "Praktisk modellering",
        ],
        "Geometri": [
            "Trigonometri i rettvinklede trekanter",
            "Sinus, cosinus og tangens",
            "Målestokk og formlikhet",
            "Volum av kjegle, sylinder, kule",
        ],
        "Sannsynlighet og statistikk": [
            "Sannsynlighetsmodeller",
            "Kombinatorikk",
            "Kritisk vurdering av statistikk",
        ],
        "Eksamensoppgaver": [
            "Del 1 oppgaver (uten hjelpemidler)",
            "Del 2 oppgaver (med hjelpemidler)",
        ],
    },
    "VG1 1T": {
        "Algebra": [
            "Regneregler og parenteser",
            "Potenser og røtter",
            "Rasjonale uttrykk",
            "Faktorisering",
            "Likninger og ulikheter",
            "Formelregning",
        ],
        "Funksjoner": [
            "Lineære funksjoner",
            "Andregradsfunksjoner",
            "Polynomfunksjoner",
            "Rasjonale funksjoner",
            "Eksponentialfunksjoner",
            "Logaritmer",
        ],
        "Geometri": [
            "Trigonometri",
            "Vektorer i planet",
            "Analytisk geometri",
        ],
        "Sannsynlighet": [
            "Kombinatorikk",
            "Sannsynlighetsberegning",
            "Ordnet og uordnet utvalg",
        ],
    },
    "VG1 1P": {
        "Tall og algebra": [
            "Prosentregning",
            "Vekstfaktor",
            "Praktisk bruk av formler",
            "Likninger",
        ],
        "Økonomi": [
            "Budsjett og regnskap",
            "Lån og sparing",
            "Renter og avdrag",
            "Skatteberegning",
        ],
        "Funksjoner": [
            "Lineære modeller",
            "Praktiske funksjoner",
            "Grafisk framstilling",
        ],
        "Geometri": [
            "Måling og beregning",
            "Praktisk trigonometri",
        ],
        "Statistikk": [
            "Dataanalyse",
            "Kritisk vurdering",
            "Presentasjon av data",
        ],
    },
    "VG2 R1": {
        "Algebra": [
            "Polynomdivisjon",
            "Faktorisering av polynomer",
            "Rasjonale uttrykk",
            "Eksponential- og logaritmefunksjoner",
            "Likninger med logaritmer",
        ],
        "Funksjoner": [
            "Polynomfunksjoner",
            "Rasjonale funksjoner",
            "Sammensetning av funksjoner",
            "Kontinuitet",
            "Grenseverdier",
        ],
        "Derivasjon": [
            "Definisjon av derivasjon",
            "Derivasjonsregler",
            "Kjerneregelen",
            "Implisitt derivasjon",
            "Drøfting av funksjoner",
        ],
        "Geometri": [
            "Vektorer i rommet",
            "Skalarprodukt",
            "Parametriske kurver",
        ],
        "Kombinatorikk og sannsynlighet": [
            "Kombinatorikk",
            "Sannsynlighetsmodeller",
            "Binomisk sannsynlighetsmodell",
        ],
    },
    "VG3 R2": {
        "Funksjoner og derivasjon": [
            "Trigonometriske funksjoner",
            "Derivasjon av trigonometriske funksjoner",
            "Logaritme- og eksponentialfunksjoner",
            "Anvendelser av derivasjon",
        ],
        "Integralregning": [
            "Ubestemte integraler",
            "Integrasjonsteknikker",
            "Bestemte integraler",
            "Areal mellom kurver",
            "Volum av omdreiningslegemer",
        ],
        "Differensiallikninger": [
            "Separable differensiallikninger",
            "Lineære differensiallikninger",
            "Modellering",
        ],
        "Rekker": [
            "Aritmetiske rekker",
            "Geometriske rekker",
            "Uendelige rekker",
            "Konvergens",
        ],
    },
}

# LK20 Kompetansemål (utvalgte hovedmål per trinn)
COMPETENCY_GOALS = {
    "8. trinn": [
        "Utforske og beskrive strukturer og forandringer i geometriske mønster",
        "Beskrive og generalisere mønster med bokstaver og andre symboler",
        "Utforske og øve på strategier for regning med brøk, desimaltall og prosent",
        "Utforske sammenhengen mellom brøk, desimaltall og prosent",
        "Lage og programmere algoritmer med bruk av variabler og vilkår",
        "Utforske Pytagoras' setning og bruke den til å beregne lengder",
        "Utforske og argumentere for formler for areal og volum",
        "Samle inn, sortere og vurdere data og presentere med og uten digitale verktøy",
    ],
    "9. trinn": [
        "Behandle og faktorisere algebraiske uttrykk, og bruke dette i likninger og ulikheter",
        "Modellere situasjoner knyttet til reelle datasett og vurdere modellene",
        "Utforske og beskrive ulike representasjoner av funksjoner",
        "Utforske strategier for å løse likninger og likningssett",
        "Lage og bruke budsjett og regnskap med inntekt, utgifter og sparing",
        "Beregne og vurdere renter ved lån og sparing",
        "Bruke formlikhet og trigonometri til å beregne lengder og vinkler",
        "Planlegge, gjennomføre og presentere statistiske undersøkelser",
    ],
    "10. trinn": [
        "Utforske matematiske egenskaper og sammenhenger ved å bruke programmering",
        "Behandle og faktorisere enkle algebraiske uttrykk, og regne med formler",
        "Løse likninger og ulikheter av første og andre grad",
        "Utforske og beskrive egenskaper ved ulike funksjonstyper",
        "Analysere og presentere datasett med relevante statistiske mål",
        "Bruke trigonometri til å beregne lengder og vinkler i praktiske oppgaver",
        "Beregne overflate og volum av sylinder, kjegle og kule",
        "Vurdere og drøfte sannsynligheter ved hjelp av simuleringer",
    ],
    "VG1 1T": [
        "Omforme og forenkle sammensatte uttrykk, løse likninger og ulikheter",
        "Utforske, analysere og drøfte polynomfunksjoner og rasjonale funksjoner",
        "Utforske, forstå og bruke eksponentialfunksjoner og logaritmer",
        "Bruke trigonometri til beregninger og problemløsning",
        "Bruke vektorer til å beskrive bevegelse, beregne lengder og finne vinkler",
        "Kombinatorikk og sannsynlighetsberegning med ordnet og uordnet utvalg",
    ],
    "VG1 1P": [
        "Planlegge, gjennomføre og presentere selvstendig arbeid knyttet til økonomi",
        "Bruke funksjonsbegrepet i praktiske sammenhenger og gjøre rede for lineære modeller",
        "Analysere og presentere et datamateriale og drøfte ulike dataframstillinger",
        "Gjøre rede for og bruke formler i praktiske situasjoner",
        "Bruke trigonometri til beregninger i praktiske sammenhenger",
    ],
    "VG2 R1": [
        "Finne grenseverdier og drøfte kontinuitet til funksjoner",
        "Derivere og drøfte polynomfunksjoner, rasjonale funksjoner og eksponentialfunksjoner",
        "Løse likninger med eksponential- og logaritmefunksjoner analytisk og grafisk",
        "Bruke derivasjon til å løse praktiske optimeringsproblemer",
        "Gjøre rede for vektorer i rommet og regne med skalarproduktet",
        "Gjøre rede for binomisk sannsynlighetsmodell og bruke den til beregninger",
    ],
    "VG3 R2": [
        "Derivere og integrere trigonometriske funksjoner",
        "Bruke ulike teknikker for integrasjon av funksjoner",
        "Beregne areal mellom kurver og volum av omdreiningslegemer",
        "Løse separable og lineære differensiallikninger analytisk",
        "Gjøre rede for uendelige rekker og bestemme konvergens",
        "Modellere praktiske situasjoner med differensiallikninger",
    ],
}

# Oppgavetyper
EXERCISE_TYPES = {
    "standard": {
        "name": "📝 Regneoppgaver",
        "description": "Klassiske oppgaver med beregninger",
        "instruction": "Lag tradisjonelle regneoppgaver med tydelig oppgavetekst og krav om utregning"
    },
    "multiple_choice": {
        "name": "🔘 Flervalg",
        "description": "Oppgaver med svaralternativer A, B, C, D",
        "instruction": "Lag flervalgsoppgaver med 4 svaralternativer (A, B, C, D). Kun ett svar er riktig. Bruk \\begin{enumerate}[label=\\Alph*)] for alternativene"
    },
    "fill_blank": {
        "name": "📋 Utfylling",
        "description": "Fyll inn manglende tall/uttrykk",
        "instruction": "Lag utfyllingsoppgaver der eleven må fylle inn manglende tall eller uttrykk. Bruk \\underline{\\hspace{2cm}} for blanke felt"
    },
    "word_problem": {
        "name": "📖 Tekstoppgaver",
        "description": "Praktiske problemstillinger",
        "instruction": "Lag praktiske tekstoppgaver med hverdagslige situasjoner som krever matematisk modellering"
    },
    "true_false": {
        "name": "✓✗ Sant/Usant",
        "description": "Vurder om påstander er sanne",
        "instruction": "Lag sant/usant-påstander der eleven må avgjøre om matematiske utsagn er korrekte"
    },
    "matching": {
        "name": "🔗 Kobling",
        "description": "Match uttrykk med svar",
        "instruction": "Lag koblingsoppgaver der eleven må matche matematiske uttrykk i venstre kolonne med riktige svar i høyre kolonne"
    },
}


def get_topics_for_grade(grade: str) -> dict:
    """Get topics organized by category for a specific grade level."""
    # Normalize grade name
    grade_key = grade
    for key in TOPIC_LIBRARY.keys():
        if grade.lower() in key.lower() or key.lower() in grade.lower():
            grade_key = key
            break
    
    return TOPIC_LIBRARY.get(grade_key, {})


def get_all_topics_flat(grade: str) -> list:
    """Get a flat list of all topics for a grade."""
    topics = get_topics_for_grade(grade)
    flat_list = []
    for category, topic_list in topics.items():
        flat_list.extend(topic_list)
    return flat_list


def get_competency_goals(grade: str) -> list:
    """Get competency goals for a specific grade level."""
    # Normalize grade name
    grade_key = grade
    for key in COMPETENCY_GOALS.keys():
        if grade.lower() in key.lower() or key.lower() in grade.lower():
            grade_key = key
            break
    
    return COMPETENCY_GOALS.get(grade_key, [])


def get_exercise_types() -> dict:
    """Get all available exercise types."""
    return EXERCISE_TYPES
