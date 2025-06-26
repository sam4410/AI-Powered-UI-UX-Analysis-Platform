import streamlit as st
import os
import tempfile
from dotenv import load_dotenv
from PIL import Image
import sys
try:
    import pysqlite3
    sys.modules['sqlite3'] = pysqlite3
except ImportError:
    pass
from crewai_tools import VisionTool
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
import io
from utils.html_utils import extract_html_from_task_result
from utils.mockup_renderer import render_mockup_tab
from utils.diagnostics import timed_agent_task, display_latency_summary
from utils.custom_image_interpreter import CustomImageInterpreter
from utils.layout_injection import extract_layout_tree, build_mockup_prompt
from utils.wireframe_annotator import annotate_wireframe_with_suggestions
from utils.helpers import format_design_goals
import nest_asyncio
nest_asyncio.apply()

# Load environment variables
load_dotenv(override=True)

# Configure Streamlit page
st.set_page_config(
    page_title="AI-Powered UI/UX Analysis Platform",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

def initialize_agents_and_tasks(image_path: str, desc_output: str = ""):
    """Initialize all agents and tasks with the given image path"""
    goal_context = format_design_goals(st.session_state.get("design_goals", []))
    vision_tool = VisionTool()

    # --- Phase 1 Agents and Tasks ---
    description_agent = Agent(
        role="Visual Design Interpreter",
        goal=f"Analyze the provided UI/UX image ({image_path}), to understand the layout and hierarchy. Deliver a structured, detailed description of all visible elements, layout structure,  interactions, and intended user journey",
        backstory="""
        You analyze and break down visual design into a component tree and layout summary.
        You are an expert in visual systems who excels at translating static UI visuals into rich, structured semantic descriptions. 
        Your insights help bridge visual design with functional understanding.""",
        verbose=True,
        tools=[CustomImageInterpreter()],
        llm=ChatOpenAI(model="gpt-4o", 
        temperature=0.1,
        model_kwargs={
        "system_message": f"{goal_context}\n\nYou are a highly skilled visual design interpreter."})
    )

    description_task = Task(
        description="Identify and fully describe a digital image and explain its purpose",
        expected_output="""
        - Component-wise breakdown (e.g., headers, navbars, forms)
        - Layout structure (e.g., grid, hierarchy, visual flow)
        - Interaction elements (buttons, forms, etc.)
        - Purpose and user journey inference
        - Accessibility and responsiveness cues if any
        """,
        agent=description_agent
    )

    critique_agent = Agent(
        role="Usability & Design Critic",
        goal=f"Provide a deep and constructive critique of the design image ({image_path}), identifying UX problems, visual inconsistencies, interaction gaps, and accessibility concerns based on the design description.",
        backstory="With years of experience auditing interfaces, you specialize in identifying design flaws and missed opportunities that hinder user experience or brand perception.",
        verbose=True,
        tools=[CustomImageInterpreter()],
        llm=ChatOpenAI(model="gpt-4o-mini", 
        temperature=0.1,
        model_kwargs={
        "system_message": f"{goal_context}\n\nYou are a highly skilled visual design ad usability critique."})
    )

    critique_task = Task(
        description="Critically analyze the image based on its description and intended purpose",
        expected_output="""
        - UX/usability concerns (e.g., flow confusion, cognitive overload)
        - Visual design issues (e.g., contrast, spacing, alignment)
        - Inconsistencies or misalignments in design language
        - Mobile/responsive layout issues
        - Annotated list of critique points
        """,
        agent=critique_agent,
        context=[description_task]
    )

    ux_suggestion_agent = Agent(
        role="UX Design Strategist",
        goal=f"Propose clear and actionable design improvements rooted in best practices and user-centered design for the image {image_path}, using the critique and image analysis as foundation.",
        backstory="You bring UI/UX design excellence and strategic thinking to the table. Your role is to turn critique into meaningful, creative, and practical layout changes that elevate user experience.",
        verbose=True,
        tools=[CustomImageInterpreter()],
        llm=ChatOpenAI(model="gpt-4o-mini", 
        temperature=0.1,
        model_kwargs={
        "system_message": f"{goal_context}\n\nYou are a highly skilled design strategist suggesting improvements."})
    )

    ux_suggestion_task = Task(
        description="Provide suggestion for improving the image design based on the context from description and critique agents",
        expected_output="""
        - Actionable design recommendations (mapped to issues)
        - Suggested layout or component reorganization
        - Enhancements for usability, readability, and visual hierarchy
        - Specific interaction improvements (e.g., hover effects, form usability)
        - Optional references to design systems or standards (e.g., Material, HIG)
        """,
        agent=ux_suggestion_agent,
        context=[description_task, critique_task]
    )

    pm_agent = Agent(
        role="AI Product Manager",
        goal=f"Convert UX suggestions collected for the image {image_path} into well-scoped user stories with acceptance criteria, estimating impact and prioritize the suggestion based on expected business value and effort/cost considerations.",
        backstory="You operate as a client-facing product strategist, skilled at balancing user needs and business constraints. You translate insights into agile-ready requirements with clear prioritization signals.",
        verbose=True,
        tools=[CustomImageInterpreter()],
        llm=ChatOpenAI(model="gpt-4o-mini", 
        temperature=0.1,    
        model_kwargs={
        "system_message": f"{goal_context}\n\nYou are a highly skilled product manager with experience in handling UI/UX design projects."})
    )

    pm_task = Task(
        description="Write the user stories based on suggestion from the ux suggestion agent for the image and prioritize the suggestions based on probable customer feedback",
        expected_output="""
        - User stories in format: “As a [user], I want to [goal], so that [benefit]”
        - Associated acceptance criteria per story
        - Priority tagging: Critical / Medium / Low
        - Rationale for prioritization (impact vs cost/effort)
        - Optional dev/UX team note per story
        """,
        agent=pm_agent,
        context=[description_task, critique_task, ux_suggestion_task]
    )

    phase1_agents = [description_agent, critique_agent, ux_suggestion_agent, pm_agent]
    phase1_tasks = [description_task, critique_task, ux_suggestion_task, pm_task]

    # --- Phase 2: Mockup Generation ---
    phase2_agents, phase2_tasks = [], []
    combined_prompt = None

    if desc_output:
        hierarchy_tree = extract_layout_tree(desc_output or "")
        mockup_system_prompt = build_mockup_prompt(hierarchy_tree)

        with open("prompts/mockup_prompt_tailwind.txt", "r", encoding="utf-8") as f:
            tailwind_prompt = f.read()

        combined_prompt = f"{tailwind_prompt.strip()}\n\n{mockup_system_prompt.strip()}"

        mockup_agent = Agent(
            role="Mockup Generator Agent",
            goal="Generate responsive HTML wireframes using only Tailwind CSS utility classes and using the structured input from user stories, suggestions, and critiques to visually reflect the improved design.",
            backstory=(
                "You are a frontend specialist in prototyping UI layouts using Tailwind CSS. "
                "You create modern, clean HTML mockups based on UX critiques and user stories."
            ),
            verbose=True,
            tools=[CustomImageInterpreter()],
            llm=ChatOpenAI(
                model="gpt-4o",
                temperature=0.4,
                model_kwargs={
                    "system_message": combined_prompt}
                )
        )

        mockup_task = Task(
            description=(
                f"You are a senior UI developer tasked with generating a responsive, modern HTML wireframe layout for provided design image ({image_path}). Use the custom image interpreter tool"
                "based on UX critique and product manager recommendations. Your layout should follow modern UI principles "
                "with proper use of HTML5 semantics and CSS Flexbox or Grid for structure. Use cards, buttons, dropdown menus, "
                "status badges, and color-coded sections to reflect interactive elements. Do not use JavaScript. "
                "Only output clean HTML starting with <!DOCTYPE html>, including a <style> block inside <head>."
            ),
            expected_output="""
            - A Tailwind-based HTML mockup with:
            - Visual highlights on updated sections (e.g., `ring-2 ring-blue-500`)
            - Each highlighted section must include a tooltip or inline comment describing the implemented change
            - A summary block at the bottom of the HTML under `<footer>` listing each implemented recommendation
            - A polished HTML wireframe with professional CSS styling and component-based layout.
            - Visual hierarchy improvements implemented
            - Annotated highlights of incorporated suggestions
            - Design format: HTML/CSS snippet (as applicable)
            """,
            agent=mockup_agent,
            context=[description_task, critique_task, ux_suggestion_task, pm_task]
        )

        phase2_agents = [mockup_agent]
        phase2_tasks = [mockup_task]

    return {
        "phase1": {"agents": phase1_agents, "tasks": phase1_tasks},
        "phase2": {"agents": phase2_agents, "tasks": phase2_tasks},
        "prompt_used": combined_prompt
    }

def run_analysis(image_path, use_individual_tasks=False):
    try:
        status_placeholder = st.empty()
        timings = {}

        # --- Phase 1 ---
        with st.spinner("🔍 Running Phase 1: UI/UX Analysis..."):
            phase1 = initialize_agents_and_tasks(image_path)
            crew1 = Crew(
                agents=phase1["phase1"]["agents"],
                tasks=phase1["phase1"]["tasks"],
                verbose=True,
                process=Process.sequential
            )

            phase1_result, time1 = timed_agent_task("🔍 Phase 1: Analysis", lambda: crew1.kickoff(), status_placeholder)
            timings["Phase 1"] = time1
            
        desc_output = phase1["phase1"]["tasks"][0].output.response if hasattr(phase1["phase1"]["tasks"][0].output, "response") else str(phase1["phase1"]["tasks"][0].output)

        # --- Phase 2 ---
        with st.spinner("🎨 Running Phase 2: Mockup Generation..."):
            phase2 = initialize_agents_and_tasks(image_path, desc_output=desc_output)
            if not phase2["phase2"]["tasks"]:
                st.warning("⚠️ No mockup generation task created. Description output may have failed.")
                return None

            crew2 = Crew(
                agents=phase2["phase2"]["agents"],
                tasks=phase2["phase2"]["tasks"],
                verbose=True,
                process=Process.sequential
            )

            phase2_result, time2 = timed_agent_task("🎨 Phase 2: Mockup Generation", lambda: crew2.kickoff(), status_placeholder)
            timings["Phase 2"] = time2

        # Summary
        display_latency_summary(timings)

        # Store results in session state
        st.session_state["analysis_result"] = {
            "description_task": phase1["phase1"]["tasks"][0].output,
            "critique_task": phase1["phase1"]["tasks"][1].output,
            "ux_suggestion_task": phase1["phase1"]["tasks"][2].output,
            "pm_task": phase1["phase1"]["tasks"][3].output,
            "mockup_task": phase2["phase2"]["tasks"][0].output if phase2["phase2"]["tasks"] else ""
        }
        st.session_state["analysis_done"] = True
        
        return st.session_state["analysis_result"]

    except Exception as e:
        st.error(f"An error occurred during analysis: {str(e)}")
        return None

def main():
    st.title("🎨 AI-Powered UI/UX Analysis Platform")
    col_left, col_right = st.columns([1, 1])
    with col_left:
        st.markdown("""
        **Transform your UI/UX designs with intelligent multi-agent analysis and automated wireframe generation**

        This platform uses **five AI agents in two phases**:

        ### 🔍 Phase 1: Analysis
        - 🖼️ Visual Design Interpreter
        - 🔬 UX Critique Agent
        - 💡 UX Suggestion Agent
        - 📋 AI Product Manager

        ### 🎨 Phase 2: Implementation
        - 🖌️ Mockup Generator (Tailwind CSS wireframe)

        ✅ Powered by OpenAI + CrewAI agents
        """)
    
    with col_right:
        st.markdown(
            """
            <div style='
                background-color: #f9f9f9;
                padding: 1rem 1.2rem;
                border: 1px solid #ddd;
                border-radius: 10px;
                box-shadow: 2px 2px 6px rgba(0,0,0,0.05);
            '>
                <h4 style="margin-top: 0;">📦 <strong>Two-Phase Analysis Process</strong></h4>
            
            <div style='
                background-color: #f9f9f9;
                padding: 1rem 1.2rem;
                border: 1px solid #ddd;
                border-radius: 10px;
                box-shadow: 2px 2px 6px rgba(0,0,0,0.05);
            '>    
                <h5 style="margin-bottom: 0.25rem;">📊 Phase 1 - Analysis (4 Agents)</h5>
                <ul style="margin-top: 0;">
                    <li>Comprehensive design understanding</li>
                    <li>Critical evaluation and issue identification</li>
                    <li>Strategic improvement recommendations</li>
                    <li>Business-focused user story creation</li>
                </ul>
            </div>
            
            <div style='
                background-color: #f9f9f9;
                padding: 1rem 1.2rem;
                border: 1px solid #ddd;
                border-radius: 10px;
                box-shadow: 2px 2px 6px rgba(0,0,0,0.05);
            '>
                <h5 style="margin-bottom: 0.25rem;">🎨 Phase 2 - Implementation (1 Agent)</h5>
                <ul style="margin-top: 0;">
                    <li>HTML/CSS wireframe generation</li>
                    <li>Integration of all Phase 1 insights</li>
                    <li>Responsive and accessible design output</li>
                    <li>Professional component-based layout</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    st.divider()
    
    # Check for OpenAI API key
    if not os.getenv('OPENAI_API_KEY'):
        st.error("⚠️ OpenAI API key not found. Please set your OPENAI_API_KEY environment variable.")
        st.info("You can get your API key from: https://platform.openai.com/api-keys")
        return
    
    # Sidebar for instructions and info
    with st.sidebar:
        st.header("📖 How to use")
        st.markdown("""
        1. **Upload Image**: Select a UI/UX design image (PNG, JPG, JPEG)
        2. **Start Analysis**: Click the analyze button to initiate the 5-agent workflow
        3. **Review Phase 1**: Examine detailed analysis from 4 specialist agents
        4. **View Wireframe**: See the AI-generated improved mockup in Phase 2
        5. **Implement Changes**: Use prioritized recommendations and wireframe as development guide
        """)
        
        st.header("🎯 Best Results With")
        st.markdown("""
        - **Website mockups** & landing pages
        - **Mobile app interfaces** & screens  
        - **Dashboard designs** & admin panels
        - **E-commerce layouts** & product pages
        - **Navigation menus** & user flows
        - **Form designs** & checkout processes
        """)
        
        st.header("🎯 Redesign Goals")
        # Let user select one or more design goals
        selected_goals = st.multiselect(
        "Choose your design improvement focus:",
        ["Accessibility Boost", "Conversion Optimization", "Mobile-first UX"],
        help="These goals will guide how the AI agents analyze and suggest improvements",
        key="Redesign_goals_selection"
        )
        
        # Save to session state for persistence
        st.session_state["design_goals"] = selected_goals
        
        st.header("🧪 Annotation Toggle")
        st.session_state.enable_annotations = st.checkbox("🔲 Enable Visual Annotations", value=st.session_state.get("enable_annotations", False), key="enable_annotations_toggle")
        
        st.header("⚙️ System Status")
        st.success("✅ 5-agent multi-phase system ready")
        st.success("✅ Vision analysis enabled")
        st.success("✅ Wireframe generation active")
        if os.getenv('OPENAI_API_KEY'):
            st.success("✅ OpenAI API connected")
        else:
            st.error("❌ OpenAI API key missing")
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    temp_image_path = None
    
    with col1:
        st.header("📤 Upload Your UI Design")
        uploaded_file = st.file_uploader(
            "Upload design in PNG/JPG/JPEG",
            type=['png', 'jpg', 'jpeg'],
            help="Upload an image of your UI/UX design for analysis"
        )
        
        if uploaded_file:   
            # Display the uploaded image
            img = Image.open(uploaded_file)
            st.image(img, caption="Uploaded UI Design", use_container_width=True)
            
            # Show image details
            st.info(f"📊 Original Image Size is: {img.size[0]}x{img.size[1]} pixels, Format: {img.format}")
            
            # Resize to reasonable width (optional height can be auto-scaled)
            if img.width > 1000:
                ratio = 1000 / img.width
                img = img.resize((1000, int(img.height * ratio)))
                st.info(f"📐 Image resized to {img.size[0]}x{img.size[1]} pixels for faster analysis")
                
            st.session_state.uploaded_img = img  # store image in session after resizing
                
    with col2:
        # Information about the process
        st.header("🚀 Run 5-Agent Analysis")
        
        if uploaded_file:
            if st.button("🔍 Start 5-Agent AI Analysis", type="primary", use_container_width=True):
                try:
                    # Save uploaded file temporarily
                    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        temp_image_path = tmp_file.name
                
                    # Run the analysis
                    result = run_analysis(temp_image_path)
                    
                    # Store in session state
                    if result:
                        st.session_state.analysis_result = result
                        st.session_state.analysis_done = True
                        st.success("✅ 5-Agent analysis completed successfully!")
                except Exception as e:
                    st.error(f"Error during analysis: {str(e)}")
                finally:
                    if temp_image_path and os.path.exists(temp_image_path):
                        os.unlink(temp_image_path)
    
    # --- Analysis Results (Separate Block) ---
    img = st.session_state.get("uploaded_img", None)
    
    # 🔁 Re-render if already analyzed
    if st.session_state.get("analysis_done"):
        result = st.session_state.analysis_result
        enable_annotations = st.session_state.get("enable_annotations", False)
        
        show_comparison = st.checkbox("🖼️ Show Side-by-Side Comparison View", value=False, key="show_comparison_toggle")
                        
        # 🎯 Show Active Redesign Goals if present
        if st.session_state.get("design_goals"):
            st.markdown("### 🎯 Active Redesign Goals")
            st.info("These goals influenced how each agent analyzed your UI and generated suggestions:")
            st.markdown(f"**{', '.join(st.session_state['design_goals'])}**")
        
        # Display results
        st.header("📋 Full Analysis Results")
        
        # Create tabs for different sections of results
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🖼️ Description", 
            "🔬 Critique", 
            "💡 Suggestions", 
            "📋 Action Items", 
            "🎨 AI Wireframe"
            ])
                        
        with tab1:
            st.subheader("🖼️ Visual Design Interpretation")
            st.markdown("**Agent Role:** Visual Design Interpreter - Analyzes layout hierarchy and component structure")
            st.write(result["description_task"])
                        
        with tab2:
            st.subheader("🔬 UX Critique & Usability Issues")
            st.markdown("**Agent Role:** Usability & Design Critic - Identifies UX problems and design inconsistencies")
            st.write(result["critique_task"])
                        
        with tab3:
            st.subheader("💡 Strategic Design Improvements")
            st.markdown("**Agent Role:** UX Design Strategist - Provides actionable recommendations based on best practices")
            st.write(result["ux_suggestion_task"])
                        
        with tab4:
            st.subheader("📋 Prioritized User Stories & Action Items")
            st.markdown("**Agent Role:** AI Product Manager - Converts insights into development-ready user stories")
            st.write(result["pm_task"])
                        
        with tab5:
            st.subheader("🎨 AI Generated Tailwind-Based HTML Mockup")
            st.markdown("""
            **Agent Role:** Mockup Generator Agent - Creates responsive HTML wireframes incorporating all Phase 1 improvements
            """)
                            
            # Extract mockup HTML
            raw_html = extract_html_from_task_result(result.get("mockup_task", ""))
            pm_output = str(result.get("pm_task", ""))
            
            if show_comparison and img:
                st.subheader("🔍 Side-by-Side Visual Comparison")
                
                col_original, col_mockup = st.columns([1, 1])
                
                with col_original:
                    st.markdown("**📥 Original Uploaded UI Design**")
                    st.image(img, caption="Original Design", use_container_width=True)
                    
                with col_mockup:
                    st.markdown("**🎨 AI-Generated Wireframe**")
                    if enable_annotations:
                        annotated_html = annotate_wireframe_with_suggestions(raw_html, pm_output)
                        render_mockup_tab(annotated_html)
                    else:
                        render_mockup_tab(raw_html)
                            
            if not raw_html:
                st.error("❌ Could not extract valid HTML from mockup agent.")
            else:
                if enable_annotations:
                    annotated_html = annotate_wireframe_with_suggestions(raw_html, pm_output)
                    render_mockup_tab(annotated_html)
                else:
                    render_mockup_tab(raw_html)
                st.success("🎉 **Wireframe Successfully Generated!** The mockup above incorporates improvements from all 4 analysis agents.")
                        
        # Create a Markdown-formatted report from Agent 1 to 4
        markdown_report = f"""
# 🧠 AI-Powered UI/UX Analysis Summary

---

## 🔍 1. UI Layout Description (Agent 1)\n
{result.get("description_task", "_No output generated._")}

---

## 🔬 2. UX Critique & Issues (Agent 2)\n
{result.get("critique_task", "_No output generated._")}

---

## 💡 3. Design Suggestions (Agent 3)\n
{result.get("ux_suggestion_task", "_No output generated._")}

---

## 📋 4. Product Manager User Stories (Agent 4)\n
{result.get("pm_task", "_No output generated._")}
"""

        if st.session_state.get("design_goals"):
            markdown_report += f"\n---\n\n## 🎯 Redesign Goals\n{', '.join(st.session_state['design_goals'])}\n"
                        
        # Download option for results
        st.download_button(
            label="📥 Download Full Analysis Report",
            data=markdown_report,
            file_name="ui_ux_analysis_summaries.txt",
            mime="text/plain",
            help="Download a text summary of all agent outputs except the mockup HTML",
            key="full_report_download_btn"
        )
    else:
        st.info("👆 Please upload a UI/UX design image to start the comprehensive 5-agent analysis process")

    # Footer
    st.divider()
    st.markdown("""
    <div style='text-align: center; color: #666; margin-top: 2rem;'>
        <p><strong>🤖 Powered by 5-Agent CrewAI Multi-Phase System</strong></p>
        <p>Phase 1: Analysis & Strategy (4 Agents) → Phase 2: Wireframe Implementation (1 Agent)</p>
        <p>Built with Streamlit | Enhanced with Tailwind CSS Mockup Generation</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
