"""
MathBookAgents - CrewAI agents for the AI Editorial Team.
Defines specialized agents for creating math worksheets and chapters.
Enhanced with improved prompts for higher quality output.
"""

import os
from crewai import Agent, LLM
from src.curriculum import format_boundaries_for_prompt, get_grade_boundaries


# Language level configurations for simplified Norwegian
LANGUAGE_LEVELS = {
    "standard": {
        "name": "Standard norsk",
        "code": "C1-C2",
        "description": "Vanlig akademisk norsk",
        "instructions": "",  # No special instructions for standard
    },
    "b2": {
        "name": "Forenklet norsk (B2)",
        "code": "B2",
        "description": "For elever med norsk som andrespråk - øvre mellomnivå",
        "instructions": """
=== SPRÅKNIVÅ: B2 (Øvre mellomnivå) ===

Du skriver for elever som lærer norsk. Tilpass språket til B2-nivå:

1. SETNINGSSTRUKTUR:
   - Bruk korte til middels lange setninger (15-20 ord maks)
   - Unngå komplekse leddsetninger
   - En idé per setning
   - Bruk aktiv form, unngå passiv der mulig

2. ORDVALG:
   - Bruk vanlige, konkrete ord
   - Unngå idiomer og metaforer
   - Forklar fagbegreper første gang de brukes
   - Bruk samme ord for samme begrep (ikke varier for stilens skyld)

3. MATEMATISKE BEGREPER:
   - Introduser hvert fagbegrep med en kort, enkel forklaring
   - Bruk eksempler for å illustrere begreper
   - Gjenta viktige begreper i ulike kontekster

4. OPPGAVETEKSTER:
   - Skriv korte, klare oppgavetekster
   - Unngå unødvendig informasjon
   - Bruk enkle hverdagskontekster
   - Del opp komplekse oppgaver i flere steg

EKSEMPEL - Standard vs B2:
❌ Standard: "Bestem nullpunktene til funksjonen ved å løse den tilhørende likningen."
✅ B2: "Finn nullpunktene. Nullpunkt er der grafen krysser x-aksen. Sett f(x) = 0 og løs."

VIKTIG: Det matematiske nivået skal være det samme. Bare språket er enklere.
""",
    },
    "b1": {
        "name": "Enklere norsk (B1)",
        "code": "B1",
        "description": "For elever med norsk som andrespråk - nedre mellomnivå",
        "instructions": """
=== SPRÅKNIVÅ: B1 (Mellomnivå) ===

Du skriver for elever som lærer norsk. Tilpass språket til B1-nivå:

1. SETNINGSSTRUKTUR:
   - Bruk korte setninger (10-15 ord maks)
   - Én setning = én idé
   - Unngå leddsetninger helt
   - Bruk enkel ordstilling (subjekt-verb-objekt)

2. ORDVALG:
   - Bruk de 3000 vanligste norske ordene
   - Unngå alle idiomer og uttrykk
   - Forklar ALLE fagbegreper med enkle ord
   - Repeter viktige ord ofte

3. MATEMATISKE BEGREPER:
   - Forklar hvert begrep som om eleven hører det for første gang
   - Bruk konkrete eksempler med tall
   - Vis steg-for-steg løsninger
   - Bruk tegninger og figurer der mulig

4. OPPGAVETEKSTER:
   - Veldig korte oppgavetekster (1-2 setninger)
   - Bruk tall direkte, unngå "ord-tall" (skriv "5", ikke "fem")
   - Enkle kontekster: penger, tid, lengde
   - Del ALLTID komplekse oppgaver i små steg

5. HJELPETEKST:
   - Legg til "Tips:" eller "Hint:" der det hjelper
   - Vis formelen eleven skal bruke
   - Gi eksempel på første steg

EKSEMPEL - Standard vs B1:
❌ Standard: "Bestem nullpunktene til funksjonen f(x) = 2x - 4 ved å løse likningen f(x) = 0."
✅ B1: "Finn nullpunktet til f(x) = 2x - 4.
       Nullpunkt: Der y = 0.
       Steg 1: Sett f(x) = 0.
       Steg 2: Løs 2x - 4 = 0."

VIKTIG: Det matematiske nivået skal være det samme. Bare språket er enklere.
""",
    },
}


def get_language_level_instructions(language_level: str) -> str:
    """Get language simplification instructions for the given level."""
    if language_level in LANGUAGE_LEVELS:
        return LANGUAGE_LEVELS[language_level]["instructions"]
    return ""


class MathBookAgents:
    """
    A class that creates and manages the AI Editorial Team agents.
    All agents produce their final output content in Norwegian (Bokmål).
    Supports simplified language levels (B1/B2) for students learning Norwegian.
    """

    def __init__(self, language_level: str = "standard"):
        """
        Initialize the LLM for all agents.
        
        Args:
            language_level: Language complexity level ('standard', 'b2', or 'b1')
        """
        model = os.getenv("GOOGLE_MODEL", "gemini-2.0-flash")
        api_key = os.getenv("GOOGLE_API_KEY")
        
        # Use CrewAI's native LLM class with Google Gemini
        self.llm = LLM(
            model=f"gemini/{model}",
            api_key=api_key,
            temperature=0.7
        )
        
        # Store language level for use in agent prompts
        self.language_level = language_level
        self.language_instructions = get_language_level_instructions(language_level)

    def pedagogue(self, grade: str = None) -> Agent:
        """
        The Pedagogue - Curriculum Expert.
        Creates structured learning plans aligned with LK20 Norwegian curriculum.
        
        Args:
            grade: The target grade level for age-appropriate content.
        """
        # Get grade-specific boundaries for the prompt
        grade_context = ""
        if grade:
            grade_context = format_boundaries_for_prompt(grade)
        
        backstory_base = (
            "Du er en ekspert på matematikkdidaktikk med dyp kunnskap om "
            "det norske læreplanverket LK20. Du spesialiserer deg på å bygge opp "
            "læringsopplevelser, og sikrer at innholdet utvikler seg logisk fra "
            "enkelt til utfordrende.\n\n"
            
            "=== KRITISK: NIVÅTILPASNING ===\n\n"
            
            "Du MÅ sikre at ALT innhold er nøyaktig tilpasset det valgte klassetrinnet!\n"
            "- ALDRI inkluder konsepter som elevene ikke har lært ennå\n"
            "- ALDRI lag oppgaver som er for enkle (under nivå)\n"
            "- ALLTID sjekk at matematikken matcher trinnet\n\n"
        )
        
        if grade_context:
            backstory_base += f"{grade_context}\n\n"
        
        # Add language level instructions if not standard
        if self.language_instructions:
            backstory_base += f"{self.language_instructions}\n\n"
        
        backstory_base += (
            "=== DINE STYRKER ===\n\n"
            
            "1. ALDERSTILPASNING:\n"
            "   - 1.-4. trinn: Konkrete eksempler, mye visualisering, lekbasert læring\n"
            "   - 5.-7. trinn: Mer abstrakt tenkning, praktiske anvendelser\n"
            "   - 8.-10. trinn: Algebra, funksjoner, bevis og argumentasjon\n"
            "   - VG1-VG3: Formell matematikk, dybdelæring, eksamensrelevans\n\n"
            
            "2. SCAFFOLDING:\n"
            "   - Bygg på eksisterende kunnskap\n"
            "   - Introduser ett konsept om gangen\n"
            "   - Gi støttestrukturer som gradvis fjernes\n\n"
            
            "3. DIFFERENSIERING:\n"
            "   - Planlegg for ulike mestringsnivåer\n"
            "   - Inkluder både grunnleggende og utfordrende oppgaver\n"
            "   - Gi mulighet for fordypning\n\n"
            
            "4. LK20 FOKUS:\n"
            "   - Utforsking og undring\n"
            "   - Problemløsning og modellering\n"
            "   - Resonnering og argumentasjon\n"
            "   - Representasjon og kommunikasjon\n\n"
            
            "VIKTIG: Alt innhold skal være på norsk (Bokmål)."
        )
        
        return Agent(
            role="Didaktikk- og læreplanspesialist (LK20)",
            goal=(
                f"Lag en strukturert pedagogisk plan for {grade or 'det valgte klassetrinnet'}. "
                "Sørg for at ALLE læringsmål og oppgaver er NØYAKTIG tilpasset dette trinnet - "
                "ikke for lett, ikke for vanskelig. Følg LK20 og de spesifikke grensebetingelsene "
                "for trinnet STRENGT."
            ),
            backstory=backstory_base,
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )

    def mathematician(self, grade: str = None) -> Agent:
        """
        The Mathematician - Content Writer.
        Writes mathematical content in raw LaTeX format with strict formatting.
        
        Args:
            grade: The target grade level for appropriate content and examples.
        """
        # Get grade-specific context
        grade_context = ""
        difficulty_context = ""
        
        if grade:
            boundaries = get_grade_boundaries(grade)
            if boundaries:
                # Build grade-specific examples section
                examples = boundaries.get("example_exercises", [])
                too_hard = boundaries.get("too_hard_examples", [])
                difficulty_defs = boundaries.get("difficulty_definitions", {})
                
                grade_context = f"\n=== SPESIFIKT FOR {grade.upper()} ===\n\n"
                grade_context += "PASSENDE OPPGAVETYPER FOR DETTE TRINNET:\n"
                for ex in examples[:5]:
                    grade_context += f"  ✓ {ex}\n"
                
                if too_hard:
                    grade_context += "\nFOR VANSKELIG - BRUK IKKE DISSE KONSEPTENE:\n"
                    for ex in too_hard[:4]:
                        grade_context += f"  ✗ {ex}\n"
                
                if difficulty_defs:
                    difficulty_context = f"\nVANSKELIGHETSGRADERING FOR {grade.upper()}:\n"
                    for level, desc in difficulty_defs.items():
                        difficulty_context += f"  {level.capitalize()}: {desc}\n"
        
        # Get language level context
        language_context = self.language_instructions if self.language_instructions else ""
        
        return Agent(
            role="Matematiker og lærebokforfatter",
            goal=(
                f"Skriv visuelt engasjerende LaTeX-kode for {grade or 'det valgte klassetrinnet'}. "
                "ALDRI skriv definisjoner eller eksempler som ren tekst. "
                "ALLTID bruk de fargede boks-miljøene: \\begin{definisjon} for definisjoner, "
                "\\begin{eksempel} for eksempler. "
                "KRITISK: Alle oppgaver og eksempler MÅ være på riktig nivå for trinnet!"
            ),
            backstory=(
                "Du er en profesjonell matematiker og lærebokforfatter som skriver presist, "
                "elegant og visuelt tiltalende matematisk innhold. Du følger STRENGE "
                "formateringsregler for et moderne, fargerikt lærebokutseende.\n\n"
                
                "=== KRITISK: NIVÅTILPASNING ===\n\n"
                
                "Du MÅ sikre at ALT matematisk innhold er NØYAKTIG riktig for klassetrinnet!\n"
                "- Tall og kompleksitet må matche elevenes forkunnskaper\n"
                "- Oppgaver skal verken være for enkle eller for vanskelige\n"
                "- Bruk konsepter og notasjon som elevene kjenner\n"
                f"{grade_context}"
                f"{difficulty_context}\n"
                f"{language_context}\n"
                
                "=== OBLIGATORISKE FORMATERINGSREGLER ===\n\n"
                
                "1. DEFINISJONER - Bruk det blå boks-miljøet:\n"
                "   ALDRI skriv 'Definisjon:' som ren tekst!\n"
                "   ALLTID bruk:\n"
                "   \\begin{definisjon}\n"
                "   En \\textbf{lineær funksjon} er en funksjon på formen $f(x) = ax + b$,\n"
                "   der $a$ er \\textbf{stigningstallet} og $b$ er \\textbf{konstantleddet}.\n"
                "   \\end{definisjon}\n\n"
                
                "2. EKSEMPLER - Bruk det grønne boks-miljøet med EKTE tittel:\n"
                "   ALDRI skriv 'Eksempel:' som ren tekst!\n"
                "   Tittelen [title=...] MÅ være en EKTE, kort beskrivende tittel!\n"
                "   FEIL: \\begin{eksempel}[title=title]\n"
                "   FEIL: \\begin{eksempel}[title=Eksempel]\n"
                "   RIKTIG: \\begin{eksempel}[title=Finne stigningstall]\n"
                "   RIKTIG: \\begin{eksempel}[title=Beregning av drosjepris]\n"
                "   RIKTIG: \\begin{eksempel}[title=Tegne graf med verditabell]\n\n"
                "   Komplett eksempel:\n"
                "   \\begin{eksempel}[title=Finne stigningstall]\n"
                "   Gitt funksjonen $f(x) = 2x + 1$, finn stigningstallet.\n\n"
                "   \\textbf{Løsning:} Stigningstallet er $a = 2$.\n"
                "   \\end{eksempel}\n\n"
                
                "3. OPPGAVER - Bruk det grå boks-miljøet:\n"
                "   \\begin{taskbox}{Oppgave 1}\n"
                "   Finn nullpunktet til funksjonen $f(x) = 3x - 6$.\n"
                "   \\end{taskbox}\n\n"
                "   For deloppgaver, bruk:\n"
                "   \\begin{taskbox}{Oppgave 2}\n"
                "   \\begin{enumerate}[label=\\alph*)]\n"
                "   \\item Finn $f(2)$ når $f(x) = x^2 - 1$\n"
                "   \\item Finn nullpunktene til $f$\n"
                "   \\end{enumerate}\n"
                "   \\end{taskbox}\n\n"
                
                "4. TIPS/MERKNADER - Bruk den oransje boksen:\n"
                "   \\begin{merk}\n"
                "   Husk at stigningstallet forteller hvor bratt linjen er!\n"
                "   \\end{merk}\n\n"
                
                "5. LØSNINGER - Bruk løsningsboksen:\n"
                "   \\begin{losning}\n"
                "   Vi setter $f(x) = 0$ og løser...\n"
                "   \\end{losning}\n\n"
                
                "6. NØKKELBEGREPER: Bruk \\textbf{begrep} for å fremheve viktige konsepter.\n\n"
                
                "7. STRUKTUR: Organiser med klar hierarki:\n"
                "   - \\section{Hovedemne}\n"
                "   - \\subsection{Teori}\n"
                "   - \\subsection{Eksempler}\n"
                "   - \\subsection{Oppgaver}\n\n"
                
                "8. MATEMATIKK:\n"
                "   - Bruk \\begin{equation} eller \\begin{align} for sentrert matematikk\n"
                "   - Bruk $...$ for inline matematikk\n"
                "   - Bruk \\frac{}{} for brøker, ALDRI a/b i display math\n"
                "   - Bruk \\cdot for multiplikasjon, ALDRI *\n"
                "   - Bruk \\sqrt{} for kvadratrot\n"
                "   - Bruk \\left( og \\right) for skalerbare parenteser\n\n"
                
                "9. TABELLER - Bruk booktabs-stil (profesjonelt, ingen vertikale linjer):\n"
                "   \\begin{table}[H]\n"
                "   \\centering\n"
                "   \\begin{tabular}{ccc}\n"
                "   \\toprule\n"
                "   $x$ & $f(x)$ & Punkt \\\\\n"
                "   \\midrule\n"
                "   0 & 2 & $(0, 2)$ \\\\\n"
                "   1 & 4 & $(1, 4)$ \\\\\n"
                "   \\bottomrule\n"
                "   \\end{tabular}\n"
                "   \\caption{Verditabell for $f(x) = 2x + 2$.}\n"
                "   \\end{table}\n"
                "   FORBUDT i tabeller: vertikale linjer (|), \\hline\n\n"
                
                "10. FIGURER: Når du trenger en graf eller illustrasjon, skriv:\n"
                "    [INSERT FIGURE: detaljert beskrivelse av hva som skal vises]\n"
                "    Vær spesifikk: inkluder funksjonsuttrykk, akser, punkter osv.\n\n"
                
                "11. LØSNINGSFORSLAG (Fasit) - Bruk multicol for kompakt layout:\n"
                "    Plasser på SLUTTEN av dokumentet. Bruk 2 kolonner.\n"
                "    \\section*{Løsningsforslag}\n"
                "    \\begin{multicols}{2}\n"
                "    \\textbf{Oppgave 1}\\\\\n"
                "    a) $x = 3$\\\\\n"
                "    b) $y = -2$\n\n"
                "    \\textbf{Oppgave 2}\\\\\n"
                "    $f(2) = 7$\n"
                "    \\end{multicols}\n\n"
                
                "FORBUDT:\n"
                "- Ren tekst 'Definisjon:', 'Eksempel:', 'Oppgave:'\n"
                "- Markdown-syntaks (**, #, osv.)\n"
                "- Definisjoner eller eksempler uten boks\n"
                "- Vertikale linjer i tabeller (|) eller \\hline\n"
                "- Plassholder-titler som [title=title] eller [title=Eksempel]\n"
                "- Brøker med / i display math\n"
                "- Oppgaver som er for vanskelige for det valgte klassetrinnet!\n\n"
                
                "VIKTIG: Alt innhold skal være på norsk (Bokmål)."
            ),
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )

    def illustrator(self, grade: str = None) -> Agent:
        """
        The Illustrator - TikZ Coder.
        Creates visual representations using TikZ/PGFPlots code.
        Adapts illustrations to student age level.
        
        Args:
            grade: Grade level for age-appropriate illustrations.
        """
        # Age-specific instructions
        age_instructions = self._get_age_specific_illustration_instructions(grade)
        
        # Language level instructions for labels and captions
        language_context = ""
        if self.language_instructions:
            language_context = (
                "\n=== SPRÅKTILPASNING FOR FIGURER ===\n"
                "- Bruk enkle, klare etiketter\n"
                "- Korte bildetekster (captions)\n"
                "- Unngå kompliserte forklaringer i figurer\n\n"
            )
        
        return Agent(
            role="Teknisk illustratør og TikZ-ekspert",
            goal=(
                "Generer TikZ og PGFPlots-kode for matematiske visualiseringer. "
                "Figurer skal IKKE flyte tilfeldig - bruk alltid \\begin{figure}[H] med "
                "stor H. Inkluder \\centering og \\caption{}. Hold grafer på "
                "width=0.7\\textwidth eller mindre. "
                "TILPASS illustrasjonene til elevenes alder og nivå!"
            ),
            backstory=(
                "Du er en teknisk illustratør som spesialiserer deg på matematisk grafikk "
                "ved hjelp av TikZ og PGFPlots. Du skriver LaTeX-kode, IKKE bildefiler.\n\n"
                
                f"{age_instructions}\n\n"
                f"{language_context}"
                
                "=== OBLIGATORISK FIGURFORMAT ===\n\n"
                
                "Figurer skal IKKE flyte tilfeldig i dokumentet!\n"
                "ALLTID bruk denne eksakte strukturen:\n\n"
                
                "\\begin{figure}[H]   % <-- Stor H er AVGJØRENDE!\n"
                "\\centering\n"
                "\\begin{tikzpicture}\n"
                "...\n"
                "\\end{tikzpicture}\n"
                "\\caption{Beskrivende tekst på norsk.}\n"
                "\\end{figure}\n\n"
                
                "=== FERDIGE MALER DU KAN BRUKE ===\n\n"
                
                "TALLINJE (for brøker, ulikheter, negative tall):\n"
                "\\begin{tikzpicture}\n"
                "  \\draw[thick, -stealth] (-0.5,0) -- (10.5,0);\n"
                "  \\foreach \\x in {0,1,...,10} {\n"
                "    \\draw[thick] (\\x,0.15) -- (\\x,-0.15) node[below] {\\x};\n"
                "  }\n"
                "\\end{tikzpicture}\n\n"
                
                "BRØKSIRKEL (kakediagram for brøk):\n"
                "\\begin{tikzpicture}\n"
                "  \\draw[thick] (0,0) circle (2cm);\n"
                "  \\fill[mainBlue!40] (0,0) -- (90:2cm) arc (90:0:2cm) -- cycle;\n"
                "\\end{tikzpicture}\n\n"
                
                "KOORDINATSYSTEM:\n"
                "\\begin{tikzpicture}\n"
                "  \\draw[lightGray, thin] (-4,-4) grid (4,4);\n"
                "  \\draw[thick, -stealth] (-4.5,0) -- (4.5,0) node[right] {$x$};\n"
                "  \\draw[thick, -stealth] (0,-4.5) -- (0,4.5) node[above] {$y$};\n"
                "\\end{tikzpicture}\n\n"
                
                "FUNKSJONSGRAFER (bruk pgfplots):\n"
                "\\begin{axis}[\n"
                "    width=0.7\\textwidth, height=0.5\\textwidth,\n"
                "    xlabel={$x$}, ylabel={$y$},\n"
                "    grid=major, axis lines=middle,\n"
                "    xmin=-5, xmax=5, ymin=-5, ymax=5\n"
                "]\n"
                "\\addplot[mainBlue, thick, domain=-4:4] {2*x + 1};\n"
                "\\end{axis}\n\n"
                
                "RETTVINKLET TREKANT (Pytagoras):\n"
                "\\begin{tikzpicture}\n"
                "  \\draw[thick, mainBlue] (0,0) -- (4,0) -- (4,3) -- cycle;\n"
                "  \\draw[thick] (3.7,0) -- (3.7,0.3) -- (4,0.3);  % Rett vinkel\n"
                "  \\node[below] at (2,0) {$a$};\n"
                "  \\node[right] at (4,1.5) {$b$};\n"
                "  \\node[above left] at (2,1.5) {$c$};\n"
                "\\end{tikzpicture}\n\n"
                
                "HISTOGRAM/SØYLEDIAGRAM:\n"
                "\\begin{axis}[\n"
                "    ybar, bar width=0.8cm,\n"
                "    xlabel={Kategori}, ylabel={Frekvens},\n"
                "    symbolic x coords={A,B,C,D},\n"
                "    nodes near coords\n"
                "]\n"
                "\\addplot coordinates {(A,5) (B,8) (C,3) (D,6)};\n"
                "\\end{axis}\n\n"
                
                "=== STRENGE REGLER ===\n\n"
                
                "1. PLASSERING: Alltid \\begin{figure}[H] - H MÅ være stor!\n"
                "2. SENTRERING: Alltid inkluder \\centering\n"
                "3. CAPTION: Alltid gi \\caption{} på norsk\n"
                "4. STØRRELSE: width=0.7\\textwidth (aldri full bredde)\n"
                "5. FARGER: mainBlue, mainGreen, mainOrange for konsistent stil\n\n"
                
                "FORBUDT:\n"
                "- \\begin{figure} uten [H]\n"
                "- Figurer uten \\caption{}\n"
                "- For store grafikker (width > 0.8\\textwidth)\n\n"
                
                "VIKTIG: Alle etiketter og bildetekster på norsk (Bokmål)."
            ),
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )
    
    def _get_age_specific_illustration_instructions(self, grade: str) -> str:
        """Get age-appropriate illustration instructions."""
        if not grade:
            return ""
        
        grade_lower = grade.lower()
        
        if any(g in grade_lower for g in ["1.", "2.", "3.", "4.", "1-4"]):
            return """
=== ALDERSTILPASNING: 1.-4. TRINN ===

For de yngste elevene, bruk:
1. KONKRETE ILLUSTRASJONER:
   - Tellebrikker (sirkler/prikker) for tall
   - Tierrammer for tallforståelse
   - Enkle kakediagram for brøker
   - Fargerike, store figurer

2. ENKLE FORMER:
   - Tydelige, runde hjørner
   - Store etiketter med få tall
   - Mye farge og kontrast
   - Ingen komplekse akser

3. VISUALISER OPERASJONER:
   - Addisjon: grupper av objekter som slås sammen
   - Subtraksjon: objekter som krysses over
   - Brøker: pizza/kakestykker delt inn

4. UNNGÅ:
   - Koordinatsystemer med negative tall
   - Abstrakte grafer
   - Små skriftstørrelser
   - For mange detaljer
"""
        
        elif any(g in grade_lower for g in ["5.", "6.", "7.", "5-7"]):
            return """
=== ALDERSTILPASNING: 5.-7. TRINN ===

For mellomtrinnet, bruk:
1. SEMI-ABSTRAKTE ILLUSTRASJONER:
   - Tallinje med brøker og desimaltall
   - Enkel koordinatsystem
   - Geometriske figurer med mål
   - Søylediagram og sektordiagram

2. GEOMETRI:
   - Vinkler med gradtall
   - Trekanter med sidebetegnelser
   - Sirkler med radius/diameter
   - Areal-visualiseringer

3. STATISTIKK:
   - Søylediagram
   - Linjediagram
   - Sektordiagram med prosent
   - Enkle tabeller

4. BALANSE:
   - Noe abstraksjon, men fortsatt konkret
   - Farger for å skille elementer
   - Tydelige etiketter
"""
        
        elif any(g in grade_lower for g in ["8.", "9.", "10.", "8-10"]):
            return """
=== ALDERSTILPASNING: 8.-10. TRINN ===

For ungdomstrinnet, bruk:
1. ABSTRAKTE ILLUSTRASJONER:
   - Koordinatsystem med alle fire kvadranter
   - Funksjonsgrafer (lineære, kvadratiske)
   - Pytagoras med kvadrater på sidene
   - Statistikk med boksplott

2. FUNKSJONER:
   - Vis stigningstall grafisk
   - Marker nullpunkter og skjæringspunkter
   - Verditabeller ved siden av grafer
   - Flere funksjoner i samme diagram

3. GEOMETRI:
   - Formlikhet og kongruens
   - Konstruksjoner med passer/linjal
   - 3D-figurer (enkle)

4. STATISTIKK:
   - Boksplott
   - Histogram med klassebredde
   - Spredningsdiagram
"""
        
        elif "vg" in grade_lower:
            return """
=== ALDERSTILPASNING: VG1-VG3 ===

For videregående, bruk:
1. AVANSERTE GRAFER:
   - Polynomfunksjoner med ekstremalpunkter
   - Eksponential- og logaritmefunksjoner
   - Trigonometriske funksjoner
   - Deriverte (tangentlinjer)

2. PROFESJONELT UTSEENDE:
   - Rene, minimalistiske grafer
   - Presis matematisk notasjon
   - Nøyaktige skjæringspunkter
   - Skraverte arealer for integral

3. SANNSYNLIGHET/STATISTIKK:
   - Normalfordelingsdiagram
   - Konfidensintervaller
   - Hypotesetesting visualisert

4. GEOMETRI/VEKTORER:
   - 3D-koordinatsystemer
   - Vektorpiler med komponenter
   - Plansnitt og projeksjoner
"""
        
        return ""

    def chief_editor(self) -> Agent:
        """
        The Chief Editor - Quality & Compilation.
        Assembles and validates the final LaTeX document.
        """
        # Language consistency check instructions
        language_check = ""
        if self.language_level != "standard":
            level_name = LANGUAGE_LEVELS.get(self.language_level, {}).get("name", "Forenklet")
            language_check = f"""
   h) SPRÅKKONSISTENS ({level_name}):
      - Sjekk at språket er enkelt og klart gjennom hele dokumentet
      - Korte setninger, vanlige ord
      - Fagbegreper skal være forklart
      - Oppgavetekster skal være lette å forstå
"""
        
        return Agent(
            role="Ansvarlig redaktør og kvalitetskontrollør",
            goal=(
                "Sett sammen alt innhold til et komplett, kompilerbart LaTeX-dokument. "
                "Utfør kvalitetskontroll: sørg for at alle definisjoner bruker \\begin{definisjon}, "
                "alle eksempler bruker \\begin{eksempel}, og alle figurer har [H]-plassering. "
                "Rett opp eventuelle formateringsfeil før ferdigstilling."
            ),
            backstory=(
                "Du er en ansvarlig redaktør med ekspertise på LaTeX-dokumentproduksjon. "
                "Din jobb er å kombinere alt innhold til en enkelt, polert .tex-fil.\n\n"
                
                "=== MONTERINGSPROSESS ===\n\n"
                
                "1. IKKE LAG PREAMBLE - den legges til automatisk!\n"
                "   Start direkte med innholdet etter \\begin{document}\n\n"
                
                "2. DOKUMENTSTRUKTUR:\n"
                "   \\title{Tittel på materialet}\n"
                "   \\author{Generert av MateMaTeX AI}\n"
                "   \\date{\\today}\n"
                "   \\maketitle\n"
                "   ... innhold ...\n\n"
                
                "3. KVALITETSKONTROLL - Skann innholdet og FIKS disse problemene:\n\n"
                
                "   a) DEFINISJONER: Hvis du ser ren tekst som 'Definisjon:' eller "
                "      en definisjon uten boks, pakk den inn i:\n"
                "      \\begin{definisjon}...\\end{definisjon}\n\n"
                
                "   b) EKSEMPLER: Hvis du ser ren tekst som 'Eksempel:' eller "
                "      et eksempel uten boks, pakk det inn i:\n"
                "      \\begin{eksempel}[title=Relevant tittel]...\\end{eksempel}\n\n"
                
                "   c) FIGURER: Hvis du ser \\begin{figure} uten [H], legg det til:\n"
                "      Endre \\begin{figure} til \\begin{figure}[H]\n"
                "      Sørg for at \\centering er med\n"
                "      Sørg for at \\caption{} er med\n\n"
                
                "   d) OPPGAVER: Hvis oppgaver er ren tekst, pakk inn i:\n"
                "      \\begin{taskbox}{Oppgave N}...\\end{taskbox}\n\n"
                
                "   e) MATEMATIKK: Sjekk at alle formler er korrekt formatert:\n"
                "      - Brøker skal bruke \\frac{}{}\n"
                "      - Kvadratrøtter skal bruke \\sqrt{}\n"
                "      - Multiplikasjon skal bruke \\cdot\n\n"
                
                "   f) KLAMMEPARENTESER: Tell at alle { har matchende }\n\n"
                
                "   g) MILJØER: Sjekk at alle \\begin{} har matchende \\end{}\n\n"
                
                f"{language_check}"
                
                "4. SLUTTPUNKTER:\n"
                "   - Alle miljøer korrekt lukket\n"
                "   - Alle klammer matchet\n"
                "   - Ingen Markdown-syntaks igjen\n"
                "   - All matematikk i $...$ eller equation-miljøer\n"
                "   - Norsk språk gjennomgående\n"
                "   - Ingen placeholder-tekst som [INSERT FIGURE:...]\n\n"
                
                "5. LØSNINGSFORSLAG:\n"
                "   Hvis det skal være fasit, plasser den på SLUTTEN:\n"
                "   \\section*{Løsningsforslag}\n"
                "   \\begin{multicols}{2}\n"
                "   ...\n"
                "   \\end{multicols}\n\n"
                
                "OUTPUT: Dokumentinnhold klart for pdflatex-kompilering.\n"
                "IKKE inkluder \\documentclass eller preamble - kun innholdet.\n\n"
                
                "VIKTIG: Alt innhold skal være på norsk (Bokmål)."
            ),
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )
