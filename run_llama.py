import pandas as pd  # For reading/writing CSV files.
import requests  # For communicating with the Ollama instance.
import json  # For handling JSON response from the Ollama instance
import csv  # For writing CSV row by row
import os  # For checking if the output file exists

# Function to send a request and handle streaming response
def query_llama(pre_diagnosis_text):
    # Local Ollama instance URL
    url = "http://192.168.16.64:11434/api/generate"
    # Construct the custom prompt
    prompt = f"""
    Provide the top 5 possible brief diagnoses based on the following patient information. 
    Only answer with the top 5 diagnosis wr with nothing at all, NEVER PROVIDE ANYTHING ELSE.
    Keep the responses 10 words or fewer per diagnosis:
    {pre_diagnosis_text}
    """
    # Prepare the payload with model information and tuning options
    payload = {
        "model": "llama3.2-vision:90b",
        "prompt": prompt,
        "max_tokens": 200,  # Limit the response length
        "temperature": 0.7,  # Balanced creativity vs accuracy
        "top_p": 1.0,        # Conservative behavior
    }
    headers = {'Content-Type': 'application/json'}

    try:
        # Sending the POST request and handling the response with streaming
        with requests.post(url, headers=headers, data=json.dumps(payload), stream=True) as response:
            response.raise_for_status()  # Raise error for non-200 status codes
            full_response = ""  # Initialize an empty string to accumulate results
            print("Streaming response:")
            # Stream the data and concatenate chunks as they come in
            for chunk in response.iter_content(chunk_size=None):
                # Decode the bytes to string and print the chunk to show streaming progress
                chunk_text = chunk.decode('utf-8')

                # Print the chunk so user can see the progress
                print(chunk_text, end='', flush=True)

                # Accumulate the response
                full_response += chunk_text

            # Now assume `full_response` has the final string, so let's process it
            try:
                # Split into individual JSON lines and extract the responses
                json_lines = full_response.split("\n")  # Splitting by lines since we receive multiple JSON objects
                response_parts = [json.loads(line).get("response", "") for line in json_lines if line.strip()]
                
                # Join all the parts of the response to get the final result
                response_text = "".join(response_parts).strip()

                # Remove any newlines from the final response text (if needed)
                response_text = response_text.replace("\n", " ")  # Replace newlines with spaces

                return response_text

            except json.JSONDecodeError:
                print("Failed to parse JSON. Full raw response:")
                print(full_response)
                return "Invalid JSON response received from LLM."

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return f"Request to LLM failed with error: {e}"

# Function to check rows already processed in the output CSV
def get_processed_rows(output_csv_file):
    # If output file does not exist, assume no rows have been processed.
    if not os.path.exists(output_csv_file):
        return set()

    processed_rows = set()
    with open(output_csv_file, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            processed_rows.add(row["pre_diagnosis"])  # Keep track of 'pre_diagnosis' in the output CSV
    return processed_rows

# Main function to handle row-wise diagnosis and output results directly to the CSV as we go
def generate_llm_diagnosis(csv_input_file, csv_output_file):
    # Step 1: Load the diagnostic information from the input CSV
    df = pd.read_csv(csv_input_file)

    # Step 2: Retrieve any rows that have already been processed
    processed_rows = get_processed_rows(csv_output_file)

    # Step 3: Loop over each row in the input CSV DataFrame
    for index, row in df.iterrows():
        pre_diagnosis_text = row.get("pre_diagnosis", "")  # Access the 'pre_diagnosis' column value

        # Skip rows that are already in the output CSV (already processed)
        if pre_diagnosis_text in processed_rows:
            print(f"Row {index} already processed. Skipping.")
            continue  # Skip previously processed rows

        if not pre_diagnosis_text:
            print(f"Warning: No pre_diagnosis found for row {index}. Skipping.")
            continue  # Skip empty rows

        # Query the LLM with the extracted 'pre_diagnosis' text
        print(f"Querying LLM for row {index}...")

        # Streamed response will show in real-time
        diagnosis_suggestions = query_llama(pre_diagnosis_text)

        # Step 4: Open the CSV file in append mode and write the result right after each query
        with open(csv_output_file, mode='a', newline='', encoding='utf-8') as output_csv_file:
            # Initialize CSV writer (setting quoting to QUOTE_ALL to handle any commas/newlines within fields)
            writer = csv.DictWriter(output_csv_file, fieldnames=["pre_diagnosis", "llama_suggestions"], quoting=csv.QUOTE_ALL)

            # If we're working with a fresh new file, write the header:
            if not processed_rows:
                writer.writeheader()

            # Write the new suggestion into the CSV file
            writer.writerow({"pre_diagnosis": pre_diagnosis_text, "llama_suggestions": diagnosis_suggestions})
            print(f"Row {index} processed. Written to output.")

        # Recalculate processed rows after writing, so we track progress
        processed_rows.add(pre_diagnosis_text)

    # Completion message
    print(f"LLM diagnosis suggestions have been saved to {csv_output_file}")

# Entry point for the script
if __name__ == '__main__':
    # Input/Output CSV file paths
    input_csv = "cases_diagnosis_cleaned_relevant.csv"  # This should be the source CSV with diagnoses
    output_csv = "llama_answers.csv"     # New CSV that will contain Llama-generated suggestions
    # Run the diagnosis generator with the specified CSV files
    generate_llm_diagnosis(input_csv, output_csv)