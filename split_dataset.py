import pandas as pd
from sklearn.model_selection import train_test_split

# Load the CSV file into a pandas DataFrame
df = pd.read_csv('paragraphs.csv')

# Split the dataset into train, validation, and test sets
train_val, test = train_test_split(df, test_size=0.15, random_state=42)
train, validation = train_test_split(train_val, test_size=0.15/0.85, random_state=42)

# Save the splits into separate CSV files
train.to_csv('train.csv', index=False)
validation.to_csv('validation.csv', index=False)
test.to_csv('test.csv', index=False)
