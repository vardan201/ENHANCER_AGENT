# 🚀 Startup Idea Enhancer - LangGraph Workflow

AI-powered system that takes raw startup ideas and transforms them into comprehensive, validated business plans using a multi-agent LangGraph workflow.

## 🏗️ Architecture

```
START
  ↓
Normalization Agent (Clean & standardize input)
  ↓
Structuring Agent (Extract key components)
  ↓
Validation Agent (Quality check)
   ├── PASS → Enhancement Agent → END
   └── FAIL → Structuring Agent (retry up to 5 times)
```

## ✨ Features

- **Multi-Agent Workflow**: 4 specialized agents working in sequence
- **Automatic Retry Logic**: Up to 5 retry attempts with validation feedback
- **Structured Output**: Pydantic-validated JSON schema
- **Comprehensive Analysis**: 25+ data points including market size, competitors, risks
- **FastAPI Integration**: REST API for easy frontend integration
- **Groq API**: Using `deepseek/deepseek-r1-distill-llama-70b` model

## 📦 Installation

### 1. Clone and Setup

```bash
# Create project directory
mkdir startup-enhancer
cd startup-enhancer

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your Groq API key
# Get your key from: https://console.groq.com/keys
```

## 🎯 Usage

### Option 1: Direct Python Script

```python
from startup_enhancer import StartupIdeaEnhancer
import os

# Initialize
enhancer = StartupIdeaEnhancer(
    groq_api_key=os.getenv("GROQ_API_KEY"),
    max_retries=5
)

# Process idea
raw_idea = """
students struggle to find good study notes
i want to build a platform where they can share notes
and get rewards. AI can help summarize PDFs
"""

result = enhancer.process_idea(raw_idea)

# Access results
if result['final_output']:
    print(result['final_output'])
else:
    print(f"Error: {result['error']}")
```

### Option 2: FastAPI Server

```bash
# Start server
python api_server.py

# Server runs on http://localhost:8000
```

**API Request:**

```bash
curl -X POST http://localhost:8000/enhance \
  -H "Content-Type: application/json" \
  -d '{
    "raw_idea": "students struggle finding notes, want to build sharing platform with AI summaries and rewards",
    "max_retries": 5
  }'
```

**API Response:**

```json
{
  "success": true,
  "data": {
    "problem_statement": "...",
    "target_users": "...",
    "feasibility_score": 0.85,
    "market_size": {
      "tam": "$50B",
      "sam": "$5B",
      "som": "$50M"
    },
    ...
  },
  "retry_count": 0
}
```

## 📊 Output Schema

The enhancement agent produces a comprehensive JSON with:

- **Core Components**: Problem, solution, users, value prop
- **Scores**: Feasibility, desirability, viability (0-1)
- **Market Analysis**: TAM/SAM/SOM, competitors, market type
- **Risk Assessment**: Assumptions, complexity, primary risks
- **Execution Plan**: MVP scope, acquisition channels, next actions
- **Business Model**: Revenue streams, key metrics, unfair advantage

## 🔧 Configuration

### Environment Variables

```bash
GROQ_API_KEY=your_key_here       # Required
MAX_RETRIES=5                     # Optional (default: 5)
MODEL_NAME=deepseek/deepseek-r1-distill-llama-70b  # Optional
```

### Retry Logic

The workflow automatically retries the structuring → validation loop if validation fails:
- **Max retries**: 5 (configurable)
- **Feedback loop**: Validation feedback guides restructuring
- **Early exit**: Stops if validation passes before max retries

## 🎨 Agent Details

### 1. Normalization Agent
- Fixes grammar and spelling
- Removes redundancy
- Standardizes format
- Output: Clean 3-5 sentence description

### 2. Structuring Agent
- Extracts problem, solution, users
- Identifies value proposition
- Lists key assumptions
- Output: JSON with 5 core components

### 3. Validation Agent
- Checks problem clarity
- Validates user specificity
- Assesses solution concreteness
- Output: PASS/FAIL with feedback

### 4. Enhancement Agent
- Deep market analysis
- Competitive landscape
- Risk assessment
- Execution roadmap
- Output: 25+ field structured JSON

## 📝 Example Output

```json
{
  "problem_statement": "Students spend excessive time searching for quality study materials across fragmented platforms",
  "target_users": "College students aged 18-24, primarily STEM majors",
  "solution": "Centralized platform for peer-to-peer note sharing with AI-powered summarization",
  "feasibility_score": 0.82,
  "market_type": "B2C",
  "differentiation_strength": "MEDIUM",
  "competitors": [
    {
      "name": "Studocu",
      "strengths": "Large existing user base",
      "weaknesses": "Poor content quality control",
      "gaps": "No AI summarization features"
    }
  ],
  "next_best_action": "USER_INTERVIEWS",
  "mvp_scope": {
    "core_features": ["Note upload", "Basic search", "PDF viewer"],
    "build_complexity": "1_MONTH"
  }
}
```

## 🚨 Error Handling

The system handles:
- ✅ Invalid JSON from structuring
- ✅ Validation failures (with retries)
- ✅ API errors (with clear messages)
- ✅ Schema validation errors
- ✅ Max retry exhaustion

## 🔐 Security Notes

- Never commit `.env` file
- Use environment variables for API keys
- In production, restrict CORS origins
- Add rate limiting for API endpoints

## 📚 Dependencies

- `langgraph` - Workflow orchestration
- `langchain-groq` - Groq LLM integration
- `pydantic` - Data validation
- `fastapi` - API server (optional)
- `python-dotenv` - Environment management

## 🤝 Contributing

To extend the system:

1. **Add new agents**: Create new node functions in `WorkflowState`
2. **Modify schema**: Update `EnhancedStartupIdea` Pydantic model
3. **Change retry logic**: Adjust `should_retry` decision function
4. **Add validation rules**: Extend `validation_agent` criteria

## 📄 License

MIT License - feel free to use in your startup!

## 🆘 Troubleshooting

### "GROQ_API_KEY not found"
→ Ensure `.env` file exists with valid API key

### "Max retries reached"
→ Your idea might be too vague. Provide more specific details

### JSON parsing errors
→ Check model output format, may need prompt adjustments

### Model not found
→ Verify model name: `openai/gpt-oss-120b`

## 📧 Support

For issues or questions, check:
- Groq API docs: https://console.groq.com/docs
- LangGraph docs: https://python.langchain.com/docs/langgraph

---

Built with ❤️ for student entrepreneurs
