from SpeechToText import listen_and_convert
from nltk.corpus import wordnet as wn
from fuzzywuzzy import process
import nltk
import json

nltk.download('wordnet')
nltk.download('omw-1.4')

# Load your uncommon words (make sure it's a .json or .txt with a list)
with open("uncommon_words_list.txt", "r") as f:
    uncommon_words = json.load(f)

def get_closest_word(input_word, word_list, threshold=80):
    match, score = process.extractOne(input_word, word_list)
    if score >= threshold:
        return match
    return None

def get_synonyms_antonyms(word):
    synonyms = set()
    antonyms = set()

    for syn in wn.synsets(word):
        for lemma in syn.lemmas():
            synonyms.add(lemma.name().replace("_", " "))
            if lemma.antonyms():
                antonyms.update([a.name().replace("_", " ") for a in lemma.antonyms()])

    return sorted(synonyms), sorted(antonyms)

def get_definitions(word):
    definitions = []
    for syn in wn.synsets(word):
        definitions.append(syn.definition())
    return definitions

if __name__ == "__main__":
    word = listen_and_convert()
    if word:
        closest = get_closest_word(word, uncommon_words)
        if closest:
            print(f"\n🔍 Interpreted word: {closest}")
            syns, ants = get_synonyms_antonyms(closest)
            defs = get_definitions(closest)

            print("\n📚 Definitions:")
            if defs:
                for i, d in enumerate(defs[:3], start=1):
                    print(f"{i}. {d}")
            else:
                print("None found")

            print("\n📖 Synonyms:", syns if syns else "None found")
            print("⚔️ Antonyms:", ants if ants else "None found")
        else:
            print("❌ No similar word found in thesaurus.")
