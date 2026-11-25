
import speech_recognition as sr
import pyttsx3


# -------------------------------
# TEXT TO SPEECH
# -------------------------------

engine = pyttsx3.init()
engine.setProperty("rate", 170)
engine.setProperty("volume", 1.0)


def speak(text):
    print(f"\nASTRA: {text}")

    try:
        engine.say(text)
        engine.runAndWait()
    except Exception as error:
        print("Speech error:", error)


# -------------------------------
# SPEECH RECOGNITION
# -------------------------------

def recognize_speech(timeout=8, phrase_time_limit=8):
    recognizer = sr.Recognizer()
    recognizer.pause_threshold = 0.8
    recognizer.dynamic_energy_threshold = True

    try:
        with sr.Microphone() as source:
            print("\nListening...")
            recognizer.adjust_for_ambient_noise(source, duration=0.5)

            audio = recognizer.listen(
                source,
                timeout=timeout,
                phrase_time_limit=phrase_time_limit
            )

        text = recognizer.recognize_google(
            audio,
            language="en-IN"
        )

        text = text.strip().lower()
        print("You:", text)
        return text

    except sr.WaitTimeoutError:
        print("No speech detected.")
        return ""

    except sr.UnknownValueError:
        print("Sorry, I could not understand.")
        return ""

    except sr.RequestError as error:
        print("Speech recognition service error:", error)
        return ""

    except Exception as error:
        print("Microphone error:", error)
        return ""


# -------------------------------
# WAKE WORD DETECTION
# -------------------------------

def listen_for_wake_word():
    print("\nWaiting for 'Hey Astra' or 'Astra'...")

    text = recognize_speech(
        timeout=6,
        phrase_time_limit=6
    )

    if not text:
        return None

    words = text.split()

    # Accept "astra" only as the first word.
    # This prevents matching words such as "shastra".
    if words and words[0] == "astra":
        print("Wake word detected!")
        return " ".join(words[1:]).strip()

    # Accept "hey astra" at the beginning.
    if len(words) >= 2 and words[0] == "hey" and words[1] == "astra":
        print("Wake word detected!")
        return " ".join(words[2:]).strip()

    # Optional speech-recognition variation.
    if len(words) >= 2 and words[0] == "hey" and words[1] == "aster":
        print("Wake word detected!")
        return " ".join(words[2:]).strip()

    return None


# -------------------------------
# COMMAND LISTENING
# -------------------------------

def listen_for_command():
    return recognize_speech(
        timeout=10,
        phrase_time_limit=12
    )
