import os
import sys
from pathlib import Path
from groq import Groq
from dotenv import load_dotenv


def create_groq_client() -> Groq:
    """
    Create and return a Groq client instance.

    Returns:
        Groq client instance

    Raises:
        ValueError: If GROQ_API_KEY is not found in environment variables
    """
    # Load environment variables from .env file
    load_dotenv()

    # Get API key from environment
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found in environment variables. Please set it in .env file.")

    # Initialize and return Groq client
    return Groq(api_key=api_key)


def main():
    """
    Main function to run the speech-to-text transcription.
    """
    if len(sys.argv) < 2:
        print("Usage: python speechToText.py <audio_file_path>")
        print("Example: python speechToText.py audio.mp3")
        sys.exit(1)

    audio_file_path = sys.argv[1]

    try:
        # Create Groq client
        client = create_groq_client()

        # Check if audio file exists
        if not os.path.exists(audio_file_path):
            raise FileNotFoundError(f"Audio file not found: {audio_file_path}")

        print(f"Transcribing audio file: {audio_file_path}")

        # Open and transcribe the audio file
        with open(audio_file_path, "rb") as file:
            transcription = client.audio.transcriptions.create(
                file=(audio_file_path, file.read()),
                model="whisper-large-v3-turbo",
                response_format="verbose_json",
                language="en",  # Change this if needed
                temperature=0.0
            )

        # Extract the transcribed text
        transcribed_text = transcription.text

        # Create result directory if it doesn't exist
        output_file = "result/result.txt"
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Save transcription to file
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(transcribed_text)

        print(f"Transcription saved to: {output_file}")
        print(f"\nTranscribed text:\n{transcribed_text}")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
