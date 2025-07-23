import nltk
from nltk.corpus import words, brown, wordnet
from collections import Counter
import random
import json

# Download required NLTK data
nltk.download("words", quiet=True)
nltk.download("brown", quiet=True)
nltk.download("wordnet", quiet=True)
nltk.download("averaged_perceptron_tagger", quiet=True)


def get_word_info(word):
    """Get comprehensive information about a word using WordNet"""
    synsets = wordnet.synsets(word)

    if not synsets:
        return None

    # Get the most common synset (first one)
    main_synset = synsets[0]

    # Get definition
    definition = main_synset.definition()

    # Get part of speech
    pos_map = {
        'n': 'noun',
        'v': 'verb',
        'a': 'adjective',
        's': 'adjective',  # satellite adjective
        'r': 'adverb'
    }
    pos = pos_map.get(main_synset.pos(), 'unknown')

    # Get synonyms (lemmas from all synsets)
    synonyms = set()
    for syn in synsets:
        for lemma in syn.lemmas():
            if lemma.name() != word and '_' not in lemma.name():
                synonyms.add(lemma.name().replace('_', ' '))

    # Get antonyms
    antonyms = set()
    for syn in synsets:
        for lemma in syn.lemmas():
            for antonym in lemma.antonyms():
                if '_' not in antonym.name():
                    antonyms.add(antonym.name().replace('_', ' '))

    # Get example sentence if available
    examples = []
    for syn in synsets[:2]:  # Check first 2 synsets
        if syn.examples():
            examples.extend(syn.examples()[:1])  # Take first example

    return {
        'word': word,
        'definition': definition,
        'part_of_speech': pos,
        'synonyms': list(synonyms)[:8],  # Limit to 8 synonyms
        'antonyms': list(antonyms)[:5],  # Limit to 5 antonyms
        'examples': examples[:1]  # One example
    }


def main():
    print("🔄 Loading word datasets...")

    # Get all English words
    all_words = set(word.lower() for word in words.words())

    # Get frequency data from Brown corpus
    brown_words = [word.lower() for word in brown.words()]
    brown_freq = Counter(brown_words)

    # Get words that appear in Brown corpus (so they're real/used words)
    # but not the most common 1000 (so they're educational)
    most_common = set([word for word, _ in brown_freq.most_common(1000)])
    used_words = set([word for word, count in brown_freq.items() if count >= 2])

    # Target words: used in real text but not super common
    target_words = used_words - most_common

    # Filter for good candidates
    candidates = []
    for word in target_words:
        if (word.isalpha() and
                len(word) >= 4 and
                len(word) <= 12 and
                word in all_words):
            candidates.append(word)

    print(f"🔍 Found {len(candidates)} candidate words")
    print("📝 Processing words and gathering definitions...")

    # Shuffle to get variety
    random.shuffle(candidates)

    meaningful_words = []
    processed = 0

    for word in candidates:
        if len(meaningful_words) >= 3000:
            break

        processed += 1
        if processed % 100 == 0:
            print(f"   Processed {processed} words, found {len(meaningful_words)} meaningful ones...")

        word_info = get_word_info(word)

        if word_info and len(word_info['definition']) > 10:  # Must have good definition
            meaningful_words.append(word_info)

    # Sort alphabetically
    meaningful_words.sort(key=lambda x: x['word'])

    # Save to JSON file
    with open("meaningful_words_3k.json", "w", encoding='utf-8') as f:
        json.dump(meaningful_words, f, indent=2, ensure_ascii=False)

    # Create a summary file
    summary = {
        'total_words': len(meaningful_words),
        'parts_of_speech': {},
        'avg_synonyms': sum(len(w['synonyms']) for w in meaningful_words) / len(meaningful_words),
        'avg_antonyms': sum(len(w['antonyms']) for w in meaningful_words) / len(meaningful_words),
        'sample_words': meaningful_words[:5]
    }

    # Count parts of speech
    for word_info in meaningful_words:
        pos = word_info['part_of_speech']
        summary['parts_of_speech'][pos] = summary['parts_of_speech'].get(pos, 0) + 1

    with open("word_summary.json", "w", encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"✅ Generated {len(meaningful_words)} meaningful words!")
    print(f"📊 Parts of speech breakdown:")
    for pos, count in summary['parts_of_speech'].items():
        print(f"   {pos}: {count} words")
    print(f"📈 Average synonyms per word: {summary['avg_synonyms']:.1f}")
    print(f"📉 Average antonyms per word: {summary['avg_antonyms']:.1f}")
    print(f"💾 Saved to: meaningful_words_3k.json")
    print(f"📋 Summary saved to: word_summary.json")

    # Show some examples
    print(f"\n🔤 Sample words:")
    for i, word_info in enumerate(meaningful_words[:3]):
        print(f"\n{i + 1}. {word_info['word'].upper()} ({word_info['part_of_speech']})")
        print(f"   Definition: {word_info['definition']}")
        if word_info['synonyms']:
            print(f"   Synonyms: {', '.join(word_info['synonyms'][:4])}")
        if word_info['antonyms']:
            print(f"   Antonyms: {', '.join(word_info['antonyms'][:3])}")


if __name__ == "__main__":
    main()