import json
import os
import urllib.parse
import logging
import re
from concurrent.futures import ProcessPoolExecutor, as_completed

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def contains_binary_data(text):
    # Check for common binary file signatures
    pdf_signature = text.startswith('%PDF-')
    jpeg_signature = re.search(r'\xFF\xD8\xFF', text)  # JPEG signature
    png_signature = text.startswith('\x89PNG')
    # Add more signatures as needed

    # Check for high frequency of non-printable characters
    non_printable_chars = sum(1 for char in text if ord(char) < 32 and char not in '\t\n\r')

    high_non_printable = (len(text) == 0) or (non_printable_chars / len(text) > 0.1)  # Threshold for non-printable characters

    return pdf_signature or jpeg_signature or png_signature or high_non_printable

def process_file(input_file, output_folder):
    try:
        logging.info(f"Starting processing of file: {input_file}")

        # Read the JSON file assuming UTF-8 encoding
        with open(input_file, 'r', encoding='utf-8', errors='ignore') as file:
            data = json.load(file)

        logging.info(f"Successfully read file: {input_file}")

        # Create a new dictionary to store the filtered data
        filtered_data = {}

        # Iterate over the text_by_page_url dictionary
        for url, text in data.get('text_by_page_url', {}).items():
            # Check if the text contains binary data
            if not contains_binary_data(text):
                # Parse the URL to separate the path from the query parameters
                parsed_url = urllib.parse.urlparse(url)
                # Check if the path does not end with .css or .js and does not contain "/_static/" and does not contain "_jb_static
                if not parsed_url.path.endswith('.css') and not parsed_url.path.endswith('.js') and not parsed_url.path.endswith('.txt')and parsed_url.path.count("_jb_static") == 0 and parsed_url.path.count("/_static/") == 0 and parsed_url.path.count("Css") == 0:
                    filtered_data[url] = text

        # Define the output file path
        output_file = os.path.join(output_folder, os.path.basename(input_file))

        # Log the intended output file path
        logging.info(f"Attempting to save filtered data to {output_file}")

        # Save the filtered data to a new JSON file with UTF-8 encoding
        with open(output_file, 'w', encoding='utf-8') as file:
            json.dump({'text_by_page_url': filtered_data}, file, ensure_ascii=False, indent=4)

        logging.info(f"Filtered data saved to {output_file} with encoding UTF-8")

        # Additional check to confirm file existence
        if not os.path.exists(output_file):
            logging.error(f"File {output_file} was not created successfully.")
        else:
            logging.info(f"File {output_file} created successfully.")

    except Exception as e:
        logging.error(f"Error processing file {input_file}: {e}")

def process_files_in_parallel(input_folder, output_folder):
    # Create the output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # List all files in the input folder
    input_files = [os.path.join(input_folder, filename) for filename in os.listdir(input_folder)]

    logging.info(f"Processing {len(input_files)} files in parallel from {input_folder}")

    # Use ProcessPoolExecutor to parallelize the workload
    with ProcessPoolExecutor() as executor:
        future_to_file = {executor.submit(process_file, file, output_folder): file for file in input_files}
        for future in as_completed(future_to_file):
            file = future_to_file[future]
            try:
                future.result()
            except Exception as e:
                logging.error(f"Error processing file {file} in parallel: {e}")

if __name__ == '__main__':
    # Define the input and output folders

    bens_input_folder = "./../data/hackathon_data_reduced"
    bens_output_folder = "./../filtered_data/hackathon_data_reduced"
    # input_folder = os.path.join("C:/Users/futon/Desktop/ETH/FS2025/Hackerthon/data/hackathon_data")
    # output_folder = os.path.join("C:/Users/futon/Desktop/ETH/FS2025/Hackerthon/filtered_data/hackathon_data")
    input_folder = bens_input_folder
    output_folder = bens_output_folder

    # Log the start of the processing
    logging.info(f"Starting file processing from {input_folder} to {output_folder}")

    # Process files in parallel
    process_files_in_parallel(input_folder, output_folder)

    # Log the completion of the processing
    logging.info("File processing completed.")
