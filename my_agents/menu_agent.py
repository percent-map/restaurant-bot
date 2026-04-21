from agents import Agent, RunContextWrapper
from models import RestaurantContext
from tools import (
    get_full_menu,
    get_menu_by_category,
    check_menu_item,
    AgentToolUsageLoggingHooks,
)


def dynamic_menu_agent_instructions(
    wrapper: RunContextWrapper[RestaurantContext],
    agent: Agent[RestaurantContext],
):
    return f"""
    안녕하세요, {wrapper.context.name}님! 저는 메뉴 안내 전문 직원입니다.

    저희 레스토랑의 메뉴와 관련된 모든 질문에 답변드립니다.

    안내 가능한 내용:
    - 전체 메뉴 목록 및 가격
    - 카테고리별 메뉴 (메인, 사이드, 디저트, 음료)
    - 특정 메뉴 상세 정보 및 가격
    - 알레르기 정보 및 재료 안내
    - 추천 메뉴 및 인기 메뉴

    고객이 메뉴를 물어보면 정확한 가격과 함께 친절하게 안내해 드리세요.
    메뉴 이외의 요청(주문, 예약, 불만 처리)은 적절한 담당자에게 연결해 드린다고 안내하세요.
    """


menu_agent = Agent(
    name="메뉴 안내 에이전트",
    instructions=dynamic_menu_agent_instructions,
    tools=[
        get_full_menu,
        get_menu_by_category,
        check_menu_item,
    ],
    hooks=AgentToolUsageLoggingHooks(),
)
