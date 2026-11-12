"""Patch script to add missing Tanglish severe variants to the translator."""
path = "app/services/detection/tanglish_translator.py"

with open(path, encoding="utf-8") as f:
    content = f.read()

# Check if already patched
if "saaganum pola iruku" in content:
    print("Already patched.")
else:
    # Insert new phrases right after the saagalam pola lines
    old = '("saagalam pola", "feel like dying"),\n            ("jeevikka mudiyala"'
    new = ('("saagalam pola", "feel like dying"),\n'
           '            # -- Additional phonetic variants added for accuracy --\n'
           '            ("saaganum pola iruku", "I feel like dying"),\n'
           '            ("saganum pola iruku", "I feel like dying"),\n'
           '            ("saaganum pola", "feel like dying"),\n'
           '            ("saganum pola", "feel like dying"),\n'
           '            ("sagaanum pola iruku", "I feel like dying"),\n'
           '            ("inaiku setha nalla irukum", "dying today would be good"),\n'
           '            ("setha nalla irukum", "dying would be good"),\n'
           '            ("setha irukalam", "could just die"),\n'
           '            ("setha poidalam", "could just die"),\n'
           '            ("sethu poiduven", "I will die"),\n'
           '            ("sethuralam", "I feel like dying"),\n'
           '            ("sethudalam", "let me die"),\n'
           '            ("naan saaga poren", "I am going to die"),\n'
           '            ("naan saga poren", "I am going to die"),\n'
           '            ("ellame mudichukanum", "I want to end everything"),\n'
           '            ("uyir vittuviduven", "I will end my life"),\n'
           '            ("thookku pottukkanum", "I want to hang myself"),\n'
           '            ("jeevikka mudiyala"')

    if old in content:
        content = content.replace(old, new, 1)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print("SUCCESS: All missing phrases added.")
    else:
        print("ERROR: Anchor phrase not found. Manual edit needed.")
        print("Snippet around line 68:")
        idx = content.find("saagalam pola")
        print(repr(content[idx-50:idx+200]))
