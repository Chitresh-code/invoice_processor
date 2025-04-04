import pandas as pd
import json
from typing import Optional, Dict
from src.logger import setup_logger

logger = setup_logger(__name__)

def create_dataframe(image_dict: Dict[str, Optional[str]]) -> Optional[pd.DataFrame]:
    json_data = []
    for key, value in image_dict.items():
        if value != 'None':
            try:
                data = json.loads(value)
                if isinstance(data, list):
                    json_data.extend(data)
                elif isinstance(data, dict):
                    json_data.append(data)
                logger.info(f"Parsed JSON from page {key} successfully.")
            except json.JSONDecodeError as e:
                logger.error(f"Error decoding JSON for key {key}: {e}")
                continue

    if json_data:
        df = pd.DataFrame(json_data)
        logger.info("DataFrame created successfully.")
        return df
    else:
        logger.warning("No valid JSON data found to create DataFrame.")
        return None

def save_dataframe_to_excel(df: pd.DataFrame, file_path: str) -> None:
    try:
        with pd.ExcelWriter(file_path) as writer:
            df.to_excel(writer, sheet_name='Extracted Data', index=False)
        logger.info(f"DataFrame successfully saved to {file_path}.")
    except Exception as e:
        logger.error(f"Error saving DataFrame to Excel: {e}")