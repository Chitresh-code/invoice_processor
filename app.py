import streamlit as st
import os
import shutil  # Import shutil for directory removal
from src.preprocess import pdf_to_image_dict
from src.ai import process_image_data
from src.postprocess import create_dataframe, save_dataframe_to_excel, get_config

# Set the page configuration, including the title
st.set_page_config(page_title="Invoice Processor")

# Set the title of the Streamlit app
st.title("PDF Invoice Processor")

# File uploader for PDF files
uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

if uploaded_file is not None:
    # Create the tempDir directory if it doesn't exist
    temp_dir = "tempDir"
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    # Save the uploaded file temporarily
    pdf_path = os.path.join(temp_dir, uploaded_file.name)
    with open(pdf_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Convert PDF to image dictionary
    st.write("Converting PDF to images...")
    image_dict = pdf_to_image_dict(pdf_path)

    if image_dict is not None:
        # Process the image data to extract table information
        st.write("Processing images to extract table data...")
        processed_data = process_image_data(image_dict)

        if processed_data is not None:
            # Create a DataFrame from the processed data
            st.write("Creating DataFrame from extracted data...")
            df = create_dataframe(processed_data)

            if df is not None:
                # Display the DataFrame
                st.write("Extracted Data:")
                st.dataframe(df)

                # # Save the DataFrame to an Excel file
                # excel_file_path = os.path.join(temp_dir, "extracted_data.xlsx")
                # save_dataframe_to_excel(df, excel_file_path)

                # # Check if the file was created successfully
                # if os.path.exists(excel_file_path):
                #     # Provide a download link for the Excel file
                #     st.download_button(
                #         label="Download Excel File",
                #         data=open(excel_file_path, "rb").read(),
                #         file_name="extracted_data.xlsx",
                #         mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                #     )
                # else:
                #     st.error("Failed to create the Excel file.")
            else:
                st.error("No valid data extracted from the images.")
        else:
            st.error("Failed to process image data.")
    else:
        st.error("Failed to convert PDF to images.")

    # Print the configuration data
    config_data = get_config()
    if config_data is not None:
        st.write("Configuration Data:")
        st.write(f"API Calls: {config_data['last_api_calls']}")
        st.write(f"Token Count: {config_data['last_token_count']}")
        st.write(f"Total API Calls: {config_data['api_calls']}")
        st.write(f"Total Token Count: {config_data['total_token_count']}")
    else:
        st.error("Failed to get configuration data.")
    # Clean up temporary files if necessary
    shutil.rmtree(temp_dir)  # Remove the tempDir directory
    st.write("Temporary files cleaned up.")  # Log cleanup message
