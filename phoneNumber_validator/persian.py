import pandas as pd
import os
import re

# Convert Persian/Arabic digits to English digits
def persian_to_english(num):
    persian_digits = '۰۱۲۳۴۵۶۷۸۹'
    english_digits = '0123456789'
    return num.translate(str.maketrans(persian_digits, english_digits))

# Extract all potential phone numbers from a string (even from text with spaces/dashes)
def extract_all_phone_numbers(text):
    text = persian_to_english(str(text))  # Convert Persian/Arabic digits to English
    text = re.sub(r'[^\d]', '', text)  # Remove any non-digit characters

    # Use regex to find all digit sequences
    possible_numbers = re.findall(r'\d+', text)

    valid_numbers = []
    for number in possible_numbers:
        cleaned_number = clean_phone_number(number)
        if cleaned_number:
            valid_numbers.append(cleaned_number)

    return valid_numbers

# Clean and validate a phone number
def clean_phone_number(number):
    original_num = number  # Keep the original for logging

    if number.startswith('+98'):
        number = '0' + number[3:]
    elif number.startswith('98'):
        number = '0' + number[2:]
    elif number.startswith('9'):
        number = '0' + number

    # Check if it's a valid phone number with exactly 11 digits and starting with '09'
    if len(number) == 11 and number.startswith('09'):
        return number
    else:
        # Log dropped numbers with reasons
        print(f"Dropped: {original_num} | Cleaned: {number} | Reason: Invalid format/length")
        return None

# Process the file to extract all potential phone numbers from any column or row
def process_file(file_path):
    print(f"Processing file: {file_path}")
    if file_path.endswith('.csv'):
        df = pd.read_csv(file_path, header=None)  # Ignore headers by using header=None
    elif file_path.endswith('.xlsx'):
        df = pd.read_excel(file_path, header=None)  # Ignore headers by using header=None
    else:
        raise ValueError("Unsupported file format")

    all_phone_numbers = []

    # Scan through all rows and columns, treating each cell as a potential source of phone numbers
    for row in df.itertuples(index=False):
        for cell in row:
            valid_numbers = extract_all_phone_numbers(cell)
            all_phone_numbers.extend(valid_numbers)

    # Create a DataFrame with a single column for all phone numbers
    cleaned_data = pd.DataFrame({ 'phone_number': all_phone_numbers })

    # Remove duplicate phone numbers
    cleaned_data = cleaned_data.drop_duplicates()

    return cleaned_data

# Automatically process files in the current directory
def process_files_in_directory(directory):
    for file_name in os.listdir(directory):
        file_path = os.path.join(directory, file_name)
        if file_name.endswith('.csv') or file_name.endswith('.xlsx'):
            processed_df = process_file(file_path)
            if processed_df is not None:
                output_path = os.path.join(directory, f'processed_{file_name}')
                if file_name.endswith('.csv'):
                    processed_df.to_csv(output_path, index=False, header=False)  # Save without headers
                elif file_name.endswith('.xlsx'):
                    processed_df.to_excel(output_path, index=False, header=False)  # Save without headers
                print(f"Processed file saved to {output_path}")

# Specify the directory containing your files
directory = '.'  # Use '.' for the current directory or specify a path
process_files_in_directory(directory)
