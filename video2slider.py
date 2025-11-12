import os
from functools import partial
from typing import Callable
from pathlib import Path
from litellm import completion
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()

SYSTEM_PROMPT = """
당신은 텍스트를 Marp 형태의 프레젠테이션 슬라이드로 변환하는 전문가입니다.
현재 기업에 중요한 PPT를 빠르게 생성해야합니다.

요구사항:
- Frontmatter에 marp: true, paginate 등을 설정하세요.
- 내용을 논리적으로 구조화하고, 일목요연하게 정리하여 여러 슬라이드로 나누세요.
- 순수 Marp 마크다운만 반환하고, 다른 설명은 포함하지 마세요.
- 각 슬라이드는 명확한 제목과 핵심 내용을 포함해야 합니다.
- 필요한 경우 코드 블록, 리스트, 표 등을 활용하세요.
- 첫페이지는 메인 타이틀, 두번째는 목차가 꼭 들어가야해.
- 마지막에는 요약과 끝맽음이 각각 한페이지식 들어가야해.
- 이모지를 사용하지 마세요.
- 없는 내용에 대해서 임의로 작성하지 마세요.
"""


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


def remove_markdown_code_block(content: str) -> str:
    """
    마크다운 코드 블록 래퍼를 제거합니다.
    ```markdown으로 시작하고 ```로 끝나는 경우에만 제거합니다.
    """
    content = content.strip()

    # 시작이 ```markdown이고 끝이 ```인지 확인
    if content.startswith("```markdown") and content.endswith("```"):
        # 첫 줄 제거 (```markdown)
        lines: list[str] = content.split("\n")
        lines = lines[1:]  # 첫 줄 제거

        # 마지막 줄 제거 (```)
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        content = "\n".join(lines)

    return content.strip()


def convert_to_marp_slides(client: Callable, text: str) -> str:
    """LiteLLM completion을 이용해 텍스트를 Marp 형태의 슬라이드로 변환하고 결과를 문자열로 반환합니다."""
    response = client(
        model="openai/solar-pro2-250909",
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": f"다음 텍스트를 Marp 슬라이드로 변환해주세요:\n\n{text}"
            }
        ],
        max_completion_tokens=16000,
    )
    return response.choices[0].message.content


def main() -> None:
    # 1. result.txt 파일 읽기
    text: str = read_result_txt()

    # 2. LiteLLM 클라이언트 생성
    client: Callable = create_litellm_client()

    # 3. 텍스트를 Marp 슬라이드로 변환
    marp_slides: str = convert_to_marp_slides(client, text)

    # 4. 마크다운 코드 블록 래퍼 제거 (```markdown ... ``` 형태인 경우)
    marp_slides = remove_markdown_code_block(marp_slides)

    # 5. 결과를 result/result_marp.md에 저장
    output_file: str = "result/result_marp.md"
    output_path: Path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(marp_slides)

    print(f"Marp 슬라이드 생성 완료: {output_file}")
    print(f"\n생성된 슬라이드:\n{marp_slides}")


if __name__ == "__main__":
    main()
