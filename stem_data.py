import pandas as pd
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

# Download necessary NLTK resources (if not already downloaded)
nltk.download('punkt')
nltk.download('stopwords')

# Initialize the Porter Stemmer and the stop words for filtering out irrelevant words
ps = PorterStemmer()
stop_words = set(stopwords.words('english'))

# Load the original CSV file
input_csv_file = 'cases_with_separated_diagnosis_truncated.csv'
df = pd.read_csv(input_csv_file)

# Function to clean the diagnosis column and remove irrelevant terms
def extract_relevant_terms(diagnosis_text):
    # Convert text to lowercase for uniformity
    diagnosis_text = diagnosis_text.lower()
    
    # Remove any special characters other than alphabetic ones, to retain diagnostic info
    diagnosis_text = re.sub(r'[^a-z\s]', '', diagnosis_text)
    
    # Tokenize the diagnosis text into words
    word_tokens = nltk.word_tokenize(diagnosis_text)
    
    # Filter out irrelevant words (e.g., stop words like 'the', 'and', etc.)
    filtered_words = [word for word in word_tokens if word not in stop_words]
    
    # Stem each word in the filtered diagnosis
    stemmed_words = [ps.stem(word) for word in filtered_words]
    
    # Join the stemmed words back into a cleaned diagnosis string
    cleaned_diagnosis = ' '.join(stemmed_words)
    
    return cleaned_diagnosis

# Apply the extraction function to the "diagnosis" column, replacing it with the relevant terms
df['diagnosis'] = df['diagnosis'].apply(extract_relevant_terms)

# Save the updated DataFrame back to a new CSV file, ensuring we maintain proper CSV format
output_csv_file = 'cases_diagnosis_cleaned_relevant.csv'
df.to_csv(output_csv_file, index=False)

# Optionally print the first few rows for inspection
print(df.head())