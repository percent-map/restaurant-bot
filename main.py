import dotenv
import os

dotenv.load_dotenv()
import asyncio
import streamlit as st

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

st.set_page_config(
    page_title="레스토랑 봇",
    page_icon="🍽️",
    layout="centered",
)

AGENT_INFO = {
    "안내 에이전트":      {"emoji": "🎯", "color": "#4CAF50"},
    "메뉴 안내 에이전트": {"emoji": "🍽️", "color": "#2196F3"},
    "예약 에이전트":      {"emoji": "📅", "color": "#9C27B0"},
    "주문 에이전트":      {"emoji": "🛒", "color": "#FF9800"},
    "불만 처리 에이전트": {"emoji": "💬", "color": "#F44336"},
}

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


def agent_badge(agent_name: str):
    info = AGENT_INFO.get(agent_name, {"emoji": "🤖", "color": "#607D8B"})
    st.markdown(
        f"""<div style="
            display:inline-block;
            background:{info['color']}22;
            border-left:3px solid {info['color']};
            padding:3px 10px;
            border-radius:4px;
            font-size:0.82em;
            color:{info['color']};
            font-weight:600;
            margin-bottom:6px;
        ">{info['emoji']} {agent_name}</div>""",
        unsafe_allow_html=True,
    )


def current_agent_bar():
    name = st.session_state["agent"].name
    info = AGENT_INFO.get(name, {"emoji": "🤖", "color": "#607D8B"})
    st.markdown(
        f"""<div style="
            background:{info['color']}11;
            border:1px solid {info['color']}44;
            border-radius:8px;
            padding:7px 16px;
            margin-bottom:12px;
            font-size:0.88em;
        ">현재 담당 &nbsp;|&nbsp; <strong>{info['emoji']} {name}</strong></div>""",
        unsafe_allow_html=True,
    )


# ── 헤더 ──────────────────────────────────────────────
st.title("🍽️ 레스토랑 봇")
st.caption("메뉴 확인 · 예약 · 주문 · 불만 처리를 도와드립니다.")
current_agent_bar()


# ── 대화 히스토리 출력 ────────────────────────────────
async def paint_history():
    messages = await session.get_items()
    for message in messages:
        if "role" in message:
            with st.chat_message(message["role"]):
                if message["role"] == "user":
                    st.write(message["content"])
                elif message["type"] == "message":
                    st.write(message["content"][0]["text"].replace("$", r"\$"))


asyncio.run(paint_history())


# ── 에이전트 실행 ─────────────────────────────────────
async def run_agent(message):
    with st.chat_message("ai"):
        agent_badge(st.session_state["agent"].name)
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
                        text_placeholder.write(response.replace("$", r"\$"))

                elif event.type == "agent_updated_stream_event":
                    if st.session_state["agent"].name != event.new_agent.name:
                        new_name = event.new_agent.name
                        new_info = AGENT_INFO.get(new_name, {"emoji": "🤖", "color": "#607D8B"})
                        st.markdown(
                            f"""<div style="
                                text-align:center;
                                color:#888;
                                font-size:0.82em;
                                padding:6px 0;
                                border-top:1px dashed #ddd;
                                border-bottom:1px dashed #ddd;
                                margin:8px 0;
                            ">{new_info['emoji']} <strong>{new_name}</strong>으로 연결됩니다</div>""",
                            unsafe_allow_html=True,
                        )
                        st.session_state["agent"] = event.new_agent
                        agent_badge(new_name)
                        text_placeholder = st.empty()
                        st.session_state["text_placeholder"] = text_placeholder
                        response = ""

        except InputGuardrailTripwireTriggered:
            st.markdown(
                """<div style="
                    background:#FFF3E0;
                    border-left:3px solid #FF9800;
                    padding:6px 12px;
                    border-radius:4px;
                    font-size:0.82em;
                    color:#E65100;
                    margin-bottom:6px;
                ">[input guardrail 작동]</div>""",
                unsafe_allow_html=True,
            )
            st.write(
                "저는 레스토랑 관련 질문에 대해서만 도와드리고 있어요. "
                "메뉴를 확인하거나, 예약하거나, 음식을 주문할 수 있어요."
            )

        except OutputGuardrailTripwireTriggered:
            st.markdown(
                """<div style="
                    background:#FFEBEE;
                    border-left:3px solid #F44336;
                    padding:6px 12px;
                    border-radius:4px;
                    font-size:0.82em;
                    color:#B71C1C;
                    margin-bottom:6px;
                ">[output guardrail 작동]</div>""",
                unsafe_allow_html=True,
            )
            st.write("죄송합니다. 응답 처리 중 문제가 발생했습니다. 다시 시도해 주세요.")
            st.session_state["text_placeholder"].empty()


# ── 입력창 ────────────────────────────────────────────
message = st.chat_input("레스토랑 관련 문의 사항을 입력해 주세요")

if message:
    with st.chat_message("human"):
        st.write(message)
    asyncio.run(run_agent(message))


# ── 사이드바 ──────────────────────────────────────────
with st.sidebar:
    st.title("🍽️ 레스토랑 봇")
    st.divider()

    st.markdown("**현재 담당 에이전트**")
    name = st.session_state["agent"].name
    info = AGENT_INFO.get(name, {"emoji": "🤖", "color": "#607D8B"})
    st.markdown(f"{info['emoji']} **{name}**")

    st.divider()
    st.markdown("**에이전트 안내**")
    for n, i in AGENT_INFO.items():
        st.markdown(f"{i['emoji']} {n}")

    st.divider()
    if st.button("대화 초기화", use_container_width=True):
        asyncio.run(session.clear_session())
        st.session_state["agent"] = triage_agent
        st.rerun()
