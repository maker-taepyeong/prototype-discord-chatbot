# Discord 봇 OpenAI 연동 설계 문서

## 1. 의도 (Goal)

이 문서의 목표는 현재 Discord 봇 코드(`src/prototype_discord_chatbot/main.py`)에 OpenAI의 GPT 모델을 연동하여, 사용자가 봇을 맨션(@)하고 질문을 던지면 AI가 답변을 생성하여 응답하게 만드는 것입니다.

- **사용자 경험**: 사용자는 마치 지능을 가진 상대와 대화하는 것처럼 자연스럽게 질문하고 답변을 받을 수 있습니다.
- **핵심 기능**: Discord 채널의 대화 맥락을 이해하고, 사용자의 질문에 적절한 답변을 실시간으로 제공합니다.

## 2. 핵심 설계 (Core Design)

봇의 동작 흐름은 다음과 같이 설계합니다.

1.  **사용자 호출**: 사용자가 채널에서 봇을 `@` 맨션하며 메시지를 보냅니다.
2.  **메시지 감지**: 봇은 `on_message` 이벤트를 통해 자신을 맨션한 메시지를 감지합니다.
3.  **대화 맥락 수집**: 봇은 현재 채널의 최근 대화 기록(최대 200개)을 수집하여 OpenAI에 전달할 **문맥(Context)**을 만듭니다. 이는 더 정확하고 자연스러운 답변을 생성하기 위함입니다.
4.  **OpenAI API 호출**: 수집된 대화 맥락과 사용자의 질문을 OpenAI의 채팅 API(`ChatCompletion`)에 전달하여 답변 생성을 요청합니다.
5.  **응답 수신 및 전송**: OpenAI로부터 받은 AI 응답을 Discord 채널에 메시지로 전송하여 사용자에게 보여줍니다.

## 3. 구현 상세 (Implementation Details)

### 3.1. 의존성 추가

OpenAI API를 사용하기 위해 `openai` 라이브러리를 프로젝트에 추가해야 합니다.

- `pyproject.toml` 파일의 `dependencies` 목록에 `"openai"`를 추가합니다.
- `pip install openai` 또는 `pip install -r requirements.lock` (업데이트 후) 명령으로 라이브러리를 설치합니다.

### 3.2. 환경 변수 설정

보안을 위해 OpenAI API 키를 소스 코드에 직접 넣지 않고, `.env` 파일에 환경 변수로 추가합니다.

```dotenv
# .env 파일
DISCORD_BOT_TOKEN="your_discord_bot_token"
OPENAI_API_KEY="your_openai_api_key"
```

### 3.3. `main.py` 코드 수정

기존 `main.py` 파일을 다음과 같이 수정하여 OpenAI 연동 로직을 추가합니다.

1.  **모듈 가져오기**: `openai` 모듈을 `import` 합니다.
2.  **OpenAI 클라이언트 초기화**: 스크립트 시작 부분에서 환경 변수를 이용해 OpenAI API 키를 설정합니다.
3.  **`on_message` 이벤트 핸들러 수정**:
    - 대화 기록을 OpenAI API가 요구하는 형식(`[{'role': 'user', 'content': '...'}, ...]`)으로 변환합니다.
    - `try...except` 구문을 사용하여 OpenAI API 호출 시 발생할 수 있는 오류를 처리합니다.
    - 기존의 `"test"` 응답 대신, OpenAI로부터 받은 실제 AI 응답을 전송하도록 로직을 교체합니다.

## 4. 최종 코드 구조 (예상)

아래는 위 설계를 바탕으로 완성될 `src/prototype_discord_chatbot/main.py` 파일의 전체적인 모습입니다.

```python
# src/prototype_discord_chatbot/main.py

from dotenv import load_dotenv
import os
import discord
import openai

# .env 파일에서 환경 변수 로드
load_dotenv()

# Discord 봇 토큰 및 OpenAI API 키 설정
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# OpenAI API 키 인증
openai.api_key = OPENAI_API_KEY

# Discord 봇 클라이언트 설정
intents = discord.Intents.default()
intents.message_content = True  # 메시지 내용을 읽기 위한 권한
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    """봇이 준비되었을 때 실행되는 이벤트"""
    print(f"{client.user} is ready.")

@client.event
async def on_message(message):
    """메시지가 수신되었을 때 실행되는 이벤트"""
    # 봇 자신의 메시지는 무시
    if message.author.bot:
        return

    # 봇이 맨션되었을 때만 응답
    if client.user in message.mentions:
        channel = message.channel

        try:
            # 대화 기록을 가져와 OpenAI에 전달할 형식으로 변환
            history = [msg async for msg in channel.history(limit=10)]
            history.reverse()  # 시간 순으로 정렬

            messages_for_openai = []
            for msg in history:
                # 사용자 메시지인지, 봇의 메시지인지에 따라 역할(role)을 지정
                role = "user" if msg.author != client.user else "assistant"

                # 봇 맨션 부분은 질문에서 제외
                content = msg.content.replace(f"<@{client.user.id}>", "").strip()

                if content: # 내용이 있는 메시지만 추가
                    messages_for_openai.append({"role": role, "content": content})

            # OpenAI API 호출
            response = openai.chat.completions.create(
                model="gpt-4",  # 또는 "gpt-3.5-turbo"
                messages=messages_for_openai,
            )

            # AI의 답변을 채널에 전송
            ai_response = response.choices[0].message.content
            await channel.send(ai_response)

        except Exception as e:
            print(f"An error occurred: {e}")
            await channel.send("죄송합니다. 답변을 생성하는 동안 오류가 발생했습니다.")

# 봇 실행
client.run(DISCORD_BOT_TOKEN)
```
