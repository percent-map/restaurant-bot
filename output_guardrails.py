from agents import (
    Agent,
    output_guardrail,
    Runner,
    RunContextWrapper,
    GuardrailFunctionOutput,
)
from models import RestaurantOutputGuardRailOutput, RestaurantContext


restaurant_output_guardrail_agent = Agent(
    name="Restaurant Output Guardrail",
    instructions="""
    레스토랑 봇의 응답을 분석하여 다음을 확인하세요:

    - contains_off_topic: 레스토랑과 무관한 내용이 포함되어 있는지 (정치, 종교, 개인 상담 등)
    - contains_internal_info: 내부 정보가 노출되어 있는지 (직원 개인정보, 원가, 내부 운영 시스템, 재무 정보 등)
    - is_unprofessional: 비전문적이거나 무례한 표현이 있는지 (욕설, 비하 표현, 지나치게 캐주얼한 표현 등)

    레스토랑 관련 정상적인 응답(메뉴, 예약, 주문, 불만 처리)에는 모두 false를 반환하세요.
    """,
    output_type=RestaurantOutputGuardRailOutput,
)


@output_guardrail
async def restaurant_output_guardrail(
    wrapper: RunContextWrapper[RestaurantContext],
    agent: Agent,
    output: str,
):
    result = await Runner.run(
        restaurant_output_guardrail_agent,
        output,
        context=wrapper.context,
    )

    validation = result.final_output

    triggered = (
        validation.contains_off_topic
        or validation.contains_internal_info
        or validation.is_unprofessional
    )

    return GuardrailFunctionOutput(
        output_info=validation,
        tripwire_triggered=triggered,
    )
