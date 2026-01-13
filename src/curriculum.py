"""
LK20 Curriculum Data - Emnebibliotek og kompetansemål for norsk matematikk.
Basert på Kunnskapsløftet 2020 (LK20).
Utvidet med flere emner og kompetansemål.
"""

# Emnebibliotek organisert etter klassetrinn
TOPIC_LIBRARY = {
    "1.-4. trinn": {
        "Tall og tallforståelse": [
            "Tallene 0-100",
            "Tallene 0-1000",
            "Tallene 0-10 000",
            "Tiervenner",
            "Partall og oddetall",
            "Plassverdisystemet (enere, tiere, hundrere)",
            "Tallinja",
            "Sammenligne og ordne tall",
            "Avrunding av tall",
        ],
        "Regning": [
            "Addisjon med tierovergang",
            "Subtraksjon med tierovergang",
            "Multiplikasjon (gangetabellen 1-10)",
            "Enkel divisjon",
            "Divisjon med rest",
            "Hoderegning",
            "Regnerekkefølge",
            "Regnestrategier",
            "Likhetstegnet og likninger",
        ],
        "Brøk": [
            "Halve og hele",
            "Enkle brøker (1/2, 1/4, 1/3)",
            "Brøk som del av en mengde",
            "Sammenligne enkle brøker",
        ],
        "Måling": [
            "Lengde (mm, cm, m, km)",
            "Vekt (gram, kg)",
            "Volum (dl, liter)",
            "Tid og klokka (analog og digital)",
            "Penger og kroner",
            "Temperatur",
            "Omgjøring mellom enheter",
        ],
        "Geometri": [
            "Geometriske figurer (trekant, firkant, sirkel)",
            "Tredimensjonale figurer (kube, kule, sylinder)",
            "Symmetri",
            "Mønster og rekkefølge",
            "Speiling",
            "Retninger (høyre, venstre, opp, ned)",
        ],
        "Statistikk": [
            "Telle og sortere",
            "Enkle tabeller",
            "Søylediagram",
            "Piktogram",
        ],
    },
    "5.-7. trinn": {
        "Tall og algebra": [
            "Store tall og desimaltall",
            "Negative tall",
            "Primtall og sammensatte tall",
            "Faktorisering",
            "Potenser (kvadrattall, kubikktall)",
            "Regning med parenteser",
            "Regnerekkefølge (PEMDAS)",
            "Enkle likninger",
            "Variabler og uttrykk",
            "Tallmønster og figurtall",
        ],
        "Brøk, desimaltall og prosent": [
            "Brøkregning (addisjon og subtraksjon)",
            "Brøkregning (multiplikasjon)",
            "Desimaltall",
            "Prosent",
            "Omgjøring mellom brøk, desimal og prosent",
            "Finne prosenten av et tall",
            "Sammenligne brøker med ulik nevner",
        ],
        "Forhold og proporsjonalitet": [
            "Forholdstall",
            "Skala og målestokk",
            "Proporsjonale størrelser",
            "Pris per enhet",
        ],
        "Geometri": [
            "Vinkler (spisse, rette, stumpe)",
            "Vinkelmåling med gradskive",
            "Areal av trekanter",
            "Areal av firkanter",
            "Areal av sammensatte figurer",
            "Omkrets",
            "Volum av prisme",
            "Volum av terning",
            "Koordinatsystemet",
            "Konstruksjon med passer og linjal",
            "Formlikhet",
        ],
        "Statistikk og sannsynlighet": [
            "Gjennomsnitt",
            "Median",
            "Typetall",
            "Variasjonsbredde",
            "Diagrammer (søyle, linje, sektor)",
            "Tabeller og frekvens",
            "Enkel sannsynlighet",
            "Kombinatorikk (telle muligheter)",
        ],
    },
    "8. trinn": {
        "Tall og algebra": [
            "Regning med potenser",
            "Potensregler",
            "Kvadratrot",
            "Bokstavregning",
            "Forenkling av uttrykk",
            "Faktorisering av uttrykk",
            "Likninger med én ukjent",
            "Ulikheter",
            "Formler og formelregning",
        ],
        "Brøk, desimaltall og prosent": [
            "Brøkregning alle regnearter",
            "Prosentregning",
            "Promille",
            "Vekstfaktor",
            "Prosentvis økning og reduksjon",
            "Rabatt og påslag",
        ],
        "Geometri": [
            "Pytagoras' setning",
            "Pytagoras' setning - anvendelser",
            "Areal og omkrets av sirkler",
            "Areal og omkrets av sammensatte figurer",
            "Volum av prismer og sylindre",
            "Overflate av prismer",
            "Formlikhet og kongruens",
            "Målestokk",
        ],
        "Funksjoner": [
            "Koordinatsystemet",
            "Lineære sammenhenger",
            "Tabell, graf og formel",
            "Proporsjonale og omvendt proporsjonale størrelser",
            "Praktiske funksjoner",
        ],
        "Statistikk og sannsynlighet": [
            "Sentralmål (gjennomsnitt, median, typetall)",
            "Spredningsmål (variasjonsbredde)",
            "Enkel sannsynlighetsregning",
            "Relativ frekvens",
            "Presentasjon av data",
        ],
    },
    "9. trinn": {
        "Tall og algebra": [
            "Potenser med negative eksponenter",
            "Standardform (vitenskapelig notasjon)",
            "Faktorisering av algebraiske uttrykk",
            "Likninger og ulikheter",
            "Ligningssett (to ukjente)",
            "Grafisk løsning av likningssett",
            "Innsettingsmetoden",
            "Addisjonsmetoden",
        ],
        "Økonomi": [
            "Renter og lån",
            "Rentesrente",
            "Budsjett og regnskap",
            "Prosentvis endring",
            "Vekstfaktor og eksponentiell vekst",
            "Nedbetaling av lån",
            "Sparing",
        ],
        "Geometri": [
            "Pytagoras anvendelser i praktiske oppgaver",
            "Areal av sammensatte figurer",
            "Setninger om trekanter",
            "Konstruksjon med passer og linjal",
            "Geometriske steder",
            "Innskrevne og omskrevne sirkler",
        ],
        "Funksjoner": [
            "Lineære funksjoner",
            "Stigningstall og konstantledd",
            "Skjæringspunkt mellom linjer",
            "Praktiske problemer med funksjoner",
            "Tolkning av grafer",
            "Lineær regresjon",
        ],
        "Statistikk og sannsynlighet": [
            "Statistisk analyse",
            "Kombinatorikk",
            "Sannsynlighetsberegning",
            "Valgtre",
            "Betinget sannsynlighet",
        ],
    },
    "10. trinn": {
        "Tall og algebra": [
            "Rasjonale og irrasjonale tall",
            "Potensregler",
            "Faktorisering av andregradsuttrykk",
            "Konjugatsetningen",
            "Kvadratsetningene",
            "Andregradslikninger",
            "Abc-formelen (løsningsformelen)",
            "Formler og formelregning",
        ],
        "Funksjoner": [
            "Lineære funksjoner - repetisjon",
            "Andregradsfunksjoner (parabler)",
            "Toppunkt og bunnpunkt",
            "Nullpunkter til andregradsfunksjoner",
            "Eksponentialfunksjoner",
            "Praktisk modellering",
            "Regresjon",
        ],
        "Geometri": [
            "Trigonometri i rettvinklede trekanter",
            "Sinus, cosinus og tangens",
            "Finne ukjente sider",
            "Finne ukjente vinkler",
            "Målestokk og formlikhet",
            "Volum av kjegle",
            "Volum av sylinder",
            "Volum av kule",
            "Overflate av sylinder og kule",
        ],
        "Sannsynlighet og statistikk": [
            "Sannsynlighetsmodeller",
            "Kombinatorikk",
            "Ordnet og uordnet utvalg",
            "Kritisk vurdering av statistikk",
            "Histogram og boksplott",
        ],
        "Eksamensoppgaver": [
            "Del 1 oppgaver (uten hjelpemidler)",
            "Del 2 oppgaver (med hjelpemidler)",
            "Problemløsningsoppgaver",
            "Modelleringsoppgaver",
        ],
    },
    "VG1 1T": {
        "Algebra": [
            "Regneregler og parenteser",
            "Potenser og røtter",
            "Rasjonale uttrykk",
            "Brøkregning med variabler",
            "Faktorisering",
            "Likninger og ulikheter",
            "Formelregning",
            "Andregradslikninger",
            "Faktorisering av andregradsuttrykk",
        ],
        "Funksjoner": [
            "Lineære funksjoner",
            "Andregradsfunksjoner",
            "Polynomfunksjoner",
            "Rasjonale funksjoner",
            "Eksponentialfunksjoner",
            "Logaritmer",
            "Logaritmeregler",
            "Eksponentiallikninger",
        ],
        "Geometri": [
            "Trigonometri (sinus, cosinus, tangens)",
            "Sinussetningen",
            "Cosinussetningen",
            "Arealsetningen",
            "Vektorer i planet",
            "Vektorregning",
            "Skalarprodukt",
            "Analytisk geometri",
        ],
        "Sannsynlighet": [
            "Kombinatorikk",
            "Permutasjoner",
            "Kombinasjoner",
            "Sannsynlighetsberegning",
            "Ordnet og uordnet utvalg",
            "Med og uten tilbakelegging",
        ],
    },
    "VG1 1P": {
        "Tall og algebra": [
            "Prosentregning",
            "Vekstfaktor",
            "Praktisk bruk av formler",
            "Likninger",
            "Formelregning",
        ],
        "Økonomi": [
            "Budsjett og regnskap",
            "Lån og sparing",
            "Renter og avdrag",
            "Annuitetslån og serielån",
            "Skatteberegning",
            "Personlig økonomi",
            "Valuta",
        ],
        "Funksjoner": [
            "Lineære modeller",
            "Praktiske funksjoner",
            "Grafisk framstilling",
            "Tolkning av grafer",
            "Regresjon med digitale verktøy",
        ],
        "Geometri": [
            "Måling og beregning",
            "Praktisk trigonometri",
            "Areal og volum",
            "Målestokk",
        ],
        "Statistikk": [
            "Dataanalyse",
            "Sentralmål og spredningsmål",
            "Kritisk vurdering",
            "Presentasjon av data",
            "Utvalg og populasjon",
        ],
    },
    "VG2 R1": {
        "Algebra": [
            "Polynomdivisjon",
            "Faktorisering av polynomer",
            "Nullpunkter til polynomer",
            "Rasjonale uttrykk",
            "Eksponential- og logaritmefunksjoner",
            "Likninger med logaritmer",
            "Eksponentiallikninger",
        ],
        "Funksjoner": [
            "Polynomfunksjoner og egenskaper",
            "Rasjonale funksjoner og asympttoter",
            "Sammensetning av funksjoner",
            "Kontinuitet",
            "Grenseverdier",
            "Definisjon av grenseverdi",
        ],
        "Derivasjon": [
            "Definisjon av derivasjon",
            "Derivasjon fra definisjonen",
            "Derivasjonsregler",
            "Produktregelen",
            "Kvotientregelen",
            "Kjerneregelen",
            "Implisitt derivasjon",
            "Drøfting av funksjoner",
            "Ekstremalpunkter",
            "Vendepunkter",
            "Optimering",
        ],
        "Geometri": [
            "Vektorer i rommet",
            "Skalarprodukt i rommet",
            "Vektorprodukt",
            "Parametriske kurver",
            "Linjer i rommet",
            "Planet i rommet",
        ],
        "Kombinatorikk og sannsynlighet": [
            "Kombinatorikk - repetisjon",
            "Sannsynlighetsmodeller",
            "Binomisk sannsynlighetsmodell",
            "Binomialfordelingen",
            "Forventningsverdi og standardavvik",
        ],
    },
    "VG3 R2": {
        "Funksjoner og derivasjon": [
            "Trigonometriske funksjoner",
            "Derivasjon av trigonometriske funksjoner",
            "Logaritme- og eksponentialfunksjoner",
            "Derivasjon av ln og e^x",
            "Anvendelser av derivasjon",
            "Relaterte rater",
            "Linearisering",
        ],
        "Integralregning": [
            "Ubestemte integraler",
            "Integrasjonsregler",
            "Integrasjon ved substitusjon",
            "Delvis integrasjon",
            "Integrasjon av rasjonale funksjoner",
            "Bestemte integraler",
            "Areal under kurver",
            "Areal mellom kurver",
            "Volum av omdreiningslegemer",
        ],
        "Differensiallikninger": [
            "Separable differensiallikninger",
            "Lineære førsteordens differensiallikninger",
            "Lineære andreordens differensiallikninger",
            "Modellering med differensiallikninger",
            "Vekstmodeller",
        ],
        "Rekker": [
            "Aritmetiske rekker",
            "Geometriske rekker",
            "Uendelige geometriske rekker",
            "Konvergens og divergens",
            "Teleskoprekker",
            "Taylorrekker (introduksjon)",
        ],
    },
}

# LK20 Kompetansemål (utvidet med flere trinn)
COMPETENCY_GOALS = {
    "1.-4. trinn": [
        "Telle til 100, dele opp og bygge mengder opp til 10, sette sammen og dele opp tiergrupper",
        "Utvikle, bruke og samtale om varierte regnestrategier for addisjon og subtraksjon",
        "Utforske og beskrive strukturer og mønster i lek og spill",
        "Bruke ulike måleenheter for lengde og masse i praktiske situasjoner",
        "Utforske, lage og beskrive geometriske mønster med og uten digitale verktøy",
        "Samle, sortere og forklare data og lage enkle fremstillinger",
    ],
    "5.-7. trinn": [
        "Utforske og beskrive primtall, faktorisering og bruke det til å finne fellesnevner",
        "Sammenligne, ordne og regne med negative tall",
        "Beskrive plassering og forflytning i et koordinatsystem",
        "Utforske og bruke strategier for regning med desimaltall, brøk og prosent",
        "Utforske og argumentere for formler for omkrets, areal og volum",
        "Samle inn, sortere, presentere og lese av data og vurdere om fremstillingene er hensiktsmessige",
    ],
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
        "instruction": "Lag tradisjonelle regneoppgaver med tydelig oppgavetekst og krav om utregning. Vis mellomregninger i løsningsforslaget."
    },
    "multiple_choice": {
        "name": "🔘 Flervalg",
        "description": "Oppgaver med svaralternativer A, B, C, D",
        "instruction": "Lag flervalgsoppgaver med 4 svaralternativer (A, B, C, D). Kun ett svar er riktig. Bruk \\begin{enumerate}[label=\\Alph*)] for alternativene. Inkluder distraktorer som tester vanlige feil."
    },
    "fill_blank": {
        "name": "📋 Utfylling",
        "description": "Fyll inn manglende tall/uttrykk",
        "instruction": "Lag utfyllingsoppgaver der eleven må fylle inn manglende tall eller uttrykk. Bruk \\underline{\\hspace{2cm}} for blanke felt. Oppgavene skal teste forståelse av konsepter."
    },
    "word_problem": {
        "name": "📖 Tekstoppgaver",
        "description": "Praktiske problemstillinger",
        "instruction": "Lag praktiske tekstoppgaver med hverdagslige situasjoner som krever matematisk modellering. Bruk norske navn og realistiske tall. Oppgavene skal kreve at eleven setter opp og løser likninger eller beregninger."
    },
    "true_false": {
        "name": "✓✗ Sant/Usant",
        "description": "Vurder om påstander er sanne",
        "instruction": "Lag sant/usant-påstander der eleven må avgjøre om matematiske utsagn er korrekte. Inkluder både sanne og usanne påstander. Krever begrunnelse i løsningsforslaget."
    },
    "matching": {
        "name": "🔗 Kobling",
        "description": "Match uttrykk med svar",
        "instruction": "Lag koblingsoppgaver der eleven må matche matematiske uttrykk i venstre kolonne med riktige svar i høyre kolonne. Bruk tabeller for oversiktlig layout."
    },
    "proof": {
        "name": "📐 Bevisoppgaver",
        "description": "Matematiske bevis og resonnementer",
        "instruction": "Lag oppgaver der eleven må bevise matematiske sammenhenger eller resonnere seg frem til løsningen. Krev tydelig argumentasjon og logisk oppbygging."
    },
    "graphical": {
        "name": "📊 Grafiske oppgaver",
        "description": "Tegne, lese av eller tolke grafer",
        "instruction": "Lag oppgaver som involverer grafer og figurer. Eleven kan bli bedt om å tegne grafer, lese av verdier, eller tolke grafiske fremstillinger. Inkluder koordinatsystem eller figur i oppgaven."
    },
    "open_ended": {
        "name": "💭 Åpne oppgaver",
        "description": "Utforskende oppgaver med flere løsninger",
        "instruction": "Lag åpne oppgaver der eleven kan utforske og finne flere mulige løsninger. Oppgavene skal stimulere til matematisk tenkning og kreativitet."
    },
}

# Tidsestimater for ulike materialtyper (minutter)
TIME_ESTIMATES = {
    "arbeidsark": {
        "base": 15,
        "per_exercise": 3,
        "theory_multiplier": 1.0,
        "examples_multiplier": 1.2,
    },
    "kapittel": {
        "base": 45,
        "per_exercise": 5,
        "theory_multiplier": 1.5,
        "examples_multiplier": 1.3,
    },
    "prøve": {
        "base": 20,
        "per_exercise": 4,
        "theory_multiplier": 1.0,
        "examples_multiplier": 1.0,
    },
    "lekseark": {
        "base": 10,
        "per_exercise": 2,
        "theory_multiplier": 1.0,
        "examples_multiplier": 1.1,
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


def estimate_generation_time(
    material_type: str,
    num_exercises: int = 10,
    include_theory: bool = True,
    include_examples: bool = True,
    include_graphs: bool = True
) -> tuple[int, int]:
    """
    Estimate generation time in minutes.
    
    Args:
        material_type: Type of material (arbeidsark, kapittel, etc.)
        num_exercises: Number of exercises to generate.
        include_theory: Whether theory is included.
        include_examples: Whether examples are included.
        include_graphs: Whether graphs are included.
    
    Returns:
        Tuple of (min_minutes, max_minutes).
    """
    estimates = TIME_ESTIMATES.get(material_type, TIME_ESTIMATES["arbeidsark"])
    
    base = estimates["base"]
    exercise_time = estimates["per_exercise"] * num_exercises
    
    total = base + exercise_time
    
    if include_theory:
        total *= estimates["theory_multiplier"]
    if include_examples:
        total *= estimates["examples_multiplier"]
    if include_graphs:
        total *= 1.2  # Graphs add complexity
    
    # Add some variance
    min_time = int(total * 0.7)
    max_time = int(total * 1.3)
    
    return (max(2, min_time), max(3, max_time))


def search_topics(query: str, grade: str = None) -> list[dict]:
    """
    Search for topics matching a query.
    
    Args:
        query: Search query string.
        grade: Optional grade to filter by.
    
    Returns:
        List of matching topics with their grade and category.
    """
    results = []
    query_lower = query.lower()
    
    grades_to_search = [grade] if grade else TOPIC_LIBRARY.keys()
    
    for g in grades_to_search:
        if g not in TOPIC_LIBRARY:
            continue
        
        for category, topics in TOPIC_LIBRARY[g].items():
            for topic in topics:
                if query_lower in topic.lower() or query_lower in category.lower():
                    results.append({
                        "topic": topic,
                        "category": category,
                        "grade": g,
                    })
    
    return results


def get_related_topics(topic: str, grade: str) -> list[str]:
    """
    Get topics related to the given topic within the same grade.
    
    Args:
        topic: The topic to find related topics for.
        grade: The grade level.
    
    Returns:
        List of related topic names.
    """
    topics_by_category = get_topics_for_grade(grade)
    
    # Find which category the topic belongs to
    topic_category = None
    for category, topics in topics_by_category.items():
        if topic in topics:
            topic_category = category
            break
    
    if not topic_category:
        return []
    
    # Return other topics in the same category
    return [t for t in topics_by_category[topic_category] if t != topic]
