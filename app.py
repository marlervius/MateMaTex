"""
MateMaTeX - Matematikkverkstedet AI
AI Editorial Team for generating math worksheets and chapters in LaTeX/PDF format.
Redesigned with enhanced UX and visual aesthetics.
"""

import os
import json
from datetime import datetime
from pathlib import Path

# Load environment variables BEFORE any other imports
from dotenv import load_dotenv
load_dotenv()

import streamlit as st

# Page configuration
st.set_page_config(
    page_title="MateMaTeX",
    page_icon="◇",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CUSTOM CSS - Modern, Distinctive Design
# ============================================================================
st.markdown("""
<style>
    /* Import distinctive fonts */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&display=swap');
    
    /* CSS Variables for theming */
    :root {
        --bg-primary: #0a0a0f;
        --bg-secondary: #12121a;
        --bg-card: #1a1a24;
        --bg-card-hover: #22222e;
        --border-subtle: #2a2a3a;
        --border-accent: #3d3d52;
        --text-primary: #f0f0f5;
        --text-secondary: #9090a0;
        --text-muted: #606070;
        --accent-gold: #f0b429;
        --accent-gold-dim: #c4941f;
        --accent-amber: #f59e0b;
        --accent-emerald: #10b981;
        --accent-rose: #f43f5e;
        --accent-violet: #8b5cf6;
        --gradient-gold: linear-gradient(135deg, #f0b429 0%, #f59e0b 50%, #d97706 100%);
        --gradient-dark: linear-gradient(180deg, #0a0a0f 0%, #12121a 100%);
        --shadow-lg: 0 10px 40px rgba(0,0,0,0.4);
        --shadow-glow: 0 0 30px rgba(240,180,41,0.15);
    }
    
    /* Global styles */
    .stApp {
        background: var(--gradient-dark);
        font-family: 'Outfit', sans-serif;
    }
    
    /* Hide Streamlit branding */
    #MainMenu, footer, header, .stDeployButton {
        visibility: hidden;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background: var(--bg-secondary);
        border-right: 1px solid var(--border-subtle);
    }
    
    section[data-testid="stSidebar"] .stMarkdown {
        color: var(--text-primary);
    }
    
    /* Main content area */
    .main .block-container {
        padding: 2rem 3rem;
        max-width: 1200px;
    }
    
    /* Hero section */
    .hero-container {
        text-align: center;
        padding: 2rem 0 3rem 0;
        margin-bottom: 2rem;
    }
    
    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        background: rgba(240, 180, 41, 0.1);
        border: 1px solid rgba(240, 180, 41, 0.2);
        padding: 0.4rem 1rem;
        border-radius: 100px;
        font-size: 0.8rem;
        color: var(--accent-gold);
        margin-bottom: 1.5rem;
        font-weight: 500;
        letter-spacing: 0.5px;
    }
    
    .hero-title {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #fff 0%, #f0b429 50%, #f59e0b 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0 0 1rem 0;
        letter-spacing: -1px;
    }
    
    .hero-subtitle {
        font-size: 1.15rem;
        color: var(--text-secondary);
        max-width: 500px;
        margin: 0 auto;
        line-height: 1.6;
    }
    
    /* Card components */
    .config-card {
        background: var(--bg-card);
        border: 1px solid var(--border-subtle);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.25rem;
        transition: all 0.2s ease;
    }
    
    .config-card:hover {
        border-color: var(--border-accent);
        background: var(--bg-card-hover);
    }
    
    .card-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 1rem;
    }
    
    .card-icon {
        width: 36px;
        height: 36px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.1rem;
    }
    
    .card-icon.gold { background: rgba(240, 180, 41, 0.15); }
    .card-icon.emerald { background: rgba(16, 185, 129, 0.15); }
    .card-icon.violet { background: rgba(139, 92, 246, 0.15); }
    .card-icon.rose { background: rgba(244, 63, 94, 0.15); }
    
    .card-title {
        font-size: 0.95rem;
        font-weight: 600;
        color: var(--text-primary);
        margin: 0;
    }
    
    .card-description {
        font-size: 0.8rem;
        color: var(--text-muted);
        margin: 0;
    }
    
    /* Template cards */
    .template-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 1rem 0;
    }
    
    .template-card {
        background: var(--bg-card);
        border: 1px solid var(--border-subtle);
        border-radius: 12px;
        padding: 1.25rem;
        cursor: pointer;
        transition: all 0.2s ease;
        position: relative;
        overflow: hidden;
    }
    
    .template-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: var(--gradient-gold);
        opacity: 0;
        transition: opacity 0.2s ease;
    }
    
    .template-card:hover {
        border-color: var(--accent-gold);
        transform: translateY(-2px);
        box-shadow: var(--shadow-glow);
    }
    
    .template-card:hover::before {
        opacity: 1;
    }
    
    .template-emoji {
        font-size: 2rem;
        margin-bottom: 0.75rem;
    }
    
    .template-name {
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 0.25rem;
    }
    
    .template-desc {
        font-size: 0.8rem;
        color: var(--text-muted);
    }
    
    /* Form elements */
    .stSelectbox > div > div,
    .stMultiSelect > div > div {
        background: var(--bg-secondary) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 10px !important;
        color: var(--text-primary) !important;
    }
    
    .stSelectbox > div > div:hover,
    .stMultiSelect > div > div:hover {
        border-color: var(--accent-gold) !important;
    }
    
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: var(--bg-secondary) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 10px !important;
        color: var(--text-primary) !important;
        font-family: 'Outfit', sans-serif !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--accent-gold) !important;
        box-shadow: 0 0 0 2px rgba(240, 180, 41, 0.15) !important;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: var(--text-muted) !important;
    }
    
    /* Slider */
    .stSlider > div > div > div {
        background: var(--border-subtle) !important;
    }
    
    .stSlider > div > div > div > div {
        background: var(--accent-gold) !important;
    }
    
    /* Checkbox styling */
    .stCheckbox {
        background: var(--bg-secondary);
        border: 1px solid var(--border-subtle);
        border-radius: 10px;
        padding: 0.75rem 1rem;
        margin-bottom: 0.5rem;
        transition: all 0.2s ease;
    }
    
    .stCheckbox:hover {
        border-color: var(--border-accent);
    }
    
    .stCheckbox:has(input:checked) {
        background: rgba(240, 180, 41, 0.08);
        border-color: rgba(240, 180, 41, 0.3);
    }
    
    .stCheckbox label {
        color: var(--text-primary) !important;
        font-weight: 500 !important;
    }
    
    /* Radio buttons */
    .stRadio > div {
        background: var(--bg-secondary);
        border: 1px solid var(--border-subtle);
        border-radius: 10px;
        padding: 0.75rem;
    }
    
    .stRadio label {
        color: var(--text-primary) !important;
    }
    
    /* Generate button */
    .stButton > button {
        background: var(--gradient-gold) !important;
        color: #0a0a0f !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.875rem 2rem !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        font-family: 'Outfit', sans-serif !important;
        letter-spacing: 0.3px !important;
        width: 100% !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 20px rgba(240, 180, 41, 0.25) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 30px rgba(240, 180, 41, 0.35) !important;
    }
    
    .stButton > button:active {
        transform: translateY(0) !important;
    }
    
    /* Download buttons */
    .stDownloadButton > button {
        background: var(--bg-card) !important;
        border: 1px solid var(--border-accent) !important;
        color: var(--text-primary) !important;
        border-radius: 10px !important;
        font-family: 'Outfit', sans-serif !important;
        transition: all 0.2s ease !important;
    }
    
    .stDownloadButton > button:hover {
        background: var(--bg-card-hover) !important;
        border-color: var(--accent-gold) !important;
    }
    
    /* Progress section */
    .progress-container {
        background: var(--bg-card);
        border: 1px solid var(--border-subtle);
        border-radius: 16px;
        padding: 2rem;
        margin: 1.5rem 0;
    }
    
    .progress-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .progress-steps {
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }
    
    .progress-step {
        display: flex;
        align-items: center;
        gap: 1rem;
        padding: 0.75rem 1rem;
        border-radius: 10px;
        background: var(--bg-secondary);
        border: 1px solid transparent;
        transition: all 0.3s ease;
    }
    
    .progress-step.active {
        border-color: var(--accent-gold);
        background: rgba(240, 180, 41, 0.08);
    }
    
    .progress-step.done {
        border-color: var(--accent-emerald);
        background: rgba(16, 185, 129, 0.08);
    }
    
    .step-indicator {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 600;
        font-size: 0.85rem;
        background: var(--bg-card);
        color: var(--text-muted);
        border: 2px solid var(--border-subtle);
        transition: all 0.3s ease;
    }
    
    .progress-step.active .step-indicator {
        background: var(--accent-gold);
        color: #0a0a0f;
        border-color: var(--accent-gold);
        animation: pulse 1.5s infinite;
    }
    
    .progress-step.done .step-indicator {
        background: var(--accent-emerald);
        color: white;
        border-color: var(--accent-emerald);
    }
    
    @keyframes pulse {
        0%, 100% { box-shadow: 0 0 0 0 rgba(240, 180, 41, 0.4); }
        50% { box-shadow: 0 0 0 8px rgba(240, 180, 41, 0); }
    }
    
    .step-content {
        flex: 1;
    }
    
    .step-title {
        font-weight: 600;
        color: var(--text-primary);
        font-size: 0.9rem;
    }
    
    .step-desc {
        font-size: 0.8rem;
        color: var(--text-muted);
    }
    
    .progress-step.active .step-title {
        color: var(--accent-gold);
    }
    
    .progress-step.done .step-title {
        color: var(--accent-emerald);
    }
    
    /* Results section */
    .results-container {
        background: var(--bg-card);
        border: 1px solid var(--accent-emerald);
        border-radius: 16px;
        padding: 2rem;
        margin: 1.5rem 0;
    }
    
    .results-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 1.5rem;
    }
    
    .results-icon {
        width: 48px;
        height: 48px;
        background: rgba(16, 185, 129, 0.15);
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
    }
    
    .results-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: var(--text-primary);
        margin: 0;
    }
    
    .results-subtitle {
        font-size: 0.85rem;
        color: var(--text-secondary);
        margin: 0;
    }
    
    /* History sidebar */
    .history-item {
        background: var(--bg-card);
        border: 1px solid var(--border-subtle);
        border-radius: 10px;
        padding: 0.875rem;
        margin-bottom: 0.75rem;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .history-item:hover {
        border-color: var(--border-accent);
        background: var(--bg-card-hover);
    }
    
    .history-topic {
        font-weight: 600;
        color: var(--text-primary);
        font-size: 0.85rem;
        margin-bottom: 0.25rem;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    
    .history-meta {
        font-size: 0.75rem;
        color: var(--text-muted);
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: var(--bg-card) !important;
        border-radius: 10px !important;
        color: var(--text-primary) !important;
        font-family: 'Outfit', sans-serif !important;
    }
    
    .streamlit-expanderContent {
        background: var(--bg-card) !important;
        border: 1px solid var(--border-subtle) !important;
        border-top: none !important;
        border-radius: 0 0 10px 10px !important;
    }
    
    /* Code blocks */
    .stCodeBlock {
        background: var(--bg-secondary) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 10px !important;
    }
    
    code {
        font-family: 'JetBrains Mono', monospace !important;
    }
    
    /* Status messages */
    .stSuccess, .stInfo, .stWarning, .stError {
        background: var(--bg-card) !important;
        border-radius: 10px !important;
        font-family: 'Outfit', sans-serif !important;
    }
    
    /* PDF iframe */
    .pdf-preview {
        border: 1px solid var(--border-subtle);
        border-radius: 12px;
        overflow: hidden;
        margin-top: 1rem;
    }
    
    /* Section labels */
    .section-label {
        font-size: 0.8rem;
        font-weight: 600;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.75rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Divider */
    .divider {
        height: 1px;
        background: var(--border-subtle);
        margin: 1.5rem 0;
    }
    
    /* Stats badges */
    .stats-row {
        display: flex;
        gap: 0.75rem;
        margin-bottom: 1rem;
    }
    
    .stat-badge {
        background: var(--bg-secondary);
        border: 1px solid var(--border-subtle);
        border-radius: 8px;
        padding: 0.5rem 0.875rem;
        font-size: 0.8rem;
        color: var(--text-secondary);
    }
    
    .stat-badge strong {
        color: var(--accent-gold);
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem 0;
        color: var(--text-muted);
        font-size: 0.8rem;
        border-top: 1px solid var(--border-subtle);
        margin-top: 3rem;
    }
    
    .footer a {
        color: var(--accent-gold);
        text-decoration: none;
    }
    
    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--bg-secondary);
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--border-accent);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--text-muted);
    }
</style>
""", unsafe_allow_html=True)


# ============================================================================
# TEMPLATES - Quick-start configurations
# ============================================================================
TEMPLATES = {
    "worksheet_basic": {
        "name": "Oppgaveark",
        "emoji": "📝",
        "description": "Kun oppgaver, ingen teori",
        "config": {
            "material_type": "arbeidsark",
            "include_theory": False,
            "include_examples": False,
            "include_exercises": True,
            "include_solutions": True,
            "include_graphs": True,
            "include_tips": False,
            "num_exercises": 10,
        }
    },
    "chapter_full": {
        "name": "Fullt kapittel",
        "emoji": "📖",
        "description": "Teori, eksempler og oppgaver",
        "config": {
            "material_type": "kapittel",
            "include_theory": True,
            "include_examples": True,
            "include_exercises": True,
            "include_solutions": True,
            "include_graphs": True,
            "include_tips": True,
            "num_exercises": 8,
        }
    },
    "exam_prep": {
        "name": "Eksamenstrening",
        "emoji": "📋",
        "description": "Varierte eksamensoppgaver",
        "config": {
            "material_type": "prøve",
            "include_theory": False,
            "include_examples": False,
            "include_exercises": True,
            "include_solutions": True,
            "include_graphs": True,
            "include_tips": False,
            "num_exercises": 15,
        }
    },
    "theory_focus": {
        "name": "Teorihefte",
        "emoji": "🎓",
        "description": "Kun teori og eksempler",
        "config": {
            "material_type": "kapittel",
            "include_theory": True,
            "include_examples": True,
            "include_exercises": False,
            "include_solutions": False,
            "include_graphs": True,
            "include_tips": True,
            "num_exercises": 0,
        }
    },
    "homework": {
        "name": "Lekseark",
        "emoji": "📚",
        "description": "Enkle repetisjonsoppgaver",
        "config": {
            "material_type": "lekseark",
            "include_theory": False,
            "include_examples": True,
            "include_exercises": True,
            "include_solutions": True,
            "include_graphs": False,
            "include_tips": True,
            "num_exercises": 8,
        }
    },
    "differentiated": {
        "name": "Differensiert",
        "emoji": "📊",
        "description": "3 nivåer: lett/middels/vanskelig",
        "config": {
            "material_type": "arbeidsark",
            "include_theory": False,
            "include_examples": False,
            "include_exercises": True,
            "include_solutions": True,
            "include_graphs": True,
            "include_tips": False,
            "num_exercises": 12,
            "differentiation_mode": True,
        }
    },
}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================
def initialize_session_state():
    """Initialize session state variables."""
    defaults = {
        "latex_result": None,
        "pdf_path": None,
        "pdf_bytes": None,
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
        "history": [],
        "current_step": 0,
        "is_generating": False,
        "selected_template": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def apply_template(template_key: str):
    """Apply a template configuration to session state."""
    if template_key in TEMPLATES:
        config = TEMPLATES[template_key]["config"]
        for key, value in config.items():
            st.session_state[key] = value
        st.session_state.selected_template = template_key


def add_to_history(topic: str, grade: str, material_type: str, pdf_path: str = None, tex_content: str = None):
    """Add a generation to history (both session and persistent storage)."""
    from src.storage import add_to_history as save_to_storage
    
    # Create session entry
    entry = {
        "topic": topic,
        "grade": grade,
        "material_type": material_type,
        "timestamp": datetime.now().isoformat(),
        "pdf_path": pdf_path,
    }
    
    # Add to session state
    if "history" not in st.session_state:
        st.session_state.history = []
    st.session_state.history.insert(0, entry)
    st.session_state.history = st.session_state.history[:20]
    
    # Save to persistent storage
    if tex_content:
        saved_entry = save_to_storage(
            topic=topic,
            grade=grade,
            material_type=material_type,
            tex_content=tex_content,
            pdf_path=pdf_path,
            settings={
                "include_theory": st.session_state.get("include_theory", True),
                "include_examples": st.session_state.get("include_examples", True),
                "include_exercises": st.session_state.get("include_exercises", True),
                "include_solutions": st.session_state.get("include_solutions", True),
                "num_exercises": st.session_state.get("num_exercises", 10),
            }
        )
        # Update session entry with persistent ID
        entry["id"] = saved_entry["id"]
        entry["tex_file"] = saved_entry.get("tex_file")


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


# ============================================================================
# UI COMPONENTS
# ============================================================================
def render_sidebar():
    """Render the sidebar with history, settings, and language selection."""
    # Import storage and translations
    from src.storage import load_history, load_settings, save_settings, get_tex_content, delete_history_entry
    from src.translations import LANGUAGES, get_translator
    
    with st.sidebar:
        st.markdown("""
        <div style="padding: 1rem 0;">
            <h2 style="color: #f0b429; font-weight: 700; margin: 0; font-size: 1.4rem;">
                ◇ MateMaTeX
            </h2>
            <p style="color: #9090a0; font-size: 0.8rem; margin-top: 0.25rem;">
                AI-drevet oppgavegenerator
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Theme toggle
        from src.tools import get_theme, generate_theme_css, DARK_THEME, LIGHT_THEME
        
        col_theme, col_lang = st.columns(2)
        with col_theme:
            theme_mode = st.selectbox(
                "🎨",
                options=["Mørk", "Lys"],
                index=0 if st.session_state.get("theme_mode", "dark") == "dark" else 1,
                label_visibility="collapsed"
            )
            st.session_state.theme_mode = "dark" if theme_mode == "Mørk" else "light"
        
        # Apply theme CSS
        theme = get_theme(st.session_state.get("theme_mode", "dark"))
        st.markdown(generate_theme_css(theme), unsafe_allow_html=True)
        
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        
        # Global search
        from src.tools import global_search, get_type_icon, get_type_label
        
        search_query = st.text_input(
            "🔍 Søk",
            placeholder="Søk i alt innhold...",
            label_visibility="collapsed",
            key="global_search_input"
        )
        
        if search_query and len(search_query) >= 2:
            search_results = global_search(search_query, limit=5)
            
            if search_results:
                st.markdown(f"""
                <p style="color: #9090a0; font-size: 0.75rem; margin: 0.5rem 0;">
                    Fant {len(search_results)} resultater
                </p>
                """, unsafe_allow_html=True)
                
                for result in search_results[:5]:
                    icon = get_type_icon(result.type)
                    if st.button(
                        f"{icon} {result.title[:30]}...",
                        key=f"sr_{result.id}",
                        use_container_width=True,
                        help=f"{get_type_label(result.type)}: {result.snippet[:50]}..."
                    ):
                        # Handle result click based on type
                        if result.type == "favorite":
                            from src.tools import get_favorite
                            fav = get_favorite(result.id)
                            if fav:
                                st.session_state.latex_result = fav.latex_content
                                st.session_state.generation_complete = True
                                st.toast(f"📄 Lastet: {fav.name}")
                                st.rerun()
                        elif result.type == "exercise":
                            from src.tools import get_exercise
                            ex = get_exercise(result.id)
                            if ex:
                                st.session_state.selected_exercise = ex
                                st.toast(f"📝 Lastet oppgave: {ex.title}")
                        elif result.type == "history":
                            tex = get_tex_content(result.id)
                            if tex:
                                st.session_state.latex_result = tex
                                st.session_state.generation_complete = True
                                st.toast(f"📜 Lastet fra historikk")
                                st.rerun()
            else:
                st.markdown("""
                <p style="color: #606070; font-size: 0.8rem; text-align: center; padding: 0.5rem;">
                    Ingen resultater funnet
                </p>
                """, unsafe_allow_html=True)
        
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        
        # Language selection
        settings = load_settings()
        current_lang = settings.get("language", "no")
        
        lang_options = list(LANGUAGES.keys())
        lang_labels = list(LANGUAGES.values())
        current_idx = lang_options.index(current_lang) if current_lang in lang_options else 0
        
        selected_lang = st.selectbox(
            "🌐 Språk / Language",
            options=lang_options,
            format_func=lambda x: LANGUAGES[x],
            index=current_idx,
            key="language_selector"
        )
        
        if selected_lang != current_lang:
            settings["language"] = selected_lang
            save_settings(settings)
            st.session_state.language = selected_lang
            st.rerun()
        
        # Get translator
        t = get_translator(selected_lang)
        
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        
        # API Status
        api_configured = bool(os.getenv("GOOGLE_API_KEY"))
        model_name = os.getenv("GOOGLE_MODEL", "gemini-2.0-flash")
        
        if api_configured:
            st.markdown(f"""
            <div style="
                background: rgba(16, 185, 129, 0.1);
                border: 1px solid rgba(16, 185, 129, 0.2);
                border-radius: 8px;
                padding: 0.75rem;
                margin-bottom: 1rem;
            ">
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <span style="color: #10b981;">●</span>
                    <span style="color: #10b981; font-size: 0.85rem; font-weight: 500;">{t("connected")}</span>
                </div>
                <div style="color: #9090a0; font-size: 0.75rem; margin-top: 0.25rem;">
                    {model_name}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="
                background: rgba(244, 63, 94, 0.1);
                border: 1px solid rgba(244, 63, 94, 0.2);
                border-radius: 8px;
                padding: 0.75rem;
                margin-bottom: 1rem;
            ">
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <span style="color: #f43f5e;">●</span>
                    <span style="color: #f43f5e; font-size: 0.85rem; font-weight: 500;">{t("not_configured")}</span>
                </div>
                <div style="color: #9090a0; font-size: 0.75rem; margin-top: 0.25rem;">
                    {t("add_api_key")}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # History section - load from persistent storage
        st.markdown(f"""
        <p class="section-label" style="margin-top: 1.5rem;">
            📜 {t("history")}
        </p>
        """, unsafe_allow_html=True)
        
        # Load persistent history
        persistent_history = load_history()
        
        # Merge with session history
        all_history = st.session_state.history + [h for h in persistent_history if h not in st.session_state.history]
        
        if all_history:
            for i, entry in enumerate(all_history[:8]):
                try:
                    timestamp = datetime.fromisoformat(entry["timestamp"])
                    time_str = timestamp.strftime("%d.%m %H:%M")
                except (ValueError, KeyError):
                    time_str = "Ukjent"
                
                topic = entry.get("topic", "Ukjent emne")
                grade = entry.get("grade", "")
                entry_id = entry.get("id", "")
                
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    # Clickable history item
                    if st.button(
                        f"📄 {topic[:25]}{'...' if len(topic) > 25 else ''}",
                        key=f"hist_{entry_id}_{i}",
                        use_container_width=True
                    ):
                        # Load this entry
                        tex_content = get_tex_content(entry_id)
                        if tex_content:
                            st.session_state.latex_result = tex_content
                            st.session_state.generation_complete = True
                            st.toast(f"📄 Lastet: {topic}")
                            st.rerun()
                
                with col2:
                    # Delete button
                    if st.button("🗑️", key=f"del_{entry_id}_{i}", help="Slett"):
                        delete_history_entry(entry_id)
                        st.toast("🗑️ Slettet fra historikk")
                        st.rerun()
                
                st.markdown(f"""
                <div style="color: #606070; font-size: 0.7rem; margin-top: -0.5rem; margin-bottom: 0.5rem; padding-left: 0.25rem;">
                    {grade} • {time_str}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="
                text-align: center;
                padding: 2rem 1rem;
                color: #606070;
                font-size: 0.85rem;
            ">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">📭</div>
                {t("no_history")}
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        
        # Quick links
        st.markdown(f"""
        <p class="section-label">🔗 {t("links")}</p>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style="font-size: 0.85rem; color: #9090a0;">
            <a href="https://www.udir.no/lk20/mat01-05" target="_blank" 
               style="color: #f0b429; text-decoration: none;">
                📚 {t("curriculum_link")}
            </a>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        
        # Template builder
        st.markdown("""
        <p class="section-label">🎨 Mine maler</p>
        """, unsafe_allow_html=True)
        
        from src.tools import load_custom_templates, create_template, delete_template
        
        custom_templates = load_custom_templates()
        
        if custom_templates:
            for template in custom_templates[:5]:
                col_t1, col_t2 = st.columns([4, 1])
                with col_t1:
                    if st.button(
                        f"{template.emoji} {template.name}",
                        key=f"tmpl_{template.id}",
                        use_container_width=True,
                        help=template.description
                    ):
                        # Apply template config
                        for key, value in template.config.items():
                            if hasattr(st.session_state, key):
                                setattr(st.session_state, key, value)
                        st.toast(f"✅ Mal '{template.name}' lastet")
                        st.rerun()
                with col_t2:
                    if st.button("🗑️", key=f"del_tmpl_{template.id}", help="Slett"):
                        delete_template(template.id)
                        st.toast("🗑️ Mal slettet")
                        st.rerun()
        
        # Create new template button
        with st.expander("➕ Lag ny mal", expanded=False):
            new_name = st.text_input("Navn", placeholder="Min mal", key="new_tmpl_name")
            new_desc = st.text_input("Beskrivelse", placeholder="Kort beskrivelse", key="new_tmpl_desc")
            new_emoji = st.selectbox("Emoji", ["📝", "📖", "📋", "🎓", "📚", "📊", "⚡", "🎯"], key="new_tmpl_emoji")
            
            if st.button("💾 Lagre som mal", use_container_width=True):
                if new_name:
                    # Get current config
                    config = {
                        "material_type": st.session_state.get("material_type", "arbeidsark"),
                        "include_theory": st.session_state.get("include_theory", True),
                        "include_examples": st.session_state.get("include_examples", True),
                        "include_exercises": st.session_state.get("include_exercises", True),
                        "include_solutions": st.session_state.get("include_solutions", True),
                        "include_graphs": st.session_state.get("include_graphs", True),
                        "include_tips": st.session_state.get("include_tips", False),
                        "num_exercises": st.session_state.get("num_exercises", 10),
                    }
                    create_template(new_name, new_desc or "Egendefinert mal", config, new_emoji)
                    st.toast(f"✅ Mal '{new_name}' opprettet!")
                    st.rerun()
                else:
                    st.warning("Skriv inn et navn for malen")
        
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        
        # Favorites section
        st.markdown("""
        <p class="section-label">⭐ Favoritter</p>
        """, unsafe_allow_html=True)
        
        from src.tools import load_favorites, get_favorite, delete_favorite, render_star_rating
        
        favorites = load_favorites()
        pinned = [f for f in favorites if f.is_pinned]
        recent = [f for f in favorites if not f.is_pinned][:5]
        
        all_favs = pinned + recent
        
        if all_favs:
            for fav in all_favs[:6]:
                pin_icon = "📌 " if fav.is_pinned else ""
                stars = render_star_rating(fav.rating)
                
                col_f1, col_f2 = st.columns([4, 1])
                with col_f1:
                    if st.button(
                        f"{pin_icon}{fav.name}",
                        key=f"fav_{fav.id}",
                        use_container_width=True,
                        help=f"{stars} | {fav.topic}"
                    ):
                        # Load favorite
                        loaded = get_favorite(fav.id)
                        if loaded:
                            st.session_state.latex_result = loaded.latex_content
                            st.session_state.selected_topic = loaded.topic
                            st.session_state.selected_grade = loaded.grade_level
                            st.toast(f"⭐ Lastet: {loaded.name}")
                            st.rerun()
                with col_f2:
                    if st.button("🗑️", key=f"del_fav_{fav.id}", help="Slett"):
                        delete_favorite(fav.id)
                        st.toast("🗑️ Favoritt slettet")
                        st.rerun()
        else:
            st.markdown("""
            <div style="
                text-align: center;
                padding: 1rem;
                color: #606070;
                font-size: 0.85rem;
            ">
                <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">⭐</div>
                Ingen favoritter ennå
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        
        # Folders & Tags section
        with st.expander("📁 Mapper og tags", expanded=False):
            from src.tools import (
                load_folders, create_folder, delete_folder,
                load_tags, create_tag, delete_tag,
                FOLDER_COLORS, FOLDER_ICONS, TAG_COLORS
            )
            
            # Folders
            st.markdown("**📁 Mapper**")
            folders = load_folders()
            
            if folders:
                for folder in folders[:5]:
                    col_f1, col_f2 = st.columns([4, 1])
                    with col_f1:
                        st.markdown(f"""
                        <div style="
                            display: flex;
                            align-items: center;
                            gap: 0.5rem;
                            padding: 0.25rem;
                        ">
                            <span style="color: {folder.color};">{folder.icon}</span>
                            <span style="color: #e2e8f0; font-size: 0.85rem;">{folder.name}</span>
                            <span style="color: #606070; font-size: 0.7rem;">({folder.item_count})</span>
                        </div>
                        """, unsafe_allow_html=True)
                    with col_f2:
                        if st.button("🗑️", key=f"del_folder_{folder.id}", help="Slett"):
                            delete_folder(folder.id)
                            st.rerun()
            
            # Create new folder
            with st.container():
                new_folder_name = st.text_input("Ny mappe", placeholder="Mappenavn...", key="new_folder", label_visibility="collapsed")
                if st.button("➕ Lag mappe", use_container_width=True, disabled=not new_folder_name):
                    create_folder(new_folder_name)
                    st.toast(f"📁 Mappe '{new_folder_name}' opprettet!")
                    st.rerun()
            
            st.markdown("---")
            
            # Tags
            st.markdown("**🏷️ Tags**")
            tags = load_tags()
            
            # Show tags as pills
            tags_html = ""
            for tag in tags[:8]:
                tags_html += f"""
                <span style="
                    display: inline-block;
                    background: {tag.color}20;
                    color: {tag.color};
                    padding: 0.15rem 0.5rem;
                    border-radius: 12px;
                    font-size: 0.7rem;
                    margin: 0.1rem;
                ">{tag.name}</span>
                """
            st.markdown(f'<div style="margin-bottom: 0.5rem;">{tags_html}</div>', unsafe_allow_html=True)
            
            # Create new tag
            col_tag1, col_tag2 = st.columns([3, 1])
            with col_tag1:
                new_tag_name = st.text_input("Ny tag", placeholder="Tagnavn...", key="new_tag", label_visibility="collapsed")
            with col_tag2:
                new_tag_color = st.selectbox("Farge", options=TAG_COLORS, key="new_tag_color", label_visibility="collapsed")
            
            if st.button("🏷️ Lag tag", use_container_width=True, disabled=not new_tag_name):
                create_tag(new_tag_name, new_tag_color)
                st.toast(f"🏷️ Tag '{new_tag_name}' opprettet!")
                st.rerun()
        
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        
        # Exercise bank section
        st.markdown("""
        <p class="section-label">🏦 Oppgavebank</p>
        """, unsafe_allow_html=True)
        
        from src.tools import load_exercises, get_exercise, delete_exercise, get_exercise_stats
        
        exercises = load_exercises()
        stats = get_exercise_stats()
        
        if exercises:
            st.markdown(f"""
            <div style="
                background: rgba(240, 180, 41, 0.1);
                border-radius: 8px;
                padding: 0.5rem;
                margin-bottom: 0.75rem;
            ">
                <span style="color: #f0b429; font-weight: 500;">{stats['total']}</span>
                <span style="color: #9090a0; font-size: 0.85rem;"> oppgaver lagret</span>
            </div>
            """, unsafe_allow_html=True)
            
            # Show recent exercises
            for ex in exercises[:5]:
                difficulty_emoji = {"lett": "🟢", "middels": "🟡", "vanskelig": "🔴"}.get(ex.difficulty, "⚪")
                
                col_e1, col_e2 = st.columns([4, 1])
                with col_e1:
                    if st.button(
                        f"{difficulty_emoji} {ex.title[:25]}...",
                        key=f"ex_{ex.id}",
                        use_container_width=True,
                        help=f"{ex.topic} | Brukt {ex.usage_count}x"
                    ):
                        # Show exercise content
                        st.session_state.show_exercise = ex.id
                        st.rerun()
                with col_e2:
                    if st.button("🗑️", key=f"del_ex_{ex.id}", help="Slett"):
                        delete_exercise(ex.id)
                        st.toast("🗑️ Oppgave slettet")
                        st.rerun()
            
            if len(exercises) > 5:
                st.markdown(f"""
                <p style="color: #9090a0; font-size: 0.8rem; text-align: center;">
                    +{len(exercises) - 5} flere oppgaver
                </p>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="
                text-align: center;
                color: #9090a0;
                padding: 1rem;
                font-size: 0.85rem;
            ">
                <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">🏦</div>
                Ingen oppgaver lagret ennå
            </div>
            """, unsafe_allow_html=True)
        
        # Keyboard shortcuts help
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        
        from src.tools import get_shortcuts_help_html
        with st.expander("⌨️ Hurtigtaster", expanded=False):
            st.markdown(get_shortcuts_help_html(), unsafe_allow_html=True)


def render_hero():
    """Render the hero section."""
    st.markdown("""
    <div class="hero-container">
        <div class="hero-badge">
            ✦ Drevet av Gemini AI
        </div>
        <h1 class="hero-title">MateMaTeX</h1>
        <p class="hero-subtitle">
            Generer profesjonelle matematikkoppgaver, arbeidsark og kapitler
            tilpasset norsk læreplan (LK20)
        </p>
        </div>
        """, unsafe_allow_html=True)
    

def render_templates():
    """Render template selection cards."""
    st.markdown('<p class="section-label">⚡ Hurtigstart med mal</p>', unsafe_allow_html=True)
    
    # First row - 3 templates
    template_items = list(TEMPLATES.items())
    cols1 = st.columns(3)
    for i, (key, template) in enumerate(template_items[:3]):
        with cols1[i]:
            if st.button(
                f"{template['emoji']}\n\n**{template['name']}**\n\n{template['description']}",
                key=f"template_{key}",
                use_container_width=True,
            ):
                apply_template(key)
                st.rerun()
    
    # Second row - remaining templates
    cols2 = st.columns(3)
    for i, (key, template) in enumerate(template_items[3:6]):
        with cols2[i]:
            if st.button(
                f"{template['emoji']}\n\n**{template['name']}**\n\n{template['description']}",
                key=f"template_{key}",
                use_container_width=True,
            ):
                apply_template(key)
                st.rerun()


def render_configuration():
    """Render the main configuration section."""
    from src.curriculum import get_topics_for_grade, get_competency_goals, get_exercise_types
    
    # Initialize return values to avoid UnboundLocalError
    selected_grade = "8. trinn"
    grade_options = {}
    topic = ""
    selected_material = "arbeidsark"
    
    col1, col2 = st.columns([1.2, 0.8])
    
    with col1:
        # Grade and Topic selection
        st.markdown("""
        <div class="config-card">
            <div class="card-header">
                <div class="card-icon gold">📚</div>
                <div>
                    <p class="card-title">Velg klassetrinn og tema</p>
                    <p class="card-description">Basert på LK20 læreplan</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
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
        
        # Topic selection
        topics_by_category = get_topics_for_grade(selected_grade)
        topic_choices = ["-- Velg tema --", "✍️ Skriv eget tema..."]
        for category, topics in topics_by_category.items():
            for t in topics:
                topic_choices.append(f"{t}")
        
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
        elif selected_topic_choice != "-- Velg tema --":
            topic = selected_topic_choice
        
        # Topic suggestions
        from src.tools import get_topic_suggestions
        suggestions = get_topic_suggestions(selected_grade, topic, num_suggestions=4)
        
        if suggestions:
            st.markdown("""
            <p style="color: #9090a0; font-size: 0.8rem; margin-top: 0.5rem; margin-bottom: 0.3rem;">
                💡 Foreslåtte emner:
            </p>
            """, unsafe_allow_html=True)
            
            suggestion_cols = st.columns(4)
            for i, sugg in enumerate(suggestions[:4]):
                with suggestion_cols[i]:
                    difficulty_emoji = {"lett": "🟢", "middels": "🟡", "vanskelig": "🔴"}.get(sugg.get("difficulty", ""), "")
                    if st.button(
                        f"{difficulty_emoji} {sugg['topic'][:15]}{'...' if len(sugg['topic']) > 15 else ''}",
                        key=f"sugg_{i}",
                        help=sugg.get("description", ""),
                        use_container_width=True
                    ):
                        st.session_state.suggested_topic = sugg['topic']
                        st.rerun()
            
            # Apply suggested topic if selected
            if hasattr(st.session_state, 'suggested_topic') and st.session_state.suggested_topic:
                topic = st.session_state.suggested_topic
                st.session_state.suggested_topic = None
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Material type
        st.markdown("""
        <div class="config-card">
            <div class="card-header">
                <div class="card-icon emerald">📄</div>
                <div>
                    <p class="card-title">Materialtype</p>
                    <p class="card-description">Hva skal genereres?</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
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
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Competency goals
        competency_goals = get_competency_goals(selected_grade)
        if competency_goals:
            with st.expander("🎯 Kompetansemål (LK20)", expanded=False):
                st.markdown("""
                    <p style="color: #9090a0; font-size: 0.85rem; margin-bottom: 1rem;">
                    Velg hvilke kompetansemål materialet skal dekke.
                </p>
                """, unsafe_allow_html=True)
                
                selected_goals = []
                for i, goal in enumerate(competency_goals):
                    if st.checkbox(goal, key=f"goal_{i}"):
                        selected_goals.append(goal)
                
                st.session_state.selected_competency_goals = selected_goals
        
        # Formula library
        with st.expander("📐 Formelbibliotek", expanded=False):
            from src.tools import get_categories, get_formulas_by_category
            
            st.markdown("""
            <p style="color: #9090a0; font-size: 0.85rem; margin-bottom: 0.5rem;">
                Klikk for å kopiere formler til bruk i oppgaver.
            </p>
            """, unsafe_allow_html=True)
            
            # Category selector
            categories = get_categories()
            selected_category = st.selectbox(
                "Kategori",
                options=categories,
                label_visibility="collapsed"
            )
            
            # Show formulas in category
            formulas = get_formulas_by_category(selected_category)
            
            for formula in formulas[:8]:  # Limit to 8 per category
                col_f1, col_f2 = st.columns([3, 1])
                with col_f1:
                    st.markdown(f"**{formula.name}**")
                    st.latex(formula.latex)
                    st.caption(formula.description)
                with col_f2:
                    if st.button("📋", key=f"copy_{formula.name}", help="Kopier LaTeX"):
                        st.session_state.copied_formula = formula.latex
                        st.toast(f"✅ Kopierte {formula.name}")
    
    with col2:
        # Content options
        st.markdown("""
        <div class="config-card">
            <div class="card-header">
                <div class="card-icon violet">⚙️</div>
                <div>
                    <p class="card-title">Innhold</p>
                    <p class="card-description">Tilpass hva som inkluderes</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        st.session_state.include_theory = st.checkbox(
            "📘 Teori og definisjoner",
            value=st.session_state.include_theory
        )
        st.session_state.include_examples = st.checkbox(
            "💡 Eksempler", 
            value=st.session_state.include_examples
        )
        st.session_state.include_exercises = st.checkbox(
            "✍️ Oppgaver",
            value=st.session_state.include_exercises
        )
        st.session_state.include_solutions = st.checkbox(
            "🔑 Fasit",
            value=st.session_state.include_solutions
        )
        st.session_state.include_graphs = st.checkbox(
            "📊 Grafer/Figurer",
            value=st.session_state.include_graphs
        )
        st.session_state.include_tips = st.checkbox(
            "💬 Tips og hint",
            value=st.session_state.include_tips
        )
    
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Difficulty and exercise count
    if st.session_state.include_exercises:
            st.markdown("""
            <div class="config-card">
                <div class="card-header">
                    <div class="card-icon rose">📈</div>
                    <div>
                        <p class="card-title">Oppgaveinnstillinger</p>
                        <p class="card-description">Antall og vanskelighetsgrad</p>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            st.session_state.num_exercises = st.slider(
                "Antall oppgaver",
                min_value=3,
                max_value=25,
                value=st.session_state.num_exercises,
                step=1
            )
            
            difficulty_options = ["🟢 Lett", "🟡 Middels", "🔴 Vanskelig"]
            difficulty_index = {"Lett": 0, "Middels": 1, "Vanskelig": 2}.get(
                st.session_state.difficulty_level, 1
            )
            selected_difficulty = st.radio(
                "Vanskelighetsgrad",
                options=difficulty_options,
                index=difficulty_index,
                horizontal=True
            )
            st.session_state.difficulty_level = selected_difficulty.split(" ")[1]
            
            st.session_state.differentiation_mode = st.checkbox(
                "📊 Generer 3 nivåer (differensiering)",
                value=st.session_state.differentiation_mode
            )
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Exercise types
            exercise_types = get_exercise_types()
            with st.expander("📝 Oppgavetyper", expanded=False):
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
    
    return selected_grade, grade_options, topic, selected_material


def render_progress_indicator(current_step: int):
    """Render an animated progress indicator."""
    steps = [
        {"title": "Pedagogen planlegger", "desc": "Analyserer læreplan og strukturerer innhold"},
        {"title": "Matematikeren skriver", "desc": "Genererer oppgaver og forklaringer"},
        {"title": "Illustratøren tegner", "desc": "Lager figurer og grafer"},
        {"title": "Redaktøren ferdigstiller", "desc": "Setter sammen og kvalitetssikrer"},
    ]
    
    steps_html = ""
    for i, step in enumerate(steps):
        if i < current_step:
            status = "done"
            indicator = "✓"
        elif i == current_step:
            status = "active"
            indicator = str(i + 1)
        else:
            status = ""
            indicator = str(i + 1)
        
        steps_html += f"""
        <div class="progress-step {status}">
            <div class="step-indicator">{indicator}</div>
            <div class="step-content">
                <div class="step-title">{step['title']}</div>
                <div class="step-desc">{step['desc']}</div>
            </div>
        </div>
        """
    
    st.markdown(f"""
    <div class="progress-container">
        <div class="progress-title">
            <span>🔄</span> AI-teamet arbeider...
        </div>
        <div class="progress-steps">
            {steps_html}
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_results():
    """Render the results section with download, edit, and export options."""
    st.markdown("""
    <div class="results-container">
        <div class="results-header">
            <div class="results-icon">✨</div>
            <div>
                <p class="results-title">Materiale generert!</p>
                <p class="results-subtitle">Last ned, rediger eller eksporter</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Download buttons row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.download_button(
            "📄 LaTeX (.tex)",
            data=st.session_state.latex_result,
            file_name=f"matematikk_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tex",
            mime="text/plain",
            use_container_width=True
        )
    
    with col2:
        if st.session_state.pdf_path and Path(st.session_state.pdf_path).exists():
            with open(st.session_state.pdf_path, "rb") as f:
                pdf_bytes = f.read()
                st.session_state.pdf_bytes = pdf_bytes
                st.download_button(
                    "📕 PDF",
                    data=pdf_bytes,
                    file_name=Path(st.session_state.pdf_path).name,
                    mime="application/pdf",
                    use_container_width=True
                )
        else:
            st.button("📕 PDF", disabled=True, use_container_width=True, help="Krever pdflatex")
    
    with col3:
        # Word export
        try:
            from src.tools import is_word_export_available, latex_to_word
            if is_word_export_available():
                if st.button("📘 Word (.docx)", use_container_width=True):
                    with st.spinner("Konverterer til Word..."):
                        output_path = Path("output") / f"matematikk_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
                        output_path.parent.mkdir(exist_ok=True)
                        word_path = latex_to_word(st.session_state.latex_result, str(output_path))
                        if word_path and Path(word_path).exists():
                            st.session_state.word_path = word_path
                            st.rerun()
            else:
                st.button("📘 Word", disabled=True, use_container_width=True, help="Installer python-docx")
        except ImportError:
            st.button("📘 Word", disabled=True, use_container_width=True, help="Installer python-docx")
    
    # Show Word download if available
    if hasattr(st.session_state, 'word_path') and st.session_state.word_path:
        word_path = Path(st.session_state.word_path)
        if word_path.exists():
            with col3:
                with open(word_path, "rb") as f:
                    st.download_button(
                        "⬇️ Last ned Word",
                        data=f.read(),
                        file_name=word_path.name,
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        use_container_width=True
                    )
    
    with col4:
        if st.button("📋 Kopier kode", use_container_width=True):
            st.toast("✅ LaTeX-kode kopiert!")
    
    # PDF Preview with controls
    if hasattr(st.session_state, 'pdf_bytes') and st.session_state.pdf_bytes:
        from src.tools import create_pdf_preview_with_controls, get_pdf_bytes_base64
        
        st.markdown('<p class="section-label" style="margin-top: 1.5rem;">📄 PDF Forhåndsvisning</p>', unsafe_allow_html=True)
        
        # Add toggle for preview
        show_preview = st.checkbox("Vis forhåndsvisning", value=True, key="show_pdf_preview")
        
        if show_preview:
            pdf_base64 = get_pdf_bytes_base64(st.session_state.pdf_bytes)
            filename = f"matematikk_{datetime.now().strftime('%Y%m%d')}.pdf"
            preview_html = create_pdf_preview_with_controls(pdf_base64, height=600, filename=filename)
            st.markdown(preview_html, unsafe_allow_html=True)
    
    # LaTeX Editor
    with st.expander("✏️ Rediger LaTeX-kode", expanded=False):
        edited_latex = st.text_area(
            "LaTeX-kode",
            value=st.session_state.latex_result,
            height=400,
            label_visibility="collapsed",
            key="latex_editor"
        )
        
        col_save, col_compile = st.columns(2)
        
        with col_save:
            if st.button("💾 Lagre endringer", use_container_width=True):
                st.session_state.latex_result = edited_latex
                st.toast("✅ Endringer lagret!")
        
        with col_compile:
            if st.button("🔄 Kompiler PDF på nytt", use_container_width=True):
                st.session_state.latex_result = edited_latex
                with st.spinner("Kompilerer..."):
                    try:
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        pdf_path = generate_pdf(edited_latex, f"redigert_{timestamp}")
                        if pdf_path:
                            st.session_state.pdf_path = pdf_path
                            with open(pdf_path, "rb") as f:
                                st.session_state.pdf_bytes = f.read()
                            st.toast("✅ PDF kompilert!")
                            st.rerun()
                    except Exception as e:
                        st.error(f"Kompilering feilet: {e}")
        
        # Stats
        lines = edited_latex.count('\n')
        chars = len(edited_latex)
        exercises = edited_latex.count('\\begin{taskbox}')
        
        st.markdown(f"""
        <div class="stats-row" style="margin-top: 1rem;">
            <span class="stat-badge"><strong>{lines}</strong> linjer</span>
            <span class="stat-badge"><strong>{chars:,}</strong> tegn</span>
            <span class="stat-badge"><strong>{exercises}</strong> oppgaver</span>
        </div>
        """, unsafe_allow_html=True)
    
    # View-only LaTeX code
    with st.expander("👁️ Se LaTeX-kode (kun visning)"):
        st.code(st.session_state.latex_result, language="latex")
    
    # Print-friendly version
    with st.expander("🖨️ Utskriftsvennlig versjon", expanded=False):
        st.markdown("""
        <p style="color: #9090a0; font-size: 0.85rem; margin-bottom: 1rem;">
            Generer en versjon optimalisert for utskrift (gråtoner, tynn ramme, mindre blekk).
        </p>
        """, unsafe_allow_html=True)
        
        col_print1, col_print2 = st.columns(2)
        
        with col_print1:
            if st.button("📄 Lag utskriftsversjon", use_container_width=True):
                from src.tools import create_print_version, compile_latex_to_pdf
                with st.spinner("Lager utskriftsversjon..."):
                    try:
                        print_latex = create_print_version(st.session_state.latex_result)
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        pdf_path = compile_latex_to_pdf(print_latex, f"print_{timestamp}")
                        st.session_state.print_pdf_path = pdf_path
                        st.toast("✅ Utskriftsversjon klar!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Kunne ikke lage utskriftsversjon: {e}")
        
        with col_print2:
            if st.button("📋 Lag kun fasit-ark", use_container_width=True):
                from src.tools import create_answer_sheet, compile_latex_to_pdf
                with st.spinner("Lager fasit-ark..."):
                    try:
                        answer_latex = create_answer_sheet(st.session_state.latex_result)
                        if answer_latex:
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            pdf_path = compile_latex_to_pdf(answer_latex, f"fasit_{timestamp}")
                            st.session_state.answer_pdf_path = pdf_path
                            st.toast("✅ Fasit-ark klart!")
                            st.rerun()
                        else:
                            st.warning("Ingen løsninger funnet i dokumentet")
                    except Exception as e:
                        st.error(f"Kunne ikke lage fasit-ark: {e}")
        
        # Download print PDFs if available
        if hasattr(st.session_state, 'print_pdf_path') and st.session_state.print_pdf_path:
            if Path(st.session_state.print_pdf_path).exists():
                with open(st.session_state.print_pdf_path, "rb") as f:
                    st.download_button(
                        "⬇️ Last ned utskriftsversjon",
                        data=f.read(),
                        file_name=Path(st.session_state.print_pdf_path).name,
                        mime="application/pdf",
                        use_container_width=True
                    )
        
        if hasattr(st.session_state, 'answer_pdf_path') and st.session_state.answer_pdf_path:
            if Path(st.session_state.answer_pdf_path).exists():
                with open(st.session_state.answer_pdf_path, "rb") as f:
                    st.download_button(
                        "⬇️ Last ned fasit-ark",
                        data=f.read(),
                        file_name=Path(st.session_state.answer_pdf_path).name,
                        mime="application/pdf",
                        use_container_width=True
                    )
    
    # Section regeneration
    with st.expander("🔄 Regenerer seksjon", expanded=False):
        st.markdown("""
        <p style="color: #9090a0; font-size: 0.85rem; margin-bottom: 1rem;">
            Velg en seksjon og generer den på nytt med AI.
        </p>
        """, unsafe_allow_html=True)
        
        from src.tools import get_section_summary
        sections = get_section_summary(st.session_state.latex_result)
        
        if sections:
            section_options = [f"{s['name']} ({s['exercises']} oppgaver)" for s in sections if s['type'] in ['section', 'subsection']]
            
            if section_options:
                selected_section = st.selectbox(
                    "Velg seksjon",
                    options=section_options,
                    label_visibility="collapsed"
                )
                
                regen_col1, regen_col2 = st.columns(2)
                
                with regen_col1:
                    regen_instructions = st.text_input(
                        "Instruksjoner (valgfritt)",
                        placeholder="f.eks. Gjør oppgavene vanskeligere...",
                        label_visibility="collapsed"
                    )
                
                with regen_col2:
                    if st.button("🔄 Regenerer denne seksjonen", use_container_width=True):
                        st.info("🚧 Seksjon-regenerering krever en ny AI-forespørsel. Denne funksjonen kommer snart!")
            else:
                st.info("Ingen seksjoner funnet i dokumentet")
        else:
            st.info("Kunne ikke analysere dokumentet")
    
    # Difficulty analysis
    with st.expander("📊 Vanskelighetsanalyse", expanded=False):
        from src.tools import analyze_content, get_difficulty_emoji
        
        analysis = analyze_content(st.session_state.latex_result)
        
        if analysis.total_exercises > 0:
            # Distribution bar
            total = analysis.total_exercises
            easy_pct = analysis.easy_count / total * 100
            medium_pct = analysis.medium_count / total * 100
            hard_pct = analysis.hard_count / total * 100
            
            st.markdown(f"""
            <div style="margin-bottom: 1rem;">
                <div style="display: flex; height: 24px; border-radius: 12px; overflow: hidden; background: #1a1a24;">
                    <div style="width: {easy_pct}%; background: #10b981;" title="Lett: {analysis.easy_count}"></div>
                    <div style="width: {medium_pct}%; background: #f59e0b;" title="Middels: {analysis.medium_count}"></div>
                    <div style="width: {hard_pct}%; background: #f43f5e;" title="Vanskelig: {analysis.hard_count}"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Stats row
            col_a1, col_a2, col_a3, col_a4 = st.columns(4)
            with col_a1:
                st.metric("🟢 Lett", analysis.easy_count)
            with col_a2:
                st.metric("🟡 Middels", analysis.medium_count)
            with col_a3:
                st.metric("🔴 Vanskelig", analysis.hard_count)
            with col_a4:
                st.metric("⏱️ Est. tid", f"{analysis.estimated_time_minutes} min")
            
            # Concepts
            if analysis.concepts_covered:
                st.markdown(f"**📚 Konsepter:** {', '.join(analysis.concepts_covered)}")
            
            # Recommendations
            if analysis.recommendations:
                st.markdown("**💡 Anbefalinger:**")
                for rec in analysis.recommendations:
                    st.markdown(f"- {rec}")
            
            # Exercise details
            with st.expander("Se alle oppgaver"):
                for ex in analysis.exercises:
                    emoji = get_difficulty_emoji(ex.difficulty)
                    factors = ", ".join(ex.factors) if ex.factors else "Standard"
                    st.markdown(f"{emoji} **{ex.title}** - {ex.difficulty.capitalize()} ({factors})")
        else:
            st.info("Ingen oppgaver funnet å analysere")
    
    # QR code for answers
    with st.expander("📲 QR-kode til fasit", expanded=False):
        from src.tools import is_qr_available, generate_qr_for_worksheet
        
        if is_qr_available():
            st.markdown("""
            <p style="color: #9090a0; font-size: 0.85rem; margin-bottom: 1rem;">
                Generer en QR-kode som elever kan skanne for å se fasit.
            </p>
            """, unsafe_allow_html=True)
            
            if st.button("📲 Generer QR-kode", use_container_width=True):
                qr_data = generate_qr_for_worksheet(st.session_state.latex_result, "Matematikk Fasit")
                
                if qr_data:
                    st.session_state.qr_image = qr_data["image"]
                    st.session_state.qr_answers = qr_data["answers"]
                    st.toast("✅ QR-kode generert!")
                    st.rerun()
                else:
                    st.warning("Kunne ikke finne svar i dokumentet")
            
            # Show QR code if generated
            if hasattr(st.session_state, 'qr_image') and st.session_state.qr_image:
                st.image(st.session_state.qr_image, caption="Skann for fasit", width=200)
                
                st.download_button(
                    "⬇️ Last ned QR-kode",
                    data=st.session_state.qr_image,
                    file_name="fasit_qr.png",
                    mime="image/png",
                    use_container_width=True
                )
                
                if hasattr(st.session_state, 'qr_answers'):
                    st.markdown("**Svar i QR-koden:**")
                    for num, ans in list(st.session_state.qr_answers.items())[:5]:
                        st.markdown(f"- Oppgave {num}: {ans[:50]}...")
        else:
            st.info("📦 QR-kode krever `qrcode`-pakken. Kjør: `pip install qrcode[pil]`")
    
    # GeoGebra Integration
    with st.expander("📊 GeoGebra Grafer", expanded=False):
        from src.tools import (
            get_template_list, create_graph_from_template, 
            get_geogebra_embed_html, extract_functions_from_content
        )
        
        st.markdown("""
        <p style="color: #9090a0; font-size: 0.85rem; margin-bottom: 1rem;">
            Lag interaktive grafer med GeoGebra.
        </p>
        """, unsafe_allow_html=True)
        
        # Template selector
        templates = get_template_list()
        template_options = {t["title"]: t["key"] for t in templates}
        
        selected_template = st.selectbox(
            "Velg grafmal",
            options=list(template_options.keys()),
            label_visibility="collapsed"
        )
        
        col_ggb1, col_ggb2 = st.columns(2)
        
        with col_ggb1:
            if st.button("📊 Vis graf", use_container_width=True):
                template_key = template_options[selected_template]
                graph = create_graph_from_template(template_key)
                if graph:
                    st.session_state.geogebra_graph = graph
                    st.toast(f"✅ Graf opprettet: {graph['title']}")
                    st.rerun()
        
        with col_ggb2:
            if st.button("🔍 Fra innhold", use_container_width=True, help="Finn funksjoner i dokumentet"):
                functions = extract_functions_from_content(st.session_state.latex_result)
                if functions:
                    st.session_state.geogebra_graph = {
                        "title": "Funksjoner fra dokumentet",
                        "commands": functions,
                        "description": f"Fant {len(functions)} funksjoner",
                    }
                    st.toast(f"✅ Fant {len(functions)} funksjoner!")
                    st.rerun()
                else:
                    st.warning("Fant ingen funksjoner i dokumentet")
        
        # Show GeoGebra graph if created
        if hasattr(st.session_state, 'geogebra_graph') and st.session_state.geogebra_graph:
            graph = st.session_state.geogebra_graph
            st.markdown(f"**{graph['title']}**")
            st.caption(graph.get('description', ''))
            
            # Embed GeoGebra
            embed_html = get_geogebra_embed_html(
                commands=graph['commands'],
                width=500,
                height=350,
                show_toolbar=True
            )
            st.markdown(embed_html, unsafe_allow_html=True)
            
            # Show commands
            with st.expander("Se GeoGebra-kommandoer"):
                for cmd in graph['commands']:
                    st.code(cmd, language=None)
    
    # LK20 Coverage Report
    with st.expander("📊 LK20 Kompetansemål-dekning", expanded=False):
        from src.tools import analyze_coverage, format_coverage_report, get_coverage_badge
        
        grade = st.session_state.get("selected_grade", "8. trinn")
        topic = st.session_state.get("selected_topic", "")
        
        report = analyze_coverage(st.session_state.latex_result, grade, topic)
        
        # Coverage badge
        color, label = get_coverage_badge(report.coverage_percentage)
        st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
            <div style="
                background: {color};
                color: white;
                padding: 0.5rem 1rem;
                border-radius: 20px;
                font-weight: 600;
            ">{int(report.coverage_percentage * 100)}% - {label}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Progress bar
        st.progress(report.coverage_percentage)
        
        # Covered goals
        if report.covered_goals:
            st.markdown(f"**✅ Dekket ({len(report.covered_goals)}):**")
            for result in report.covered_goals[:5]:
                conf = int(result.confidence * 100)
                st.markdown(f"- {result.goal.text[:70]}... ({conf}%)")
        
        # Uncovered goals
        if report.uncovered_goals:
            with st.expander(f"❌ Ikke dekket ({len(report.uncovered_goals)})"):
                for goal in report.uncovered_goals:
                    st.markdown(f"- {goal.text[:70]}...")
        
        # Recommendations
        if report.recommendations:
            st.markdown("**💡 Anbefalinger:**")
            for rec in report.recommendations:
                st.info(rec)
    
    # Rubric Generator
    with st.expander("📋 Vurderingskriterier", expanded=False):
        from src.tools import generate_rubric, rubric_to_markdown
        
        st.markdown("""
        <p style="color: #9090a0; font-size: 0.85rem; margin-bottom: 1rem;">
            Generer vurderingskriterier for dette innholdet.
        </p>
        """, unsafe_allow_html=True)
        
        grade = st.session_state.get("selected_grade", "8. trinn")
        topic = st.session_state.get("selected_topic", "Matematikk")
        
        rubric = generate_rubric(topic, grade, num_exercises=10)
        
        # Display rubric summary
        col_r1, col_r2, col_r3 = st.columns(3)
        with col_r1:
            st.metric("Maks poeng", rubric.max_points)
        with col_r2:
            st.metric("Bestått", f"{int(rubric.passing_threshold * 100)}%")
        with col_r3:
            st.metric("Kriterier", len(rubric.criteria))
        
        # Show criteria
        for criterion in rubric.criteria:
            weight = int(criterion.weight * 100)
            with st.expander(f"{criterion.name} ({weight}%)"):
                st.markdown(f"*{criterion.description}*")
                for grade_val, desc in list(criterion.levels.items())[:3]:
                    st.markdown(f"**{grade_val}:** {desc}")
        
        # Download rubric
        rubric_md = rubric_to_markdown(rubric)
        st.download_button(
            "⬇️ Last ned vurderingskriterier",
            data=rubric_md,
            file_name=f"vurdering_{topic.replace(' ', '_')}.md",
            mime="text/markdown",
            use_container_width=True
        )
    
    # Differentiation Assistant
    with st.expander("🎯 Differensiering", expanded=False):
        from src.tools import LEVEL_CONFIG, get_differentiation_summary
        
        st.markdown("""
        <p style="color: #9090a0; font-size: 0.85rem; margin-bottom: 1rem;">
            Generer innhold på tre nivåer for tilpasset opplæring.
        </p>
        """, unsafe_allow_html=True)
        
        # Show level options
        for level_key, config in LEVEL_CONFIG.items():
            col_d1, col_d2 = st.columns([3, 1])
            with col_d1:
                st.markdown(f"""
                **{config['emoji']} {config['name']}**  
                {config['description']}
                """)
            with col_d2:
                if st.button(f"Generer", key=f"diff_{level_key}", use_container_width=True):
                    st.info(f"🚧 Generering av {config['name']}-nivå krever en ny AI-forespørsel. Kommer snart!")
        
        st.divider()
        st.markdown("**📊 Oversikt:**")
        st.markdown("""
        | Nivå | Oppgaver | Est. tid |
        |------|----------|----------|
        | 🟢 Grunnleggende | 12 | ~36 min |
        | 🟡 Standard | 10 | ~50 min |
        | 🔴 Utfordring | 6 | ~60 min |
        """)
    
    # Add to Favorites
    st.divider()
    col_fav1, col_fav2 = st.columns([3, 1])
    with col_fav1:
        fav_name = st.text_input(
            "Lagre som favoritt",
            placeholder="Gi favoritten et navn...",
            label_visibility="collapsed"
        )
    with col_fav2:
        if st.button("⭐ Lagre", use_container_width=True, disabled=not fav_name):
            from src.tools import add_favorite
            
            add_favorite(
                name=fav_name,
                topic=st.session_state.get("selected_topic", "Matematikk"),
                grade_level=st.session_state.get("selected_grade", "8. trinn"),
                material_type=st.session_state.get("material_type", "arbeidsark"),
                latex_content=st.session_state.latex_result,
                pdf_path=st.session_state.get("pdf_path"),
                rating=4
            )
            st.toast(f"⭐ Lagret som favoritt: {fav_name}")
    
    # Add to Exercise Bank
    with st.expander("🏦 Lagre til oppgavebank", expanded=False):
        st.markdown("""
        <p style="color: #9090a0; font-size: 0.85rem; margin-bottom: 1rem;">
            Ekstraher enkeltoppgaver fra genereringen og lagre dem for gjenbruk.
        </p>
        """, unsafe_allow_html=True)
        
        col_bank1, col_bank2 = st.columns(2)
        
        with col_bank1:
            if st.button("🔍 Finn oppgaver", use_container_width=True):
                from src.tools import extract_exercises_from_latex
                
                extracted = extract_exercises_from_latex(st.session_state.latex_result)
                
                if extracted:
                    st.session_state.extracted_exercises = extracted
                    st.toast(f"✅ Fant {len(extracted)} oppgaver")
                    st.rerun()
                else:
                    st.warning("Fant ingen oppgaver i dokumentet")
        
        with col_bank2:
            if st.button("💾 Lagre alle", use_container_width=True):
                from src.tools import add_exercises_from_latex
                
                saved = add_exercises_from_latex(
                    st.session_state.latex_result,
                    st.session_state.get("selected_topic", "Matematikk"),
                    st.session_state.get("selected_grade", "8. trinn")
                )
                
                if saved:
                    st.toast(f"✅ Lagret {len(saved)} oppgaver til banken")
                else:
                    st.warning("Fant ingen oppgaver å lagre")
        
        # Show extracted exercises
        if hasattr(st.session_state, 'extracted_exercises') and st.session_state.extracted_exercises:
            st.markdown("---")
            st.markdown("**Funne oppgaver:**")
            
            for i, ex in enumerate(st.session_state.extracted_exercises):
                difficulty_emoji = {"lett": "🟢", "middels": "🟡", "vanskelig": "🔴"}.get(ex.get("difficulty", "middels"), "⚪")
                
                with st.container():
                    col_ex1, col_ex2 = st.columns([4, 1])
                    with col_ex1:
                        st.markdown(f"{difficulty_emoji} **{ex['title']}**")
                        # Show preview of content
                        preview = ex['content'][:100].replace('\n', ' ')
                        st.caption(f"{preview}...")
                    with col_ex2:
                        if st.button("💾", key=f"save_ex_{i}", help="Lagre denne"):
                            from src.tools import add_exercise
                            
                            add_exercise(
                                title=ex['title'],
                                topic=st.session_state.get("selected_topic", "Matematikk"),
                                grade_level=st.session_state.get("selected_grade", "8. trinn"),
                                latex_content=ex['full_latex'],
                                difficulty=ex.get('difficulty', 'middels'),
                                solution=ex.get('solution'),
                                source="generated"
                            )
                            st.toast(f"✅ Lagret: {ex['title']}")


# ============================================================================
# BATCH GENERATION
# ============================================================================
def render_batch_generation():
    """Render the batch generation section."""
    st.markdown("""
    <div class="config-card">
        <div class="card-header">
            <div class="card-icon violet">📦</div>
            <div>
                <p class="card-title">Batch-generering</p>
                <p class="card-description">Generer flere emner samtidig</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    batch_topics = st.text_area(
        "Emner (ett per linje)",
        placeholder="Brøk\nProsent\nLikninger\nFunksjoner",
        height=100,
        label_visibility="collapsed"
    )
    
    if batch_topics:
        topics = [t.strip() for t in batch_topics.strip().split('\n') if t.strip()]
        
        from src.tools import estimate_batch_time
        min_time, max_time = estimate_batch_time(len(topics))
        
        st.markdown(f"""
        <div style="
            text-align: center;
            padding: 0.5rem;
            background: rgba(139, 92, 246, 0.1);
            border: 1px solid rgba(139, 92, 246, 0.2);
            border-radius: 8px;
            margin: 0.5rem 0;
            color: #8b5cf6;
            font-size: 0.85rem;
        ">
            📦 <strong>{len(topics)}</strong> emner • ⏱️ Estimert: <strong>{min_time}-{max_time} min</strong>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚀 Start batch-generering", use_container_width=True):
            st.info("🚧 Batch-generering er under utvikling. Kommer snart med full støtte!")
    
    st.markdown("</div>", unsafe_allow_html=True)


# ============================================================================
# MAIN APPLICATION
# ============================================================================
def main():
    """Main application function."""
    initialize_session_state()
    
    # Add keyboard shortcuts
    from src.tools import get_shortcut_js
    st.markdown(get_shortcut_js(), unsafe_allow_html=True)
    
    # Render sidebar
    render_sidebar()
    
    # Render hero
    render_hero()
    
    # Render templates
    render_templates()
    
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    # Render configuration
    selected_grade, grade_options, topic, selected_material = render_configuration()
    
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    # Batch generation toggle
    with st.expander("📦 Batch-generering (flere emner)", expanded=False):
        render_batch_generation()
    
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    # Validation
    api_configured = bool(os.getenv("GOOGLE_API_KEY"))
    can_generate = api_configured and bool(topic)
    
    if not topic:
        st.warning("⚠️ Velg eller skriv inn et tema for å generere materiale")
    
    # Estimated generation time
    if topic and api_configured:
        from src.curriculum import estimate_generation_time
        min_time, max_time = estimate_generation_time(
            material_type=selected_material,
            num_exercises=st.session_state.num_exercises if st.session_state.include_exercises else 0,
            include_theory=st.session_state.include_theory,
            include_examples=st.session_state.include_examples,
            include_graphs=st.session_state.include_graphs
        )
        st.markdown(f"""
        <div style="
            text-align: center;
            padding: 0.75rem;
            background: rgba(240, 180, 41, 0.08);
            border: 1px solid rgba(240, 180, 41, 0.2);
            border-radius: 10px;
            margin-bottom: 1rem;
            color: #f0b429;
            font-size: 0.9rem;
        ">
            ⏱️ Estimert tid: <strong>{min_time}-{max_time} minutter</strong>
        </div>
        """, unsafe_allow_html=True)
    
    # Generate Button
    if st.button("◇ Generer materiale", disabled=not can_generate, use_container_width=True):
        st.session_state.latex_result = None
        st.session_state.pdf_path = None
        st.session_state.pdf_bytes = None
        st.session_state.generation_complete = False
        st.session_state.is_generating = True
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_topic = "".join(c for c in topic if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_topic = safe_topic.replace(' ', '_')[:30]
        filename = f"{safe_topic}_{selected_grade.replace(' ', '_').replace('.', '')}_{timestamp}"
        
        # Build content options
        from src.curriculum import get_exercise_types
        exercise_types = get_exercise_types()
        exercise_type_instructions = []
        for etype in st.session_state.selected_exercise_types:
            if etype in exercise_types:
                exercise_type_instructions.append(exercise_types[etype]["instruction"])
        
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
        
        # Build instructions
        content_instructions = []
        num_exercises = st.session_state.num_exercises
        
        if not st.session_state.include_theory:
            content_instructions.append("IKKE inkluder teori eller definisjoner")
        if not st.session_state.include_examples:
            content_instructions.append("IKKE inkluder eksempler")
        if st.session_state.include_exercises:
            content_instructions.append(f"Lag {num_exercises} oppgaver")
        if st.session_state.differentiation_mode:
            content_instructions.append("Lag tre nivåer: lett, middels, vanskelig")
        
        instructions = ". ".join(content_instructions)
        
        # Progress placeholder
        progress_placeholder = st.empty()
        
        try:
            with progress_placeholder.container():
                render_progress_indicator(0)
            
            with st.spinner(""):
                latex_result = run_crew(
                    grade=grade_options[selected_grade],
                    topic=topic,
                    material_type=selected_material,
                    instructions=instructions,
                    content_options=content_options
                )
                st.session_state.latex_result = latex_result
            
            progress_placeholder.empty()
            
            # Save files
            with st.spinner("Lagrer filer..."):
                tex_path = save_tex_file(latex_result, filename)
                pdf_path = generate_pdf(latex_result, filename)
                if pdf_path:
                    st.session_state.pdf_path = pdf_path
                    with open(pdf_path, "rb") as f:
                        st.session_state.pdf_bytes = f.read()
            
            # Add to history
            add_to_history(topic, selected_grade, selected_material, pdf_path, latex_result)
            
            st.session_state.generation_complete = True
            st.session_state.is_generating = False
            st.rerun()
            
        except Exception as e:
            progress_placeholder.empty()
            st.session_state.is_generating = False
            st.error(f"❌ Feil under generering: {e}")
    
    # Show results if complete
    if st.session_state.generation_complete and st.session_state.latex_result:
        render_results()
    
    # Footer
    st.markdown("""
    <div class="footer">
        <p>MateMaTeX © 2026 • Bygget med <a href="https://www.crewai.com/" target="_blank">CrewAI</a> og <a href="https://streamlit.io/" target="_blank">Streamlit</a></p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
