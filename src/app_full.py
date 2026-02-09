"""
MateMaTeX - Matematikkverkstedet AI
Streamlined UI - Clean, focused, user-friendly.
"""

import os
import base64
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

import streamlit as st

# Page configuration
st.set_page_config(
    page_title="MateMaTeX",
    page_icon="◇",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Inject styles
from src.ui import inject_styles
inject_styles()


# ============================================================================
# TEMPLATES
# ============================================================================
TEMPLATES = {
    "worksheet_basic": {
        "name": "Oppgaveark",
        "emoji": "📝",
        "description": "Kun oppgaver",
        "config": {
            "material_type": "arbeidsark",
            "include_theory": False, "include_examples": False,
            "include_exercises": True, "include_solutions": True,
            "include_graphs": True, "include_tips": False,
            "num_exercises": 10,
        }
    },
    "chapter_full": {
        "name": "Fullt kapittel",
        "emoji": "📖",
        "description": "Teori + oppgaver",
        "config": {
            "material_type": "kapittel",
            "include_theory": True, "include_examples": True,
            "include_exercises": True, "include_solutions": True,
            "include_graphs": True, "include_tips": True,
            "num_exercises": 8,
        }
    },
    "exam_prep": {
        "name": "Eksamen",
        "emoji": "📋",
        "description": "Eksamensoppgaver",
        "config": {
            "material_type": "prøve",
            "include_theory": False, "include_examples": False,
            "include_exercises": True, "include_solutions": True,
            "include_graphs": True, "include_tips": False,
            "num_exercises": 15,
        }
    },
    "differentiated": {
        "name": "Differensiert",
        "emoji": "📊",
        "description": "3 nivåer",
        "config": {
            "material_type": "arbeidsark",
            "include_theory": False, "include_examples": False,
            "include_exercises": True, "include_solutions": True,
            "include_graphs": True, "include_tips": False,
            "num_exercises": 12, "differentiation_mode": True,
        }
    },
}


# ============================================================================
# SESSION STATE
# ============================================================================
def initialize_session_state():
    """Initialize session state with sensible defaults."""
    defaults = {
        "latex_result": None,
        "pdf_path": None,
        "pdf_bytes": None,
        "generation_complete": False,
        "include_theory": True,
        "include_examples": True,
        "include_exercises": True,
        "include_solutions": True,
        "include_graphs": True,
        "include_tips": False,
        "difficulty_level": "Middels",
        "selected_exercise_types": ["standard"],
        "differentiation_mode": False,
        "num_exercises": 10,
        "selected_competency_goals": [],
        "selected_template": None,
        "language_level": "standard",
        "history": [],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def apply_template(template_key: str):
    """Apply a template configuration."""
    if template_key in TEMPLATES:
        config = TEMPLATES[template_key]["config"]
        for key, value in config.items():
            st.session_state[key] = value
        st.session_state.selected_template = template_key


# ============================================================================
# CORE FUNCTIONS
# ============================================================================
def run_crew(grade: str, topic: str, material_type: str, instructions: str, content_options: dict) -> str:
    """Run the CrewAI editorial team to generate content."""
    from crewai import Crew, Process
    from src.agents import MathBookAgents
    from src.tasks import MathTasks

    language_level = content_options.get("language_level", "standard")
    agents = MathBookAgents(language_level=language_level)
    tasks = MathTasks()

    pedagogue = agents.pedagogue(grade=grade)
    mathematician = agents.mathematician(grade=grade)
    illustrator = agents.illustrator(grade=grade)
    chief_editor = agents.chief_editor()

    full_topic = f"{topic}\n\nTilleggsinstruksjoner: {instructions}" if instructions else topic

    task1 = tasks.plan_content_task(pedagogue, grade, full_topic, material_type, content_options)
    task2 = tasks.write_content_task(mathematician, task1, content_options)
    task3 = tasks.generate_graphics_task(illustrator, task2, content_options)
    task4 = tasks.final_assembly_task(chief_editor, task3, content_options)

    crew = Crew(
        agents=[pedagogue, mathematician, illustrator, chief_editor],
        tasks=[task1, task2, task3, task4],
        process=Process.sequential,
        verbose=True
    )

    result = crew.kickoff()
    return result.raw if hasattr(result, 'raw') else str(result)


def generate_pdf(latex_content: str, filename: str) -> str | None:
    """Generate PDF from LaTeX content."""
    from src.tools import compile_latex_to_pdf
    try:
        return compile_latex_to_pdf(latex_content, filename)
    except (FileNotFoundError, RuntimeError) as e:
        st.error(f"PDF-kompilering feilet: {e}")
        return None


def save_tex_file(latex_content: str, filename: str) -> str:
    """Save LaTeX content to .tex file."""
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    tex_path = output_dir / f"{filename}.tex"
    tex_path.write_text(latex_content, encoding="utf-8")
    return str(tex_path)


# ============================================================================
# MAIN APPLICATION
# ============================================================================
def main():
    """Main application - clean, linear flow."""
    initialize_session_state()

    api_configured = bool(os.getenv("GOOGLE_API_KEY"))
    model_name = os.getenv("GOOGLE_MODEL", "gemini-2.0-flash")

    # ------------------------------------------------------------------
    # HEADER
    # ------------------------------------------------------------------
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0 1rem 0;">
        <h1 style="
            font-size: 2.5rem; font-weight: 800; margin: 0;
            background: linear-gradient(135deg, #f8fafc 0%, #f59e0b 80%);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            letter-spacing: -1px;
        ">◇ MateMaTeX</h1>
        <p style="color: #94a3b8; font-size: 0.95rem; margin-top: 0.5rem;">
            Generer matematikkoppgaver tilpasset norsk læreplan
        </p>
    </div>
    """, unsafe_allow_html=True)

    # API status - minimal
    if api_configured:
        st.markdown(f"""
        <div style="text-align: center; margin-bottom: 1.5rem;">
            <span style="
                background: rgba(16,185,129,0.1); border: 1px solid rgba(16,185,129,0.25);
                padding: 0.3rem 0.8rem; border-radius: 20px;
                color: #10b981; font-size: 0.75rem;
            ">● {model_name}</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.error("API-nøkkel mangler. Legg til GOOGLE_API_KEY i miljøvariablene.")
        return

    # ------------------------------------------------------------------
    # STEP 1: Quick-start templates
    # ------------------------------------------------------------------
    st.markdown("##### Hurtigstart")
    cols = st.columns(4)
    for i, (key, tmpl) in enumerate(TEMPLATES.items()):
        with cols[i]:
            is_selected = st.session_state.selected_template == key
            if st.button(
                f"{tmpl['emoji']} {tmpl['name']}",
                key=f"tmpl_{key}",
                use_container_width=True,
                type="primary" if is_selected else "secondary",
            ):
                apply_template(key)
                st.rerun()

    st.markdown("---")

    # ------------------------------------------------------------------
    # STEP 2: Grade + Topic (the two most important choices)
    # ------------------------------------------------------------------
    from src.cache import get_curriculum_topics

    grade_options = {
        "1.-4. trinn": "1-4. trinn",
        "5.-7. trinn": "5-7. trinn",
        "8. trinn": "8. trinn",
        "9. trinn": "9. trinn",
        "10. trinn": "10. trinn",
        "VG1 1T": "VG1 1T",
        "VG1 1P": "VG1 1P",
        "VG2 R1": "VG2 R1",
        "VG3 R2": "VG3 R2",
    }

    col_grade, col_topic = st.columns([1, 2])

    with col_grade:
        st.markdown("##### Klassetrinn")
        selected_grade = st.selectbox(
            "Klassetrinn",
            options=list(grade_options.keys()),
            index=4,
            label_visibility="collapsed"
        )

    with col_topic:
        st.markdown("##### Tema")
        topics_by_category = get_curriculum_topics(selected_grade)
        topic_choices = ["✍️ Skriv eget tema..."]
        for _cat, topics_list in topics_by_category.items():
            topic_choices.extend(topics_list)

        selected_topic_choice = st.selectbox(
            "Velg tema",
            options=topic_choices,
            label_visibility="collapsed"
        )

    topic = ""
    if selected_topic_choice == "✍️ Skriv eget tema...":
        topic = st.text_input(
            "Skriv tema",
            placeholder="f.eks. Lineære funksjoner, Pytagoras, Brøk...",
            label_visibility="collapsed"
        )
    else:
        topic = selected_topic_choice

    # ------------------------------------------------------------------
    # STEP 3: Content toggles - simple row
    # ------------------------------------------------------------------
    st.markdown("---")
    st.markdown("##### Innhold")

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1:
        st.session_state.include_theory = st.checkbox("📘 Teori", value=st.session_state.include_theory)
    with c2:
        st.session_state.include_examples = st.checkbox("💡 Eksempler", value=st.session_state.include_examples)
    with c3:
        st.session_state.include_exercises = st.checkbox("✍️ Oppgaver", value=st.session_state.include_exercises)
    with c4:
        st.session_state.include_solutions = st.checkbox("🔑 Fasit", value=st.session_state.include_solutions)
    with c5:
        st.session_state.include_graphs = st.checkbox("📊 Grafer", value=st.session_state.include_graphs)
    with c6:
        st.session_state.include_tips = st.checkbox("💬 Tips", value=st.session_state.include_tips)

    # Exercise count + difficulty (only if exercises enabled)
    if st.session_state.include_exercises:
        col_count, col_diff = st.columns(2)
        with col_count:
            st.session_state.num_exercises = st.slider(
                "Antall oppgaver", min_value=3, max_value=25,
                value=st.session_state.num_exercises, step=1
            )
        with col_diff:
            difficulty_options = ["🟢 Lett", "🟡 Middels", "🔴 Vanskelig"]
            diff_idx = {"Lett": 0, "Middels": 1, "Vanskelig": 2}.get(st.session_state.difficulty_level, 1)
            selected_difficulty = st.radio(
                "Vanskelighetsgrad",
                options=difficulty_options,
                index=diff_idx,
                horizontal=True
            )
            st.session_state.difficulty_level = selected_difficulty.split(" ")[1]

    # ------------------------------------------------------------------
    # STEP 4: Advanced options (collapsed by default)
    # ------------------------------------------------------------------
    with st.expander("⚙️ Flere innstillinger", expanded=False):
        adv_col1, adv_col2 = st.columns(2)

        with adv_col1:
            # Differentiation
            st.session_state.differentiation_mode = st.checkbox(
                "📊 Generer 3 nivåer (differensiering)",
                value=st.session_state.differentiation_mode
            )

            # Language level
            lang_options = {"Standard norsk": "standard", "Forenklet (B2)": "b2", "Enklere (B1)": "b1"}
            current_lang = st.session_state.get("language_level", "standard")
            lang_idx = list(lang_options.values()).index(current_lang) if current_lang in lang_options.values() else 0
            selected_lang = st.selectbox(
                "Språknivå",
                options=list(lang_options.keys()),
                index=lang_idx,
                help="For elever med norsk som andrespråk"
            )
            st.session_state.language_level = lang_options[selected_lang]

        with adv_col2:
            # Exercise types
            if st.session_state.include_exercises:
                from src.cache import get_all_exercise_types
                exercise_types = get_all_exercise_types()
                selected_types = []
                for type_key, type_info in list(exercise_types.items())[:6]:
                    if st.checkbox(
                        type_info["name"],
                        value=type_key in st.session_state.selected_exercise_types,
                        key=f"extype_{type_key}"
                    ):
                        selected_types.append(type_key)
                st.session_state.selected_exercise_types = selected_types if selected_types else ["standard"]

        # Competency goals
        from src.cache import get_curriculum_goals
        competency_goals = get_curriculum_goals(selected_grade)
        if competency_goals:
            st.markdown("**🎯 Kompetansemål (LK20)**")
            selected_goals = []
            for i, goal in enumerate(competency_goals[:6]):
                display = goal[:80] + "..." if len(goal) > 80 else goal
                if st.checkbox(display, key=f"goal_{i}", help=goal):
                    selected_goals.append(goal)
            st.session_state.selected_competency_goals = selected_goals

    # ------------------------------------------------------------------
    # GENERATE BUTTON
    # ------------------------------------------------------------------
    st.markdown("---")

    can_generate = api_configured and bool(topic)

    if not topic:
        st.info("Velg eller skriv inn et tema for å starte.")

    generate_clicked = st.button(
        "◇ Generer materiale",
        disabled=not can_generate,
        use_container_width=True,
        type="primary"
    )

    # ------------------------------------------------------------------
    # GENERATION LOGIC
    # ------------------------------------------------------------------
    if generate_clicked:
        st.session_state.latex_result = None
        st.session_state.pdf_path = None
        st.session_state.pdf_bytes = None
        st.session_state.generation_complete = False

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_topic = "".join(c for c in topic if c.isalnum() or c in (' ', '-', '_')).strip().replace(' ', '_')[:30]
        filename = f"{safe_topic}_{selected_grade.replace(' ', '_').replace('.', '')}_{timestamp}"

        # Build content options
        from src.cache import get_all_exercise_types
        exercise_types = get_all_exercise_types()
        exercise_type_instructions = [
            exercise_types[et]["instruction"]
            for et in st.session_state.selected_exercise_types
            if et in exercise_types
        ]

        selected_material = "arbeidsark"
        for tmpl in TEMPLATES.values():
            if st.session_state.selected_template and st.session_state.selected_template in TEMPLATES:
                selected_material = TEMPLATES[st.session_state.selected_template]["config"].get("material_type", "arbeidsark")
                break

        content_options = {
            "include_theory": st.session_state.include_theory,
            "include_examples": st.session_state.include_examples,
            "include_exercises": st.session_state.include_exercises,
            "include_solutions": st.session_state.include_solutions,
            "include_graphs": st.session_state.include_graphs,
            "include_tips": st.session_state.include_tips,
            "num_exercises": st.session_state.num_exercises,
            "difficulty": st.session_state.difficulty_level,
            "material_type": selected_material,
            "competency_goals": st.session_state.selected_competency_goals,
            "exercise_types": st.session_state.selected_exercise_types,
            "exercise_type_instructions": exercise_type_instructions,
            "differentiation_mode": st.session_state.differentiation_mode,
            "language_level": st.session_state.get("language_level", "standard"),
        }

        # Build instructions
        content_instructions = []
        if not st.session_state.include_theory:
            content_instructions.append("IKKE inkluder teori eller definisjoner")
        if not st.session_state.include_examples:
            content_instructions.append("IKKE inkluder eksempler")
        if st.session_state.include_exercises:
            content_instructions.append(f"Lag {st.session_state.num_exercises} oppgaver")
        if st.session_state.differentiation_mode:
            content_instructions.append("Lag tre nivåer: lett, middels, vanskelig")
        instructions = ". ".join(content_instructions)

        # Progress
        progress_bar = st.progress(0, text="Pedagogen planlegger innholdet...")

        try:
            progress_bar.progress(10, text="🎓 Pedagogen planlegger...")

            latex_result = run_crew(
                grade=grade_options[selected_grade],
                topic=topic,
                material_type=selected_material,
                instructions=instructions,
                content_options=content_options
            )
            st.session_state.latex_result = latex_result

            progress_bar.progress(80, text="📄 Lagrer filer...")

            tex_path = save_tex_file(latex_result, filename)
            pdf_path = generate_pdf(latex_result, filename)
            if pdf_path:
                st.session_state.pdf_path = pdf_path
                with open(pdf_path, "rb") as f:
                    st.session_state.pdf_bytes = f.read()

            progress_bar.progress(100, text="✅ Ferdig!")

            # Record history
            try:
                from src.storage import add_to_history as save_to_storage
                save_to_storage(
                    topic=topic, grade=selected_grade,
                    material_type=selected_material,
                    tex_content=latex_result, pdf_path=pdf_path
                )
            except Exception:
                pass

            # Record usage
            try:
                from src.tools import record_generation
                record_generation(
                    topic=topic, grade=selected_grade,
                    material_type=selected_material,
                    num_exercises=st.session_state.num_exercises
                )
            except Exception:
                pass

            st.session_state.generation_complete = True
            st.rerun()

        except Exception as e:
            progress_bar.empty()
            st.error(f"Feil under generering: {e}")

    # ------------------------------------------------------------------
    # RESULTS
    # ------------------------------------------------------------------
    if st.session_state.generation_complete and st.session_state.latex_result:
        st.markdown("---")
        st.success("Materiale generert!")

        # Download row
        dl_col1, dl_col2, dl_col3 = st.columns(3)

        with dl_col1:
            st.download_button(
                "📄 Last ned LaTeX",
                data=st.session_state.latex_result,
                file_name=f"matematikk_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tex",
                mime="text/plain",
                use_container_width=True
            )

        with dl_col2:
            if st.session_state.pdf_bytes:
                st.download_button(
                    "📕 Last ned PDF",
                    data=st.session_state.pdf_bytes,
                    file_name=f"matematikk_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            else:
                st.button("📕 PDF", disabled=True, use_container_width=True, help="Krever pdflatex")

        with dl_col3:
            try:
                from src.tools import is_word_export_available, latex_to_word
                if is_word_export_available():
                    if st.button("📘 Word (.docx)", use_container_width=True):
                        with st.spinner("Konverterer..."):
                            output_path = Path("output") / f"matematikk_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
                            output_path.parent.mkdir(exist_ok=True)
                            word_path = latex_to_word(st.session_state.latex_result, str(output_path))
                            if word_path and Path(word_path).exists():
                                with open(word_path, "rb") as f:
                                    st.download_button(
                                        "⬇️ Last ned Word",
                                        data=f.read(),
                                        file_name=Path(word_path).name,
                                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                        use_container_width=True
                                    )
                else:
                    st.button("📘 Word", disabled=True, use_container_width=True)
            except ImportError:
                st.button("📘 Word", disabled=True, use_container_width=True)

        # PDF Preview
        if st.session_state.pdf_bytes:
            pdf_b64 = base64.b64encode(st.session_state.pdf_bytes).decode('utf-8')
            st.markdown(f'''
            <iframe
                src="data:application/pdf;base64,{pdf_b64}"
                width="100%" height="600"
                style="border: 1px solid #334155; border-radius: 12px; margin-top: 1rem;"
            ></iframe>
            ''', unsafe_allow_html=True)

        # LaTeX code viewer
        with st.expander("👁️ Se LaTeX-kode"):
            st.code(st.session_state.latex_result, language="latex")

        # Re-compile after edit
        with st.expander("✏️ Rediger og kompiler på nytt"):
            edited = st.text_area(
                "LaTeX", value=st.session_state.latex_result,
                height=300, label_visibility="collapsed"
            )
            if st.button("🔄 Kompiler på nytt", use_container_width=True):
                st.session_state.latex_result = edited
                with st.spinner("Kompilerer..."):
                    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                    pdf_path = generate_pdf(edited, f"redigert_{ts}")
                    if pdf_path:
                        st.session_state.pdf_path = pdf_path
                        with open(pdf_path, "rb") as f:
                            st.session_state.pdf_bytes = f.read()
                        st.rerun()

    # ------------------------------------------------------------------
    # FOOTER
    # ------------------------------------------------------------------
    st.markdown("""
    <div style="text-align: center; color: #64748b; font-size: 0.75rem; margin-top: 3rem; padding: 1rem 0;">
        MateMaTeX &copy; 2026 &bull; <a href="https://www.crewai.com/" target="_blank" style="color: #f59e0b; text-decoration: none;">CrewAI</a>
        + <a href="https://streamlit.io/" target="_blank" style="color: #f59e0b; text-decoration: none;">Streamlit</a>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
