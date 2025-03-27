import os
import sys
import csv
import argparse
import shutil
import pandas as pd  # Import pandas for CSV handling

# Setup argument parser
parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input', type=str, help="Input directory", default='data')
parser.add_argument('-o', '--output', type=str, help="Output csv file", default='experiment_data.csv')
parser.add_argument('-r', '--review', type=str, help="Output directory for files requiring review", default='review')
parser.add_argument('-e', '--errors', type=str, help="Output directory for files that failed to process", default='errors')
parser.add_argument('--interactive', action='store_true', help="Run interactive manual review", default=False)
args = parser.parse_args()

os.chdir(sys.path[0])
input_dir = args.input

valid_objects = ["bag", "basket", "bell", "bricks", "brush", "bucket", "button", "camera", "cart", "cup", "gun", "hammer", "hook", "horn", "kettle", "key", "knife", "match", "needle", "pencil", "plate", "scissors", "screwdriver", "spoon", "umbrella", "watch", "whistle", "wire"]

csv_out = "SubjectNumber,Codeword,Session,Age,ColourBlind,Gender,TotalRecall,NAMErecallTotal,NAMEproportion,NAMErt,COLOURrecallTotal,COLOURproportion,COLOURrt,FUNCTIONrecallTotal,FUNCTIONproportion,FUNCTIONrt,NOTES\n"

# Create directories for review and errors if they don't exist
if args.review:
    os.makedirs(args.review, exist_ok=True)

if args.errors:
    os.makedirs(args.errors, exist_ok=True)

manual_review = [] # List to store files that require manual review

def on_error(file, reason): # Function to handle errors during processing
    print(f'Error processing file {file}: {reason}')
    if args.errors: 
        shutil.copyfile(file, os.path.join(args.errors, file)) 

notes = {} # Allow to store notes in the CSV output
if os.path.exists(args.output):
    with open(args.output, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            notes[row['Codeword']] = row['NOTES']

# Function to count functional repetitions
def count_functional_repetitions(input_dir): 
    repetition_counts = {}
    for root, dirs, files in os.walk(input_dir): 
        for file in files:
            if not file.lower().endswith('.csv'):
                continue
            path = os.path.join(root, file) 
            df = pd.read_csv(path) # Read the CSV file into a DataFrame
            filtered_df = df[df['question_text'].str.contains("What is the FUNCTION of this object?", na=False)] # Filter rows containing the FUNCTION question
            answers = filtered_df[['a1', 'a2', 'a3', 'a4']].apply(lambda x: x.dropna().unique(), axis=1) # Get unique answers for each row
            repetition_count = answers.apply(lambda x: len(x)).sum() # Count the number of unique answers
            repetition_counts[file] = repetition_count # Store the repetition count in the dictionary
    return repetition_counts

# Function to add functional repetition counts to the CSV output
def add_functional_repetition_to_csv(csv_out, repetition_counts): 
    lines = csv_out.split("\n")
    header = lines[0] + ",Functional Repetition\n"
    new_csv_out = [header]
    for line in lines[1:]:
        if line.strip() == "":
            continue
        participant_code = line.split(',')[1]
        repetition_count = repetition_counts.get(participant_code + ".csv", 0)
        new_csv_out.append(line + f",{repetition_count}\n")
    return "".join(new_csv_out)

# Process each file
for root, dirs, files in os.walk(input_dir):
    for file in files:
        if not file.lower().endswith('.csv'):
            continue
        path = os.path.join(root, file)
        # This part represents processing each file, as you would normally do
        # Placeholder for your file processing logic

# Insert here your existing file processing logic

# After processing all files, calculate functional repetitions and add to csv_out
repetition_counts = count_functional_repetitions(input_dir)
csv_out = add_functional_repetition_to_csv(csv_out, repetition_counts)

# Write the final csv output
if args.output:
    with open(args.output, "w") as f:
        f.write(csv_out)

print("Processing complete.")
