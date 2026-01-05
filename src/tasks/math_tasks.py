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
        content_type: str
    ) -> Task:
        """
        Task 1: Plan Content (Pedagogue).
        Analyzes user input and produces a structured pedagogical outline.

        Args:
            agent: The Pedagogue agent.
            grade: Target grade level (e.g., "8. trinn", "VG1").
            topic: Mathematical topic (e.g., "Lineære funksjoner").
            content_type: Type of content ("arbeidsark", "kapittel", "prøve").

        Returns:
            A Task for content planning.
        """
        return Task(
            description=f"""
Analyze the following request and create a detailed pedagogical plan:

**Grade Level:** {grade}
**Topic:** {topic}
**Content Type:** {content_type}

Your task:
1. Identify the relevant competence goals from the Norwegian curriculum (LK20) for this grade and topic.
2. Break down the topic into logical sub-sections that progress from basic to advanced.
3. For each sub-section, specify:
   - Learning objective (what the student should be able to do)
   - Key concepts to introduce
   - Suggested number of examples
   - Suggested number of exercises (with difficulty levels: lett/middels/vanskelig)
4. Identify where visual illustrations would enhance understanding.
5. Suggest a total time estimate for the content.

Remember: All content must be in Norwegian (Bokmål).
""",
            expected_output="""
A structured outline in Norwegian (Bokmål) containing:
- Title of the worksheet/chapter
- List of LK20 competence goals addressed
- Detailed section-by-section breakdown with:
  * Section title
  * Learning objectives
  * Concepts to cover
  * Number of examples needed
  * Number and difficulty of exercises
  * Notes on where illustrations are needed
- Total estimated time
- Pedagogical notes on progression and scaffolding
""",
            agent=agent
        )

    def write_content_task(
        self,
        agent: Agent,
        plan_task: Task
    ) -> Task:
        """
        Task 2: Write Content (Mathematician).
        Writes the full mathematical content in LaTeX format.

        Args:
            agent: The Mathematician agent.
            plan_task: The completed plan_content_task (for context).

        Returns:
            A Task for content writing.
        """
        return Task(
            description="""
Based on the pedagogical plan provided, write the complete mathematical content in LaTeX format.

Your task:
1. Write clear explanations for each concept in Norwegian (Bokmål).
2. Include formal definitions using \\begin{definisjon}...\\end{definisjon}.
3. Provide worked examples using \\begin{eksempel}[title=Beskrivende tittel]...\\end{eksempel}.
4. Create exercises using \\begin{taskbox}{Oppgave N}...\\end{taskbox}.
5. Where a visual illustration is needed, insert: [INSERT FIGURE: description]
6. At the END of the document, add an Answer Key section:
   \\section*{Løsningsforslag}
   \\begin{multicols}{2}
   \\textbf{Oppgave 1}\\\\
   a) Svar ...\\\\
   b) Svar ...
   
   \\textbf{Oppgave 2}\\\\
   Svar ...
   \\end{multicols}

IMPORTANT FORMATTING RULES:
- Use ONLY LaTeX syntax, NEVER Markdown.
- All fractions must use \\frac{}{}, not a/b in display math.
- Use \\cdot for multiplication, not *.
- Tables: use booktabs (\\toprule, \\midrule, \\bottomrule), NO vertical lines.
- All text must be in Norwegian (Bokmål).
""",
            expected_output="""
Complete mathematical content in raw LaTeX format containing:
- Section and subsection headings (\\section{}, \\subsection{})
- Explanatory text in Norwegian
- Definitions and theorems in proper LaTeX environments
- Worked examples with full solutions
- Exercises organized by difficulty with labels
- Complete exercise solutions
- Placeholder markers [INSERT FIGURE: ...] where illustrations are needed

The output should be the BODY content only (no preamble, no \\begin{document}).
All mathematical expressions must use proper LaTeX syntax.
""",
            agent=agent,
            context=[plan_task]
        )

    def generate_graphics_task(
        self,
        agent: Agent,
        content_task: Task
    ) -> Task:
        """
        Task 3: Generate Graphics (Illustrator).
        Creates TikZ/PGFPlots code for all visual elements.

        Args:
            agent: The Illustrator agent.
            content_task: The completed write_content_task (for context).

        Returns:
            A Task for graphics generation.
        """
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
        graphics_task: Task
    ) -> Task:
        """
        Task 4: Final Assembly (Chief Editor).
        Assembles the complete, compilable LaTeX document.

        Args:
            agent: The Chief Editor agent.
            graphics_task: The completed generate_graphics_task (for context).

        Returns:
            A Task for final document assembly.
        """
        return Task(
            description="""
Assemble all the content into a complete, compilable LaTeX document.

Your task:
1. Create a proper LaTeX preamble with:
   - Document class: \\documentclass[a4paper,11pt]{article}
   - Language support: \\usepackage[norsk]{babel}
   - Math packages: \\usepackage{amsmath,amssymb,amsthm}
   - Graphics: \\usepackage{tikz,pgfplots}
   - Required TikZ libraries: \\usetikzlibrary{arrows.meta,calc,patterns,positioning}
   - PGFPlots compatibility: \\pgfplotsset{compat=1.18}
   - Float control: \\usepackage{float}
   - Geometry: \\usepackage[margin=2.5cm]{geometry}
   - Font encoding: \\usepackage[T1]{fontenc} and \\usepackage[utf8]{inputenc}

2. Define theorem environments:
   - \\newtheorem{theorem}{Teorem}[section]
   - \\newtheorem{definition}[theorem]{Definisjon}
   - \\newtheorem{example}[theorem]{Eksempel}

3. Structure the document:
   - \\begin{document}
   - \\maketitle (with appropriate \\title{} and \\date{})
   - All content sections
   - \\end{document}

4. Quality checks:
   - Ensure all LaTeX syntax is correct
   - Verify all environments are properly opened and closed
   - Check that all TikZ code is complete
   - Ensure consistent formatting throughout

CRITICAL: The output must be a single, complete .tex file that compiles without errors.
""",
            expected_output="""
A complete, valid LaTeX document as a single string containing:
1. Full preamble with all necessary packages
2. Theorem/definition environment declarations
3. Title and author information
4. \\begin{document}
5. All content (text, math, exercises, solutions, figures)
6. \\end{document}

The document must:
- Be in Norwegian (Bokmål)
- Compile without errors using pdflatex
- Have proper structure with sections and subsections
- Include all TikZ graphics inline
- Be ready for PDF generation
""",
            agent=agent,
            context=[graphics_task]
        )
