# 🎓 Academix.io

**Your AI-Powered Academic Automation Platform**

Academix is a comprehensive full-stack web application that leverages AI agents to automate academic tasks, including universal lab report generation, video transcription, and intelligent academic assistance. Built with Next.js 16, FastAPI, and powered by CrewAI multi-agent systems.

![Version](https://img.shields.io/badge/version-2.0.0-blue)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Next.js](https://img.shields.io/badge/next.js-16.2.3-black)
![License](https://img.shields.io/badge/license-MIT-green)

---

## ✨ Features

### 🤖 AI Academic Assistant
- Interactive chat interface with AI-powered academic support
- Context-aware responses for academic queries
- Real-time conversation with intelligent agents
- Memory persistence across sessions

### 📝 Universal Lab Report Generator (AI-Powered)
- **Universal Support**: Works with ANY lab manual type
  - Programming (Python, C, Java, JavaScript, etc.)
  - Numerical Methods (Octave, MATLAB)
  - Operating Systems, Networking, DSA, Web Development
  - Database, Machine Learning, Theory-based labs
- **Automatic Lab Type Detection**: Adapts theory length based on content
  - Coding labs: Minimal theory (2-3 lines), 80% code focus
  - Numerical labs: Balanced (40% theory, 60% code)
  - Theory labs: Detailed explanations (90% theory)
- **Exercise-First Approach**: Prioritizes solving exercises over theory
- **Anti-Hallucination System**: Preserves exact method names from input
- **Smart Tool Selection**: Automatically chooses appropriate execution tools
- Upload lab manuals or assignments (PDF, DOCX)
- Complete structured academic report generation
- Export reports in multiple formats (PDF, DOCX, Markdown)
- Optional Notion integration for workspace export
- Grammar checking and LaTeX rendering support

### 🎥 Transcription Hub (Fast Pipeline)
- YouTube video transcription with bot bypass system
- Audio/video file upload support
- Automatic study notes generation
- Fast 4-thread processing pipeline with FFmpeg
- Downloadable transcripts

### 🧠 Advanced AI Tools
- **Code Compilation**: Execute and test code snippets (Python, C, Java)
- **Octave/MATLAB Execution**: Run numerical computation code
- **Data Visualization**: Generate charts and graphs
- **Image Creation**: AI-powered image generation
- **Wolfram Integration**: Mathematical computations
- **Web Search**: Real-time information retrieval (Serper)
- **Citation Finder**: Academic reference management
- **Plagiarism Checker**: Content originality verification
- **Notion Integration**: Optional workspace export

---

## 🏗️ Architecture

### System Overview

![Academix Architecture](docs/academix_architecture.png)

For detailed architecture documentation, see [docs/architecture.md](docs/architecture.md)

### High-Level Components

```
academix/
├── frontend/          # Next.js 16 + TypeScript + Tailwind CSS
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── pages/        # Next.js pages
│   │   ├── store/        # Zustand state management
│   │   └── utils/        # API utilities
│   └── public/           # Static assets
│
├── backend/           # FastAPI + Python
│   ├── app/
│   │   ├── llm.py           # LLM integration (OpenAI/Groq)
│   │   └── report_exporter.py  # Report export logic
│   └── main.py              # FastAPI application
│
└── src/cua/          # CrewAI Multi-Agent System
    ├── config/
    │   ├── agents.yaml      # Agent definitions
    │   └── tasks.yaml       # Task configurations
    ├── tools/               # Custom AI tools (15+ tools)
    │   ├── youtube_video_downloader_tool.py  # YouTube bot bypass
    │   ├── lab_report_generator_tool.py      # Universal lab reports
    │   ├── code_compiler_tool.py             # Code execution
    │   ├── octave_online_tool.py             # MATLAB/Octave
    │   └── ...                               # 10+ more tools
    ├── crew.py              # Crew orchestration
    └── main.py              # Entry point
```

### Key Features

- **Multi-Agent AI System**: CrewAI orchestrates specialized agents for different tasks
- **Universal Lab Report Generation**: Supports all lab manual types with adaptive formatting
- **YouTube Bot Bypass**: User agent rotation, retry logic, and cookie support
- **Parallel Processing**: 4-thread transcription pipeline with FFmpeg
- **Client-Side Security**: API keys stored in browser localStorage, never on server
- **Scalable Architecture**: Stateless backend ready for horizontal scaling
- **Anti-Hallucination**: Method name preservation and validation system

---

## 🚀 Quick Start

### Prerequisites

- **Python**: 3.10 - 3.13
- **Node.js**: 18.x or higher
- **npm** or **yarn**
- **UV** (Python package manager)
- **FFmpeg** (for video transcription)

### Installation

#### 1. Clone the Repository

```bash
git clone https://github.com/M-SAAD-BIN-MAZHAR/Academix.io.git
cd Academix.io
```

#### 2. Backend Setup

```bash
# Install UV (if not already installed)
pip install uv

# Install Python dependencies
crewai install

# Or manually with UV
uv pip install -r requirements.txt
```

#### 3. Frontend Setup

```bash
cd frontend
npm install
# or
yarn install
```

#### 4. Environment Configuration

Create a `.env` file in the root directory:

```env
# Required: At least one LLM API key
OPENAI_API_KEY=your_openai_api_key_here
# OR
GROQ_API_KEY=your_groq_api_key_here

# Optional: Recommended for web search
SERPER_API_KEY=your_serper_api_key_here

# Optional: Additional integrations
WOLFRAM_APP_ID=your_wolfram_app_id
NOTION_API_KEY=your_notion_api_key
NOTION_DATABASE_ID=your_notion_database_id
```

Create `frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Create `frontend/.env.production`:

```env
NEXT_PUBLIC_API_URL=https://your-backend-url.railway.app
```

---

## 🎯 Running the Application

### Development Mode

#### Start Backend (FastAPI)

```bash
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: `http://localhost:8000`

#### Start Frontend (Next.js)

```bash
cd frontend
npm run dev
# or
yarn dev
```

Frontend will be available at: `http://localhost:3000`

### Production Mode

#### Build Frontend

```bash
cd frontend
npm run build
npm start
```

#### Run Backend

```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## 🛠️ Technology Stack

### Frontend
- **Framework**: Next.js 16.2.3
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: Lucide React Icons
- **Animations**: Framer Motion
- **Particles**: @tsparticles/react
- **State Management**: Zustand
- **HTTP Client**: Axios
- **Analytics**: Vercel Analytics

### Backend
- **Framework**: FastAPI
- **Language**: Python 3.10+
- **AI Framework**: CrewAI
- **LLM**: OpenAI GPT-4o-mini / Groq Llama3-70B
- **Package Manager**: UV

### AI Tools & Integrations
- OpenAI GPT-4o-mini
- Groq LLM (Llama3-70B)
- Serper (Web Search)
- Wolfram Alpha
- Notion API
- YouTube Transcript API
- Whisper (Audio Transcription)
- FFmpeg (Video Processing)
- Octave Online API

---

## 📁 Project Structure

### Frontend Pages

- `/` - Dashboard with AI chat assistant
- `/report` - Universal Lab Report Generator
- `/transcribe` - Transcription Hub for video/audio
- `/history` - Memory and conversation history
- `/settings` - API key configuration and setup guides

### Backend Endpoints

- `POST /chat` - AI chat conversation
- `POST /report/generate` - Generate universal lab report
- `POST /transcribe` - Transcribe video/audio
- `GET /history` - Retrieve conversation history
- `POST /export` - Export reports (PDF/DOCX/MD)

### AI Agents

Defined in `src/cua/config/agents.yaml`:
- **Elite Academic Document Architect**: Lab report generation specialist
- **Research Agent**: Information gathering and analysis
- **Writing Agent**: Content creation and structuring
- **Review Agent**: Quality assurance and editing
- **Citation Agent**: Reference management

---

## 🎨 Features in Detail

### Universal Lab Report Generator
1. Upload lab manual (PDF, DOCX) or paste text
2. **Automatic Lab Type Detection**:
   - TYPE_A (Coding): Programming, OS, Networking, DSA, Web Dev, DB
   - TYPE_B (Numerical): Numerical Methods, MATLAB, Octave
   - TYPE_C (Theory): Pure theory-based labs
3. **Adaptive Theory Length**:
   - Coding: 2-3 lines theory, 80% code
   - Numerical: 40% theory, 60% code
   - Theory: 90% detailed theory
4. **Exercise-First Approach**: If exercises exist, 90% solving, 10% theory
5. **Anti-Hallucination System**: Preserves exact method names
6. **Smart Tool Selection**: Auto-selects CodeCompiler or OctaveOnline
7. Export in PDF, DOCX, or Markdown
8. Optional Notion integration

### Transcription Hub
1. Paste YouTube URL or upload audio/video
2. **YouTube Bot Bypass**: User agent rotation, retry logic
3. Automatic transcription using Whisper
4. AI-generated study notes
5. Fast 4-thread processing pipeline
6. Downloadable transcript

### AI Chat Assistant
- Context-aware academic support
- Multi-turn conversations
- Memory persistence
- Real-time responses
- User/environment API key support

---

## 🔧 Configuration

### LLM Priority

The system uses the following priority for LLM selection:
1. User-supplied OpenAI key (from Settings page)
2. User-supplied Groq key (from Settings page)
3. Environment OpenAI key (from .env)
4. Environment Groq key (from .env)

### Agent Configuration

Edit `src/cua/config/agents.yaml` to customize AI agents:

```yaml
Elite_Academic_Document_Architect:
  role: "Elite Academic Document Architect & Universal Lab Report Specialist"
  goal: "Generate comprehensive, accurate lab reports for ANY subject"
  backstory: "World-class academic writer with expertise across all domains"
  tools:
    - lab_report_generator_tool
    - code_compiler_tool
    - octave_online_tool
```

### Task Configuration

Edit `src/cua/config/tasks.yaml` to define workflows with anti-hallucination rules.

---

## 🧪 Development

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Code Quality

```bash
# Python linting
flake8 src/

# TypeScript linting
cd frontend
npm run lint
```

---

## 📦 Deployment

### Frontend (Vercel)

1. Connect your GitHub repository to Vercel
2. Set environment variables in Vercel dashboard:
   - `NEXT_PUBLIC_API_URL=https://your-backend-url.railway.app`
3. Deploy automatically on push to main

### Backend (Railway)

1. Connect your GitHub repository to Railway
2. Set environment variables in Railway dashboard:
   - `OPENAI_API_KEY` or `GROQ_API_KEY`
   - `SERPER_API_KEY` (optional)
   - Other optional API keys
3. Railway will auto-detect FastAPI and deploy
4. Use `backend/Procfile` for custom start command

---

## 🔑 API Keys Setup

### Required (at least one)
- **OpenAI**: https://platform.openai.com/api-keys
- **Groq**: https://console.groq.com/keys

### Recommended
- **Serper** (Web Search): https://serper.dev/api-key

### Optional
- **Wolfram Alpha**: https://developer.wolframalpha.com/
- **Notion**: https://www.notion.so/my-integrations
- **Adobe PDF Services**: https://developer.adobe.com/

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License.

---

## 🙏 Acknowledgments

- [CrewAI](https://crewai.com) - Multi-agent AI framework
- [OpenAI](https://openai.com) - GPT models
- [Groq](https://groq.com) - Fast LLM inference
- [Next.js](https://nextjs.org) - React framework
- [FastAPI](https://fastapi.tiangolo.com) - Python web framework
- [Tailwind CSS](https://tailwindcss.com) - Utility-first CSS
- [Vercel](https://vercel.com) - Frontend hosting
- [Railway](https://railway.app) - Backend hosting

---

## 📞 Support

For questions, issues, or feature requests:

- Open an issue on GitHub: https://github.com/M-SAAD-BIN-MAZHAR/Academix.io/issues
- Contact: Muhammad Saad bin Mazhar

---

## 🌟 Key Improvements in v2.0.0

- ✅ Universal lab report generation (all subjects)
- ✅ Automatic lab type detection and adaptive formatting
- ✅ Exercise-first approach for coding labs
- ✅ Anti-hallucination system with method name preservation
- ✅ No citations/web search for coding exercises
- ✅ Optional Notion integration (no errors if missing)
- ✅ YouTube bot bypass with user agent rotation
- ✅ Vercel Analytics integration
- ✅ Next.js 16 upgrade
- ✅ Client-side API key storage for security

---

**Built with ❤️ by Muhammad Saad bin Mazhar using AI and modern web technologies**
