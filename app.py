"""
MateMaTeX - Matematikkverkstedet AI
AI Editorial Team for generating math worksheets and chapters in LaTeX/PDF format.
"""

import os

# Load environment variables BEFORE any other imports
from dotenv import load_dotenv
load_dotenv()

import streamlit as st
from pathlib import Path
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="MateMaTeX",
    page_icon="📐",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Dark theme CSS
st.markdown("""
<style>
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Global dark theme */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        font-family: 'Inter', sans-serif;
    }
    
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main container */
    .main-container {
        max-width: 600px;
        margin: 0 auto;
        padding: 2rem 1rem;
    }
    
    /* Logo and title */
    .logo-title {
        text-align: center;
        margin-bottom: 2rem;
    }
    .logo-title h1 {
        color: #f8fafc;
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
    }
    .logo-title p {
        color: #94a3b8;
        font-size: 0.95rem;
        margin-top: 0.5rem;
    }
    
    /* Card styling */
    .input-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 1rem;
    }
    
    .card-label {
        color: #94a3b8;
        font-size: 0.85rem;
        font-weight: 500;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Custom select boxes */
    .stSelectbox > div > div {
        background: #0f172a !important;
        border: 1px solid #334155 !important;
        border-radius: 10px !important;
        color: #f8fafc !important;
    }
    
    .stSelectbox > div > div:hover {
        border-color: #3b82f6 !important;
    }
    
    /* Custom text input */
    .stTextInput > div > div > input {
        background: #0f172a !important;
        border: 1px solid #334155 !important;
        border-radius: 10px !important;
        color: #f8fafc !important;
        padding: 0.75rem 1rem !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2) !important;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: #64748b !important;
    }
    
    /* Toggle cards section */
    .toggle-section {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    
    .toggle-header {
        color: #94a3b8;
        font-size: 0.85rem;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        cursor: pointer;
        margin-bottom: 1rem;
    }
    
    .toggle-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 0.75rem;
    }
    
    .toggle-card {
        background: #0f172a;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 1rem;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .toggle-card:hover {
        border-color: #3b82f6;
    }
    
    .toggle-card.active {
        background: rgba(59, 130, 246, 0.15);
        border-color: #3b82f6;
    }
    
    .toggle-card-title {
        color: #f8fafc;
        font-size: 0.9rem;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 0.25rem;
    }
    
    .toggle-card-desc {
        color: #64748b;
        font-size: 0.75rem;
    }
    
    /* Generate button */
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.875rem 2rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        width: 100% !important;
        margin-top: 1rem !important;
        transition: all 0.2s ease !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4) !important;
    }
    
    /* Status messages */
    .stSuccess, .stInfo, .stWarning, .stError {
        background: #1e293b !important;
        border-radius: 10px !important;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: #1e293b !important;
        border-radius: 10px !important;
        color: #f8fafc !important;
    }
    
    /* Expander content */
    .streamlit-expanderContent {
        background: #1e293b !important;
        border: 1px solid #334155 !important;
        border-top: none !important;
        border-radius: 0 0 10px 10px !important;
    }
    
    /* Slider styling */
    .stSlider > div > div > div {
        background: #334155 !important;
    }
    
    .stSlider > div > div > div > div {
        background: #3b82f6 !important;
    }
    
    /* Multiselect styling */
    .stMultiSelect > div > div {
        background: #0f172a !important;
        border: 1px solid #334155 !important;
        border-radius: 10px !important;
    }
    
    /* Download buttons */
    .stDownloadButton > button {
        background: #1e293b !important;
        border: 1px solid #334155 !important;
        color: #f8fafc !important;
        border-radius: 10px !important;
    }
    
    .stDownloadButton > button:hover {
        background: #334155 !important;
        border-color: #3b82f6 !important;
    }
    
    /* Checkbox styling */
    .stCheckbox {
        background: #0f172a;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 0.5rem;
    }
    
    .stCheckbox:has(input:checked) {
        background: rgba(59, 130, 246, 0.15);
        border-color: #3b82f6;
    }
    
    /* Checkbox label text - make it more readable */
    .stCheckbox label {
        color: #e2e8f0 !important;
        font-weight: 500 !important;
    }
    
    .stCheckbox label span {
        color: #e2e8f0 !important;
    }
    
    .stCheckbox p {
        color: #e2e8f0 !important;
    }
    
    /* Radio button styling */
    .stRadio > div {
        background: #0f172a;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 0.75rem;
    }
    
    .stRadio label {
        color: #e2e8f0 !important;
        font-weight: 500 !important;
    }
    
    .stRadio [data-baseweb="radio"] {
        background: #334155 !important;
    }
    
    .stRadio [data-baseweb="radio"]:has(input:checked) {
        background: #3b82f6 !important;
    }
    
    /* API status badge */
    .api-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1rem;
        background: rgba(34, 197, 94, 0.15);
        border: 1px solid rgba(34, 197, 94, 0.3);
        border-radius: 20px;
        color: #22c55e;
        font-size: 0.8rem;
        margin-bottom: 1.5rem;
    }
    
    .api-badge.error {
        background: rgba(239, 68, 68, 0.15);
        border-color: rgba(239, 68, 68, 0.3);
        color: #ef4444;
    }
    
    /* Progress section */
    .progress-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    .progress-item {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.5rem 0;
        color: #94a3b8;
    }
    
    .progress-item.active {
        color: #3b82f6;
    }
    
    .progress-item.done {
        color: #22c55e;
    }
    
    /* Results section */
    .results-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    /* Divider */
    hr {
        border: none;
        border-top: 1px solid #334155;
        margin: 1.5rem 0;
    }
    
    /* Hide streamlit branding */
    .viewerBadge_container__1QSob {
        display: none;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables."""
    defaults = {
        "latex_result": None,
        "pdf_path": None,
        "pdf_bytes": None,  # For PDF preview
        "generation_complete": False,
        "error_message": None,
        "include_theory": True,
        "include_examples": True,
        "include_exercises": True,
        "include_solutions": True,
        "include_graphs": True,
        "include_tips": False,
        "difficulty_level": "Middels",
        "selected_topic": None,
        "custom_topic": "",
        "selected_competency_goals": [],
        "selected_exercise_types": ["standard"],
        "differentiation_mode": False,
        "num_exercises": 10,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def run_crew(grade: str, topic: str, material_type: str, instructions: str, content_options: dict) -> str:
    """Run the CrewAI editorial team to generate content."""
    from crewai import Crew, Process
    from src.agents import MathBookAgents
    from src.tasks import MathTasks
    
    agents = MathBookAgents()
    tasks = MathTasks()
    
    pedagogue = agents.pedagogue()
    mathematician = agents.mathematician()
    illustrator = agents.illustrator()
    chief_editor = agents.chief_editor()
    
    full_topic = topic
    if instructions:
        full_topic = f"{topic}\n\nTilleggsinstruksjoner: {instructions}"
    
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
    
    if hasattr(result, 'raw'):
        return result.raw
    return str(result)


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


def main():
    """Main application function."""
    initialize_session_state()
    
    # Check API status
    api_configured = bool(os.getenv("GOOGLE_API_KEY"))
    model_name = os.getenv("GOOGLE_MODEL", "gemini-2.0-flash")
    
    # Header
    st.markdown("""
    <div class="logo-title">
        <h1>📐 MateMaTeX</h1>
        <p>Generer profesjonelle matematikkoppgaver med AI</p>
    </div>
    """, unsafe_allow_html=True)
    
    # API Status Badge
    if api_configured:
        st.markdown(f"""
        <div style="text-align: center;">
            <span class="api-badge">✓ {model_name}</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="text-align: center;">
            <span class="api-badge error">✕ API ikke konfigurert</span>
        </div>
        """, unsafe_allow_html=True)
    
    # Import curriculum data
    from src.curriculum import get_topics_for_grade, get_competency_goals, get_exercise_types
    
    # Grade Level
    st.markdown('<p class="card-label">📚 Klassetrinn</p>', unsafe_allow_html=True)
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
    selected_grade = st.selectbox(
        "Klassetrinn",
        options=list(grade_options.keys()),
        index=4,
        label_visibility="collapsed"
    )
    
    # Material Type
    st.markdown('<p class="card-label">📄 Materialtype</p>', unsafe_allow_html=True)
    material_options = {
        "📖 Kapittel / Lærestoff": "kapittel",
        "📝 Arbeidsark": "arbeidsark",
        "📋 Prøve / Eksamen": "prøve",
        "📚 Lekseark": "lekseark",
    }
    selected_material_display = st.selectbox(
        "Materialtype",
        options=list(material_options.keys()),
        label_visibility="collapsed"
    )
    selected_material = material_options[selected_material_display]
    
    # ===== FEATURE 1: Topic Library =====
    st.markdown('<p class="card-label">📖 Tema fra læreplan</p>', unsafe_allow_html=True)
    
    topics_by_category = get_topics_for_grade(selected_grade)
    
    # Build flat topic list with category prefix
    topic_choices = ["-- Velg tema --", "✍️ Skriv eget tema..."]
    for category, topics in topics_by_category.items():
        for t in topics:
            topic_choices.append(f"{t}")
    
    selected_topic_choice = st.selectbox(
        "Velg tema",
        options=topic_choices,
        label_visibility="collapsed"
    )
    
    # Custom topic input if selected
    topic = ""
    if selected_topic_choice == "✍️ Skriv eget tema...":
        st.markdown('<p class="card-label">✏️ Eget tema</p>', unsafe_allow_html=True)
        topic = st.text_input(
            "Skriv tema",
            placeholder="f.eks. Lineære funksjoner, Pytagoras, Brøk...",
            label_visibility="collapsed"
        )
    elif selected_topic_choice != "-- Velg tema --":
        topic = selected_topic_choice
    
    # ===== FEATURE 3: LK20 Competency Goals =====
    competency_goals = get_competency_goals(selected_grade)
    
    if competency_goals:
        with st.expander("🎯 Kompetansemål (LK20)", expanded=False):
            st.markdown("""
            <p style="color: #94a3b8; font-size: 0.85rem; margin-bottom: 1rem;">
            Velg hvilke kompetansemål materialet skal dekke. Disse vil vises øverst i dokumentet.
            </p>
            """, unsafe_allow_html=True)
            
            selected_goals = []
            for i, goal in enumerate(competency_goals):
                if st.checkbox(goal, key=f"goal_{i}"):
                    selected_goals.append(goal)
            
            st.session_state.selected_competency_goals = selected_goals
    
    # Content customization
    st.markdown('<p class="card-label">⚙️ Tilpass innhold</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.session_state.include_theory = st.checkbox(
            "📘 Teori",
            value=st.session_state.include_theory,
            help="Definisjoner og forklaringer"
        )
        st.session_state.include_examples = st.checkbox(
            "💡 Eksempler", 
            value=st.session_state.include_examples,
            help="Gjennomgåtte eksempler"
        )
        st.session_state.include_graphs = st.checkbox(
            "📊 Grafer/Figurer",
            value=st.session_state.include_graphs,
            help="TikZ-illustrasjoner"
        )
    
    with col2:
        st.session_state.include_exercises = st.checkbox(
            "✍️ Oppgaver",
            value=st.session_state.include_exercises,
            help="Øvingsoppgaver"
        )
        st.session_state.include_solutions = st.checkbox(
            "🔑 Fasit",
            value=st.session_state.include_solutions,
            help="Løsningsforslag"
        )
        st.session_state.include_tips = st.checkbox(
            "💬 Tips",
            value=st.session_state.include_tips,
            help="Hint og huskelapper"
        )
    
    # Number of exercises selector (only shown when exercises are enabled)
    if st.session_state.include_exercises:
        st.markdown('<p class="card-label">🔢 Antall oppgaver</p>', unsafe_allow_html=True)
        st.session_state.num_exercises = st.slider(
            "Antall oppgaver",
            min_value=3,
            max_value=25,
            value=st.session_state.num_exercises,
            step=1,
            label_visibility="collapsed"
        )
        
        # ===== FEATURE 2: Exercise Types =====
        exercise_types = get_exercise_types()
        
        with st.expander("📝 Oppgavetyper", expanded=False):
            st.markdown("""
            <p style="color: #94a3b8; font-size: 0.85rem; margin-bottom: 1rem;">
            Velg hvilke typer oppgaver som skal inkluderes. Du kan velge flere.
            </p>
            """, unsafe_allow_html=True)
            
            selected_types = []
            cols = st.columns(2)
            for i, (type_key, type_info) in enumerate(exercise_types.items()):
                with cols[i % 2]:
                    if st.checkbox(
                        type_info["name"],
                        value=type_key in st.session_state.selected_exercise_types,
                        help=type_info["description"],
                        key=f"extype_{type_key}"
                    ):
                        selected_types.append(type_key)
            
            if selected_types:
                st.session_state.selected_exercise_types = selected_types
            else:
                st.session_state.selected_exercise_types = ["standard"]
    
    # Difficulty level selector
    st.markdown('<p class="card-label">📈 Vanskelighetsgrad</p>', unsafe_allow_html=True)
    difficulty_options = ["🟢 Lett", "🟡 Middels", "🔴 Vanskelig"]
    difficulty_index = {"Lett": 0, "Middels": 1, "Vanskelig": 2}.get(
        st.session_state.difficulty_level, 1
    )
    selected_difficulty = st.radio(
        "Vanskelighetsgrad",
        options=difficulty_options,
        index=difficulty_index,
        horizontal=True,
        label_visibility="collapsed"
    )
    # Extract clean difficulty name
    st.session_state.difficulty_level = selected_difficulty.split(" ")[1]
    
    # ===== FEATURE 4: Differentiation Mode =====
    st.markdown('<p class="card-label">🎚️ Differensiering</p>', unsafe_allow_html=True)
    st.session_state.differentiation_mode = st.checkbox(
        "📊 Generer 3 nivåer (lett, middels, vanskelig)",
        value=st.session_state.differentiation_mode,
        help="Lag tre versjoner av arbeidsarket med ulik vanskelighetsgrad"
    )
    
    # Build instructions from checkboxes and difficulty
    content_instructions = []
    
    # Get number of exercises (default to 10 if not set)
    num_exercises = st.session_state.get("num_exercises", 10)
    
    # Build explicit content inclusion/exclusion lists
    include_list = []
    exclude_list = []
    
    if st.session_state.include_theory:
        include_list.append("teori og definisjoner")
    else:
        exclude_list.append("teori")
        exclude_list.append("definisjoner")
    
    if st.session_state.include_examples:
        include_list.append("gjennomgåtte eksempler")
    else:
        exclude_list.append("eksempler")
    
    if st.session_state.include_exercises:
        include_list.append(f"{num_exercises} oppgaver")
    else:
        exclude_list.append("oppgaver")
    
    if st.session_state.include_solutions:
        include_list.append("løsningsforslag/fasit")
    else:
        exclude_list.append("løsningsforslag")
        exclude_list.append("fasit")
    
    if st.session_state.include_graphs:
        include_list.append("grafer og figurer")
    else:
        exclude_list.append("grafer")
        exclude_list.append("figurer")
        exclude_list.append("TikZ-illustrasjoner")
    
    if st.session_state.include_tips:
        include_list.append("tips og hint")
    else:
        exclude_list.append("tips")
        exclude_list.append("hint")
    
    # Create very explicit instructions
    if exclude_list:
        content_instructions.append(
            f"VIKTIG - IKKE INKLUDER følgende: {', '.join(exclude_list)}. "
            f"Disse elementene skal IKKE være med i dokumentet overhodet."
        )
    
    if include_list:
        content_instructions.append(
            f"INKLUDER KUN følgende: {', '.join(include_list)}. "
            f"Ingenting annet skal være med."
        )
    
    # Special handling for worksheet mode (arbeidsark)
    is_worksheet = selected_material == "arbeidsark"
    
    if is_worksheet:
        # Check if ONLY exercises are selected (no theory, no examples)
        only_exercises = (
            st.session_state.include_exercises and 
            not st.session_state.include_theory and 
            not st.session_state.include_examples
        )
        
        if only_exercises:
            content_instructions.insert(0,
                f"RENT OPPGAVEARK: Dette dokumentet skal KUN inneholde oppgaver. "
                f"ABSOLUTT INGEN teori, definisjoner, forklaringer eller eksempler. "
                f"Start dokumentet med kun en tittel, deretter gå DIREKTE til oppgavene. "
                f"Lag NØYAKTIG {num_exercises} oppgaver med stigende vanskelighetsgrad. "
                f"Bruk \\begin{{taskbox}}{{Oppgave N}} for hver oppgave."
            )
        else:
            content_instructions.insert(0,
                f"ARBEIDSARK: Lag et arbeidsark med {num_exercises} oppgaver."
            )
        
        if st.session_state.include_solutions:
            content_instructions.append(
                "Inkluder løsningsforslag (fasit) på SLUTTEN av dokumentet i multicols-format."
            )
    else:
        # For kapittel/prøve modes
        if st.session_state.include_exercises:
            content_instructions.append(f"Lag {num_exercises} oppgaver med varierende vanskelighetsgrad.")
    
    # Add difficulty level instruction
    difficulty = st.session_state.difficulty_level
    if st.session_state.differentiation_mode:
        content_instructions.append(
            "DIFFERENSIERING: Lag TRE separate seksjoner med økende vanskelighetsgrad: "
            "1) 'Nivå 1 - Lett' med enkle oppgaver, "
            "2) 'Nivå 2 - Middels' med moderate oppgaver, "
            "3) 'Nivå 3 - Vanskelig' med utfordrende oppgaver. "
            "Hver seksjon skal ha like mange oppgaver."
        )
    elif difficulty == "Lett":
        content_instructions.append("Vanskelighetsgrad: LETT - Bruk enkle tall, grunnleggende konsepter, mye støtte og hint. Oppgavene skal være lette å løse")
    elif difficulty == "Vanskelig":
        content_instructions.append("Vanskelighetsgrad: VANSKELIG - Bruk komplekse tall, avanserte konsepter, utfordrende oppgaver med flere steg. Krev dypere forståelse")
    else:
        content_instructions.append("Vanskelighetsgrad: MIDDELS - Balansert vanskelighetsgrad med variasjon fra enkle til litt utfordrende oppgaver")
    
    # Add competency goals instruction
    if st.session_state.selected_competency_goals:
        goals_text = "; ".join(st.session_state.selected_competency_goals)
        content_instructions.append(
            f"KOMPETANSEMÅL: Materialet skal dekke følgende LK20-kompetansemål: {goals_text}. "
            "List disse kompetansemålene øverst i dokumentet under overskriften 'Kompetansemål'."
        )
    
    # Add exercise types instruction
    exercise_types = get_exercise_types()
    if st.session_state.selected_exercise_types and len(st.session_state.selected_exercise_types) > 0:
        type_instructions = []
        for etype in st.session_state.selected_exercise_types:
            if etype in exercise_types:
                type_instructions.append(exercise_types[etype]["instruction"])
        if type_instructions:
            content_instructions.append("OPPGAVETYPER: " + " ".join(type_instructions))
    
    # Graph instruction (applies to both modes)
    if not is_worksheet and not st.session_state.include_graphs:
        pass  # Already handled above
    elif is_worksheet and st.session_state.include_graphs:
        content_instructions.append("Inkluder relevante figurer/grafer i oppgavene der det er nyttig")
    
    if st.session_state.include_tips and not is_worksheet:
        content_instructions.append("Inkluder tips og huskelapper i merk-bokser")
    
    instructions = ". ".join(content_instructions) if content_instructions else ""
    
    # Validation
    can_generate = api_configured and bool(topic)
    
    if not topic:
        st.warning("Skriv inn et tema for å generere materiale")
    
    # Generate Button
    if st.button("🚀 Generer Materiale", disabled=not can_generate, use_container_width=True):
        st.session_state.latex_result = None
        st.session_state.pdf_path = None
        st.session_state.generation_complete = False
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_topic = "".join(c for c in topic if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_topic = safe_topic.replace(' ', '_')[:30]
        filename = f"{safe_topic}_{selected_grade.replace(' ', '_').replace('.', '')}_{timestamp}"
        
        # Progress display
        progress = st.empty()
        
        with progress.container():
            st.markdown("""
            <div class="progress-card">
                <div class="progress-item active">🎓 Pedagogen planlegger...</div>
                <div class="progress-item">🔢 Matematikeren skriver...</div>
                <div class="progress-item">🎨 Illustratøren tegner...</div>
                <div class="progress-item">✍️ Redaktøren ferdigstiller...</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Build exercise type instructions
        exercise_type_instructions = []
        exercise_types = get_exercise_types()
        for etype in st.session_state.selected_exercise_types:
            if etype in exercise_types:
                exercise_type_instructions.append(exercise_types[etype]["instruction"])
        
        # Build content options dictionary
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
        }
        
        try:
            with st.spinner("AI-teamet arbeider... (2-5 min)"):
                latex_result = run_crew(
                    grade=grade_options[selected_grade],
                    topic=topic,
                    material_type=selected_material,
                    instructions=instructions,
                    content_options=content_options
                )
                st.session_state.latex_result = latex_result
            
            progress.empty()
            
            # Save files
            with st.spinner("Lagrer filer..."):
                tex_path = save_tex_file(latex_result, filename)
                pdf_path = generate_pdf(latex_result, filename)
                if pdf_path:
                    st.session_state.pdf_path = pdf_path
                    # Store PDF bytes for preview
                    with open(pdf_path, "rb") as f:
                        st.session_state.pdf_bytes = f.read()
            
            st.session_state.generation_complete = True
            st.rerun()
            
        except Exception as e:
            progress.empty()
            st.error(f"Feil under generering: {e}")
    
    # Results
    if st.session_state.generation_complete and st.session_state.latex_result:
        st.markdown("---")
        st.success("✨ Materiale generert!")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.download_button(
                "📄 Last ned .tex",
                data=st.session_state.latex_result,
                file_name=f"matematikk_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tex",
                mime="text/plain",
                use_container_width=True
            )
        
        with col2:
            if st.session_state.pdf_path and Path(st.session_state.pdf_path).exists():
                with open(st.session_state.pdf_path, "rb") as f:
                    st.download_button(
                        "📕 Last ned PDF",
                        data=f.read(),
                        file_name=Path(st.session_state.pdf_path).name,
                        mime="application/pdf",
                        use_container_width=True
                    )
            else:
                st.info("PDF krever pdflatex")
        
        # ===== FEATURE 5: PDF Preview =====
        if st.session_state.pdf_bytes:
            import base64
            st.markdown('<p class="card-label" style="margin-top: 1.5rem;">👁️ Forhåndsvisning</p>', unsafe_allow_html=True)
            
            # Encode PDF to base64 for embedding
            pdf_base64 = base64.b64encode(st.session_state.pdf_bytes).decode('utf-8')
            pdf_display = f'''
            <iframe 
                src="data:application/pdf;base64,{pdf_base64}" 
                width="100%" 
                height="600px" 
                style="border: 1px solid #334155; border-radius: 10px; background: #fff;"
            ></iframe>
            '''
            st.markdown(pdf_display, unsafe_allow_html=True)
        
        with st.expander("👁️ Se LaTeX-kode"):
            st.code(st.session_state.latex_result, language="latex")
    
    # Footer
    st.markdown("""
    <div style="text-align: center; color: #64748b; font-size: 0.8rem; margin-top: 3rem;">
        MateMaTeX © 2026 • Bygget med CrewAI
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
