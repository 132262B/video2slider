def extract_json_from_response(content: str) -> str:
    """
    LLM 응답에서 JSON 코드 블록을 제거하고 순수 JSON 문자열만 추출합니다.

    Args:
        content: LLM 응답 문자열 (```json ... ``` 형태일 수 있음)

    Returns:
        정제된 JSON 문자열
    """
    content = content.strip()

    # JSON 코드 블록 제거 (```json ... ``` 또는 ``` ... ``` 형태)
    if content.startswith("```json"):
        lines = content.split("\n")
        lines = lines[1:]  # 첫 줄 제거 (```json)
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]  # 마지막 줄 제거 (```)
        content = "\n".join(lines)
    elif content.startswith("```"):
        lines = content.split("\n")
        lines = lines[1:]  # 첫 줄 제거 (```)
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]  # 마지막 줄 제거 (```)
        content = "\n".join(lines)

    return content.strip()
