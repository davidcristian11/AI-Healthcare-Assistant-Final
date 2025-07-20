from flask import Flask, request, jsonify, render_template, redirect, url_for
import logging
import os
import base64
from werkzeug.utils import secure_filename
import uuid
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from knowledge_base import AzureKnowledgeBase, get_ai_response_with_knowledge_azure
from ai_service import get_ai_response
from image_service import get_ai_response_for_image

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = os.urandom(24)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

knowledge_base = AzureKnowledgeBase(data_path="knowledge/medical_conditions")


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def index():
    """Serve the main chat interface page"""
    return render_template('index.html')


@app.route("/about")
def about():
    """Serve the about page with project information"""
    return render_template('about.html')


@app.route("/admin")
def admin():
    """Admin interface for managing the knowledge base"""
    documents = knowledge_base.documents
    return render_template('admin.html', documents=documents)


@app.route("/admin/add", methods=["POST"])
def add_document():
    """Add a new document to the knowledge base"""
    title = request.form.get("title")
    content = request.form.get("content")
    category = request.form.get("category")

    if not title or not content:
        return jsonify({"error": "Title and content are required"}), 400

    success = knowledge_base.add_document(title, content, category)
    if success:
        logger.info(f"Added new document: {title}")
        return redirect(url_for('admin'))
    else:
        return jsonify({"error": "Failed to add document"}), 500


@app.route("/chat", methods=["POST"])
def chat():
    """Handle chat requests from the frontend"""
    data = request.json
    if not data or "message" not in data:
        logger.warning("Received request with no message")
        return jsonify({"error": "No message provided"}), 400

    user_input = data["message"]
    conversation_history = data.get("conversation", [])

    context = None
    if conversation_history:
        for message in reversed(conversation_history):
            if message.get("role") == "assistant":
                context = message.get("content")
                break

    logger.info(f"Received message: {user_input[:30]}...")

    try:
        if knowledge_base.documents:
            response = get_ai_response_with_knowledge_azure(user_input, knowledge_base, context)
            logger.info("Successfully processed message with knowledge base")
        else:
            response = get_ai_response(user_input, context)
            logger.info("Successfully processed message without knowledge base")

        return jsonify({"response": response})
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return jsonify({"error": "Failed to process your request"}), 500


@app.route('/upload-image', methods=['POST'])
def upload_image():
    """Handle image uploads"""
    if 'image' not in request.files:
        return jsonify({"error": "No image provided"}), 400

    file = request.files['image']

    if file.filename == '':
        return jsonify({"error": "No image selected"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)

        file.save(filepath)

        logger.info(f"Image uploaded: {unique_filename}")

        return jsonify({"filename": unique_filename, "success": True})

    return jsonify({"error": "Invalid file type"}), 400


@app.route('/analyze-image', methods=['POST'])
def analyze_image():
    """Analyze an uploaded image using the healthcare AI"""
    data = request.json

    if not data or "filename" not in data:
        return jsonify({"error": "No image specified"}), 400

    filename = data["filename"]
    question = data.get("question", "What can you tell me about this medical image?")
    conversation_history = data.get("conversation", [])

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    if not os.path.exists(filepath):
        return jsonify({"error": "Image not found"}), 404

    logger.info(f"Analyzing image: {filename}")

    try:
        with open(filepath, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode('utf-8')

        context = None
        if conversation_history:
            for message in reversed(conversation_history):
                if message.get("role") == "assistant":
                    context = message.get("content")
                    break

        response = get_ai_response_for_image(encoded_image, question, context)

        return jsonify({"response": response})

    except Exception as e:
        logger.error(f"Error analyzing image: {str(e)}")
        return jsonify({"error": "Failed to analyze the image"}), 500


@app.route("/status")
def status():
    """Return the status of the application including model in use"""
    return jsonify({
        "status": "online",
        "model": "gpt-4o",
        "documents": len(knowledge_base.documents)
    })


if __name__ == "__main__":
    token = os.environ.get("AZURE_API_KEY")
    if not token:
        logger.warning("No GitHub PAT token found")
        print("Warning: GitHub PAT token not found in environment variables")
        print("Set it with: export AZURE_API_KEY='github_pat_...'")

    logger.info(f"Knowledge base has {len(knowledge_base.documents)} documents")

    logger.info(f"Starting Smart Healthcare Assistant with Knowledge Base using Azure AI")

    print("Server starting at http://127.0.0.1:5000/")
    app.run(debug=True)