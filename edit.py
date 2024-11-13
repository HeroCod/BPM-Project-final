def add_newline_after_comma(data):
    result = []
    inside_quotes = False

    for char in data:
        if char == '"':
            inside_quotes = not inside_quotes
        if char == ',' and not inside_quotes:
            result.append('~')
        else:
            result.append(char)

    return ''.join(result)

# Define file paths
input_file = 'cases.csv'
output_file = 'cases_modified.csv'

# Read the input file
with open(input_file, 'r') as file:
    input_data = file.read()

# Process the data
output_data = add_newline_after_comma(input_data)

# Write the output file
with open(output_file, 'w') as file:
    file.write(output_data)

print(f"Processed data saved to {output_file}")