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
    """Add a generation to history."""
    entry = {
        "topic": topic,
        "grade": grade,
        "material_type": material_type,
        "timestamp": datetime.now().isoformat(),
        "pdf_path": pdf_path,
        "tex_content": tex_content,
    }
    if "history" not in st.session_state:
        st.session_state.history = []
    st.session_state.history.insert(0, entry)
    # Keep only last 20 entries
    st.session_state.history = st.session_state.history[:20]


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
    """Render the sidebar with history and settings."""
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
                    <span style="color: #10b981; font-size: 0.85rem; font-weight: 500;">Tilkoblet</span>
                </div>
                <div style="color: #9090a0; font-size: 0.75rem; margin-top: 0.25rem;">
                    {model_name}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="
                background: rgba(244, 63, 94, 0.1);
                border: 1px solid rgba(244, 63, 94, 0.2);
                border-radius: 8px;
                padding: 0.75rem;
                margin-bottom: 1rem;
            ">
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <span style="color: #f43f5e;">●</span>
                    <span style="color: #f43f5e; font-size: 0.85rem; font-weight: 500;">Ikke konfigurert</span>
                </div>
                <div style="color: #9090a0; font-size: 0.75rem; margin-top: 0.25rem;">
                    Legg til GOOGLE_API_KEY i .env
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # History section
        st.markdown("""
        <p class="section-label" style="margin-top: 1.5rem;">
            📜 Historikk
        </p>
        """, unsafe_allow_html=True)
        
        if st.session_state.history:
            for i, entry in enumerate(st.session_state.history[:5]):
                timestamp = datetime.fromisoformat(entry["timestamp"])
                time_str = timestamp.strftime("%d.%m %H:%M")
                
                st.markdown(f"""
                <div class="history-item">
                    <div class="history-topic">{entry["topic"][:30]}...</div>
                    <div class="history-meta">{entry["grade"]} • {time_str}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="
                text-align: center;
                padding: 2rem 1rem;
                color: #606070;
                font-size: 0.85rem;
            ">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">📭</div>
                Ingen genererte dokumenter ennå
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        
        # Quick links
        st.markdown("""
        <p class="section-label">🔗 Lenker</p>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="font-size: 0.85rem; color: #9090a0;">
            <a href="https://www.udir.no/lk20/mat01-05" target="_blank" 
               style="color: #f0b429; text-decoration: none;">
                📚 LK20 Læreplan
            </a>
        </div>
        """, unsafe_allow_html=True)


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
    """Render the results section."""
    st.markdown("""
    <div class="results-container">
        <div class="results-header">
            <div class="results-icon">✨</div>
            <div>
                <p class="results-title">Materiale generert!</p>
                <p class="results-subtitle">Last ned filene nedenfor</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.download_button(
            "📄 Last ned LaTeX (.tex)",
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
            st.info("💡 PDF krever pdflatex")
    
    with col3:
        # Copy to clipboard button using Streamlit's native functionality
        if st.button("📋 Kopier LaTeX", use_container_width=True):
            st.session_state.copied = True
            st.toast("✅ LaTeX-kode kopiert til utklippstavlen!")
        
        # JavaScript for clipboard (fallback)
        st.markdown(f"""
        <script>
        function copyLatex() {{
            navigator.clipboard.writeText(`{st.session_state.latex_result[:500]}...`);
        }}
        </script>
        """, unsafe_allow_html=True)
    
    # PDF Preview
    if st.session_state.pdf_bytes:
        import base64
        st.markdown('<p class="section-label" style="margin-top: 1.5rem;">👁️ Forhåndsvisning</p>', unsafe_allow_html=True)
        
        pdf_base64 = base64.b64encode(st.session_state.pdf_bytes).decode('utf-8')
        st.markdown(f'''
        <div class="pdf-preview">
            <iframe 
                src="data:application/pdf;base64,{pdf_base64}" 
                width="100%" 
                height="600px" 
                style="border: none; background: #fff;"
            ></iframe>
        </div>
        ''', unsafe_allow_html=True)
    
    # LaTeX code expander with copy functionality
    with st.expander("👁️ Se LaTeX-kode"):
        st.code(st.session_state.latex_result, language="latex")
        
        # Stats about the generated content
        lines = st.session_state.latex_result.count('\n')
        chars = len(st.session_state.latex_result)
        exercises = st.session_state.latex_result.count('\\begin{taskbox}')
        
        st.markdown(f"""
        <div class="stats-row" style="margin-top: 1rem;">
            <span class="stat-badge"><strong>{lines}</strong> linjer</span>
            <span class="stat-badge"><strong>{chars:,}</strong> tegn</span>
            <span class="stat-badge"><strong>{exercises}</strong> oppgaver</span>
        </div>
        """, unsafe_allow_html=True)


# ============================================================================
# MAIN APPLICATION
# ============================================================================
def main():
    """Main application function."""
    initialize_session_state()
    
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
