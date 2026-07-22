import json
from typing import Any

import requests

BASE_URL = "http://127.0.0.1:8000"
CHAT_ENDPOINT = f"{BASE_URL}/rag/chat"


def ask_question(question: str, top_k: int = 4) -> dict[str, Any]:
    payload = {
        "question": question,
        "top_k": top_k,
    }

    response = requests.post(CHAT_ENDPOINT, json=payload, timeout=120)
    response.raise_for_status()

    content_type = response.headers.get("content-type", "")
    if "application/json" not in content_type.lower():
        raise ValueError(f"Expected JSON response, got: {content_type}")

    try:
        data: dict[str, Any] = response.json()
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON response: {response.text[:300]}") from exc

    return data


def main():
    print("RAG Chat CLI")
    print("Type 'exit' to quit.\n")

    while True:
        question = input("You: ").strip()

        if not question:
            continue

        if question.lower() in {"exit", "quit"}:
            print("Goodbye.")
            break

        try:
            result = ask_question(question)

            print("\nAssistant:")
            print(result.get("answer", "No answer returned."))

            print("\nTrace:")
            print(f"- model_used: {result.get('model_used')}")
            print(f"- embedding_model_used: {result.get('embedding_model_used')}")
            print(f"- retrieval_backend: {result.get('retrieval_backend')}")
            print(f"- prompt_version: {result.get('prompt_version')}")

            sources = result.get("sources", [])
            if sources:
                print("\nSources:")
                for item in sources:
                    score = float(item.get("score", 0.0))
                    print(
                        f"- rank={item.get('rank')} "
                        f"score={score:.4f} "
                        f"file={item.get('source_file')} "
                        f"chunk_id={item.get('chunk_id')}"
                    )
            print()

        except requests.HTTPError as exc:
            if exc.response is not None:
                try:
                    print("\nError:", exc.response.json())
                except Exception:
                    print("\nError:", exc.response.text)
            else:
                print("\nError: No response from server (connection failed)")
        except Exception as exc:
            print("\nUnexpected error:", str(exc))


if __name__ == "__main__":
    main()