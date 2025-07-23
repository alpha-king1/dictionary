import json
from nltk.stem import WordNetLemmatizer
import nltk

# Download WordNet if not already done
nltk.download('wordnet')
nltk.download('omw-1.4')

# Initialize lemmatizer
lemmatizer = WordNetLemmatizer()

# Function to normalize user input
def normalize_word(word):
    return lemmatizer.lemmatize(word.lower())

# Function to search in your dataset
def search_word(word, dataset):
    normalized = normalize_word(word)
    for entry in dataset:
        if entry["word"].lower() == normalized:
            return entry
    return {"message": "Word not found"}

# Load dataset
with open("words.json", "r") as f:
    dataset = json.load(f)

# --- Example usage ---
if __name__ == "__main__":
    user_input = input("Enter a word: ")
    result = search_word(user_input, dataset)
    print(json.dumps(result, indent=4))
