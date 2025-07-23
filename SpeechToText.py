import speech_recognition as sr

def listen_and_convert():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Speak a word...")
        audio = recognizer.listen(source)

        try:
            word = recognizer.recognize_google(audio)
            print(f"🗣 You said: {word}")
            return word.lower()
        except sr.UnknownValueError:
            print("❌ Could not understand the audio.")
        except sr.RequestError:
            print("❌ Error connecting to the recognition service.")
        return None

# Test
if __name__ == "__main__":
    spoken_word = listen_and_convert()
    if spoken_word:
        print("📝 Searching thesaurus for:", spoken_word)



