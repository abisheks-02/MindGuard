import csv
import random

# Framework definitions
# Normal (Baseline): Everyday talk, no distress
# Mild: General stress, tiredness, mild sadness
# Moderate: Hopelessness, feeling trapped, intense emotional pain but no self-harm
# Severe/Crisis: Explicit self-harm, suicidal ideation, finality

def get_ratio(text):
    # Rough approximation of Tamil% vs English% based on word lists
    english_keywords = ["feel", "very", "sad", "tired", "today", "hope", "future", "die", "life", "meaningless", "pain", "stress", "work", "hate", "myself", "nothing", "everything", "end"]
    words = text.lower().split()
    if not words: return 0, 0
    eng_count = sum(1 for w in words if any(ek in w for ek in english_keywords))
    eng_pct = int((eng_count / len(words)) * 100)
    return 100 - eng_pct, eng_pct

data = []

# --- NORMAL (50 samples) ---
normal_templates = [
    "Innaiku romba happy ah iruken", "Movie sema mass ah irunthuchu", "Nalla thookam vanthuchu", 
    "Food taste nalla iruku", "Naalai office poganum", "Friends kooda veliya poren", 
    "Vera level performance today", "Exam nalla pannen", "Nothing special, just chilling",
    "Weekend plans enna machan", "Saptiya da", "I am feeling good today", "All is well",
    "Match epo start aaguthu", "Song romba nalla iruku"
]
while len(data) < 50:
    text = random.choice(normal_templates)
    # Add slight variations to avoid exact duplicates
    text = text + random.choice(["", " da", " machan", " bro", " pa"])
    tam, eng = get_ratio(text)
    data.append((text, tam, eng, "Normal", 1.0))

# --- MILD (50 samples) ---
mild_templates = [
    "Konjam tired aa iruku", "Innaiku work romba stress", "Thala vali thaangamudiyala", 
    "Mood out aagiduchu", "Sariyana thookam illa", "I feel a bit sad today", 
    "Ennamo pola iruku", "Boring day", "Velaiku poga pidikala", 
    "Konjam upset ah iruken", "Body full pain ah iruku", "Manasu sariyilla",
    "Nothing feels right today", "Slightly depressed about the result"
]
while len(data) < 100:
    text = random.choice(mild_templates) + random.choice(["", " pa", " machan", " thala", "..."])
    tam, eng = get_ratio(text)
    data.append((text, tam, eng, "Mild", 0.9))

# --- MODERATE (50 samples) ---
moderate_templates = [
    "Life ye veruthuduchu", "Ethukum oru meaning illatha mathiri iruku", "Romba alone ah feel panren",
    "Nobody understands my pain", "Future patha bayama iruku", "Kastama iruku thaanga mudiyala",
    "Ellam thappa nadakuthu", "I am feeling very hopeless", "Enaku yaru me illa",
    "Azhanum pola iruku", "Depression la iruken", "Mind totally blocked", 
    "Narakam mathiri iruku life", "I hate myself right now", "En thevai illanu thonuthu"
]
while len(data) < 150:
    text = random.choice(moderate_templates) + random.choice(["", "...", " da", " literally"])
    tam, eng = get_ratio(text)
    data.append((text, tam, eng, "Moderate", 0.9))

# --- SEVERE/CRISIS (50 samples) ---
severe_templates = [
    "Saaganum pola iruku", "Death ku poitu vanduvaan", "Sethuralam nu thonuthu",
    "I want to end my life", "Ellame mudichukanum pola iruku", "Uyira vitudalam",
    "Inimel uyiroda iruka pidikala", "Naan saaga poren", "Setha nalla irukum",
    "Vazhkai mudinjiduchu suicide thaan", "I am going to kill myself", 
    "Thooku potukalam nu iruken", "Poison kudichidalam", "No reason to live anymore",
    "Jeevikka mudiyala", "Saagalam pola iruku", "Innaikoda ellam over"
]
while len(data) < 200:
    text = random.choice(severe_templates) + random.choice(["", "...", " machan", " bye", " permanently"])
    tam, eng = get_ratio(text)
    data.append((text, tam, eng, "Severe", 0.95))

# Write to CSV
with open("c:/Projects/MindGuard/backend/data/tanglish_eval_dataset.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Text", "Tamil%", "English%", "Severity_Label", "Confidence"])
    for row in data:
        writer.writerow(row)

print("Created tanglish_eval_dataset.csv with 200 phrases.")
