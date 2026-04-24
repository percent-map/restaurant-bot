import dotenv
import os

dotenv.load_dotenv()
import asyncio
import streamlit as st

# Streamlit Cloud 환경에서는 st.secrets에서 API 키를 읽어옴
if "OPENAI_API_KEY" in st.secrets:
    os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
from agents import (
    Runner,
    SQLiteSession,
    InputGuardrailTripwireTriggered,
    OutputGuardrailTripwireTriggered,
)
from models import RestaurantContext
from my_agents.triage_agent import triage_agent

restaurant_ctx = RestaurantContext(
    customer_id=1,
    name="고객",
    table_number=5,
)


if "session" not in st.session_state:
    st.session_state["session"] = SQLiteSession(
        "chat-history",
        "restaurant-bot-memory.db",
    )
session = st.session_state["session"]

if "agent" not in st.session_state:
    st.session_state["agent"] = triage_agent


async def paint_history():
    messages = await session.get_items()
    for message in messages:
        if "role" in message:
            with st.chat_message(message["role"]):
                if message["role"] == "user":
                    st.write(message["content"])
                else:
                    if message["type"] == "message":
                        st.write(message["content"][0]["text"].replace("$", "\$"))


asyncio.run(paint_history())


async def run_agent(message):

    with st.chat_message("ai"):
        text_placeholder = st.empty()
        response = ""

        st.session_state["text_placeholder"] = text_placeholder

        try:

            stream = Runner.run_streamed(
                st.session_state["agent"],
                message,
                session=session,
                context=restaurant_ctx,
            )

            async for event in stream.stream_events():
                if event.type == "raw_response_event":

                    if event.data.type == "response.output_text.delta":
                        response += event.data.delta
                        text_placeholder.write(response.replace("$", "\$"))

                elif event.type == "agent_updated_stream_event":

                    if st.session_state["agent"].name != event.new_agent.name:

                        st.write(
                            f"🤖 {st.session_state['agent'].name} → {event.new_agent.name} 로 연결됩니다"
                        )

                        st.session_state["agent"] = event.new_agent

                        text_placeholder = st.empty()

                        st.session_state["text_placeholder"] = text_placeholder
                        response = ""

        except InputGuardrailTripwireTriggered:
            st.write("[input guardrail 작동]")
            st.write(
                "저는 레스토랑 관련 질문에 대해서만 도와드리고 있어요. "
                "메뉴를 확인하거나, 예약하거나, 음식을 주문할 수 있어요."
            )

        except OutputGuardrailTripwireTriggered:
            st.write("[output guardrail 작동]")
            st.write(
                "죄송합니다. 응답을 처리하는 중 문제가 발생했습니다. 다시 시도해 주세요."
            )
            st.session_state["text_placeholder"].empty()


message = st.chat_input(
    "레스토랑 관련 문의 사항을 입력해 주세요",
)

if message:

    if message:
        with st.chat_message("human"):
            st.write(message)
        asyncio.run(run_agent(message))


with st.sidebar:
    st.title("🍽️ 레스토랑 봇")
    reset = st.button("대화 초기화")
    if reset:
        asyncio.run(session.clear_session())
        st.session_state["agent"] = triage_agent
    st.divider()
    st.write(asyncio.run(session.get_items()))
