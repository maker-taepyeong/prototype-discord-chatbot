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