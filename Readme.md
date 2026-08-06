# AI Voice Interview Agent

> An AI-powered real-time voice interview assistant built with **LiveKit Agents**, **OpenAI Realtime API**, and **Supabase**.

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![LiveKit](https://img.shields.io/badge/LiveKit-Agents-green)
![OpenAI](https://img.shields.io/badge/OpenAI-Realtime_API-black)
![Supabase](https://img.shields.io/badge/Supabase-Database-3ECF8E)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## Overview

This project provides a conversational AI interviewer capable of conducting real-time voice interviews, collecting structured candidate information, and generating automated interview assessments.

Designed for recruitment workflows, it combines low-latency voice interaction with AI-powered evaluation to streamline candidate screening.

---

## Features

- Real-time voice conversations
- AI-powered interview assistant
- Structured candidate data extraction
- Automated interview evaluation
- Supabase database integration
- Configurable interview prompts
- Low-latency speech pipeline using LiveKit

---

## Tech Stack

| Technology | Purpose |
|------------|---------|
| Python | Backend |
| LiveKit Agents | Real-time voice communication |
| OpenAI Realtime API | Speech & conversation |
| GPT-4o | Language model |
| Supabase | Database |
| Silero VAD | Voice activity detection |

---

## Project Structure

```text
.
├── agent.py
├── database.py
├── prompt.txt
├── .env.local
├── requirements.txt
└── README.md
```

---

## Getting Started

### Clone the repository

```bash
git clone https://github.com/<your-username>/<repository-name>.git
cd <repository-name>
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Configure environment variables

Create a `.env.local` file.

```env
OPENAI_API_KEY=
LIVEKIT_URL=
LIVEKIT_API_KEY=
LIVEKIT_API_SECRET=

SUPABASE_URL=
SUPABASE_KEY=
```

### Run the application

```bash
python agent.py
```

---

## Configuration

The interview workflow and assistant behavior are defined in `prompt.txt`, making it easy to customize questions, conversation flow, and evaluation logic without modifying the application code.

---

## Roadmap

- Resume parsing
- ATS integration
- Interview summaries
- Candidate ranking
- Multi-language support
- Recruiter dashboard

---
