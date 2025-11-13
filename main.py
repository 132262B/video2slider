import sys
from typing import Optional
from src.speech_to_text import main as speech_to_text_main
from src.video_processor import main as video_processor_main

def main() -> None:
    hash_folder: str = speech_to_text_main()
    video_processor_main(hash_folder)


if __name__ == "__main__":
    main()
