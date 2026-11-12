"""
Comprehensive test suite for the analyze endpoint.
Tests: positive, negative, Tanglish, negation, gibberish, emoji, questions, etc.
"""

import urllib.request
import json
import sys

API = 'http://localhost:8000/api/v1/analyze'

def run_case(text, expected_label, description=""):
    try:
        req = urllib.request.Request(
            API,
            data=json.dumps({'session_id': 'test', 'text': text}).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        res = urllib.request.urlopen(req)
        data = json.loads(res.read().decode('utf-8'))
        actual = data.get('predicted_class', 'ERROR')
        conf = data.get('confidence', 0)
        status = data.get('status', 'ok')
        
        # Allow status-based responses
        if status != 'ok' and expected_label == 'Out-of-scope':
            actual = 'Out-of-scope'
        
        ok = actual == expected_label
        mark = "✓" if ok else "✗"
        print(f"  {mark} [{actual:12s} conf={conf:3d}%] expected={expected_label:12s} | {description or text[:50]}")
        return ok
    except Exception as e:
        print(f"  ✗ ERROR: {e} | {description or text[:50]}")
        return False

def main():
    passed = 0
    total = 0
    
    print("\n═══ POSITIVE / NORMAL ═══")
    cases = [
        ("I am happy", "Normal", "English positive"),
        ("I feel great today", "Normal", "English positive"),
        ("I am fine", "Normal", "English fine"),
        ("life is good", "Normal", "English positive"),
        ("I love my family", "Normal", "English positive"),
        ("today was wonderful", "Normal", "English positive"),
        ("jolly aa iruken", "Normal", "Tanglish: I am happy"),
        ("nalla iruken", "Normal", "Tanglish: I am fine"),
        ("santhosam aa iruken", "Normal", "Tanglish: I am happy"),
        ("romba happy", "Normal", "Tanglish: very happy"),
        ("super aa iruken", "Normal", "Tanglish: I am great"),
        ("nimmathi aa iruken", "Normal", "Tanglish: I am peaceful"),
    ]
    for text, label, desc in cases:
        total += 1
        if run_case(text, label, desc): passed += 1

    print("\n═══ NEGATED SEVERE → SHOULD BE NORMAL/MILD ═══")
    cases = [
        ("yennaku saga virupam illa", "Normal", "Tanglish: I don't want to die"),
        ("I do not want to die", "Normal", "English: negated death"),
        ("I don't want to kill myself", "Normal", "English: negated suicide"),
        ("suicide panna mattan", "Normal", "Tanglish: I won't commit suicide"),
        ("saaga maatten", "Normal", "Tanglish: I will not die"),
        ("I never want to die", "Normal", "English: never die"),
        ("I am not suicidal", "Normal", "English: negated suicidal"),
    ]
    for text, label, desc in cases:
        total += 1
        if run_case(text, label, desc): passed += 1

    print("\n═══ MILD ═══")
    cases = [
        ("I feel a bit stressed", "Mild", "English mild stress"),
        ("I am tired today", "Mild", "English tired"),
        ("I feel low", "Mild", "English low"),
        ("konjam kavalai aa iruku", "Mild", "Tanglish: a little worried"),
        ("I am nervous about exams", "Mild", "English nervous"),
    ]
    for text, label, desc in cases:
        total += 1
        if run_case(text, label, desc): passed += 1

    print("\n═══ MODERATE ═══")
    cases = [
        ("I feel very sad and hopeless", "Moderate", "English moderate"),
        ("I feel like a burden to everyone", "Moderate", "English burden"),
        ("everything is falling apart", "Moderate", "English despair"),
        ("I cry every day", "Moderate", "English crying"),
        ("I feel worthless", "Moderate", "English worthless"),
    ]
    for text, label, desc in cases:
        total += 1
        if run_case(text, label, desc): passed += 1

    print("\n═══ SEVERE (TRUE CRISIS) ═══")
    cases = [
        ("I want to kill myself", "Severe", "English explicit suicide"),
        ("sagalam pola iruku", "Severe", "Tanglish: I feel like dying"),
        ("I want to end my life", "Severe", "English end life"),
    ]
    for text, label, desc in cases:
        total += 1
        if run_case(text, label, desc): passed += 1

    print("\n═══ OUT-OF-SCOPE ═══")
    cases = [
        ("", "Out-of-scope", "Empty input"),
        ("😀😊🎉", "Out-of-scope", "Emoji only"),
        ("xkqzw plmn brtv", "Out-of-scope", "Gibberish"),
    ]
    for text, label, desc in cases:
        total += 1
        if run_case(text, label, desc): passed += 1

    print(f"\n{'═'*60}")
    print(f"RESULTS: {passed}/{total} passed ({passed/total*100:.0f}%)")
    if passed == total:
        print("🎉 ALL TESTS PASSED!")
    else:
        print(f"⚠️  {total - passed} tests failed")
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())
