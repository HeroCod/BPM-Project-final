import pandas as pd
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

# Download necessary NLTK resources
nltk.download('punkt')
nltk.download('stopwords')

# Initialize the Porter Stemmer and the stop words for filtering
ps = PorterStemmer()
stop_words = set(stopwords.words('english'))

# Define a dictionary for common medical abbreviations and synonyms
medical_terms_dict = {
    'leprosy': ['lep', 'hansen'],
    'multiple osteochondromas': ['mo', 'hme', 'hereditary multiple exostoses'],
    'osteoarthritis': ['oa', 'degenerative joint disease'],
    'juvenile idiopathic arthritis': ['jia', 'juvenile rheumatoid arthritis', 'jra'],
    'sarcoma': ['sarcom', 'soft tissue tumor'],
    'chronic osteomyelitis': ['co'],
    'multibacillary leprosy': ['mb leprosy', 'mb lep', 'multibacillary lep'],
    'pauci-bacillary leprosy': ['pb leprosy', 'pb lep', 'paucibacillary lep'],
    'tuberculosis': ['tb', 'consumption'],
    'rheumatoid arthritis': ['ra'],
    'systemic lupus erythematosus': ['sle', 'lupus'],
    'ankylosing spondylitis': ['as'],
    'psoriatic arthritis': ['psa'],
    'reactive arthritis': ['reiter syndrome'],
    'sarcoidosis': ['sarcoid'],
    'systemic sclerosis': ['scleroderma'],
    'spondyloarthritis': ['spa'],
    'systemic vasculitis': ['vasculitis']
}

# Function to replace known medical abbreviations and synonyms with their full form
def expand_medical_abbreviations(text):
    for full_term, abbreviations in medical_terms_dict.items():
        for abbreviation in abbreviations:
            if abbreviation in text:
                text = text.replace(abbreviation, full_term)
    return text

# Function to clean, separate words, and stem the diagnosis data
def extract_relevant_terms(text):
    # Convert text to lowercase for uniformity
    text = text.lower()

    # Expand any medical abbreviations or synonyms
    text = expand_medical_abbreviations(text)

    # Remove any non-alphabetic characters
    text = re.sub(r'[^a-z\s]', '', text)

    # Tokenize the words
    words = nltk.word_tokenize(text)

    # Remove stopwords
    relevant_words = [word for word in words if word not in stop_words]

    # Stem relevant words
    stemmed_words = [ps.stem(word) for word in relevant_words]

    return set(stemmed_words)

# Function to extract the 5 diagnoses (from llama_suggestions)
def extract_diagnoses_from_llamasuggestions(suggestions_text):
    try:
        # Use regex to extract the five diagnosis options (numbered 1-5)
        diagnosis_list = re.findall(r'\d+\.\s([^\d]+)', suggestions_text)
        if len(diagnosis_list) == 5:
            return diagnosis_list
        else:
            return None  # Return None if there aren't exactly 5 diagnoses
    except Exception as e:
        print(f"Error extracting diagnoses: {e}")
        return None

# Load the datasets
answers_df = pd.read_csv('llama_answers.csv')
cases_df = pd.read_csv('cases_diagnosis_cleaned_relevant.csv')

# Create list to hold the results
rows_output = []

# Iterate over each row from 'answers.csv' and 'cases_diagnosis_cleaned_relevant.csv'
for idx, row in answers_df.iterrows():
    llama_suggestions = row['llama_suggestions']
    diagnoses = extract_diagnoses_from_llamasuggestions(llama_suggestions)

    # Proceed only if 5 diagnoses were extracted successfully
    if diagnoses:
        # Find the case in cases_df using matching 'pre_diagnosis'
        case_row = cases_df.loc[cases_df['pre_diagnosis'] == row['pre_diagnosis']]

        if not case_row.empty:
            case_diagnosis = case_row.iloc[0]['diagnosis']
            case_id = case_row.iloc[0]['case_id']

            # Clean and extract relevant terms for both suggestions and actual diagnosis
            cleaned_suggestions = [extract_relevant_terms(diag) for diag in diagnoses]
            cleaned_case_diagnosis = extract_relevant_terms(case_diagnosis)

            # Compare each suggestion against the real diagnosis using set intersection
            results = []
            for suggestion in cleaned_suggestions:
                # Use set intersection to check for any common terms between suggestion and actual diagnosis
                if suggestion & cleaned_case_diagnosis:  # If there's overlap in the sets
                    results.append(1)
                else:
                    results.append(0)

            # Append results to the output
            row_output = {
                'case_id': case_id,
                'match_1': results[0],
                'match_2': results[1],
                'match_3': results[2],
                'match_4': results[3],
                'match_5': results[4]
            }
                
            rows_output.append(row_output)

# Convert the results into a DataFrame
output_df = pd.DataFrame(rows_output)

# Write the output DataFrame to a new CSV file
output_csv_file = 'cases_with_binary_similarity_scores.csv'
output_df.to_csv(output_csv_file, index=False)

# Optionally, print the first few records for inspection
print(output_df.head())