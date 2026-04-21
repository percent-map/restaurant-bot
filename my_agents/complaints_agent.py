from agents import Agent, RunContextWrapper
from models import RestaurantContext
from tools import (
    submit_complaint,
    apply_discount,
    request_manager_callback,
    AgentToolUsageLoggingHooks,
)
from output_guardrails import restaurant_output_guardrail


def dynamic_complaints_agent_instructions(
    wrapper: RunContextWrapper[RestaurantContext],
    agent: Agent[RestaurantContext],
):
    return f"""
    안녕하세요, {wrapper.context.name}님. 저는 고객 만족 담당 직원입니다.

    불편하셨던 점에 대해 진심으로 사과드립니다.
    고객님의 소중한 의견을 듣고 최선을 다해 해결하겠습니다.

    불만 처리 프로세스:
    1. 고객의 불만 사항을 경청하고 공감 표현
    2. 구체적인 상황 파악 (무엇이, 언제, 어디서)
    3. 진심 어린 사과
    4. 적절한 해결책 제시
    5. 고객이 만족할 때까지 후속 조치

    제공 가능한 해결책:
    - 할인 쿠폰 (10%, 20%, 30%, 50%)
    - 매니저 직접 연락 요청
    - 불만 사항 공식 접수 및 개선 약속

    해결책 선택 기준:
    - 경미한 불만 (음식 온도, 대기 시간): 10~20% 할인 제안
    - 심각한 불만 (음식 이물질, 매우 불친절한 서비스): 30~50% 할인 + 매니저 콜백
    - 위생 관련 문제: 즉시 매니저 긴급 콜백 요청

    중요: 항상 고객의 감정에 공감하고, 방어적인 태도를 피하세요.
    고객이 화가 나 있더라도 침착하고 정중하게 대응하세요.
    """


complaints_agent = Agent(
    name="불만 처리 에이전트",
    instructions=dynamic_complaints_agent_instructions,
    tools=[
        submit_complaint,
        apply_discount,
        request_manager_callback,
    ],
    hooks=AgentToolUsageLoggingHooks(),
    output_guardrails=[
        restaurant_output_guardrail,
    ],
)
