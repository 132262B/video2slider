import os
import tempfile
from pathlib import Path
from groq import Groq
from dotenv import load_dotenv
import gdown
from moviepy import VideoFileClip

GOOGLE_DRIVE_URL = "https://drive.google.com/file/d/1GmJeV25_6yZJL0UA6nBHMyaeULbCZMj1/view?usp=drive_link"

def download_from_gdrive(gdrive_url: str) -> bytes:
    print(f"Google Drive에서 파일 다운로드 중...")

    with tempfile.TemporaryDirectory() as temp_dir:
        output_path = os.path.join(temp_dir, "downloaded_video.mp4")

        output_file = gdown.download(gdrive_url, output=output_path, fuzzy=True)

        if not output_file:
            raise Exception("Google Drive에서 파일 다운로드 실패")

        with open(output_file, "rb") as f:
            file_bytes = f.read()

        print(f"파일 다운로드 완료: {len(file_bytes)} bytes")
        return file_bytes


def convert_mp4_to_mp3(video_bytes: bytes) -> bytes:
    print(f"비디오를 MP3로 변환 중...")

    with tempfile.TemporaryDirectory() as temp_dir:
        input_path = os.path.join(temp_dir, "input.mp4")
        output_path = os.path.join(temp_dir, "output.mp3")

        with open(input_path, "wb") as f:
            f.write(video_bytes)

        video = VideoFileClip(input_path)
        video.audio.write_audiofile(
            output_path,
            ffmpeg_params=["-ac", "1", "-ar", "16000", "-b:a", "96k"]
        )
        video.close()

        with open(output_path, "rb") as f:
            audio_bytes = f.read()

        print(f"변환 완료: {len(audio_bytes)} bytes")
        return audio_bytes


def create_groq_client() -> Groq:
    load_dotenv()

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY가 환경 변수에 없습니다. .env 파일에 설정해주세요.")

    return Groq(api_key=api_key)


def transcribe_audio(client: Groq, audio_bytes: bytes) -> str:
    print(f"오디오 전사 중...")

    # 바이트를 사용하여 오디오 전사 (파일명은 API에서 필요하지만 임의의 값이 가능)
    transcription = client.audio.transcriptions.create(
        file=("audio.mp3", audio_bytes),
        prompt="한국어를 기본으로 분석하되 한국어로 적지 않아도 되는 영어 단어는 영어로 표현해주세요.",
        model="whisper-large-v3-turbo",
        response_format="verbose_json",
        language="ko",  # 필요시 변경
        temperature=0.0
    )

    # 전사된 텍스트 추출
    transcribed_text = transcription.text
    print("전사 완료")

    return transcribed_text


def main():
    try:
        # 1. Google Drive에서 파일을 바이트로 다운로드
        video_bytes = download_from_gdrive(GOOGLE_DRIVE_URL)

        # 2. MP4를 MP3로 변환하고 오디오 바이트 가져오기
        audio_bytes = convert_mp4_to_mp3(video_bytes)

        # 3. Groq 클라이언트 생성
        client = create_groq_client()

        # 4. Groq를 사용하여 오디오 전사
        transcribed_text = transcribe_audio(client, audio_bytes)

        # 5. 전사 결과를 result.txt에 저장
        output_file = "result/result.txt"
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(transcribed_text)

        print(f"\n전사 결과 저장 완료: {output_file}")
        print(f"\n전사된 텍스트:\n{transcribed_text}")

    except Exception as e:
        print(f"오류: {e}")
        import sys
        sys.exit(1)


if __name__ == "__main__":
    main()
