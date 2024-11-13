import re
import pandas as pd

# Define the file paths for the input and output files
input_file = 'cases_with_diagnosis.csv'
output_file = 'cases_with_separated_diagnosis_truncated.csv'

def separate_diagnosis(case_text, diagnosis_keywords=None):
    """
    Separates the 'pre-diagnosis' description from the 'diagnosis' itself using heuristic rules.
    
    Parameters:
    - case_text: The text of the case (symptoms, medical history, etc.).
    - diagnosis_keywords: A list of keywords that specifically signal a final diagnosis.
    
    Returns:
    - pre_diagnosis_text: Text that describes symptoms, medical reports but NOT the final diagnosis.
    - diagnosis_text: Text that specifies the final diagnosis.
    """
    # Default keywords signaling the diagnosis portion of text
    if diagnosis_keywords is None:
        diagnosis_keywords = [
            r'the final diagnosis was'
        ]
    
    # Combine keywords into a regex pattern to detect them in text
    diagnosis_pattern = re.compile('|'.join(diagnosis_keywords), re.IGNORECASE)
    
    # Split case_text based on matched diagnostic keywords
    split_sections = diagnosis_pattern.split(case_text, maxsplit=1)
    
    # Define pre-diagnosis and diagnosis section based on splitting
    pre_diagnosis_text = split_sections[0].strip()
    diagnosis_text = split_sections[1].strip() if len(split_sections) > 1 else "Diagnosis not explicitly stated"
    
    return pre_diagnosis_text, diagnosis_text

def truncate_diagnosis(diagnosis_text):
    """
    Truncates the diagnosis text to keep only the portion before the first dot (.).
    
    Parameters:
    - diagnosis_text: The diagnosis string to be truncated.
    
    Returns:
    - truncated_text: The substring of the diagnosis text before the first dot.
    """
    period_position = diagnosis_text.find('.')
    
    if period_position != -1:
        # Return only the diagnosis part before the first dot
        return diagnosis_text[:period_position + 1].strip()  # Keeps the first sentence (including the dot)
    else:
        # No period found, return the full diagnosis text
        return diagnosis_text.strip()

def process_cases_in_csv(input_file, output_file):
    """
    Reads the input CSV file, processes each case to separate the pre-diagnosis from the diagnosis,
    truncates the diagnosis after the first dot, and then writes the results to a new CSV file.
    Discards any cases where the diagnosis has over 1000 characters.
    
    Parameters:
    - input_file: The path to the input CSV file.
    - output_file: The path to the output CSV file.
    """
    # Load the CSV into a DataFrame
    df = pd.read_csv(input_file)
    
    # Verify that required columns exist in the CSV
    if 'case_id' not in df.columns or 'gender' not in df.columns or 'age' not in df.columns or 'case_text' not in df.columns:
        print("Error: The input CSV file must contain the columns: 'case_id', 'gender', 'age', 'case_text'.")
        return
    
    # Lists to store separated and filtered data
    pre_diagnosis_list = []
    diagnosis_list = []
    
    # Loop over each case in the dataframe
    for _, row in df.iterrows():
        case_text = row['case_text']
        
        # Check if the case_text length is within 1000 characters
        if len(case_text) > 3000:
            print(f"Skipping case {row['case_id']} - Diagnosis longer than 1000 characters.")
            continue  # Skip current row if diagnosis is more than 1000 characters

        # Separate the pre-diagnosis from diagnosis in the case text
        pre_diagnosis, diagnosis = separate_diagnosis(case_text)
        
        # Truncate the diagnosis at the first dot.
        truncated_diagnosis = truncate_diagnosis(diagnosis)
        
        # Append the results to lists
        pre_diagnosis_list.append(pre_diagnosis)
        diagnosis_list.append(truncated_diagnosis)
    
    # Update the DataFrame with the new columns
    df = df.loc[0:len(pre_diagnosis_list)-1]  # Select rows matching filtered cases
    df['pre_diagnosis'] = pre_diagnosis_list
    df['diagnosis'] = diagnosis_list
    
    # Save the modified DataFrame to a new CSV file, without discarded rows
    df.to_csv(output_file, index=False)
    print(f"Processed data has been saved to {output_file}")

# Run the processing function
process_cases_in_csv(input_file, output_file)