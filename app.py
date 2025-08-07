import os
import fitz  # PyMuPDF
from dotenv import load_dotenv
from flask import Flask, request, render_template
import uuid
import vertexai
from vertexai.preview.vision_models import ImageGenerationModel
from PIL import Image as PIL_Image
import io

# --- Load environment variables ---
load_dotenv()

# --- Config ---
UPLOAD_FOLDER = 'uploads'
STATIC_FOLDER = 'static/output'

# --- Setup ---
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(STATIC_FOLDER, exist_ok=True)

# --- Initialize Vertex AI ---
# Get project ID and credentials from environment
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT_ID")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
CREDENTIALS_PATH = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

if not PROJECT_ID:
    raise ValueError("GOOGLE_CLOUD_PROJECT_ID must be set in .env file")

if CREDENTIALS_PATH and os.path.exists(CREDENTIALS_PATH):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = CREDENTIALS_PATH
    print(f"Using service account from: {CREDENTIALS_PATH}")
else:
    print("Warning: Service account key file not found, using default credentials")

print(f"Initializing Vertex AI with Project: {PROJECT_ID}, Location: {LOCATION}")

try:
    vertexai.init(project=PROJECT_ID, location=LOCATION)
    generation_model = ImageGenerationModel.from_pretrained("imagen-3.0-generate-001")
    print("✓ Vertex AI initialized successfully")
except Exception as e:
    print(f"❌ Error initializing Vertex AI: {e}")
    raise

# --- Utility: Extract text from PDF ---
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text[:3000]

# --- Prompt Template ---
def build_prompt(topic, chapter_text, grade):
    # Create very simple, safe prompts that won't be filtered
    grade_num = int(grade) if grade.isdigit() else int(grade.replace('Grade ', ''))
    
    # Very simple, concrete prompts that are unlikely to be filtered
    if grade_num <= 3:
        # Use extremely simple, safe prompts for young children
        simple_prompts = {
            'moral': "Cartoon-style flat illustration showing a well-lit classroom with toys, books, charts, and a blackboard with drawings",
    'story': "An educational illustration of a bright classroom desk with books, pencils, and a glowing lamp",
    'reading': "Illustration of an open colorful storybook on a school desk with classroom posters in the background",
    'children': "Cartoon-style school bag with learning material on a desk in a colorful classroom",
    'learn': "Illustration of a blackboard with alphabet letters, books, and stationery in a cartoon classroom",
    'school': "Cartoon drawing of a school building exterior with a garden, books, and sun in the sky"
        }
        
        # Find matching prompt or use default
        for keyword, simple_prompt in simple_prompts.items():
            if keyword in topic.lower():
                return simple_prompt
        
        # Default very simple prompt
        return "A bright cartoon illustration with happy children"
    
    # For older grades, still keep it simple
    return f"An educational illustration about {topic} for students"

# --- Image Generation Function ---
def generate_educational_image(prompt):
    try:
        print(f"Generating image with prompt: {prompt}")
        
        # Use only basic parameters supported by imagen-3.0-generate-001
        response = generation_model.generate_images(
            prompt=prompt,
            number_of_images=1
        )

        print("Full response object:")
        try:
            print(response.__dict__)  # Sometimes helpful
        except:
            print(response)  # Fallback if __dict__ not accessible
        
        print(f"Response type: {type(response)}")
        print(f"Images list length: {len(response.images)}")
        
        if response.images and len(response.images) > 0:
            print("✓ Image generated successfully")
            return response.images[0]
        else:
            print("❌ No images in response - likely filtered by safety mechanisms")
            return None
            
    except Exception as e:
        print(f"Error generating image: {e}")
        import traceback
        traceback.print_exc()
        return None

# --- Helper function to save Vertex AI image ---
def save_vertex_image(vertex_image, filename):
    try:
        # Get PIL image from Vertex AI image object
        pil_image = vertex_image._pil_image
        
        # Convert to RGB if necessary
        if pil_image.mode != "RGB":
            pil_image = pil_image.convert("RGB")
        
        # Save the image
        pil_image.save(filename, "PNG")
        return True
    except Exception as e:
        print(f"Error saving image: {e}")
        return False

# --- Routes ---
@app.route('/', methods=['GET', 'POST'])
def index():
    image_url = None
    error_message = None

    if request.method == 'POST':
        try:
            pdf_file = request.files['pdf']
            topic = request.form['topic']
            grade = request.form['grade']

            print(f"Received request - Topic: {topic}, Grade: {grade}")

            # Save PDF
            filename = os.path.join(app.config['UPLOAD_FOLDER'], pdf_file.filename)
            pdf_file.save(filename)

            # Extract text and build prompt
            chapter_text = extract_text_from_pdf(filename)
            print(f"Extracted text length: {len(chapter_text)}")
            print(f"First 200 chars: {chapter_text[:200]}")
            
            prompt = build_prompt(topic, chapter_text, grade)
            print(f"Built prompt length: {len(prompt)}")

            # Generate image using Vertex AI Imagen
            vertex_image = generate_educational_image(prompt)
            
            if vertex_image:
                # Save image
                image_filename = f"{uuid.uuid4().hex}.png"
                image_path = os.path.join(STATIC_FOLDER, image_filename)
                
                if save_vertex_image(vertex_image, image_path):
                    image_url = f"/static/output/{image_filename}"
                    print(f"✓ Image saved successfully: {image_filename}")
                else:
                    error_message = "Failed to save generated image"
            else:
                error_message = "Failed to generate image. The model may have filtered the content or encountered an issue. Try a different topic or more specific description."
                
        except Exception as e:
            error_message = f"An error occurred: {str(e)}"
            print(f"Exception in main route: {e}")
            import traceback
            traceback.print_exc()

    return render_template('index.html', image_url=image_url, error_message=error_message)

# --- Run ---
if __name__ == '__main__':
    app.run(debug=True)