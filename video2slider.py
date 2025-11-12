import json
from pathlib import Path
from typing import Callable, Optional
from llm import create_litellm_client, summarize_transcript

# 기본 해시 폴더 (main 인자가 없을 때 사용)
DEFAULT_HASH_FOLDER = "9ba432c126"


def read_result_json(hash_folder: str) -> dict:
    """result/{hash_folder}/result.json 파일을 읽어서 딕셔너리로 반환합니다."""
    file_path: Path = Path("result") / hash_folder / "result.json"
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)



def main(hash_folder: Optional[str] = None) -> None:
    # 0. hash_folder가 없으면 기본값 사용
    if hash_folder is None:
        hash_folder = DEFAULT_HASH_FOLDER
        print(f"hash_folder가 지정되지 않아 기본값 사용: {hash_folder}")

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
    output_dir: Path = Path("result") / hash_folder
    summary_output_file: Path = output_dir / "result_summary.json"
    with open(summary_output_file, "w", encoding="utf-8") as f:
        json.dump({
            "duration": result_data.get("duration"),
            "segments": summarized_segments
        }, f, ensure_ascii=False, indent=2)
    print(f"\n요약된 JSON 저장 완료: {summary_output_file}")
    print(f"총 {len(summarized_segments)}개의 요약된 segments가 저장되었습니다.")


if __name__ == "__main__":
    main()
