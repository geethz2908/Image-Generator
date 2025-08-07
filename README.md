
# 📚 EduSketch: Educational Illustration Generator using Vertex AI

**EduSketch** is a Flask-based web app that enables educators and students to generate AI-powered educational illustrations by uploading chapter PDFs and entering a topic and grade level. It leverages **Google Vertex AI’s Imagen 3.0** model to produce age-appropriate, context-aware images.

---

## 🌟 Features

* 📄 Upload chapter PDFs for context
* 📝 Enter a topic and select the target grade (Grades 1–12)
* 🎨 AI-generated educational illustrations tailored to the topic
* 🧠 Uses age-appropriate prompt engineering for child-friendly visuals
* 💾 Locally saves generated images for download or sharing

---

## 🛠️ Tech Stack

| Component         | Technology                          |
| ----------------- | ----------------------------------- |
| **Backend**       | Python, Flask                       |
| **AI Model**      | Google Cloud Vertex AI – Imagen 3.0 |
| **PDF Parsing**   | PyMuPDF (`fitz`)                    |
| **Image Utility** | PIL (Pillow)                        |
| **Frontend**      | HTML                                |
| **Environment**   | `python-dotenv` for env management  |

---

## Notes & Limitations

* Some prompts may be filtered or blocked by Vertex AI for safety.
* Error handling is basic—errors are printed to the terminal.
* No login or user history is stored—this is a simple demo app.
