
import subprocess
import webbrowser

APP_COMMANDS = {
    "notepad": ["notepad.exe"],
    "calculator": ["calc.exe"],
    "paint": ["mspaint.exe"],
    "chrome": ["cmd", "/c", "start", "", "chrome"],
    "opera": ["cmd", "/c", "start", "", "opera"],
    "settings": ["cmd", "/c", "start", "", "ms-settings:"],
}

PROCESS_NAMES = {
    "notepad": "notepad.exe",
    "calculator": "CalculatorApp.exe",
    "paint": "mspaint.exe",
    "chrome": "chrome.exe",
    "opera": "opera.exe",
}

def open_application(app_name):
    app_name = app_name.lower().strip()

    if app_name == "whatsapp":
        webbrowser.open("https://web.whatsapp.com")
        return "Opening WhatsApp Web."

    if app_name in APP_COMMANDS:
        try:
            subprocess.Popen(APP_COMMANDS[app_name])
            return f"Opening {app_name}."
        except Exception as error:
            return f"Could not open {app_name}: {error}"

    return f"I don't know how to open {app_name} yet."


def close_application(app_name):
    app_name = app_name.lower().strip()

    if app_name not in PROCESS_NAMES:
        return f"I cannot close {app_name}. It is not in my allowed application list."

    process = PROCESS_NAMES[app_name]

    try:
        result = subprocess.run(
            ["taskkill", "/IM", process, "/T", "/F"],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            return f"Closed {app_name}."

        return f"{app_name} is not running or could not be closed."

    except Exception as error:
        return f"Could not close {app_name}: {error}"
