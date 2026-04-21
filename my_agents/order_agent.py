from agents import Agent, RunContextWrapper
from models import RestaurantContext
from tools import (
    place_food_order,
    check_order_status,
    modify_order,
    get_full_menu,
    AgentToolUsageLoggingHooks,
)


def dynamic_order_agent_instructions(
    wrapper: RunContextWrapper[RestaurantContext],
    agent: Agent[RestaurantContext],
):
    table_info = f"테이블 번호: {wrapper.context.table_number}번" if wrapper.context.table_number else "테이블 번호 미확인"

    return f"""
    안녕하세요, {wrapper.context.name}님! 저는 주문 담당 직원입니다.
    {table_info}

    음식 주문과 관련된 모든 업무를 도와드립니다.

    처리 가능한 업무:
    - 음식 주문 접수
    - 주문 현황 확인
    - 주문 수정 (조리 시작 전에만 가능)
    - 메뉴 안내 (간단한 메뉴 정보 제공)

    주문 접수 절차:
    1. 고객이 원하는 메뉴 확인
    2. 수량 및 특별 요청 사항 확인
    3. 주문 내용 재확인 후 접수
    4. 예상 조리 시간 안내

    주문 시 주의사항:
    - 알레르기가 있는 경우 반드시 사전에 알려주시도록 안내
    - 조리 시작 후에는 주문 변경이 어려울 수 있음을 안내
    - 주문 완료 후 주문 번호를 제공
    """


order_agent = Agent(
    name="주문 에이전트",
    instructions=dynamic_order_agent_instructions,
    tools=[
        place_food_order,
        check_order_status,
        modify_order,
        get_full_menu,
    ],
    hooks=AgentToolUsageLoggingHooks(),
)
