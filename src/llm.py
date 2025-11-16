import os
import json
from functools import partial
from typing import Callable, Dict, Any, List
from dotenv import load_dotenv
from litellm import completion
from utils import extract_json_from_response


def create_litellm_client() -> Callable:
    """LiteLLM completion client를 생성합니다."""
    load_dotenv()

    api_key: str | None = os.getenv("UPSTAGE_API_KEY")
    if not api_key:
        raise ValueError("UPSTAGE_API_KEY 환경 변수가 설정되지 않았습니다.")

    # api_key와 base_url이 미리 설정된 completion 함수를 반환
    client: Callable = partial(
        completion,
        api_key=api_key,
        base_url="https://api.upstage.ai/v1"
    )
    return client


def summarize_transcript(client: Callable, segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    transcript segments를 요약합니다.
    각 segment의 start, end, text를 유지하면서 text만 요약합니다.

    Args:
        client: LiteLLM completion 클라이언트
        segments: transcript segments 리스트 (start, end, text 포함)

    Returns:
        요약된 segments 리스트 (start, end, text 유지)
    """
    # segments를 텍스트로 변환
    full_text = "\n".join([
        f"[{seg['start']:.2f}s - {seg['end']:.2f}s] {seg['text']}"
        for seg in segments
    ])

    system_prompt = """
**당신은 비디오 transcript를 요약하는 전문가입니다.**
주어진 transcript의 각 segment를 분석하여, 내용의 섹션별로 일목요연 잘 정리해 주세요.

# 요구사항
- 전체 segment를 읽고 나눠진 문장을 합쳐 섹션별로 정리하여야 합니다..
- start와 end는 기존 segment를 참조해서 문장이 시작되는 부분, 문장이 끝나는 부분을 계산하여 넣어주세요.
- 원본의 의미를 왜곡하지 마세요
- JSON 형태로 반환하세요
"""

    user_prompt = f"""
다음 transcript를 정리해 주세요:

{full_text}

JSON 형태로 반환하세요:
[
  {{"start": 0.0, "end": 4.3, "text": "요약된 텍스트"}},
  ...
]
"""

    response = client(
        model="openai/solar-pro2-250909",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        max_completion_tokens=16000,
        temperature=0.3,
        reasoning_effort="high",
        allowed_openai_params=["reasoning_effort"]
    )

    # 응답에서 JSON 추출 및 파싱
    content = response.choices[0].message.content
    cleaned_content = extract_json_from_response(content)
    summarized_segments = json.loads(cleaned_content)

    return summarized_segments


