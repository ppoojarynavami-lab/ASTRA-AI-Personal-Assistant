
import screen_brightness_control as sbc
from pycaw.pycaw import AudioUtilities


# -------------------------------
# AUDIO CONTROL
# -------------------------------

def get_audio_controller():
    devices = AudioUtilities.GetSpeakers()
    return devices.EndpointVolume


def change_volume(action, amount=10):
    try:
        audio = get_audio_controller()
        current = audio.GetMasterVolumeLevelScalar()

        if action == "increase":
            new_volume = min(1.0, current + amount / 100)

        elif action == "decrease":
            new_volume = max(0.0, current - amount / 100)

        elif action == "set":
            new_volume = max(0.0, min(1.0, amount / 100))

        elif action == "mute":
            audio.SetMute(1, None)
            return "Volume muted."

        elif action == "unmute":
            audio.SetMute(0, None)
            return "Volume unmuted."

        else:
            return "Unknown volume command."

        audio.SetMasterVolumeLevelScalar(new_volume, None)

        return f"Volume set to {round(new_volume * 100)} percent."

    except Exception as error:
        return f"Volume error: {error}"


# -------------------------------
# BRIGHTNESS CONTROL
# -------------------------------

def change_brightness(action, amount=10):
    try:
        current = sbc.get_brightness()

        if isinstance(current, list):
            current = current[0]

        current = int(current)

        if action == "increase":
            new_brightness = min(100, current + amount)

        elif action == "decrease":
            new_brightness = max(0, current - amount)

        elif action == "set":
            new_brightness = max(0, min(100, amount))

        else:
            return "Unknown brightness command."

        sbc.set_brightness(new_brightness)

        return f"Brightness set to {new_brightness} percent."

    except Exception as error:
        return f"Brightness error: {error}"
