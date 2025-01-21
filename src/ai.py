import os
import requests
from dotenv import load_dotenv
import google.generativeai as genai
from src.logger import setup_logger  # Import the logger
from typing import Optional  # Import Optional for type hinting
from PIL import Image
import io
# from src.postprocess import config
from src.database import write_user_details

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
            "row": "<row number>",
            "item_number": "<item number>",
            "description": "<description>",
            "net_weight": "<net_weight>",
            "quantity": "<quantity>",
            "unit": "<unit>",
            "price": "<price>",
            "amount": "<amount>",
            "preferential_status": "<preferential_status>", (P, NP, or N/A)
    }},
    ...
    Note that the values and table headers in the invoice can change.
    In the field description if there are additional details, make sure to include them in a separate field.
    For the extra fields in the description, you can use the following format:
     - The extra fields will be in the format "extra_field_name: extra_field_value".
     In the json you can add them as:
    {{
        "extra_field_name1": "<extra_field_value2>",
        "extra_field_name2": "<extra_field_value2>",
        ...
    }}
    - Do not write the extra fields as extra_field_name1: extra_field_value1, etc. use the actual names of the fields.
    If there is no table, return None.
    Make sure the field names are written in small letters with underscores.
    Ensure that the JSON is not complex and can be easily converted to a Pandas DataFrame.
    """
    
    try:
        # Call the Gemini API using the model
        response = model.generate_content([image_data, prompt])
        
        # Extract the total_token_count
        total_token_count = response.usage_metadata.total_token_count
        
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
            
            return json_text, total_token_count
        else:
            raise ValueError("Response does not contain valid JSON.")
    return None

def process_image_data(username: str, image_dict: dict) -> Optional[dict]:
    """
    Processes a dictionary of image data to extract table information.
    """
    if not image_dict:  # Check if the dictionary is empty
        logger.error("Image dictionary is None or empty")  # Log the error
        return None
    
    try:
        total_token_count = 0
        api_calls = 0
        for key, image_bytes in image_dict.items():
            try:
                # Convert bytes to a PIL Image
                image = Image.open(io.BytesIO(image_bytes))
                
                # Call the Gemini API with the PIL Image
                result, token_count = extract_table_from_image(image)
                image_dict[key] = result
                api_calls += 1
                total_token_count += token_count
            except Exception as e:
                logger.error(f"Error processing image for page {key}: {e}")
                continue
        
        # config(username, api_calls, total_token_count)  # Update the configuration
        write_user_details(username, api_calls, total_token_count)  # Update the configuration
        logger.info(f"Total API calls made: {api_calls}")
        return image_dict # Return the dictionary after changing it
    except Exception as e:
        logger.error(f"Error processing image data: {e}")  # Log the error
        return None

