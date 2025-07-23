import tkinter as tk
from tkinter import messagebox, scrolledtext
from nltk.corpus import wordnet as wn
import nltk
import speech_recognition as sr
import threading

# Download NLTK data
nltk.download('wordnet')
nltk.download('omw-1.4')

# Sample uncommon word list for demo (extend with your 3000-word dataset)
word_list = sorted(list(set(w.name().split('.')[0] for w in wn.all_synsets())))

def get_word_data(word):
    word = word.lower()
    meanings = []
    synonyms = set()
    antonyms = set()
    parts_of_speech = set()

    for syn in wn.synsets(word):
        parts_of_speech.add(syn.pos())
        meanings.append(syn.definition())
        for lemma in syn.lemmas():
            synonyms.add(lemma.name().replace('_', ' '))
            for ant in lemma.antonyms():
                antonyms.add(ant.name().replace('_', ' '))

    return {
        'meanings': meanings if meanings else ["No definition found."],
        'synonyms': sorted(synonyms),
        'antonyms': sorted(antonyms),
        'parts_of_speech': sorted(parts_of_speech) if parts_of_speech else ["N/A"]
    }

def listen_and_convert():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        messagebox.showinfo("Speech Input", "🎤 Speak a word...")
        try:
            audio = recognizer.listen(source, timeout=5)
            word = recognizer.recognize_google(audio)
            search_var.set(word)
            search_word()
        except sr.UnknownValueError:
            messagebox.showerror("Error", "Could not understand audio.")
        except sr.RequestError:
            messagebox.showerror("Error", "Could not connect to the recognition service.")
        except sr.WaitTimeoutError:
            messagebox.showerror("Timeout", "No speech detected.")

def threaded_listen():
    threading.Thread(target=listen_and_convert).start()

def search_word():
    word = search_var.get().strip().lower()
    if word not in word_list:
        messagebox.showinfo("Not Found", f"'{word}' is not in the thesaurus.")
        return
    data = get_word_data(word)
    result_text.config(state='normal')
    result_text.delete(1.0, tk.END)
    result_text.insert(tk.END, f"📌 Word: {word}\n")
    result_text.insert(tk.END, f"📚 Part of Speech: {', '.join(data['parts_of_speech'])}\n\n")
    result_text.insert(tk.END, "📝 Definitions:\n")
    for i, m in enumerate(data['meanings'], 1):
        result_text.insert(tk.END, f"{i}. {m}\n")
    result_text.insert(tk.END, "\n✨ Synonyms: " + (", ".join(data['synonyms']) if data['synonyms'] else "None") + "\n")
    result_text.insert(tk.END, "⚔️ Antonyms: " + (", ".join(data['antonyms']) if data['antonyms'] else "None"))
    result_text.config(state='disabled')

def on_word_select(event):
    try:
        index = word_listbox.curselection()[0]
        word = word_listbox.get(index)
        search_var.set(word)
        search_word()
    except IndexError:
        pass

def exit_app():
    root.destroy()

# UI Setup
root = tk.Tk()
root.title("Smart Thesaurus")
root.attributes('-fullscreen', True)

search_var = tk.StringVar()

# Sidebar
sidebar = tk.Frame(root, width=200, bg='#e0e0e0')
sidebar.pack(fill=tk.Y, side=tk.LEFT)

tk.Label(sidebar, text="📚 Word List", bg='#e0e0e0', font=('Helvetica', 14, 'bold')).pack(pady=10)

word_listbox = tk.Listbox(sidebar)
for word in word_list:
    word_listbox.insert(tk.END, word)
word_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
word_listbox.bind('<<ListboxSelect>>', on_word_select)

# Main Area
main = tk.Frame(root)
main.pack(fill=tk.BOTH, expand=True)

tk.Label(main, text="Smart Thesaurus", font=('Helvetica', 28, 'bold')).pack(pady=20)

search_frame = tk.Frame(main)
search_frame.pack(pady=10)

entry = tk.Entry(search_frame, textvariable=search_var, font=('Helvetica', 16), width=40)
entry.grid(row=0, column=0, padx=5)

tk.Button(search_frame, text="Search", command=search_word, font=('Helvetica', 12)).grid(row=0, column=1, padx=5)
tk.Button(search_frame, text="🎤 Speak", command=threaded_listen, font=('Helvetica', 12)).grid(row=0, column=2, padx=5)

result_text = scrolledtext.ScrolledText(main, font=('Helvetica', 14), wrap=tk.WORD, height=20)
result_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
result_text.config(state='disabled')

tk.Button(main, text="Exit", command=exit_app, font=('Helvetica', 12), bg='red', fg='white').pack(pady=10)

root.mainloop()
