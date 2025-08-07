import os
import fitz  # PyMuPDF
from dotenv import load_dotenv
from flask import Flask, request, render_template
import google.generativeai as genai
import uuid

# --- Load API Key from .env ---
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# --- Config ---
UPLOAD_FOLDER = 'uploads'
STATIC_FOLDER = 'static/output'

# --- Setup ---
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(STATIC_FOLDER, exist_ok=True)

# --- Utility: Extract text from PDF ---
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text[:3000]

# --- Prompt Template ---
def build_prompt(topic, chapter_text, grade):
    return f"""
You are an AI educational assistant.

You are given:
1. A topic: "{topic}"
2. Chapter content extracted from a textbook PDF: "{chapter_text}"
3. The grade level of the textbook: "{grade}"

Your task:
- Generate a high-quality, realistic, and grade-appropriate educational image based on the given topic.
- Ensure the image content is derived from the chapter and suitable for the specified grade level.
- The image should be informative, visually engaging, and contextually relevant.
- Keep complexity aligned with the grade. For lower grades, keep it simple and colorful. For higher grades, add scientific/technical accuracy.
"""

# --- Routes ---
@app.route('/', methods=['GET', 'POST'])
def index():
    image_url = None

    if request.method == 'POST':
        pdf_file = request.files['pdf']
        topic = request.form['topic']
        grade = request.form['grade']

        # Save PDF
        filename = os.path.join(app.config['UPLOAD_FOLDER'], pdf_file.filename)
        pdf_file.save(filename)

        # Extract text and build prompt
        chapter_text = extract_text_from_pdf(filename)
        prompt = build_prompt(topic, chapter_text, grade)

        # Use Gemini model for image generation
        model = genai.GenerativeModel("gemini-2.0-flash-preview-image-generation")
        response = model.generate_image(prompt=prompt)
        image_bytes = response.image

        # Save image
        image_filename = f"{uuid.uuid4().hex}.png"
        image_path = os.path.join(STATIC_FOLDER, image_filename)
        with open(image_path, 'wb') as f:
            f.write(image_bytes)

        image_url = f"/static/output/{image_filename}"

    return render_template('index.html', image_url=image_url)

# --- Run ---
if __name__ == '__main__':
    app.run(debug=True)



# from google import genai
# from google.genai import types
# from PIL import Image
# from io import BytesIO

# client = genai.Client(api_key="YOUR_API_KEY")

# # Educational prompt template
# prompt = f"""
# You are an AI educational assistant.

# You are given:
# 1. A topic: "{topic}"
# 2. Chapter content extracted from a textbook PDF: "{chapter_text}"
# 3. The grade level of the textbook: "{grade}"

# Your task:
# - Generate a high-quality, realistic, and grade-appropriate educational image for the topic.
# - Ensure content is derived from the chapter and suitable for the grade level.
# - Make it visually engaging and informative.
# - Keep complexity aligned with the grade (simple & colorful for lower, accurate & technical for higher grades).
# """

# response = client.models.generate_image(
#     model="imagen-3.0-generate-002",
#     prompt=prompt,
#     config=types.GenerateImageConfig(
#         number_of_images=1,
#         output_mime_type="image/png"
#     )
# )

# # Access and save image
# img_bytes = response.generated_images[0].image.image_bytes
# image = Image.open(BytesIO(img_bytes))
# image.save("educational_visual.png")
# image.show()
