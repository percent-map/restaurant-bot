from agents import Agent, RunContextWrapper
from models import RestaurantContext
from tools import (
    make_reservation,
    check_reservation,
    cancel_reservation,
    AgentToolUsageLoggingHooks,
)


def dynamic_reservation_agent_instructions(
    wrapper: RunContextWrapper[RestaurantContext],
    agent: Agent[RestaurantContext],
):
    existing_reservation = ""
    if wrapper.context.reservation_date and wrapper.context.reservation_time:
        existing_reservation = (
            f"\n    현재 예약 정보: {wrapper.context.reservation_date} "
            f"{wrapper.context.reservation_time}"
        )

    return f"""
    안녕하세요, {wrapper.context.name}님! 저는 예약 담당 직원입니다.{existing_reservation}

    예약과 관련된 모든 업무를 도와드립니다.

    처리 가능한 업무:
    - 새 예약 접수 (날짜, 시간, 인원 수 필요)
    - 기존 예약 확인
    - 예약 취소

    예약 접수 시 반드시 확인할 사항:
    1. 날짜 (YYYY-MM-DD 형식, 예: 2026-04-25)
    2. 시간 (HH:MM 형식, 예: 19:00)
    3. 인원 수
    4. 특별 요청 사항 (선택)

    날짜와 시간 정보를 정확히 수집한 후 예약을 진행해 주세요.
    예약 완료 후에는 예약 번호를 안내하고 날짜/시간을 재확인해 드리세요.
    """


reservation_agent = Agent(
    name="예약 에이전트",
    instructions=dynamic_reservation_agent_instructions,
    tools=[
        make_reservation,
        check_reservation,
        cancel_reservation,
    ],
    hooks=AgentToolUsageLoggingHooks(),
)
