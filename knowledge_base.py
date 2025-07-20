import os
import json
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import logging
import random
from dotenv import load_dotenv
from azure.ai.inference import EmbeddingsClient, ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage, AssistantMessage
from azure.core.credentials import AzureKeyCredential

load_dotenv()

logger = logging.getLogger(__name__)

token = os.environ.get("AZURE_API_KEY","you_key_here")
endpoint = os.environ.get("AZURE_ENDPOINT", "https://models.inference.ai.azure.com")
chat_model_name = os.environ.get("AZURE_MODEL_NAME", "gpt-4o")
embedding_model_name = os.environ.get("AZURE_EMBEDDING_MODEL", "text-embedding-ada-002")

chat_client = ChatCompletionsClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(token),
)

embedding_client = EmbeddingsClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(token),
)


class AzureKnowledgeBase:
    def __init__(self, data_path="knowledge"):
        """
        Initialize the knowledge base with documents from the specified directory.

        Args:
            data_path (str): Path to the directory containing knowledge documents
        """
        self.documents = []
        self.embeddings = []
        self.data_path = data_path
        self.load_documents(data_path)

    def load_documents(self, data_path):
        """Load documents from the knowledge directory."""
        try:
            if not os.path.exists(data_path):
                os.makedirs(data_path)
                logger.warning(f"Created empty knowledge directory at {data_path}")
                return

            for filename in os.listdir(data_path):
                if filename.endswith('.json'):
                    with open(os.path.join(data_path, filename), 'r') as f:
                        doc = json.load(f)
                        if 'content' in doc and 'title' in doc:
                            self.documents.append(doc)

            logger.info(f"Loaded {len(self.documents)} documents from knowledge base")
        except Exception as e:
            logger.error(f"Error loading knowledge base: {str(e)}")

    def create_embeddings(self):
        """
        This method is disabled as the embeddings API isn't working as expected.
        We'll use a keyword-based approach instead.
        """
        logger.warning("Embeddings creation is disabled - using keyword search instead")
        return

    def add_document(self, title, content, category=None):
        """
        Add a new document to the knowledge base.

        Args:
            title (str): Title of the document
            content (str): Text content of the document
            category (str, optional): Category for organizing documents
        """
        try:
            doc = {
                "title": title,
                "content": content,
                "category": category
            }

            self.documents.append(doc)
            self._save_document(doc)
            logger.info(f"Added new document: {title}")
            return True
        except Exception as e:
            logger.error(f"Error adding document: {str(e)}")
            return False

    def _save_document(self, doc):
        """Save a document to the knowledge directory."""
        try:
            filename = "".join(x for x in doc['title'] if x.isalnum() or x in " _").strip()
            filename = filename.replace(" ", "_").lower()

            with open(os.path.join(self.data_path, f"{filename}.json"), 'w') as f:
                json.dump(doc, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving document: {str(e)}")

    def _keyword_search(self, query, top_k=3):
        """
        Perform a simple keyword-based search of the documents.

        Args:
            query (str): The search query
            top_k (int): Number of results to return

        Returns:
            list: Top k relevant documents
        """
        if not self.documents:
            return []

        query = query.lower()
        query_terms = query.split()

        scores = []
        for doc in self.documents:
            title = doc['title'].lower()
            content = doc['content'].lower()

            title_score = sum(3 for term in query_terms if term in title)
            content_score = sum(1 for term in query_terms if term in content)

            score = title_score + content_score
            scores.append(score)

        top_indices = np.argsort(scores)[-top_k:][::-1]

        filtered_indices = [idx for idx in top_indices if scores[idx] > 0]

        if not filtered_indices:
            if self.documents:
                available_indices = list(range(len(self.documents)))
                filtered_indices = random.sample(
                    available_indices,
                    min(top_k, len(available_indices))
                )

        results = []
        for idx in filtered_indices:
            doc = self.documents[idx].copy()
            doc['similarity'] = 0.5
            results.append(doc)

        return results

    def search(self, query, top_k=3):
        """
        Search for relevant documents based on the query.

        Args:
            query (str): The search query
            top_k (int): Number of results to return

        Returns:
            list: Top k relevant documents
        """
        if not self.documents:
            logger.warning("Knowledge base is empty")
            return []

        try:
            results = self._keyword_search(query, top_k)
            logger.info(f"Found {len(results)} relevant documents using keyword search")
            return results
        except Exception as e:
            logger.error(f"Error performing keyword search: {str(e)}")
            return []


def get_ai_response_with_knowledge_azure(user_input, knowledge_base, context=None):
    """
    Get an AI response enhanced with domain-specific knowledge using Azure AI.

    Args:
        user_input (str): The user's question
        knowledge_base (AzureKnowledgeBase): Knowledge base for retrieving context
        context (str, optional): Previous conversation context

    Returns:
        str: The AI's response
    """
    try:
        relevant_docs = knowledge_base.search(user_input)

        system_prompt = (
            "You are a specialized healthcare assistant providing accurate medical information. "
            "Focus on symptoms, conditions, and general wellness advice. "
            "Keep responses concise but informative. "
            "Always include appropriate disclaimers about consulting healthcare professionals for definitive advice."
        )

        if relevant_docs:
            system_prompt += "\n\nUse the following specialized information to inform your response:\n\n"
            for i, doc in enumerate(relevant_docs, 1):
                system_prompt += f"{doc['title']}: {doc['content']}\n\n"


        messages = [SystemMessage(system_prompt)]

        if context:
            messages.append(AssistantMessage(context))

        messages.append(UserMessage(user_input))

        logger.info("Sending enhanced request to Azure AI")
        logger.info(f"Using model: {chat_model_name}")

        response = chat_client.complete(
            messages=messages,
            temperature=0.7,
            top_p=0.95,
            max_tokens=250,
            model=chat_model_name
        )

        answer = response.choices[0].message.content
        logger.info(f"Received enhanced response from Azure AI")

        return answer

    except Exception as e:
        logger.error(f"Error getting AI response: {str(e)}")
        return "I'm sorry, I encountered an error while processing your request. Please try again later."