import pandas as pd
from sklearn.model_selection import train_test_split
from langdetect import detect

# Load the CSV file into a pandas DataFrame
df = pd.read_csv('../scripts_extraction/paragraphs.csv')

# Filter out rows where the text is not in Italian
italian_rows = []
for index, row in df.iterrows():
    try:
        if detect(row['text']) == 'it':
            italian_rows.append(index)
    except:
        pass

# Keep only the Italian rows in the DataFrame
df = df.loc[italian_rows]

# Substitute characters in each row text using the regex pattern
df['text'] = df['text'].str.replace(r"\[.*?\]\s", "", regex=True)

# Split the dataset into train, validation, and test sets
train_val, test = train_test_split(df, test_size=0.15, random_state=42)
train, validation = train_test_split(train_val, test_size=0.15/0.85, random_state=42)

# Save the splits into separate CSV files
train.to_csv('train.csv', index=False)
validation.to_csv('validation.csv', index=False)
test.to_csv('test.csv', index=False)
