# CurAIte: Smart Lesson Planner
### **_Internship Project with AI Agent for IBM AI Internship_**

An intelligent web application designed to empower educators by automating the creation of high-quality, customized micro-lesson plans. This project leverages the power of Large Language Models to reduce administrative workload and support teachers in delivering quality education.
---
## Preview
<img width="1902" height="1079" alt="image" src="https://github.com/user-attachments/assets/d803143d-ed92-4c69-9045-b99748ae40f6" />

---
### Live Demo (Hugging Face): https://huggingface.co/spaces/ishitaakolkar/PlanIT
---

## Overview

The Smart Lesson Planner is a user-friendly tool built with Python and Streamlit that generates 15-minute lesson plans in seconds. It is specifically tailored for the Indian education system, providing dynamic, curriculum-aware inputs that guide the AI to produce relevant and practical content for the classroom.

###  SDG Alignment
This project is fundamentally aligned with the **United Nations' Sustainable Development Goal 4: Quality Education**. By providing a free and accessible tool that saves teachers' time and reduces burnout, it empowers them to focus on high-impact instruction, student engagement, and professional development.

---

## 🚀 Key Features

* **Dynamic Curriculum Selection:** Cascading dropdown menus for Board (CBSE/GSEB), Grade, Subject, and Topic ensure the generated content is highly relevant.
* **AI-Powered Content Generation:** Utilizes the Google Gemini API to generate well-structured and contextually appropriate lesson plans.
* **Interactive Visual Output:** Displays the generated plan in a clean, organized layout with collapsible sections and key metrics.
* **Multi-Format Export:** Allows teachers to instantly download lesson plans as printable **PDF** files or editable **Microsoft Word (DOCX)** documents.
* **Copy-to-Clipboard:** A simple code block for quickly copying the raw lesson plan text.
* **Customizable Theme:** Supports both Light and Dark modes, respecting the user's operating system preference via a settings menu toggle.
* **Aesthetic UI:** Features a polished interface with a custom background for a professional user experience.

---

## 🛠️ Technology Stack

* **Core Language:** **Python 3.10+**
* **Web Framework:** **Streamlit**
* **AI Engine:** **Google Gemini API** (`gemini-1.5-flash-latest`)
* **File Generation:** **FPDF2** (for PDF), **python-docx** (for Word)
* **Configuration:** **python-dotenv**
* **IDE:** **VS Code**
* **Version Control:** **Git & GitHub**
