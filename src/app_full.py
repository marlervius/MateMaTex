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
# INJECT CSS STYLES FROM FILE
# ============================================================================
from src.ui import inject_styles
inject_styles()


# CSS is now loaded from src/ui/styles.css


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
        "school_name_data": "",
        "watermark_template": "generic",
        "watermark_active": False,
        "cover_page_active": False,
        "cover_style_id": "standard",
        "cover_teacher_name": "",
        "cover_class_name": "",
        "language_level": "standard",  # Language complexity: standard, b2, b1
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
    
    # Get language level from content_options
    language_level = content_options.get("language_level", "standard")
    
    agents = MathBookAgents(language_level=language_level)
    tasks = MathTasks()

    # Pass grade to all agents for level-appropriate content
    pedagogue = agents.pedagogue(grade=grade)
    mathematician = agents.mathematician(grade=grade)
    illustrator = agents.illustrator(grade=grade)
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
    # Import storage, translations, and cached functions
    from src.storage import save_settings, get_tex_content, delete_history_entry
    from src.cache import get_history, get_settings, invalidate_history_cache
    from src.translations import LANGUAGES, get_translator
    
    with st.sidebar:
        # Brand header
        st.markdown("""
        <div class="sidebar-brand">
            <h2>◇ MateMaTeX</h2>
            <p>AI-drevet oppgavegenerator</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Theme and language in compact row
        from src.tools import get_theme, generate_theme_css
        
        col_theme, col_lang = st.columns(2)
        with col_theme:
            theme_mode = st.selectbox(
                "Tema",
                options=["🌙 Mørk", "☀️ Lys"],
                index=0 if st.session_state.get("theme_mode", "dark") == "dark" else 1,
                label_visibility="collapsed"
            )
            st.session_state.theme_mode = "dark" if "Mørk" in theme_mode else "light"
        
        with col_lang:
            settings = get_settings()
            current_lang = settings.get("language", "no")
            lang_options = list(LANGUAGES.keys())
            current_idx = lang_options.index(current_lang) if current_lang in lang_options else 0
            
            selected_lang = st.selectbox(
                "Språk",
                options=lang_options,
                format_func=lambda x: LANGUAGES[x],
                index=current_idx,
                label_visibility="collapsed",
                key="language_selector"
            )
            
            if selected_lang != current_lang:
                settings["language"] = selected_lang
                save_settings(settings)
                st.session_state.language = selected_lang
                st.rerun()
        
        # Apply theme CSS
        theme = get_theme(st.session_state.get("theme_mode", "dark"))
        st.markdown(generate_theme_css(theme), unsafe_allow_html=True)
        
        # Get translator
        t = get_translator(selected_lang)
        
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        
        # Global search - always visible
        from src.tools import global_search, get_type_icon, get_type_label
        
        search_query = st.text_input(
            "🔍 Søk",
            placeholder="Søk i historikk, favoritter...",
            label_visibility="collapsed",
            key="global_search_input"
        )
        
        if search_query and len(search_query) >= 2:
            search_results = global_search(search_query, limit=5)
            
            if search_results:
                st.caption(f"Fant {len(search_results)} resultater")
                
                for result in search_results[:5]:
                    icon = get_type_icon(result.type)
                    if st.button(
                        f"{icon} {result.title[:28]}{'...' if len(result.title) > 28 else ''}",
                        key=f"sr_{result.id}",
                        use_container_width=True,
                        help=f"{get_type_label(result.type)}: {result.snippet[:50]}..."
                    ):
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
                st.caption("Ingen resultater funnet")
        
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        
        # API Status - compact
        api_configured = bool(os.getenv("GOOGLE_API_KEY"))
        model_name = os.getenv("GOOGLE_MODEL", "gemini-2.0-flash")
        
        if api_configured:
            st.markdown(f"""
            <div style="
                background: rgba(16, 185, 129, 0.08);
                border: 1px solid rgba(16, 185, 129, 0.2);
                border-radius: 8px;
                padding: 0.6rem 0.75rem;
                margin-bottom: 0.75rem;
            ">
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <span style="color: #10b981;">●</span>
                    <span style="color: #10b981; font-size: 0.8rem; font-weight: 500;">{t("connected")}</span>
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
        
        # History section - in expander for cleaner UI
        persistent_history = get_history()
        all_history = st.session_state.history + [h for h in persistent_history if h not in st.session_state.history]
        history_count = len(all_history)
        
        with st.expander(f"📜 {t('history')} ({history_count})", expanded=False):
            if all_history:
                for i, entry in enumerate(all_history[:6]):
                    try:
                        timestamp = datetime.fromisoformat(entry["timestamp"])
                        time_str = timestamp.strftime("%d.%m %H:%M")
                    except (ValueError, KeyError):
                        time_str = ""
                    
                    topic = entry.get("topic", "Ukjent emne")
                    grade = entry.get("grade", "")
                    entry_id = entry.get("id", "")
                    
                    col1, col2 = st.columns([5, 1])
                    
                    with col1:
                        if st.button(
                            f"📄 {topic[:22]}{'...' if len(topic) > 22 else ''}",
                            key=f"hist_{entry_id}_{i}",
                            use_container_width=True,
                            help=f"{grade} • {time_str}"
                        ):
                            tex_content = get_tex_content(entry_id)
                            if tex_content:
                                st.session_state.latex_result = tex_content
                                st.session_state.generation_complete = True
                                st.toast(f"📄 Lastet: {topic}")
                                st.rerun()
                    
                    with col2:
                        if st.button("🗑️", key=f"del_{entry_id}_{i}", help="Slett"):
                            delete_history_entry(entry_id)
                            st.toast("🗑️ Slettet")
                            st.rerun()
            else:
                st.caption(f"📭 {t('no_history')}")
        
        # My templates - in expander
        from src.tools import create_template, delete_template
        from src.cache import get_custom_templates
        custom_templates = get_custom_templates()
        
        with st.expander(f"🎨 {t('my_templates')} ({len(custom_templates)})", expanded=False):
            if custom_templates:
                for template in custom_templates[:5]:
                    col_t1, col_t2 = st.columns([5, 1])
                    with col_t1:
                        if st.button(
                            f"{template.emoji} {template.name}",
                            key=f"tmpl_{template.id}",
                            use_container_width=True,
                            help=template.description
                        ):
                            for key, value in template.config.items():
                                if hasattr(st.session_state, key):
                                    setattr(st.session_state, key, value)
                            st.toast(f"✅ Mal '{template.name}' lastet")
                            st.rerun()
                    with col_t2:
                        if st.button("🗑️", key=f"del_tmpl_{template.id}", help="Slett"):
                            delete_template(template.id)
                            st.toast("🗑️ Slettet")
                            st.rerun()
            
            st.markdown("---")
            st.caption("➕ Lag ny mal")
            new_name = st.text_input("Navn", placeholder="Min mal", key="new_tmpl_name", label_visibility="collapsed")
            col_emoji, col_save = st.columns([1, 2])
            with col_emoji:
                new_emoji = st.selectbox("Emoji", ["📝", "📖", "📋", "🎓", "📚"], key="new_tmpl_emoji", label_visibility="collapsed")
            with col_save:
                if st.button("💾 Lagre", use_container_width=True):
                    if new_name:
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
                        create_template(new_name, "Egendefinert mal", config, new_emoji)
                        st.toast(f"✅ Opprettet!")
                        st.rerun()
                    else:
                        st.warning("Skriv navn")
        
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        
        # Quick link to LK20
        st.markdown(f"""
        <a href="https://www.udir.no/lk20/mat01-05" target="_blank" 
           style="color: var(--accent-primary); text-decoration: none; font-size: 0.85rem; display: flex; align-items: center; gap: 0.5rem;">
            📚 {t("curriculum_link")} ↗
        </a>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        
        # Favorites section
        st.markdown(f"""
        <p class="section-label">⭐ {t("favorites")}</p>
        """, unsafe_allow_html=True)
        
        from src.tools import (
            get_favorite,
            delete_favorite,
            render_star_rating,
            get_item_folder,
            remove_item_from_index,
        )
        from src.cache import get_favorites, invalidate_favorites_cache
        
        favorites = get_favorites()
        
        # Apply folder/tag filters if set
        selected_folder_filter = st.session_state.get("filter_folder_id")
        selected_tag_filters: list[str] = st.session_state.get("filter_tags", []) or []
        
        def _fav_matches_filters(fav) -> bool:
            if selected_folder_filter:
                if get_item_folder("favorite", fav.id) != selected_folder_filter:
                    return False
            if selected_tag_filters:
                fav_tags = set(getattr(fav, "tags", []) or [])
                if not set(selected_tag_filters).issubset(fav_tags):
                    return False
            return True
        
        favorites_filtered = [f for f in favorites if _fav_matches_filters(f)]
        pinned = [f for f in favorites_filtered if f.is_pinned]
        recent = [f for f in favorites_filtered if not f.is_pinned][:5]
        
        all_favs = pinned + recent
        
        if all_favs:
            for fav in all_favs[:6]:
                pin_icon = "📌 " if fav.is_pinned else ""
                stars = render_star_rating(fav.rating)
                folder_id = get_item_folder("favorite", fav.id)
                folder_icon = "📁 " if folder_id else ""
                
                col_f1, col_f2 = st.columns([4, 1])
                with col_f1:
                    if st.button(
                        f"{folder_icon}{pin_icon}{fav.name}",
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
                        remove_item_from_index("favorite", fav.id)
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
                TAG_COLORS,
                get_folder_counts
            )
            
            # Folders
            st.markdown("**📁 Mapper**")
            folders = load_folders()
            folder_counts = get_folder_counts()
            
            # Filters
            st.markdown("**🔎 Filter**")
            folder_options = {"Alle mapper": None}
            for f in folders:
                folder_options[f"{f.icon} {f.name}"] = f.id
            
            selected_folder_label = st.selectbox(
                "Mappefilter",
                options=list(folder_options.keys()),
                index=0,
                label_visibility="collapsed",
                key="folder_filter_select",
            )
            st.session_state.filter_folder_id = folder_options.get(selected_folder_label)
            
            tags = load_tags()
            tag_names = [t.name for t in tags]
            selected_tags = st.multiselect(
                "Tagfilter",
                options=tag_names,
                default=st.session_state.get("filter_tags", []),
                label_visibility="collapsed",
                key="tag_filter_select",
            )
            st.session_state.filter_tags = selected_tags
            
            st.markdown("---")
            
            if folders:
                for folder in folders[:5]:
                    count = folder_counts.get(folder.id, 0)
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
                            <span style="color: #606070; font-size: 0.7rem;">({count})</span>
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
        st.markdown(f"""
        <p class="section-label">🏦 {t("exercise_bank")}</p>
        """, unsafe_allow_html=True)
        
        from src.tools import get_exercise, delete_exercise, get_exercise_stats, get_item_folder, remove_item_from_index
        from src.cache import get_exercises, invalidate_exercises_cache
        
        exercises = get_exercises()
        stats = get_exercise_stats()
        
        selected_folder_filter = st.session_state.get("filter_folder_id")
        selected_tag_filters = st.session_state.get("filter_tags", []) or []
        
        def _ex_matches_filters(ex) -> bool:
            if selected_folder_filter:
                if get_item_folder("exercise", ex.id) != selected_folder_filter:
                    return False
            if selected_tag_filters:
                ex_tags = set(getattr(ex, "tags", []) or [])
                if not set(selected_tag_filters).issubset(ex_tags):
                    return False
            return True
        
        exercises_filtered = [e for e in exercises if _ex_matches_filters(e)]
        
        if exercises_filtered:
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
            for ex in exercises_filtered[:5]:
                difficulty_emoji = {"lett": "🟢", "middels": "🟡", "vanskelig": "🔴"}.get(ex.difficulty, "⚪")
                folder_icon = "📁 " if get_item_folder("exercise", ex.id) else ""
                
                col_e1, col_e2 = st.columns([4, 1])
                with col_e1:
                    if st.button(
                        f"{difficulty_emoji} {folder_icon}{ex.title[:25]}...",
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
                        remove_item_from_index("exercise", ex.id)
                        st.toast("🗑️ Oppgave slettet")
                        st.rerun()
            
            if len(exercises_filtered) > 5:
                st.markdown(f"""
                <p style="color: #9090a0; font-size: 0.8rem; text-align: center;">
                    +{len(exercises_filtered) - 5} flere oppgaver
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
                Ingen oppgaver (eller ingen matcher filter)
            </div>
            """, unsafe_allow_html=True)
        
        # Usage Dashboard
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        
        with st.expander("📊 Bruksdashboard", expanded=False):
            from src.tools import get_usage_stats, get_dashboard_html, get_achievements, render_achievements_html
            
            stats = get_usage_stats()
            
            if stats.total_generations > 0:
                st.markdown(get_dashboard_html(stats), unsafe_allow_html=True)
                
                # Achievements
                achievements = get_achievements(stats)
                if achievements:
                    st.markdown("**🏆 Dine badges:**")
                    st.markdown(render_achievements_html(achievements), unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="text-align: center; padding: 1rem; color: #606070;">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">📊</div>
                    <p style="font-size: 0.85rem;">Ingen data ennå - generer noe innhold!</p>
                </div>
                """, unsafe_allow_html=True)
        
        # Watermark settings
        with st.expander("🖼️ Vannmerke / Logo", expanded=False):
            st.markdown("""
            <p style="color: #9090a0; font-size: 0.85rem; margin-bottom: 0.75rem;">
                Legg til skolelogo og navn på PDF-dokumenter.
            </p>
            """, unsafe_allow_html=True)
            
            # School name
            school_name = st.text_input(
                "Skolenavn",
                value=st.session_state.school_name_data,
                placeholder="F.eks. Trondheim videregående skole",
                key="watermark_school_name_select"
            )
            st.session_state.school_name_data = school_name
            
            # Template selection
            from src.tools import SCHOOL_TEMPLATES, render_watermark_preview_html
            
            template_options = {t["name"]: key for key, t in SCHOOL_TEMPLATES.items()}
            
            # Find current index for selectbox
            current_template_id = st.session_state.get("watermark_template", "generic")
            template_names = list(template_options.keys())
            try:
                current_index = [template_options[name] for name in template_names].index(current_template_id)
            except ValueError:
                current_index = 0

            selected_template_name = st.selectbox(
                "Mal",
                options=template_names,
                index=current_index,
                key="watermark_template_select"
            )
            st.session_state.watermark_template = template_options.get(selected_template_name, "generic")
            
            # Preview
            if school_name:
                st.markdown("**Forhåndsvisning:**")
                preview_html = render_watermark_preview_html(school_name, st.session_state.watermark_template)
                st.markdown(preview_html, unsafe_allow_html=True)
            
            # Enable watermark checkbox
            watermark_active = st.checkbox(
                "Aktiver vannmerke på PDF",
                value=st.session_state.watermark_active,
                key="watermark_active_toggle"
            )
            st.session_state.watermark_active = watermark_active
        
        # Cover page settings
        with st.expander("📄 Forside", expanded=False):
            st.markdown("""
            <p style="color: #9090a0; font-size: 0.85rem; margin-bottom: 0.75rem;">
                Legg til profesjonell forside på dokumentet.
            </p>
            """, unsafe_allow_html=True)
            
            from src.tools import COVER_STYLES
            
            # Enable cover page
            cover_page_active = st.checkbox(
                "Inkluder forside",
                value=st.session_state.cover_page_active,
                key="cover_page_active_toggle"
            )
            st.session_state.cover_page_active = cover_page_active
            
            if st.session_state.cover_page_active:
                # Style selection
                style_options = list(COVER_STYLES.keys())
                
                try:
                    style_index = style_options.index(st.session_state.cover_style_id)
                except (ValueError, AttributeError):
                    style_index = 0

                selected_style = st.selectbox(
                    "Forsidestil",
                    options=style_options,
                    format_func=lambda x: COVER_STYLES[x],
                    index=style_index,
                    key="cover_style_select"
                )
                st.session_state.cover_style_id = selected_style
                
                # Optional teacher name
                teacher_name = st.text_input(
                    "Lærernavn (valgfritt)",
                    value=st.session_state.cover_teacher_name,
                    placeholder="F.eks. Ola Nordmann",
                    key="cover_teacher_name_input"
                )
                st.session_state.cover_teacher_name = teacher_name
                
                # Class name override
                class_name = st.text_input(
                    "Klasse (valgfritt)",
                    value=st.session_state.cover_class_name,
                    placeholder="F.eks. 10A eller Matte 2P",
                    key="cover_class_name_input"
                )
                st.session_state.cover_class_name = class_name
                
                # Preview style
                style_previews = {
                    "modern": "🎨 Moderne design med geometriske aksenter",
                    "classic": "📚 Tradisjonelt lærebokutseende",
                    "minimal": "✨ Enkelt og profesjonelt",
                    "colorful": "🌈 Fargerikt for yngre elever",
                }
                st.info(style_previews.get(selected_style, ""))
        
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
    """Render the main configuration section with tabs for cleaner UX."""
    from src.cache import get_curriculum_topics, get_curriculum_goals, get_all_exercise_types
    
    # Initialize return values
    selected_grade = "8. trinn"
    grade_options = {}
    topic = ""
    selected_material = "arbeidsark"
    
    # Grade options
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
    
    # Use tabs for organized configuration
    tab1, tab2, tab3 = st.tabs(["📚 Innhold & Tema", "⚙️ Oppsett", "🎯 Avansert"])
    
    # ============================================
    # TAB 1: Content & Topic
    # ============================================
    with tab1:
        col1, col2 = st.columns([1.2, 0.8])
        
        with col1:
            st.markdown("""
            <div class="config-card">
                <div class="card-header">
                    <div class="card-icon gold">📚</div>
                    <div>
                        <p class="card-title">Klassetrinn og tema</p>
                        <p class="card-description">Basert på LK20 læreplan</p>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            selected_grade = st.selectbox(
                "Klassetrinn",
                options=list(grade_options.keys()),
                index=4,
                label_visibility="collapsed"
            )
            
            # Topic selection
            topics_by_category = get_curriculum_topics(selected_grade)
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
                st.caption("💡 Foreslåtte emner:")
                suggestion_cols = st.columns(2)
                for i, sugg in enumerate(suggestions[:4]):
                    with suggestion_cols[i % 2]:
                        difficulty_emoji = {"lett": "🟢", "middels": "🟡", "vanskelig": "🔴"}.get(sugg.get("difficulty", ""), "")
                        if st.button(
                            f"{difficulty_emoji} {sugg['topic']}",
                            key=f"sugg_{i}",
                            help=sugg.get("description", ""),
                            use_container_width=True
                        ):
                            st.session_state.suggested_topic = sugg['topic']
                            st.rerun()
                
                if hasattr(st.session_state, 'suggested_topic') and st.session_state.suggested_topic:
                    topic = st.session_state.suggested_topic
                    st.session_state.suggested_topic = None
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col2:
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
            
            # Quick content toggles
            st.markdown("""
            <div class="config-card">
                <div class="card-header">
                    <div class="card-icon violet">✨</div>
                    <div>
                        <p class="card-title">Inkluder</p>
                        <p class="card-description">Velg innholdstyper</p>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            col_a, col_b = st.columns(2)
            with col_a:
                st.session_state.include_theory = st.checkbox("📘 Teori", value=st.session_state.include_theory)
                st.session_state.include_examples = st.checkbox("💡 Eksempler", value=st.session_state.include_examples)
                st.session_state.include_exercises = st.checkbox("✍️ Oppgaver", value=st.session_state.include_exercises)
            with col_b:
                st.session_state.include_solutions = st.checkbox("🔑 Fasit", value=st.session_state.include_solutions)
                st.session_state.include_graphs = st.checkbox("📊 Grafer", value=st.session_state.include_graphs)
                st.session_state.include_tips = st.checkbox("💬 Tips", value=st.session_state.include_tips)
            
            st.markdown("</div>", unsafe_allow_html=True)
    
    # ============================================
    # TAB 2: Settings
    # ============================================
    with tab2:
        # Language level selector (for students with Norwegian as second language)
        st.markdown("""
        <div class="config-card">
            <div class="card-header">
                <div class="card-icon blue">🌍</div>
                <div>
                    <p class="card-title">Språknivå</p>
                    <p class="card-description">For elever med norsk som andrespråk</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        from src.agents.math_agents import LANGUAGE_LEVELS
        
        language_options = {
            "🇳🇴 Standard norsk": "standard",
            "📖 Forenklet norsk (B2)": "b2",
            "📝 Enklere norsk (B1)": "b1",
        }
        
        # Find current selection
        current_lang_level = st.session_state.get("language_level", "standard")
        current_lang_index = list(language_options.values()).index(current_lang_level) if current_lang_level in language_options.values() else 0
        
        selected_lang_display = st.selectbox(
            "Velg språknivå",
            options=list(language_options.keys()),
            index=current_lang_index,
            help="Velg enklere språk for elever som lærer norsk. Matematikknivået forblir det samme.",
            label_visibility="collapsed"
        )
        st.session_state.language_level = language_options[selected_lang_display]
        
        # Show description of selected level
        selected_level_info = LANGUAGE_LEVELS.get(st.session_state.language_level, {})
        if st.session_state.language_level != "standard":
            st.info(f"**{selected_level_info.get('code', '')}:** {selected_level_info.get('description', '')}")
            st.caption("💡 Det matematiske innholdet er det samme - bare språket er tilpasset.")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Exercise settings
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
            
            if st.session_state.include_exercises:
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
            else:
                st.caption("Aktiver 'Oppgaver' i Innhold-fanen for å se innstillinger.")
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col2:
            # Exercise types
            st.markdown("""
            <div class="config-card">
                <div class="card-header">
                    <div class="card-icon blue">📝</div>
                    <div>
                        <p class="card-title">Oppgavetyper</p>
                        <p class="card-description">Velg hvilke typer oppgaver</p>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            if st.session_state.include_exercises:
                exercise_types = get_all_exercise_types()
                selected_types = []
                for type_key, type_info in list(exercise_types.items())[:6]:
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
            else:
                st.caption("Aktiver 'Oppgaver' først.")
            
            st.markdown("</div>", unsafe_allow_html=True)
    
    # ============================================
    # TAB 3: Advanced
    # ============================================
    with tab3:
        col1, col2 = st.columns(2)
        
        with col1:
            # Competency goals
            st.markdown("""
            <div class="config-card">
                <div class="card-header">
                    <div class="card-icon gold">🎯</div>
                    <div>
                        <p class="card-title">Kompetansemål (LK20)</p>
                        <p class="card-description">Velg mål materialet skal dekke</p>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            competency_goals = get_curriculum_goals(selected_grade)
            if competency_goals:
                selected_goals = []
                for i, goal in enumerate(competency_goals[:8]):
                    if st.checkbox(goal[:60] + "..." if len(goal) > 60 else goal, key=f"goal_{i}", help=goal):
                        selected_goals.append(goal)
                st.session_state.selected_competency_goals = selected_goals
            else:
                st.caption("Ingen kompetansemål tilgjengelig for dette trinnet.")
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col2:
            # Formula library
            st.markdown("""
            <div class="config-card">
                <div class="card-header">
                    <div class="card-icon emerald">📐</div>
                    <div>
                        <p class="card-title">Formelbibliotek</p>
                        <p class="card-description">Kopier formler til oppgaver</p>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            from src.cache import get_formula_categories, get_formulas_for_category
            
            categories = get_formula_categories()
            selected_category = st.selectbox(
                "Kategori",
                options=categories,
                label_visibility="collapsed"
            )
            
            formulas = get_formulas_for_category(selected_category)
            
            for formula in formulas[:5]:
                col_f1, col_f2 = st.columns([4, 1])
                with col_f1:
                    st.markdown(f"**{formula.name}**")
                    st.latex(formula.latex)
                with col_f2:
                    if st.button("📋", key=f"copy_{formula.name}", help="Kopier"):
                        st.session_state.copied_formula = formula.latex
                        st.toast(f"✅ Kopiert!")
            
            st.markdown("</div>", unsafe_allow_html=True)
    
    return selected_grade, grade_options, topic, selected_material


def render_progress_indicator(current_step: int):
    """Render an animated progress indicator using native Streamlit components."""
    steps = [
        {"emoji": "🎓", "title": "Pedagogen planlegger", "desc": "Analyserer læreplan og strukturerer innhold"},
        {"emoji": "📐", "title": "Matematikeren skriver", "desc": "Genererer oppgaver og forklaringer"},
        {"emoji": "🎨", "title": "Illustratøren tegner", "desc": "Lager figurer og grafer"},
        {"emoji": "📝", "title": "Redaktøren ferdigstiller", "desc": "Setter sammen og kvalitetssikrer"},
    ]
    
    st.markdown("### 🔄 AI-teamet arbeider...")
    st.caption("Dette kan ta 30-60 sekunder")
    
    st.markdown("---")
    
    for i, step in enumerate(steps):
        if i < current_step:
            # Done
            st.success(f"✅ **{step['title']}** — {step['desc']}")
        elif i == current_step:
            # Active
            st.info(f"{step['emoji']} **{step['title']}** — {step['desc']}")
        else:
            # Pending
            st.markdown(f"⏳ {step['title']} — _{step['desc']}_")


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
        # PowerPoint export
        from src.tools import is_pptx_available, latex_to_pptx
        
        if is_pptx_available():
            if st.button("📽️ PowerPoint", use_container_width=True):
                with st.spinner("Lager presentasjon..."):
                    output_path = Path("output") / f"matematikk_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pptx"
                    output_path.parent.mkdir(exist_ok=True)
                    pptx_path = latex_to_pptx(st.session_state.latex_result, str(output_path))
                    if pptx_path and Path(pptx_path).exists():
                        st.session_state.pptx_path = pptx_path
                        st.toast("✅ Presentasjon opprettet!")
                        st.rerun()
        else:
            st.button("📽️ PPTX", disabled=True, use_container_width=True, help="Installer python-pptx")
    
    # Show PPTX download if available
    if hasattr(st.session_state, 'pptx_path') and st.session_state.pptx_path:
        pptx_path = Path(st.session_state.pptx_path)
        if pptx_path.exists():
            with col4:
                with open(pptx_path, "rb") as f:
                    st.download_button(
                        "⬇️ Last ned PPTX",
                        data=f.read(),
                        file_name=pptx_path.name,
                        mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
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
            
            fav = add_favorite(
                name=fav_name,
                topic=st.session_state.get("selected_topic", "Matematikk"),
                grade_level=st.session_state.get("selected_grade", "8. trinn"),
                material_type=st.session_state.get("material_type", "arbeidsark"),
                latex_content=st.session_state.latex_result,
                pdf_path=st.session_state.get("pdf_path"),
                rating=4
            )
            # Assign folder if user selected one
            try:
                from src.tools import set_item_folder
                folder_id = st.session_state.get("filter_folder_id")
                if folder_id and fav:
                    set_item_folder("favorite", fav.id, folder_id)
            except Exception as e:
                import logging
                logging.warning(f"Kunne ikke tilordne mappe til favoritt: {e}")
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
                    # Assign folder based on current filter
                    try:
                        from src.tools import set_item_folder
                        folder_id = st.session_state.get("filter_folder_id")
                        if folder_id:
                            for ex_obj in saved:
                                set_item_folder("exercise", ex_obj.id, folder_id)
                    except Exception as e:
                        import logging
                        logging.warning(f"Kunne ikke tilordne mappe til oppgaver: {e}")
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
                            
                            ex_obj = add_exercise(
                                title=ex['title'],
                                topic=st.session_state.get("selected_topic", "Matematikk"),
                                grade_level=st.session_state.get("selected_grade", "8. trinn"),
                                latex_content=ex['full_latex'],
                                difficulty=ex.get('difficulty', 'middels'),
                                solution=ex.get('solution'),
                                source="generated"
                            )
                            # Assign folder based on current filter
                            try:
                                from src.tools import set_item_folder
                                folder_id = st.session_state.get("filter_folder_id")
                                if folder_id and ex_obj:
                                    set_item_folder("exercise", ex_obj.id, folder_id)
                            except Exception as e:
                                import logging
                                logging.warning(f"Kunne ikke tilordne mappe til oppgave: {e}")
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
    
    # Generate Button - wrapped for gold styling
    st.markdown('<div class="generate-button">', unsafe_allow_html=True)
    generate_clicked = st.button("◇ Generer materiale", disabled=not can_generate, use_container_width=True, type="primary")
    st.markdown('</div>', unsafe_allow_html=True)
    
    if generate_clicked:
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
        from src.cache import get_all_exercise_types
        exercise_types = get_all_exercise_types()
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
            "language_level": st.session_state.get("language_level", "standard"),
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
            
            # Apply watermark if enabled
            if st.session_state.watermark_active and st.session_state.school_name_data:
                from src.tools import apply_watermark_template
                latex_result = apply_watermark_template(
                    latex_result,
                    template_key=st.session_state.watermark_template,
                    school_name=st.session_state.school_name_data,
                    document_title=topic,
                    class_name=selected_grade
                )
                st.session_state.latex_result = latex_result
            
            # Apply cover page if enabled
            if st.session_state.cover_page_active:
                from src.tools import CoverPageConfig, insert_cover_page
                cover_config = CoverPageConfig(
                    title=topic,
                    subtitle=selected_material.title() if selected_material else None,
                    grade=selected_grade,
                    school_name=st.session_state.school_name_data,
                    teacher_name=st.session_state.cover_teacher_name,
                    class_name=st.session_state.cover_class_name or selected_grade,
                    style=st.session_state.cover_style_id
                )
                latex_result = insert_cover_page(latex_result, cover_config)
                st.session_state.latex_result = latex_result
            
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
            
            # Record usage statistics
            from src.tools import record_generation
            record_generation(
                topic=topic,
                grade=selected_grade,
                material_type=selected_material,
                num_exercises=st.session_state.get("num_exercises", 10)
            )
            
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
