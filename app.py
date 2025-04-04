from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
from src.preprocess import pdf_to_image_dict
from src.ai import process_image_data
from src.postprocess import create_dataframe, save_dataframe_to_excel

app = FastAPI()

# Enable CORS for frontend interaction
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static folders
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/data", StaticFiles(directory="data"), name="data")

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/extract-invoice/")
async def extract_invoice_data_from_pdf_api(pdf: UploadFile = File(...), username: str = "local_user"):
    temp_dir = "tempDir"
    os.makedirs(temp_dir, exist_ok=True)
    pdf_path = os.path.join(temp_dir, pdf.filename)

    with open(pdf_path, "wb") as buffer:
        shutil.copyfileobj(pdf.file, buffer)

    image_dict = pdf_to_image_dict(pdf_path)
    if image_dict is None:
        shutil.rmtree(temp_dir)
        return {"error": "Failed to preprocess the PDF."}

    processed_data = process_image_data(username, image_dict)
    if processed_data is None:
        shutil.rmtree(temp_dir)
        return {"error": "Failed to process the PDF."}

    extracted_df = create_dataframe(processed_data)
    if extracted_df is None:
        shutil.rmtree(temp_dir)
        return {"error": "No valid data extracted from the PDF."}

    output_dir = "data"
    os.makedirs(output_dir, exist_ok=True)
    excel_file_path = os.path.join(output_dir, f"{os.path.splitext(pdf.filename)[0]}_extracted.xlsx")
    save_dataframe_to_excel(extracted_df, excel_file_path)

    shutil.rmtree(temp_dir)
    return {"message": "✅ Data extracted successfully.", "excel_path": excel_file_path}

@app.delete("/clear-data/")
async def clear_data_folder():
    folder = "data"
    if not os.path.exists(folder):
        return {"message": "Nothing to clear."}

    try:
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
        return {"message": "🧹 All extracted files have been cleared."}
    except Exception as e:
        return {"error": f"Failed to clear files: {str(e)}"}