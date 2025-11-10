import os
from functools import partial
from typing import Callable
from litellm import completion
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()

def read_result_txt() -> str:
    """result/result.txt 파일을 읽어서 텍스트를 반환합니다."""
    file_path: str = "result/result.txt"
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def create_litellm_client() -> Callable:
    """LiteLLM completion client를 생성합니다."""
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


def summarize_text(client: Callable, text: str) -> str:
    """LiteLLM completion을 이용해 텍스트를 요약하고 결과를 문자열로 반환합니다."""
    response = client(
        model="openai/solar-pro2-250909",
        messages=[
            {
                "role": "system",
                "content": """
                당신은 텍스트를 간결하게 요약하는 전문가입니다. 주요 내용을 핵심만 추려서 요약해주세요.
                
                다음 텍스트를 요약해주세요.
                """
            },
            {
                "role": "user",
                "content": f"{text}"
            }
        ]
    )
    return response.choices[0].message.content


def main() -> None:
    # 1. result.txt 파일 읽기
    text: str = read_result_txt()

    # 2. LiteLLM 클라이언트 생성
    client: Callable = create_litellm_client()

    # 3. 텍스트 요약
    summary: str = summarize_text(client, text)

    # 4. 결과 출력
    print(summary)


if __name__ == "__main__":
    main()
