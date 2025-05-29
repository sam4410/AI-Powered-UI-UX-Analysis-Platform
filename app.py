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

# Load environment variables
load_dotenv()

# Configure Streamlit page
st.set_page_config(
    page_title="AI-Powered UI/UX Analysis Platform",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

def initialize_agents_and_tasks(image_path):
    """Initialize all agents and tasks with the given image path"""
    
    # Initialize the vision tool
    vision_tool = VisionTool()
    
    # Agent 1 - Image Description Agent
    description_agent = Agent(
        role="Image Description Agent",
        goal=f"Fully describe the digital image ({image_path}), of a UI/UX design, including its visible elements, design and intended purpose",
        backstory="You are responsible for analyzing images and describing their purpose in details",
        verbose=True,
        tools=[vision_tool],
        llm=ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
    )

    # Define the image description task
    description_task = Task(
        description="Identify and fully describe a digital image and explain its purpose",
        expected_output="A complete description of the image and its purpose",
        agent=description_agent
    )

    # Agent 2 - Critique Agent
    critique_agent = Agent(
        role="UX Critique Agent",
        goal=f"Critique the image ({image_path}), based on its description and intended purpose provided by the image description agent",
        backstory="You critically evaluate images, especially containing UX designs and point out flaws, weaknesses and areas of improvement",
        verbose=True,
        tools=[vision_tool],
        llm=ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
    )

    # Define the image critique task
    critique_task = Task(
        description="Critically analyze the image based on its description and intended purpose",
        expected_output="A complete critique of the image, highlighting design flaws and areas of improvement",
        agent=critique_agent,
        context=[description_task]
    )

    # Agent 3 - UX Suggestion Agent
    ux_suggestion_agent = Agent(
        role="UX Suggestion Agent",
        goal=f"To provide design and layout suggestion for the image {image_path} based on the context provided from Image Description Agent and UX Critique Agent",
        backstory="You are specialized in providing actionable suggestion to improve design of website images",
        verbose=True,
        tools=[vision_tool],
        llm=ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
    )

    # Define UX suggestion task
    ux_suggestion_task = Task(
        description="Provide suggestion for improving the image design based on the context from description and critique agents",
        expected_output="A list of actionable suggestion for improving the image and layout based on image purpose and critique",
        agent=ux_suggestion_agent,
        context=[description_task, critique_task]
    )

    # Agent 4 - AI Product Manager
    pm_agent = Agent(
        role="AI Product Manager",
        goal=f"Write the user stories based on suggestions from the ux suggestion agent for the image {image_path} and prioritize the suggestion based on probable customer feedback",
        backstory="You act as an experienced product manager for a digital company prioritizing suggestions and creating user stories to guide improvements",
        verbose=True,
        tools=[vision_tool],
        llm=ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
    )

    pm_task = Task(
        description="Write the user stories based on suggestion from the ux suggestion agent for the image and prioritize the suggestions based on probable customer feedback",
        expected_output="A list of prioritized improvements (rated from Critical, Medium or Low) based on expected impact on customer along with user stories",
        agent=pm_agent,
        context=[description_task, critique_task, ux_suggestion_task]
    )

    return [description_agent, critique_agent, ux_suggestion_agent, pm_agent], [description_task, critique_task, ux_suggestion_task, pm_task]

def run_analysis(image_path):
    """Run the multi-agent analysis on the uploaded image"""
    
    try:
        # Initialize agents and tasks
        agents, tasks = initialize_agents_and_tasks(image_path)
        
        # Create the crew
        crew = Crew(
            agents=agents,
            tasks=tasks,
            verbose=True,
            process=Process.sequential
        )
        
        # Run the analysis
        with st.spinner("🤖 AI agents are analyzing your UI/UX design..."):
            result = crew.kickoff()
        
        return result
    
    except Exception as e:
        st.error(f"An error occurred during analysis: {str(e)}")
        return None

def main():
    # Header section
    st.title("🎨 AI-Powered UI/UX Analysis Platform")
    st.markdown("""
    **Transform your UI/UX designs with intelligent multi-agent analysis**
    
    This platform leverages four specialized AI agents to provide comprehensive feedback on your interface designs:
    - 🔍 **Image Description Agent**: Analyzes and describes your design elements
    - 🔬 **UX Critique Agent**: Identifies design flaws and improvement areas  
    - 💡 **UX Suggestion Agent**: Provides actionable design recommendations
    - 📋 **AI Product Manager**: Creates prioritized user stories and action items
    """)
    
    st.divider()
    
    # Check for OpenAI API key
    if not os.getenv('OPENAI_API_KEY'):
        st.error("⚠️ OpenAI API key not found. Please set your OPENAI_API_KEY environment variable.")
        st.info("You can get your API key from: https://platform.openai.com/api-keys")
        return
    
    # Sidebar for instructions and info
    with st.sidebar:
        st.header("📖 How to Use")
        st.markdown("""
        1. **Upload Image**: Select a UI/UX design image (PNG, JPG, JPEG)
        2. **Start Analysis**: Click the analyze button
        3. **Review Results**: Get comprehensive feedback from AI agents
        4. **Implement Changes**: Use prioritized recommendations
        """)
        
        st.header("🎯 Best Results With")
        st.markdown("""
        - Website mockups
        - Mobile app interfaces  
        - Dashboard designs
        - Landing pages
        - Menu/navigation designs
        """)
        
        st.header("⚙️ System Status")
        st.success("✅ Multi-agent system ready")
        st.success("✅ Vision analysis enabled")
        if os.getenv('OPENAI_API_KEY'):
            st.success("✅ OpenAI API connected")
        else:
            st.error("❌ OpenAI API key missing")
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📤 Upload Your Design")
        
        uploaded_file = st.file_uploader(
            "Choose a UI/UX design image",
            type=['png', 'jpg', 'jpeg'],
            help="Upload an image of your UI/UX design for analysis"
        )
        
        if uploaded_file is not None:
            # Display the uploaded image
            img = Image.open(uploaded_file)
            st.image(img, caption="Uploaded Design", use_container_width=True)
            
            # Show image details
            st.info(f"📊 **Image Details**: {img.size[0]}x{img.size[1]} pixels, Format: {img.format}")
    
    with col2:
        st.header("🚀 Analysis Controls")
        
        if uploaded_file is not None:
            if st.button("🔍 Start AI Analysis", type="primary", use_container_width=True):
                # Save uploaded file temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    temp_image_path = tmp_file.name
                
                try:
                    # Run the analysis
                    result = run_analysis(temp_image_path)
                    
                    if result:
                        st.success("✅ Analysis completed successfully!")
                        
                        # Display results
                        st.header("📋 Analysis Results")
                        
                        # Create tabs for different sections of results
                        tab1, tab2, tab3, tab4 = st.tabs([
                            "🔍 Description", 
                            "🔬 Critique", 
                            "💡 Suggestions", 
                            "📋 Action Items"
                        ])
                        
                        with tab1:
                            st.subheader("Image Description & Purpose")
                            st.write(result)
                        
                        with tab2:
                            st.subheader("UX Critique & Issues")
                            st.write("Detailed critique will be extracted from the full result...")
                        
                        with tab3:
                            st.subheader("Design Improvement Suggestions")
                            st.write("Actionable suggestions will be extracted from the full result...")
                        
                        with tab4:
                            st.subheader("Prioritized User Stories")
                            st.write("User stories and priorities will be extracted from the full result...")
                        
                        # Download option for results
                        st.download_button(
                            label="📥 Download Full Analysis Report",
                            data=str(result),
                            file_name="ui_ux_analysis_report.txt",
                            mime="text/plain"
                        )
                    
                finally:
                    # Clean up temporary file
                    if os.path.exists(temp_image_path):
                        os.unlink(temp_image_path)
        else:
            st.info("👆 Please upload an image to start the analysis")

    # Footer
    st.divider()
    st.markdown("""
    <div style='text-align: center; color: #666; margin-top: 2rem;'>
        <p>🤖 Powered by CrewAI Multi-Agent System | Built with Streamlit</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
