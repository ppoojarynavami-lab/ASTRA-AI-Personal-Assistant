
import os
import json
import re

from pathlib import Path
from dotenv import load_dotenv
from google import genai

from modules.voice import (
    speak,
    listen_for_wake_word,
    listen_for_command
)

from modules.app_control import (
    open_application,
    close_application
)

from modules.device_control import (
    change_volume,
    change_brightness
)


# ==========================================
# LOAD GEMINI API KEY
# ==========================================

PROJECT_FOLDER = Path(__file__).resolve().parent.parent

load_dotenv(PROJECT_FOLDER / ".env", override=True)

API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

if not API_KEY:
    raise ValueError(
        "GEMINI_API_KEY is missing. Check your .env file."
    )

client = genai.Client(api_key=API_KEY)

MODEL_NAME = "gemini-3.5-flash-lite"


# ==========================================
# ALLOWED APPLICATIONS
# ==========================================

ALLOWED_APPS = {
    "notepad",
    "calculator",
    "paint",
    "chrome",
    "opera",
    "whatsapp",
    "settings"
}

ALLOWED_CLOSE_APPS = {
    "notepad",
    "calculator",
    "paint",
    "chrome",
    "opera"
}


# ==========================================
# UNDERSTAND USER REQUEST USING GEMINI
# ==========================================

def understand_request(user_text):

    prompt = f"""
You are ASTRA, a Windows personal assistant.

Understand the user's request and return ONLY valid JSON.

Choose one of these actions:

1. Open application:
{{
    "action": "open_application",
    "app": "chrome"
}}

2. Close application:
{{
    "action": "close_application",
    "app": "chrome"
}}

3. Control volume:
{{
    "action": "volume_control",
    "operation": "increase",
    "amount": 10
}}

Allowed volume operations:
increase, decrease, set, mute, unmute.

4. Control brightness:
{{
    "action": "brightness_control",
    "operation": "increase",
    "amount": 10
}}

Allowed brightness operations:
increase, decrease, set.

5. General conversation:
{{
    "action": "chat",
    "reply": "Your answer here"
}}

Rules:

- Opening applications is allowed for:
  notepad, calculator, paint, chrome, opera, whatsapp, settings.

- Closing applications is allowed for:
  notepad, calculator, paint, chrome, opera.

- For increase volume, use increase.
- For reduce/lower/decrease volume, use decrease.
- For mute volume, use mute.
- For unmute volume, use unmute.
- For a requested volume percentage, use set and that percentage.
- For increase brightness, use increase.
- For reduce brightness, use decrease.
- For a requested brightness percentage, use set and that percentage.
- Default increase/decrease amount is 10.
- Amount must be a number between 0 and 100.
- Never generate shell commands or Python code.
- Never invent application names.
- Do not claim an action has already happened.
- Return JSON only, without Markdown.

User request: {user_text}
"""

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )

        result = response.text.strip()

        result = re.sub(
            r"^```(?:json)?\s*",
            "",
            result
        )

        result = re.sub(
            r"\s*```$",
            "",
            result
        )

        data = json.loads(result)

        if not isinstance(data, dict):
            raise ValueError("Invalid Gemini response.")

        return data

    except Exception as error:

        print("Gemini error:", error)

        return {
            "action": "chat",
            "reply": (
                "Sorry, I could not understand your request. "
                "Please try again."
            )
        }


# ==========================================
# CONFIRMATION BEFORE CLOSING APPLICATION
# ==========================================

def confirm_closing(app_name):

    speak(
        f"Do you want me to close {app_name}? "
        "Please say yes close or cancel closing."
    )

    for attempt in range(3):

        print("\nWaiting for your confirmation...")

        confirmation = listen_for_command()

        if not confirmation:
            speak("I could not hear you. Please try again.")
            continue

        confirmation = confirmation.lower().strip()

        print("Confirmation:", confirmation)

        cancel_phrases = [
            "cancel",
            "cancel closing",
            "do not close",
            "don't close",
            "dont close",
            "keep it open",
            "leave it open",
            "no",
            "nahi",
            "nahin"
        ]

        if any(
            phrase in confirmation
            for phrase in cancel_phrases
        ):
            return f"Okay. {app_name} will remain open."

        confirm_phrases = [
            "confirm close",
            "confirm closing",
            "yes close",
            "close it",
            "go ahead",
            "please close",
            "yes",
            "haan",
            "haan ji"
        ]

        if any(
            phrase in confirmation
            for phrase in confirm_phrases
        ):
            return close_application(app_name)

        speak(
            "Please say yes close or cancel closing."
        )

    return (
        f"Confirmation not received. "
        f"{app_name} will remain open."
    )


# ==========================================
# PROCESS USER REQUEST
# ==========================================

def process_request(user_text):

    if not user_text:
        speak("Please tell me what you want me to do.")
        return

    print("\nProcessing:", user_text)

    result = understand_request(user_text)

    action = result.get("action", "chat")

    # --------------------------------------
    # OPEN APPLICATION
    # --------------------------------------

    if action == "open_application":

        app_name = str(
            result.get("app", "")
        ).lower().strip()

        if app_name not in ALLOWED_APPS:
            speak("That application is not in my allowed list.")
            return

        message = open_application(app_name)
        speak(message)
        return

    # --------------------------------------
    # CLOSE APPLICATION
    # --------------------------------------

    elif action == "close_application":

        app_name = str(
            result.get("app", "")
        ).lower().strip()

        if app_name not in ALLOWED_CLOSE_APPS:
            speak("I cannot close that application.")
            return

        message = confirm_closing(app_name)
        speak(message)
        return

    # --------------------------------------
    # VOLUME CONTROL
    # --------------------------------------

    elif action == "volume_control":

        operation = str(
            result.get("operation", "")
        ).lower().strip()

        try:
            amount = float(result.get("amount", 10))

            if not 0 <= amount <= 100:
                raise ValueError("Amount must be between 0 and 100.")

            amount = int(amount)

        except (TypeError, ValueError):
            speak("Please specify a valid volume percentage.")
            return

        if operation not in {
            "increase",
            "decrease",
            "set",
            "mute",
            "unmute"
        }:
            speak("I could not identify the volume operation.")
            return

        message = change_volume(operation, amount)
        speak(message)
        return

    # --------------------------------------
    # BRIGHTNESS CONTROL
    # --------------------------------------

    elif action == "brightness_control":

        operation = str(
            result.get("operation", "")
        ).lower().strip()

        try:
            amount = float(result.get("amount", 10))

            if not 0 <= amount <= 100:
                raise ValueError("Amount must be between 0 and 100.")

            amount = int(amount)

        except (TypeError, ValueError):
            speak("Please specify a valid brightness percentage.")
            return

        if operation not in {
            "increase",
            "decrease",
            "set"
        }:
            speak("I could not identify the brightness operation.")
            return

        message = change_brightness(operation, amount)
        speak(message)
        return

    # --------------------------------------
    # GENERAL CONVERSATION
    # --------------------------------------

    elif action == "chat":

        reply = result.get(
            "reply",
            "I am here. How can I help you?"
        )

        speak(reply)
        return

    speak("I could not identify that action.")


# ==========================================
# MAIN VOICE ASSISTANT
# ==========================================

def voice_assistant():

    speak(
        "Hello! Astra is ready. "
        "Say Astra to activate me."
    )

    while True:

        wake_command = listen_for_wake_word()

        if wake_command is None:
            continue

        # EXIT COMMAND
        if wake_command.strip().lower() in [
            "exit",
            "quit",
            "stop",
            "shutdown"
        ]:
            speak("Goodbye! Astra is shutting down.")
            break

        # WAKE WORD ONLY
        if not wake_command:

            speak("Yes? How can I help you?")
            user_command = listen_for_command()

        else:

            # Example: Astra increase volume
            user_command = wake_command

        if not user_command:
            speak("I did not hear a command. Please try again.")
            continue

        if user_command.lower().strip() in [
            "exit",
            "quit",
            "stop",
            "shutdown"
        ]:
            speak("Goodbye! Astra is shutting down.")
            break

        process_request(user_command)


# ==========================================
# RUN ASTRA
# ==========================================

if __name__ == "__main__":

    try:
        voice_assistant()

    except KeyboardInterrupt:
        print("\nASTRA stopped by user.")

    except Exception as error:
        print("\nASTRA error:", error)
