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

def get_ai_response(user_input, context=None):
    """
    Get a response from Azure AI using GPT-4o.

    Args:
        user_input (str): The message from the user
        context (str, optional): Previous message context for continuity

    Returns:
        str: The AI's response
    """
    try:
        messages = [
            SystemMessage(
                "You are a healthcare assistant providing brief, accurate medical information. "
                "Focus on symptoms, conditions, and general wellness advice. "
                "Keep responses concise but informative. "
                "Always include appropriate disclaimers about consulting healthcare professionals for definitive advice."
            )
        ]

        if context:
            messages.append(AssistantMessage(context))

        messages.append(UserMessage(user_input))

        logger.info("Sending request to Azure AI")
        logger.info(f"Using token: {token[:5]}...{token[-4:]} (partial for security)")
        logger.info(f"Using model: {model_name}")

        # Get response from Azure
        response = client.complete(
            messages=messages,
            temperature=0.7,
            top_p=0.95,
            max_tokens=150,
            model=model_name
        )

        answer = response.choices[0].message.content
        logger.info(f"Received response from Azure AI: {answer[:50]}...")

        return answer

    except Exception as e:
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Error message: {str(e)}")
        logger.error(f"Error details: {repr(e)}")

        if "quota" in str(e).lower() or "exceeded" in str(e).lower():
            return "I'm unable to respond due to API quota limitations. The account has reached its usage limit."
        elif "authentication" in str(e).lower() or "key" in str(e).lower():
            return "There appears to be an issue with the API configuration. Please check the application setup and ensure the API key is valid."
        elif "rate limit" in str(e).lower():
            return "The service is currently experiencing high demand. Please try again in a few moments."
        elif "context length" in str(e).lower() or "token" in str(e).lower():
            return "Your question or conversation history is too long for me to process. Please try asking a shorter question or starting a new conversation."
        elif "content filter" in str(e).lower():
            return "I cannot provide information on this topic due to content restrictions. Please try asking about something else."
        elif "connection" in str(e).lower() or "timeout" in str(e).lower() or "network" in str(e).lower():
            return "I'm having trouble connecting to my knowledge source. This might be due to network issues. Please check your internet connection and try again shortly."
        else:
            return "I'm sorry, I encountered an error while processing your request. Please try again later."