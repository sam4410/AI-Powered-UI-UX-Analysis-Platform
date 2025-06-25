# 🎨 AI-Powered UI/UX Analysis Platform

A sophisticated multi-agent system built with CrewAI that provides comprehensive UI/UX design analysis and automated wireframe generation. This platform leverages **5 specialized AI agents** working in **two distinct phases** to deliver actionable insights and improved design mockups.

## 🔍 Overview

Transform your UI/UX designs with intelligent analysis that combines human design expertise with AI-powered automation. The platform analyzes uploaded design images and provides detailed feedback, suggestions, and generates improved wireframes automatically.

## 🏗️ Architecture

### Two-Phase Multi-Agent System

#### 📊 **Phase 1: Analysis & Strategy** (4 Agents)
1. **🖼️ Visual Design Interpreter** - Analyzes layout hierarchy, component structure, and visual elements
2. **🔬 UX Critique Agent** - Identifies usability issues, accessibility gaps, and design inconsistencies
3. **💡 UX Suggestion Agent** - Provides evidence-based design improvements and best practices
4. **📋 AI Product Manager** - Creates prioritized user stories with acceptance criteria and business impact

#### 🎨 **Phase 2: Visual Implementation** (1 Agent)
5. **🖼️ Mockup Generator Agent** - Creates responsive HTML wireframes using Tailwind CSS, incorporating Phase 1 insights

### Agent Workflow
```
Image Upload → Phase 1 (Sequential Analysis) → Phase 2 (Mockup Generation) → Results Dashboard
```

## ✨ Key Features

- **Multi-Agent Collaboration**: 5 specialized AI agents working sequentially
- **Comprehensive Analysis**: Deep dive into visual design, UX issues, and improvement opportunities
- **Automated Wireframing**: AI-generated HTML/CSS mockups with Tailwind CSS
- **Business Integration**: User stories with acceptance criteria and prioritization
- **Interactive Dashboard**: Streamlit-powered web interface with real-time analysis
- **Performance Monitoring**: Built-in timing and latency tracking
- **Export Capabilities**: Download analysis reports and wireframe code

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- OpenAI API Key
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ai-uiux-analysis-platform
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   # Create .env file
   OPENAI_API_KEY=your_openai_api_key_here
   ```

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

5. **Access the platform**
   Open your browser to `http://localhost:8501`

## 📦 Dependencies

### Core Libraries
```
streamlit>=1.28.0
crewai>=0.22.0
crewai-tools>=0.1.0
langchain-openai>=0.1.0
python-dotenv>=1.0.0
Pillow>=10.0.0
nest-asyncio>=1.5.0
```

### AI Models
- **Primary**: GPT-4o (Description Agent, Mockup Generator)
- **Secondary**: GPT-4o-mini (Critique, Suggestion, Product Manager agents)

## 🎯 Usage Guide

### 1. Upload Design Image
- Supported formats: PNG, JPG, JPEG
- Recommended: Website mockups, mobile interfaces, dashboards
- Images are automatically resized for optimal performance

### 2. Start Analysis
- Click "Start 5-Agent AI Analysis"
- Monitor progress through real-time status updates
- Phase 1 completes before Phase 2 begins

### 3. Review Results
Navigate through 5 result tabs:
- **Description**: Detailed component and layout analysis
- **Critique**: Identified UX issues and problems
- **Suggestions**: Actionable improvement recommendations
- **Action Items**: Prioritized user stories and acceptance criteria
- **AI Wireframe**: Interactive HTML mockup with improvements

### 4. Export and Implement
- Download complete analysis report
- Copy wireframe HTML/CSS code
- Use prioritized user stories for development planning

## 📁 Project Structure

```
ai-uiux-analysis-platform/
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── .env                           # Environment variables (create this)
├── utils/
│   ├── html_utils.py              # HTML extraction utilities
│   ├── mockup_renderer.py         # Wireframe rendering functions
│   ├── diagnostics.py             # Performance monitoring
│   ├── custom_image_interpreter.py # Custom vision tool
│   └── layout_injection.py        # Layout analysis helpers
├── prompts/
│   └── mockup_prompt_tailwind.txt # Tailwind CSS generation prompts
└── README.md                      # This file
```

## 🔧 Configuration

### Environment Variables
```bash
# Required
OPENAI_API_KEY=your_api_key_here

# Optional
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langchain_key
```

### Agent Configuration
Each agent can be customized with:
- **Temperature**: Controls creativity (0.1-0.4 range used)
- **Model**: GPT-4o for complex tasks, GPT-4o-mini for focused analysis
- **Tools**: Vision analysis, custom image interpretation
- **Context**: Sequential task dependencies

## 🎨 Best Results With

### Recommended Design Types
- **Website mockups** & landing pages
- **Mobile app interfaces** & screen flows
- **Dashboard designs** & admin panels
- **E-commerce layouts** & product pages
- **Navigation systems** & user flows
- **Form designs** & checkout processes

### Image Guidelines
- **Resolution**: 1000px+ width recommended
- **Quality**: Clear, high-contrast designs
- **Format**: PNG preferred for crisp UI elements
- **Content**: Complete interface views work best

## 🚀 Advanced Features

### Performance Monitoring
- Real-time agent execution timing
- Phase-by-phase latency tracking
- Bottleneck identification
- Resource usage optimization

### Custom Tools Integration
- **VisionTool**: Advanced image analysis
- **CustomImageInterpreter**: Specialized UI understanding
- **Layout extraction**: Component tree generation
- **HTML utilities**: Clean code extraction

### Responsive Wireframes
- **Tailwind CSS**: Utility-first styling
- **Mobile-first**: Responsive design principles
- **Accessibility**: WCAG compliance considerations
- **Modern components**: Cards, buttons, forms, navigation

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Install development dependencies
4. Follow the existing code structure
5. Test with various design types
6. Submit a pull request

### Code Style
- Follow PEP 8 for Python code
- Use descriptive variable names
- Add docstrings for functions
- Include error handling
- Test agent interactions

## 📊 Performance Benchmarks

### Typical Analysis Times
- **Phase 1** (4 agents): 30-60 seconds
- **Phase 2** (1 agent): 15-30 seconds
- **Total pipeline**: 45-90 seconds
- **Image processing**: 2-5 seconds

### Resource Usage
- **Memory**: 2-4GB during analysis
- **API calls**: 5-8 OpenAI requests per analysis
- **Storage**: Minimal (temporary files only)

## 🔒 Security & Privacy

- **API Keys**: Stored in environment variables only
- **Images**: Processed temporarily, automatically deleted
- **Data**: No persistent storage of user content
- **Privacy**: Images sent to OpenAI for analysis (per their terms)

## 🐛 Troubleshooting

### Common Issues

**API Key Errors**
```bash
# Check environment variable
echo $OPENAI_API_KEY

# Verify .env file exists
cat .env
```

**Image Processing Failures**
- Ensure image format is supported (PNG, JPG, JPEG)
- Check image size (very large images may timeout)
- Verify image is not corrupted

**Agent Execution Timeouts**
- Reduce image resolution
- Check internet connection
- Verify OpenAI API quota

**Mockup Generation Issues**
- Ensure Phase 1 completed successfully
- Check for HTML extraction errors
- Verify Tailwind CSS prompt file exists

## 📈 Roadmap

### Upcoming Features
- [ ] Batch processing for multiple designs
- [ ] Custom agent fine-tuning
- [ ] Integration with design tools (Figma, Sketch)
- [ ] Real-time collaboration features
- [ ] Enhanced accessibility analysis
- [ ] Mobile app for on-the-go analysis

### Version History
- **v1.0.0**: Initial release with 5-agent system
- **v1.1.0**: Added performance monitoring
- **v1.2.0**: Enhanced wireframe generation
- **v1.3.0**: Improved UI/UX analysis depth

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **CrewAI**: Multi-agent orchestration framework
- **OpenAI**: GPT-4 models for intelligent analysis
- **Streamlit**: Web application framework
- **Tailwind CSS**: Utility-first styling framework
- **LangChain**: AI application development tools

## 📞 Support

For questions, issues, or contributions:
- Create an issue on GitHub
- Check the troubleshooting section
- Review the documentation
- Contact the development team

---

**🤖 Powered by 5-Agent CrewAI Multi-Phase System**  
*Phase 1: Analysis & Strategy (4 Agents) → Phase 2: Wireframe Implementation (1 Agent)*

## Live Demo
[Your Streamlit Cloud URL will go here]" > (https://ai-powered-ui-ux-analysis-platform-jbsnhd8nwnzdj5mg2gq8tc.streamlit.app/)
