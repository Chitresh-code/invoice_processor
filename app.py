import streamlit as st
import os
import shutil
import pandas as pd
from src.preprocess import pdf_to_image_dict
from src.ai import process_image_data
from src.postprocess import create_dataframe, save_dataframe_to_excel

# Set page configuration
st.set_page_config(page_title="Simple Invoice Extractor", page_icon="📄", layout="centered")

def main():
    st.title("📄 Simple PDF Invoice Extractor")
    st.write("Upload a PDF invoice to extract table data.")

    uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])
    extracted_df = None

    if uploaded_file is not None:
        # Create a temp directory to store the PDF
        temp_dir = "tempDir"
        os.makedirs(temp_dir, exist_ok=True)

        # Save uploaded PDF
        pdf_path = os.path.join(temp_dir, uploaded_file.name)
        with open(pdf_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Preprocess PDF into images
        st.write("🔄 Preprocessing the PDF...")
        image_dict = pdf_to_image_dict(pdf_path)

        if image_dict is not None:
            # Process image data using AI model
            st.write("🤖 Extracting data...")
            processed_data = process_image_data("anonymous_user", image_dict)  # Placeholder username

            if processed_data is not None:
                # Convert to DataFrame
                st.write("📊 Building table...")
                extracted_df = create_dataframe(processed_data)

                if extracted_df is not None:
                    st.success("✅ Data extracted successfully!")
                    st.dataframe(extracted_df)

                    # Save to Excel
                    excel_file_path = os.path.join(temp_dir, "extracted_data.xlsx")
                    save_dataframe_to_excel(extracted_df, excel_file_path)

                    # Download button
                    st.download_button(
                        label="⬇️ Download Excel File",
                        data=open(excel_file_path, "rb").read(),
                        file_name="extracted_data.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    )
                else:
                    st.error("⚠️ No valid data extracted from the PDF.")
            else:
                st.error("❌ Failed to process the PDF.")
        else:
            st.error("❌ Failed to preprocess the PDF.")

        # Cleanup
        uploaded_file.close()
        shutil.rmtree(temp_dir)

if __name__ == "__main__":
    main()