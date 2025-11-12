import os
import tempfile
from pathlib import Path
from groq import Groq
from dotenv import load_dotenv
import gdown
from moviepy import VideoFileClip
import json
from typing import Dict, Any

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


def transcribe_audio(client: Groq, audio_bytes: bytes) -> Dict[str, Any]:
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

    # transcription 객체를 딕셔너리로 변환 (Pydantic 모델)
    if hasattr(transcription, 'model_dump'):
        result_dict = transcription.model_dump()
    elif hasattr(transcription, 'dict'):
        result_dict = transcription.dict()
    else:
        # 직접 속성 접근으로 변환
        result_dict = {
            # "text": transcription.text,
            "duration": transcription.duration,
            "segments": transcription.segments
        }

    # 최상위 레벨에서 불필요한 필드 제거
    top_level_fields_to_remove = ["text", "task", "language"]
    for field in top_level_fields_to_remove:
        if field in result_dict:
            del result_dict[field]

    # segments에서 불필요한 필드 제거
    segment_fields_to_remove = ["tokens", "temperature", "avg_logprob", "compression_ratio", "no_speech_prob", "id", "seek"]
    if "segments" in result_dict and result_dict["segments"]:
        for segment in result_dict["segments"]:
            for field in segment_fields_to_remove:
                if field in segment:
                    del segment[field]

    print("전사 완료")
    return result_dict


def main() -> None:
    # 1. Google Drive에서 파일을 바이트로 다운로드
    video_bytes = download_from_gdrive(GOOGLE_DRIVE_URL)

    # 2. MP4를 MP3로 변환하고 오디오 바이트 가져오기
    audio_bytes = convert_mp4_to_mp3(video_bytes)

    # 3. Groq 클라이언트 생성
    client = create_groq_client()

    # 4. Groq를 사용하여 오디오 전사
    transcription_result = transcribe_audio(client, audio_bytes)

    # 5. 전사 결과를 result.json에 저장
    output_file = "result/result.json"
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(transcription_result, f, ensure_ascii=False, indent=2)

    print(f"\n전사 결과 저장 완료: {output_file}")


if __name__ == "__main__":
    main()
