import os
import io
from dotenv import load_dotenv
from typing import Optional
from PIL import Image
from google import genai
from src.logger import setup_logger

load_dotenv()
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
logger = setup_logger(__name__)

def extract_table_from_image(image_data: str) -> Optional[str]:
    prompt = """
    You are an expert in understanding bank statements.
    Extract the table of items from the bank statement in a simple JSON format.
    The JSON should use lowercase field names with underscores and should be easily convertible to a Pandas DataFrame.
    If there is no table, return None.
    """
    try:
        response = client.models.generate_content(
            contents=[image_data, prompt],
            model='gemini-2.0-flash',
        )
        total_token_count = response.usage_metadata.total_token_count
    except Exception as e:
        logger.error(f"Error calling Gemini API: {e}")
        return None

    if response:
        response_text = response.text.strip()
        if not response_text:
            raise ValueError("Response is empty.")
        if response_text.startswith("```json") and response_text.endswith("```"):
            json_text = response_text[8:-3].strip()
            return json_text, total_token_count
        else:
            raise ValueError("Response does not contain valid JSON.")
    return None

def process_image_data(username: str, image_dict: dict) -> Optional[dict]:
    if not image_dict:
        logger.error("Image dictionary is empty")
        return None
    try:
        total_token_count = 0
        api_calls = 0
        for key, image_bytes in image_dict.items():
            try:
                image = Image.open(io.BytesIO(image_bytes))
                result, token_count = extract_table_from_image(image)
                logger.info(f"Extracted data for page {key} with token count: {token_count}")
                if not result:
                    logger.warning(f"No data extracted for page {key}")
                    continue
                image_dict[key] = result
                api_calls += 1
                total_token_count += token_count
            except Exception as e:
                logger.error(f"Error processing image for page {key}: {e}")
                continue
        logger.info(f"Total API calls made: {api_calls}")
        return image_dict
    except Exception as e:
        logger.error(f"Error processing image data: {e}")
        return None
