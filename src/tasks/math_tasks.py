"""
MathTasks - CrewAI tasks for the AI Editorial Team.
Defines the workflow for creating math worksheets and chapters.
"""

from crewai import Task, Agent


class MathTasks:
    """
    A class that creates tasks for the math content generation workflow.
    Tasks are designed to chain together, with each task's output
    serving as context for the next.
    """

    def plan_content_task(
        self,
        agent: Agent,
        grade: str,
        topic: str,
        content_type: str,
        content_options: dict = None
    ) -> Task:
        """
        Task 1: Plan Content (Pedagogue).
        Analyzes user input and produces a structured pedagogical outline.

        Args:
            agent: The Pedagogue agent.
            grade: Target grade level (e.g., "8. trinn", "VG1").
            topic: Mathematical topic (e.g., "Lineære funksjoner").
            content_type: Type of content ("arbeidsark", "kapittel", "prøve").
            content_options: Dictionary with content inclusion flags.

        Returns:
            A Task for content planning.
        """
        if content_options is None:
            content_options = {}
        
        include_theory = content_options.get("include_theory", True)
        include_examples = content_options.get("include_examples", True)
        include_exercises = content_options.get("include_exercises", True)
        include_solutions = content_options.get("include_solutions", True)
        include_graphs = content_options.get("include_graphs", True)
        num_exercises = content_options.get("num_exercises", 10)
        difficulty = content_options.get("difficulty", "Middels")
        competency_goals = content_options.get("competency_goals", [])
        exercise_type_instructions = content_options.get("exercise_type_instructions", [])
        differentiation_mode = content_options.get("differentiation_mode", False)
        language_level = content_options.get("language_level", "standard")
        
        # Build content restrictions
        content_restrictions = []
        if not include_theory:
            content_restrictions.append("IKKE inkluder teori eller definisjoner")
        if not include_examples:
            content_restrictions.append("IKKE inkluder eksempler")
        if not include_exercises:
            content_restrictions.append("IKKE inkluder oppgaver")
        if not include_graphs:
            content_restrictions.append("IKKE inkluder grafer eller figurer")
        
        restrictions_text = ""
        if content_restrictions:
            restrictions_text = "\n\n**VIKTIGE RESTRIKSJONER:**\n" + "\n".join(f"- {r}" for r in content_restrictions)
        
        # Build competency goals text
        competency_text = ""
        if competency_goals:
            goals_list = "\n".join(f"- {goal}" for goal in competency_goals)
            competency_text = f"\n\n**LK20 KOMPETANSEMÅL:**\n{goals_list}"
        
        # Build exercise types text
        exercise_types_text = ""
        if exercise_type_instructions:
            exercise_types_text = "\n\n**OPPGAVETYPER:**\n" + "\n".join(f"- {instr}" for instr in exercise_type_instructions)
        
        # Build differentiation text
        differentiation_text = ""
        if differentiation_mode:
            differentiation_text = """

**DIFFERENSIERING:**
Lag TRE separate nivåer av oppgaver:
1. Nivå 1 (Lett) - Grunnleggende oppgaver for elever som trenger ekstra støtte
2. Nivå 2 (Middels) - Standard oppgaver for de fleste elever
3. Nivå 3 (Vanskelig) - Utfordrende oppgaver for elever som trenger ekstra utfordring
"""
        
        # Build language level text
        language_level_text = ""
        if language_level == "b2":
            language_level_text = """

**SPRÅKNIVÅ: B2 (Forenklet norsk)**
Materialet er for elever med norsk som andrespråk. Bruk:
- Korte setninger (15-20 ord maks)
- Vanlige, konkrete ord
- Forklar alle fagbegreper
- Enkle oppgavetekster
Det matematiske nivået skal være det samme - bare språket er enklere.
"""
        elif language_level == "b1":
            language_level_text = """

**SPRÅKNIVÅ: B1 (Enklere norsk)**
Materialet er for elever som lærer norsk. Bruk:
- Veldig korte setninger (10-15 ord maks)
- De vanligste norske ordene
- Forklar ALLE begreper som om eleven hører det første gang
- Korte oppgavetekster med konkrete eksempler
- Del komplekse oppgaver i små steg
Det matematiske nivået skal være det samme - bare språket er enklere.
"""
        
        # Check if this is exercises-only mode
        exercises_only = include_exercises and not include_theory and not include_examples
        
        if exercises_only:
            return Task(
                description=f"""
**RENT OPPGAVEARK - INGEN TEORI ELLER EKSEMPLER**

**Grade Level:** {grade}
**Topic:** {topic}
**Content Type:** {content_type}
**Antall oppgaver:** {num_exercises}
**Vanskelighetsgrad:** {difficulty}
{competency_text}
{exercise_types_text}
{differentiation_text}
{language_level_text}

Dette er et RENT oppgaveark. Planen skal KUN inneholde oppgaver.

IKKE planlegg:
- Teori
- Definisjoner
- Eksempler
- Forklaringer

Planlegg KUN:
- Tittel på arbeidsarket
{"- Kompetansemål som skal listes øverst i dokumentet" if competency_goals else ""}
- {num_exercises} oppgaver{"fordelt på 3 nivåer (lett/middels/vanskelig)" if differentiation_mode else " med stigende vanskelighetsgrad"}
- Typer oppgaver som dekker temaet
{"- Løsningsforslag" if include_solutions else "- INGEN løsningsforslag"}

Remember: All content must be in Norwegian (Bokmål).
""",
                expected_output=f"""
En enkel plan for et rent oppgaveark:
- Tittel
{"- LK20 kompetansemål som dekkes" if competency_goals else ""}
- Liste over {num_exercises} oppgaver som skal lages (kort beskrivelse av hver)
{"- Tre separate nivåer: Lett, Middels, Vanskelig" if differentiation_mode else "- Vanskelighetsgrad for hver oppgave"}
{"- Notater om løsningsforslag" if include_solutions else ""}

IKKE inkluder teori, definisjoner eller eksempler i planen.
""",
                agent=agent
            )
        
        return Task(
            description=f"""
Analyze the following request and create a detailed pedagogical plan:

**Grade Level:** {grade}
**Topic:** {topic}
**Content Type:** {content_type}
**Antall oppgaver:** {num_exercises}
**Vanskelighetsgrad:** {difficulty}
{restrictions_text}
{language_level_text}

Your task:
1. Identify the relevant competence goals from the Norwegian curriculum (LK20) for this grade and topic.
2. Break down the topic into logical sub-sections that progress from basic to advanced.
3. For each sub-section, specify:
   - Learning objective (what the student should be able to do)
   - Key concepts to introduce
   {"- Suggested number of examples" if include_examples else "- NO examples (user disabled this)"}
   {"- " + str(num_exercises) + " exercises total (with difficulty levels: lett/middels/vanskelig)" if include_exercises else "- NO exercises (user disabled this)"}
{"4. Identify where visual illustrations would enhance understanding." if include_graphs else "4. NO graphs or figures (user disabled this)."}
5. Suggest a total time estimate for the content.

Remember: All content must be in Norwegian (Bokmål).
""",
            expected_output=f"""
A structured outline in Norwegian (Bokmål) containing:
- Title of the worksheet/chapter
- List of LK20 competence goals addressed
- Detailed section-by-section breakdown with:
  * Section title
  * Learning objectives
  {"* Concepts to cover" if include_theory else ""}
  {"* Number of examples needed" if include_examples else ""}
  {"* Number and difficulty of exercises (total " + str(num_exercises) + ")" if include_exercises else ""}
  {"* Notes on where illustrations are needed" if include_graphs else ""}
- Total estimated time
- Pedagogical notes on progression and scaffolding
""",
            agent=agent
        )

    def write_content_task(
        self,
        agent: Agent,
        plan_task: Task,
        content_options: dict = None
    ) -> Task:
        """
        Task 2: Write Content (Mathematician).
        Writes the full mathematical content in LaTeX format.

        Args:
            agent: The Mathematician agent.
            plan_task: The completed plan_content_task (for context).
            content_options: Dictionary with content inclusion flags.

        Returns:
            A Task for content writing.
        """
        if content_options is None:
            content_options = {}
        
        include_theory = content_options.get("include_theory", True)
        include_examples = content_options.get("include_examples", True)
        include_exercises = content_options.get("include_exercises", True)
        include_solutions = content_options.get("include_solutions", True)
        include_graphs = content_options.get("include_graphs", True)
        num_exercises = content_options.get("num_exercises", 10)
        competency_goals = content_options.get("competency_goals", [])
        exercise_type_instructions = content_options.get("exercise_type_instructions", [])
        differentiation_mode = content_options.get("differentiation_mode", False)
        language_level = content_options.get("language_level", "standard")
        
        # Build language level instruction
        language_instruction = ""
        if language_level == "b2":
            language_instruction = """

**SPRÅKNIVÅ B2 - FORENKLET NORSK:**
- Skriv korte setninger (15-20 ord)
- Bruk vanlige ord, unngå idiomer
- Forklar alle fagbegreper første gang
- Enkle oppgavetekster med klar struktur
- Matematisk nivå er UENDRET - bare språket er enklere
"""
        elif language_level == "b1":
            language_instruction = """

**SPRÅKNIVÅ B1 - ENKLERE NORSK:**
- Skriv veldig korte setninger (10-15 ord)
- Bruk de mest vanlige norske ordene
- Forklar ALLE begreper enkelt
- Korte oppgavetekster, én idé per setning
- Del komplekse oppgaver i steg med "Steg 1:", "Steg 2:" osv.
- Legg til "Tips:" der det hjelper
- Matematisk nivå er UENDRET - bare språket er enklere
"""
        
        # Build competency goals instruction
        competency_instruction = ""
        if competency_goals:
            goals_list = "\\n".join(f"\\\\item {goal}" for goal in competency_goals)
            competency_instruction = f"""
VIKTIG: Start dokumentet med en seksjon som lister kompetansemålene:
\\section*{{Kompetansemål}}
\\begin{{itemize}}
{goals_list}
\\end{{itemize}}
"""
        
        # Build exercise types instruction
        exercise_types_instruction = ""
        if exercise_type_instructions:
            exercise_types_instruction = "\n\nOPPGAVETYPER som skal brukes:\n" + "\n".join(f"- {instr}" for instr in exercise_type_instructions)
        
        # Check if this is exercises-only mode
        exercises_only = include_exercises and not include_theory and not include_examples
        
        if exercises_only:
            # Special task for exercises-only worksheet
            solutions_instruction = ""
            if include_solutions:
                solutions_instruction = """
6. At the END of the document, add an Answer Key section:
   \\section*{Løsningsforslag}
   \\begin{multicols}{2}
   \\textbf{Oppgave 1}\\\\
   Svar ...
   
   \\textbf{Oppgave 2}\\\\
   Svar ...
   \\end{multicols}
"""
            else:
                solutions_instruction = "\n6. IKKE inkluder løsningsforslag."
            
            graphs_instruction = ""
            if include_graphs:
                graphs_instruction = "5. Der en figur er nyttig for oppgaven, skriv: [INSERT FIGURE: beskrivelse]"
            
            differentiation_instruction = ""
            if differentiation_mode:
                differentiation_instruction = f"""

DIFFERENSIERING - Organiser oppgavene i TRE nivåer:
\\section*{{Nivå 1 - Lett}}
Lag {num_exercises // 3} enkle oppgaver

\\section*{{Nivå 2 - Middels}}
Lag {num_exercises // 3} moderate oppgaver

\\section*{{Nivå 3 - Vanskelig}}
Lag {num_exercises - 2*(num_exercises // 3)} utfordrende oppgaver
"""
            
            if not include_graphs:
                graphs_instruction = "5. IKKE inkluder figurer eller grafer."
            
            return Task(
                description=f"""
**RENT OPPGAVEARK - BARE OPPGAVER**

VIKTIG: Dette er et RENT oppgaveark. Skriv KUN oppgaver i LaTeX-format.
{competency_instruction}
{exercise_types_instruction}
{differentiation_instruction}
{language_instruction}

IKKE SKRIV:
- Teori
- Definisjoner
- Forklaringer av konsepter
- Eksempler
- Introduksjonstekst

SKRIV KUN:
{"1. Kompetansemål-seksjon øverst" if competency_goals else ""}
1. En kort tittel med \\section*{{Tittel}}
2. Gå DIREKTE til oppgavene - ingen introduksjon
3. Lag NØYAKTIG {num_exercises} oppgaver{"fordelt på 3 nivåer" if differentiation_mode else " med stigende vanskelighetsgrad"}
4. Bruk \\begin{{taskbox}}{{Oppgave N}} for hver oppgave
{graphs_instruction}
{solutions_instruction}

FORMATTING:
- Use ONLY LaTeX syntax, NEVER Markdown.
- All fractions must use \\frac{{}}{{}}, not a/b in display math.
- Use \\cdot for multiplication, not *.
- All text must be in Norwegian (Bokmål).
""",
                expected_output=f"""
LaTeX-kode for et RENT oppgaveark med:
{"- Kompetansemål øverst" if competency_goals else ""}
- En kort tittel
- {num_exercises} oppgaver i \\begin{{taskbox}}{{Oppgave N}} format
{"- Tre separate nivåer (lett/middels/vanskelig)" if differentiation_mode else "- Varierende vanskelighetsgrad"}
{"- Løsningsforslag på slutten" if include_solutions else "- INGEN løsningsforslag"}

INGEN teori, definisjoner eller eksempler.
""",
                agent=agent,
                context=[plan_task]
            )
        
        # Build task instructions based on options
        task_parts = ["Based on the pedagogical plan provided, write the mathematical content in LaTeX format.\n\nYour task:"]
        
        if include_theory:
            task_parts.append("1. Write clear explanations for each concept in Norwegian (Bokmål).")
            task_parts.append("2. Include formal definitions using \\begin{definisjon}...\\end{definisjon}.")
        else:
            task_parts.append("1. SKIP theory and definitions - do NOT include them.")
            task_parts.append("2. SKIP \\begin{definisjon} environments - do NOT use them.")
        
        if include_examples:
            task_parts.append("3. Provide worked examples using \\begin{eksempel}[title=Beskrivende tittel]...\\end{eksempel}.")
        else:
            task_parts.append("3. SKIP examples - do NOT include any \\begin{eksempel} environments.")
        
        if include_exercises:
            task_parts.append(f"4. Create {num_exercises} exercises using \\begin{{taskbox}}{{Oppgave N}}...\\end{{taskbox}}.")
        else:
            task_parts.append("4. SKIP exercises - do NOT include any \\begin{taskbox} environments.")
        
        if include_graphs:
            task_parts.append("5. Where a visual illustration is needed, insert: [INSERT FIGURE: description]")
        else:
            task_parts.append("5. SKIP figures - do NOT insert any [INSERT FIGURE: ...] placeholders.")
        
        if include_solutions and include_exercises:
            task_parts.append("""6. At the END of the document, add an Answer Key section:
   \\section*{Løsningsforslag}
   \\begin{multicols}{2}
   \\textbf{Oppgave 1}\\\\
   a) Svar ...
   
   \\textbf{Oppgave 2}\\\\
   Svar ...
   \\end{multicols}""")
        else:
            task_parts.append("6. SKIP answer key - do NOT include \\section*{Løsningsforslag}.")
        
        task_parts.append(f"""
IMPORTANT FORMATTING RULES:
- Use ONLY LaTeX syntax, NEVER Markdown.
- All fractions must use \\frac{{}}{{}}, not a/b in display math.
- Use \\cdot for multiplication, not *.
- Tables: use booktabs (\\toprule, \\midrule, \\bottomrule), NO vertical lines.
- All text must be in Norwegian (Bokmål).
{language_instruction}""")
        
        # Build expected output based on options
        output_parts = ["Complete mathematical content in raw LaTeX format containing:"]
        output_parts.append("- Section and subsection headings (\\section{}, \\subsection{})")
        
        if include_theory:
            output_parts.append("- Explanatory text in Norwegian")
            output_parts.append("- Definitions and theorems in proper LaTeX environments")
        
        if include_examples:
            output_parts.append("- Worked examples with full solutions")
        
        if include_exercises:
            output_parts.append(f"- {num_exercises} exercises organized by difficulty with labels")
        
        if include_solutions and include_exercises:
            output_parts.append("- Complete exercise solutions")
        
        if include_graphs:
            output_parts.append("- Placeholder markers [INSERT FIGURE: ...] where illustrations are needed")
        
        output_parts.append("\nThe output should be the BODY content only (no preamble, no \\begin{document}).")
        output_parts.append("All mathematical expressions must use proper LaTeX syntax.")
        
        return Task(
            description="\n".join(task_parts),
            expected_output="\n".join(output_parts),
            agent=agent,
            context=[plan_task]
        )

    def generate_graphics_task(
        self,
        agent: Agent,
        content_task: Task,
        content_options: dict = None
    ) -> Task:
        """
        Task 3: Generate Graphics (Illustrator).
        Creates TikZ/PGFPlots code for all visual elements.

        Args:
            agent: The Illustrator agent.
            content_task: The completed write_content_task (for context).
            content_options: Dictionary with content inclusion flags.

        Returns:
            A Task for graphics generation.
        """
        if content_options is None:
            content_options = {}
        
        include_graphs = content_options.get("include_graphs", True)
        
        if not include_graphs:
            # Skip graphics generation
            return Task(
                description="""
Brukeren har valgt å IKKE inkludere grafer eller figurer.

Din oppgave:
1. Returner innholdet UENDRET
2. IKKE legg til noen figurer eller grafer
3. Hvis det er noen [INSERT FIGURE: ...] plassholdere, FJERN dem

Output the content exactly as received, without any figures.
""",
                expected_output="""
The LaTeX content exactly as received, with no figures added.
Any [INSERT FIGURE: ...] placeholders should be removed.
""",
                agent=agent,
                context=[content_task]
            )
        
        return Task(
            description="""
Review the LaTeX content provided and generate TikZ/PGFPlots code for all visual elements.

Your task:
1. Find all [INSERT FIGURE: ...] placeholders in the content.
2. For each placeholder, create appropriate TikZ or PGFPlots code.
3. Replace EACH placeholder with a complete, working \\begin{tikzpicture}...\\end{tikzpicture} or \\begin{figure}...\\end{figure} environment.
4. Ensure all graphics are:
   - Properly sized (use appropriate scale)
   - Clearly labeled (labels in Norwegian)
   - Using appropriate colors for clarity
   - Self-contained (no external dependencies)

For function graphs, use PGFPlots with \\begin{axis}...\\end{axis}.
For geometric figures, use TikZ with proper coordinates and labels.
For diagrams, use TikZ with nodes and arrows as needed.

IMPORTANT:
- Output the COMPLETE content with all placeholders replaced by actual TikZ code.
- Do NOT remove any of the original LaTeX content.
- All labels and captions must be in Norwegian (Bokmål).
""",
            expected_output="""
The complete LaTeX content with ALL [INSERT FIGURE: ...] placeholders replaced by working TikZ/PGFPlots code.

Each figure should be wrapped appropriately:
- Use \\begin{figure}[H] with \\centering for standalone figures
- Include \\caption{} in Norwegian
- Use \\label{} for cross-referencing

The TikZ code must be complete and compilable, including all necessary coordinates, styles, and labels.
Output the full content - not just the graphics code.
""",
            agent=agent,
            context=[content_task]
        )

    def final_assembly_task(
        self,
        agent: Agent,
        graphics_task: Task,
        content_options: dict = None
    ) -> Task:
        """
        Task 4: Final Assembly (Chief Editor).
        Assembles the complete, compilable LaTeX document.

        Args:
            agent: The Chief Editor agent.
            graphics_task: The completed generate_graphics_task (for context).
            content_options: Dictionary with content inclusion flags.

        Returns:
            A Task for final document assembly.
        """
        if content_options is None:
            content_options = {}
        
        include_theory = content_options.get("include_theory", True)
        include_examples = content_options.get("include_examples", True)
        include_exercises = content_options.get("include_exercises", True)
        include_solutions = content_options.get("include_solutions", True)
        
        # Check if this is exercises-only mode
        exercises_only = include_exercises and not include_theory and not include_examples
        
        quality_check_extra = ""
        if exercises_only:
            quality_check_extra = """
5. CRITICAL CONTENT CHECK for exercises-only worksheet:
   - REMOVE any \\begin{definisjon} environments - they should NOT be in this document
   - REMOVE any \\begin{eksempel} environments - they should NOT be in this document  
   - REMOVE any theory or explanatory text that isn't part of an exercise
   - The document should ONLY contain: title, exercises (taskbox), and optionally solutions
   - If you find theory/definitions/examples, DELETE them entirely
"""
        
        return Task(
            description=f"""
Assemble all the content into a complete, compilable LaTeX document.

Your task:
1. Create a proper LaTeX preamble with:
   - Document class: \\documentclass[a4paper,11pt]{{article}}
   - Language support: \\usepackage[norsk]{{babel}}
   - Math packages: \\usepackage{{amsmath,amssymb,amsthm}}
   - Graphics: \\usepackage{{tikz,pgfplots}}
   - Required TikZ libraries: \\usetikzlibrary{{arrows.meta,calc,patterns,positioning}}
   - PGFPlots compatibility: \\pgfplotsset{{compat=1.18}}
   - Float control: \\usepackage{{float}}
   - Geometry: \\usepackage[margin=2.5cm]{{geometry}}
   - Font encoding: \\usepackage[T1]{{fontenc}} and \\usepackage[utf8]{{inputenc}}

2. Define theorem environments:
   - \\newtheorem{{theorem}}{{Teorem}}[section]
   - \\newtheorem{{definition}}[theorem]{{Definisjon}}
   - \\newtheorem{{example}}[theorem]{{Eksempel}}

3. Structure the document:
   - \\begin{{document}}
   - \\maketitle (with appropriate \\title{{}} and \\date{{}})
   - All content sections
   - \\end{{document}}

4. Quality checks:
   - Ensure all LaTeX syntax is correct
   - Verify all environments are properly opened and closed
   - Check that all TikZ code is complete
   - Ensure consistent formatting throughout
{quality_check_extra}
CRITICAL: The output must be a single, complete .tex file that compiles without errors.
""",
            expected_output=f"""
A complete, valid LaTeX document as a single string containing:
1. Full preamble with all necessary packages
2. Theorem/definition environment declarations
3. Title and author information
4. \\begin{{document}}
5. All content {"(ONLY exercises and solutions - NO theory or examples)" if exercises_only else "(text, math, exercises, solutions, figures)"}
6. \\end{{document}}

The document must:
- Be in Norwegian (Bokmål)
- Compile without errors using pdflatex
- {"Contain ONLY exercises (taskbox) and optionally solutions - NO theory, definitions, or examples" if exercises_only else "Have proper structure with sections and subsections"}
- Be ready for PDF generation
""",
            agent=agent,
            context=[graphics_task]
        )
