import pandas as pd

# Read CSV with proper quote character and delimiter
df = pd.read_csv('cases.csv', quotechar='"', delimiter=',')

def has_final_diagnosis(text):
    diagnosis_patterns = [
        'the final diagnosis was'
    ]
    
    if isinstance(text, str):
        text_lower = text.lower()
        return any(pattern in text_lower for pattern in diagnosis_patterns)
    return False

# Filter based on case_text column
diagnosed = df[df['case_text'].apply(has_final_diagnosis)]
undiagnosed = df[~df['case_text'].apply(has_final_diagnosis)]

# Save filtered datasets
diagnosed.to_csv('cases_with_diagnosis.csv', index=False)
#undiagnosed.to_csv('cases_without_diagnosis.csv', index=False)

print(f"Cases with diagnosis: {len(diagnosed)}")
#print(f"Cases without diagnosis: {len(undiagnosed)}")

# Display first few rows of diagnosed cases to verify
print("\nSample of diagnosed cases:")
print(diagnosed['case_text'].head())