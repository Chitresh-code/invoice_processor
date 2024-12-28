import os
import requests
from dotenv import load_dotenv
import google.generativeai as genai
from src.logger import setup_logger  # Import the logger
from typing import Optional  # Import Optional for type hinting
from PIL import Image
import io

load_dotenv()  # Load environment variables from .env file

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Load Gemini 1.5 Flash
model = genai.GenerativeModel('gemini-1.5-flash')

logger = setup_logger(__name__)  # Set up the logger

def extract_table_from_image(image_data: str) -> Optional[str]:
    """
    Extracts the table of items from an invoice image using the Gemini API.
    """
    prompt = """
    You are an expert in understanding invoices.
    Extract the table of items from the invoice in a simple JSON format.
    The JSON can have a structure like this:
    {{
            "item": "Item Name",
            "model": "Model Name",
            "description": "Description",
            "c/o": "C/O",
            "quantity": "Quantity",
            "price": "Price",
            "amount": "Amount",
    }},
    ...
    Note that the values and table headers in the invoice can change.
    If there is no table, return None.
    Ensure that the JSON is not complex and can be easily converted to a Pandas DataFrame.
    """
    logger.info(f"Prompt: {prompt}")
    try:
        # Call the Gemini API using the model
        response = model.generate_content([image_data, prompt])
    except Exception as e:
        logger.error(f"Error calling Gemini API: {e}")  # Log the error
        return None
    
    if response:
        response_text = response.text.strip()

        if not response_text:
            raise ValueError("Response is empty after generation.")

        # Extract the JSON string from the response, cleaning any unnecessary parts
        if response_text.startswith("```json\n") and response_text.endswith("\n```"):
            json_text = response_text[8:-4].strip()  # Strip the ` ```json\n` and `\n``` `
            logger.info(f"Response: {json_text}")
            return json_text
        else:
            raise ValueError("Response does not contain valid JSON.")
    return None

def process_image_data(image_dict: dict) -> Optional[dict]:
    """
    Processes a dictionary of image data to extract table information.
    """
    if not image_dict:  # Check if the dictionary is empty
        logger.error("Image dictionary is None or empty")  # Log the error
        return None
    
    try:
        for key, image_bytes in image_dict.items():
            try:
                # Convert bytes to a PIL Image
                image = Image.open(io.BytesIO(image_bytes))
                
                # Call the Gemini API with the PIL Image
                # Assuming you have a function `call_gemini_api` that takes a PIL Image
                result = extract_table_from_image(image)
                image_dict[key] = result
            except Exception as e:
                logger.error(f"Error processing image for page {key}: {e}")
                continue
        
        return image_dict # Return the dictionary after changing it
    except Exception as e:
        logger.error(f"Error processing image data: {e}")  # Log the error
        return None

