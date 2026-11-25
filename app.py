
from modules.ai_brain import voice_assistant


if __name__ == "__main__":
    try:
        voice_assistant()

    except KeyboardInterrupt:
        print("\nASTRA stopped by user.")

    except Exception as error:
        print("\nASTRA error:", error)
