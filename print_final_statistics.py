import pandas as pd

# Load the CSV file into a DataFrame
df = pd.read_csv('cases_with_binary_similarity_scores.csv')

# Initialize counters
total_rows = len(df)
total_zeros = [0] * 5
total_ones = [0] * 5
undetected_count = 0
well_suggested_count = 0
suggested_count = 0

# Iterate through each row in the DataFrame
for index, row in df.iterrows():
    # Check if all matches from match_1 to match_5 are 0 for "undetected"
    if row['match_1'] == 0 and row['match_2'] == 0 and row['match_3'] == 0 and row['match_4'] == 0 and row['match_5'] == 0:
        undetected_count += 1
    
    # Check if the first match is 1 for "well suggested"
    if row['match_1'] == 1:
        well_suggested_count += 1
    
    # Check if at least one match from match_1 to match_5 is 1 for "suggested"
    if row['match_1'] == 1 or row['match_2'] == 1 or row['match_3'] == 1 or row['match_4'] == 1 or row['match_5'] == 1:
        suggested_count += 1

    # Count number of 1's and 0's for each match position (match_1 to match_5)
    for i in range(5):
        if row[f'match_{i+1}'] == 1:
            total_ones[i] += 1
        else:
            total_zeros[i] += 1

# Calculate percentages for 1's and 0's in each match position
percent_zeros = [(zeros / total_rows) * 100 for zeros in total_zeros]
percent_ones = [(ones / total_rows) * 100 for ones in total_ones]

# Calculate overall success percentages
undetected_percentage = (undetected_count / total_rows) * 100
well_suggested_percentage = (well_suggested_count / total_rows) * 100
suggested_percentage = (suggested_count / total_rows) * 100

# Print overall statistics
print("Match Position Statistics (in %):")
for i in range(5):
    print(f"Match_{i+1}: {percent_zeros[i]:.2f}% are 0, {percent_ones[i]:.2f}% are 1")

# Print success definitions
print(f"\nUnsuggested (all zeros): {undetected_percentage:.2f}%")
print(f"Well suggested (first match is 1): {well_suggested_percentage:.2f}%")
print(f"Suggested (at least one match is 1): {suggested_percentage:.2f}%")