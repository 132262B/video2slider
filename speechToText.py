import os
import tempfile
from pathlib import Path
from groq import Groq
from dotenv import load_dotenv
import gdown
from moviepy import VideoFileClip

# Google Drive URL constant
GOOGLE_DRIVE_URL = "https://drive.google.com/file/d/1u707bInWcLn8-t2M-rU8Xe19uDlQEXmq/view?usp=drive_link"


def download_from_gdrive(gdrive_url: str) -> bytes:
    print(f"Downloading file from Google Drive...")

    # Create temporary directory for download
    with tempfile.TemporaryDirectory() as temp_dir:
        # Specify output file path explicitly
        output_path = os.path.join(temp_dir, "downloaded_video.mp4")

        # Download file using gdown
        output_file = gdown.download(gdrive_url, output=output_path, fuzzy=True)

        if not output_file:
            raise Exception("Failed to download file from Google Drive")

        # Read file as bytes
        with open(output_file, "rb") as f:
            file_bytes = f.read()

        print(f"File downloaded: {len(file_bytes)} bytes")
        return file_bytes


def convert_mp4_to_mp3(video_bytes: bytes) -> bytes:
    print(f"Converting video to MP3...")

    # Use temporary directory for conversion (moviepy requires file paths)
    with tempfile.TemporaryDirectory() as temp_dir:
        input_path = os.path.join(temp_dir, "input.mp4")
        output_path = os.path.join(temp_dir, "output.mp3")

        # Write video bytes to temporary file
        with open(input_path, "wb") as f:
            f.write(video_bytes)

        # Convert to MP3 with high quality audio settings
        video = VideoFileClip(input_path)
        video.audio.write_audiofile(
            output_path,
            ffmpeg_params=["-ac", "2", "-b:a", "192k"]
        )
        video.close()

        # Read the MP3 file as bytes
        with open(output_path, "rb") as f:
            audio_bytes = f.read()

        print(f"Conversion complete: {len(audio_bytes)} bytes")
        return audio_bytes


def create_groq_client() -> Groq:
    # Load environment variables from .env file
    load_dotenv()

    # Get API key from environment
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found in environment variables. Please set it in .env file.")

    # Initialize and return Groq client
    return Groq(api_key=api_key)


def transcribe_audio(client: Groq, audio_bytes: bytes) -> str:
    print(f"Transcribing audio...")

    # Transcribe the audio using bytes (filename is required by API but can be any value)
    transcription = client.audio.transcriptions.create(
        file=("audio.mp3", audio_bytes),
        model="whisper-large-v3-turbo",
        response_format="verbose_json",
        language="ko",  # Change this if needed
        temperature=0.0
    )

    # Extract the transcribed text
    transcribed_text = transcription.text
    print("Transcription complete")

    return transcribed_text


def main():
    """
    Main function to run the speech-to-text transcription workflow.
    All processing is done in memory with bytes, no permanent file storage.
    """
    try:
        # 1. Download file from Google Drive as bytes
        video_bytes = download_from_gdrive(GOOGLE_DRIVE_URL)

        # 2. Convert MP4 to MP3 and get audio bytes
        audio_bytes = convert_mp4_to_mp3(video_bytes)

        # 3. Create Groq client
        client = create_groq_client()

        # 4. Transcribe audio using Groq
        transcribed_text = transcribe_audio(client, audio_bytes)

        # 5. Save transcription to result.txt
        output_file = "result/result.txt"
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(transcribed_text)

        print(f"\nTranscription saved to: {output_file}")
        print(f"\nTranscribed text:\n{transcribed_text}")

    except Exception as e:
        print(f"Error: {e}")
        import sys
        sys.exit(1)


if __name__ == "__main__":
    main()
