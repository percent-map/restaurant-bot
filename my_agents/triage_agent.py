import streamlit as st
from agents import (
    Agent,
    RunContextWrapper,
    input_guardrail,
    Runner,
    GuardrailFunctionOutput,
    handoff,
)
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX
from agents.extensions import handoff_filters
from models import RestaurantContext, InputGuardRailOutput, HandoffData
from my_agents.menu_agent import menu_agent
from my_agents.reservation_agent import reservation_agent
from my_agents.order_agent import order_agent
from my_agents.complaints_agent import complaints_agent


input_guardrail_agent = Agent(
    name="Input Guardrail Agent",
    instructions="""
    고객의 메시지가 레스토랑과 관련된 내용인지 확인하세요.

    허용되는 주제:
    - 메뉴 문의 (음식, 음료, 가격, 재료, 알레르기)
    - 예약 관련 (예약 접수, 확인, 취소)
    - 음식 주문 (주문 접수, 확인, 수정)
    - 불만 및 피드백 (음식 품질, 서비스, 환경)
    - 일반적인 인사말 또는 간단한 대화

    거부해야 하는 주제:
    - 레스토랑과 전혀 관련 없는 질문 (정치, 뉴스, 날씨, 개인 상담, 투자 등)
    - 부적절하거나 불쾌한 언어 사용
    - 다른 업체나 서비스에 대한 문의

    레스토랑과 관련 없는 내용이면 is_off_topic을 true로, 이유를 reason에 작성하세요.
    자연스러운 인사말이나 가벼운 대화는 허용하세요.
""",
    output_type=InputGuardRailOutput,
)


@input_guardrail
async def off_topic_guardrail(
    wrapper: RunContextWrapper[RestaurantContext],
    agent: Agent[RestaurantContext],
    input: str,
):
    result = await Runner.run(
        input_guardrail_agent,
        input,
        context=wrapper.context,
    )

    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=result.final_output.is_off_topic,
    )


def dynamic_triage_agent_instructions(
    wrapper: RunContextWrapper[RestaurantContext],
    agent: Agent[RestaurantContext],
):
    return f"""
    {RECOMMENDED_PROMPT_PREFIX}

    안녕하세요! 저는 레스토랑 안내 직원입니다.
    고객님의 성함은 {wrapper.context.name}님이시군요, 반갑습니다!

    저는 고객님의 요청을 파악하여 적절한 담당 직원에게 연결해 드립니다.

    담당 직원 분류:

    🍽️ 메뉴 안내 에이전트 - 다음과 같은 경우 연결:
    - 메뉴 종류나 가격 문의
    - 음식 재료, 알레르기 정보
    - 추천 메뉴 요청
    - "뭐가 맛있어요?", "가격이 얼마예요?", "채식 메뉴 있나요?"

    📅 예약 에이전트 - 다음과 같은 경우 연결:
    - 테이블 예약 요청
    - 예약 확인 또는 취소
    - "예약하고 싶어요", "예약 확인해 주세요", "예약 취소하고 싶어요"

    🛒 주문 에이전트 - 다음과 같은 경우 연결:
    - 음식 주문
    - 주문 현황 확인
    - 주문 수정 요청
    - "주문하고 싶어요", "내 주문 어떻게 됐어요?", "주문 바꾸고 싶어요"

    😔 불만 처리 에이전트 - 다음과 같은 경우 연결:
    - 음식 품질 불만
    - 서비스 불만
    - 환경(청결도, 소음 등) 불만
    - "별로였어요", "불친절해요", "음식에 이물질이 있어요", "환불 원해요"

    연결 전에 고객님께 어떤 담당자에게 연결되는지 간략히 안내해 주세요.
    """


def handle_handoff(
    wrapper: RunContextWrapper[RestaurantContext],
    input_data: HandoffData,
):
    with st.sidebar:
        st.write(
            f"""
            Handing off to {input_data.to_agent_name}
            Reason: {input_data.reason}
            Issue Type: {input_data.issue_type}
            Description: {input_data.issue_description}
        """
        )


def make_handoff(agent):
    return handoff(
        agent=agent,
        on_handoff=handle_handoff,
        input_type=HandoffData,
        input_filter=handoff_filters.remove_all_tools,
    )


triage_agent = Agent(
    name="안내 에이전트",
    instructions=dynamic_triage_agent_instructions,
    input_guardrails=[
        off_topic_guardrail,
    ],
    handoffs=[
        make_handoff(menu_agent),
        make_handoff(reservation_agent),
        make_handoff(order_agent),
        make_handoff(complaints_agent),
    ],
)
