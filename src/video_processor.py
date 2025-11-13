import json
from pathlib import Path
from typing import Callable, Optional, List, Dict, Any
from moviepy import VideoFileClip
from PIL import Image
from src.llm import create_litellm_client, summarize_transcript

# 기본 해시 폴더 (main 인자가 없을 때 사용)
DEFAULT_HASH_FOLDER = "9ba432c126"

def read_result_json(hash_folder: str) -> dict:
    file_path: Path = Path("result") / hash_folder / "result.json"
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def extract_frames_from_video(
    video_path: Path,
    segments: List[Dict[str, Any]],
    output_dir: Path
) -> List[Dict[str, Any]]:
    """
    비디오에서 각 segment의 프레임을 이미지로 추출합니다.

    Args:
        video_path: 비디오 파일 경로
        segments: segment 리스트 (start, end, text 포함)
        output_dir: 이미지를 저장할 디렉토리

    Returns:
        이미지 파일명과 텍스트를 포함한 슬라이드 정보 리스트
    """
    # 이미지 저장 폴더 생성
    images_dir = output_dir / "images"
    images_dir.mkdir(exist_ok=True)

    # 비디오 로드
    video = VideoFileClip(str(video_path))

    slides: List[Dict[str, Any]] = []

    for idx, segment in enumerate(segments):
        start: float = segment["start"]
        end: float = segment["end"]
        text: str = segment["text"]

        # start와 end의 중간 지점에서 프레임 추출
        capture_time: float = (start + end) / 2.0

        # 비디오 길이를 초과하지 않도록 조정
        if capture_time > video.duration:
            capture_time = video.duration - 0.1

        # 프레임 추출
        frame = video.get_frame(capture_time)

        # 이미지 파일명 생성 (slide_0001.jpg, slide_0002.jpg, ...)
        image_filename = f"slide_{idx:04d}.jpg"
        image_path = images_dir / image_filename

        # 이미지 저장
        img = Image.fromarray(frame)
        img.save(str(image_path), quality=85)

        # 슬라이드 정보 저장
        slides.append({
            "index": idx,
            "image": f"images/{image_filename}",
            "text": text,
            "start": start,
            "end": end
        })

    video.close()

    return slides



def main(hash_folder: Optional[str] = None) -> None:
    # 0. hash_folder가 없으면 기본값 사용
    if hash_folder is None:
        hash_folder = DEFAULT_HASH_FOLDER
        print(f"hash_folder가 지정되지 않아 기본값 사용: {hash_folder}")

    output_dir: Path = Path("result") / hash_folder

    # 1. result.json 파일 읽기
    result_data: dict = read_result_json(hash_folder)
    segments: list = result_data.get("segments", [])
    print(f"총 {len(segments)}개의 transcript segments 로드됨")

    # 2. LiteLLM 클라이언트 생성
    client: Callable = create_litellm_client()

    # 3. transcript 요약 (start, end, text 유지)
    print("Transcript 요약 중...")
    summarized_segments: list = summarize_transcript(client, segments)
    print(f"요약 완료: {len(summarized_segments)}개의 segments")

    # 4. 요약된 JSON을 result_summary.json에 저장
    summary_output_file: Path = output_dir / "result_summary.json"
    with open(summary_output_file, "w", encoding="utf-8") as f:
        json.dump({
            "duration": result_data.get("duration"),
            "segments": summarized_segments
        }, f, ensure_ascii=False, indent=2)
    print(f"\n요약된 JSON 저장 완료: {summary_output_file}")
    print(f"총 {len(summarized_segments)}개의 요약된 segments가 저장되었습니다.")

    # 5. 비디오에서 프레임 추출 및 슬라이드 생성
    print("\n비디오에서 프레임 추출 중...")
    video_path: Path = output_dir / "video.mp4"
    slides: List[Dict[str, Any]] = extract_frames_from_video(
        video_path=video_path,
        segments=summarized_segments,
        output_dir=output_dir
    )
    print(f"프레임 추출 완료: {len(slides)}개의 이미지 생성됨")

    # 6. 슬라이드 정보를 slides.json에 저장
    slides_output_file: Path = output_dir / "slides.json"
    with open(slides_output_file, "w", encoding="utf-8") as f:
        json.dump({
            "total_slides": len(slides),
            "slides": slides
        }, f, ensure_ascii=False, indent=2)
    print(f"슬라이드 정보 저장 완료: {slides_output_file}")
    print(f"이미지 저장 경로: {output_dir / 'images'}")


if __name__ == "__main__":
    main()
