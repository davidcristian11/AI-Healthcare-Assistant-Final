import os
import logging
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage, AssistantMessage
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

token = os.environ.get("AZURE_API_KEY", "you_key_here")
endpoint = os.environ.get("AZURE_ENDPOINT", "https://models.inference.ai.azure.com")
model_name = os.environ.get("AZURE_MODEL_NAME", "gpt-4o")
client = ChatCompletionsClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(token),
)

def get_ai_response_for_image(base64_image, question="Please analyze this medical image.", context=None):
    """
    Get a response from Azure AI about an image.

    Args:
        base64_image (str): The base64-encoded image data.
        question (str): The instruction for analysis (default provided).
        context (str, optional): Previous conversation context.

    Returns:
        str: The AI's response.
    """
    try:
        vision_prompt = {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": question
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                }
            ]
        }

        system_prompt = (
            "You are a specialized healthcare assistant providing accurate medical information based on images. "
            "You can analyze formal medical images like MRIs, X-rays, or CT scans. "
            "For casual photos or non-medical images, explain that you're designed for professional medical imagery only, "
            "and suggest proper medical consultation. "
            "Avoid making definitive diagnostic claims and always include appropriate medical disclaimers."
        )

        messages = [SystemMessage(system_prompt)]

        if context:
            messages.append(AssistantMessage(context))

        messages.append(UserMessage(vision_prompt))

        logger.info("Sending image analysis request to Azure AI")
        logger.info(f"Using model: {model_name}")

        response = client.complete(
            messages=messages,
            temperature=0.7,
            top_p=0.95,
            max_tokens=300,
            model=model_name
        )

        answer = response.choices[0].message.content
        logger.info("Received image analysis response from Azure AI")
        return answer

    except Exception as e:
        logger.error(f"Error analyzing image: {str(e)}")

        if "content policy" in str(e).lower() or "unsafe" in str(e).lower():
            return ("I'm not able to analyze this particular type of image due to safety guidelines. "
                    "I'm designed to work primarily with formal medical imagery like MRIs, X-rays, and CT scans. "
                    "For personal photos of medical conditions, please consult a healthcare professional for evaluation.")

        if "vision" in str(e).lower() or "image" in str(e).lower():
            return ("I'm currently having difficulty processing this image. I work best with clearly labeled medical imagery such as MRIs or X-rays. "
                    "Personal photos may be difficult for me to analyze accurately. Please consider sharing medical imaging from your healthcare provider instead.")

        return ("I encountered an issue while analyzing this image. My capabilities are best suited for formal medical images like MRIs or X-rays. "
                "Please consider consulting with a healthcare professional for a proper evaluation.")

