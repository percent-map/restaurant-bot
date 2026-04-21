import streamlit as st
from agents import function_tool, AgentHooks, Agent, Tool, RunContextWrapper
from models import RestaurantContext
import random

# =============================================================================
# VIRTUAL MENU
# =============================================================================

MENU = {
    "메인": [
        {"name": "채끝 스테이크", "price": 45000, "description": "28일 숙성 채끝살, 계절 야채 곁들임"},
        {"name": "파스타 카르보나라", "price": 18000, "description": "판체타, 파르미지아노 치즈, 유기농 달걀"},
        {"name": "해산물 리조또", "price": 22000, "description": "새우, 관자, 오징어, 사프란 육수"},
        {"name": "버거 세트", "price": 15000, "description": "200g 수제 패티, 감자튀김, 음료 포함"},
        {"name": "피자 마르게리타", "price": 22000, "description": "토마토 소스, 모짜렐라, 바질"},
    ],
    "사이드": [
        {"name": "시저 샐러드", "price": 12000, "description": "로메인, 파르미지아노, 크루통, 시저 드레싱"},
        {"name": "어니언 수프", "price": 8000, "description": "카라멜라이즈드 양파, 그뤼에르 치즈 토핑"},
    ],
    "디저트": [
        {"name": "티라미수", "price": 9000, "description": "마스카포네, 에스프레소, 카카오"},
        {"name": "초콜릿 케이크", "price": 8000, "description": "벨기에 다크 초콜릿, 바닐라 아이스크림"},
    ],
    "음료": [
        {"name": "아메리카노", "price": 5000, "description": "싱글 오리진 원두, 아이스/핫 선택 가능"},
        {"name": "수제 레모네이드", "price": 6000, "description": "제주 레몬, 민트, 탄산수"},
    ],
}


# =============================================================================
# MENU TOOLS
# =============================================================================


@function_tool
def get_full_menu(context: RestaurantContext) -> str:
    """
    Return the full restaurant menu with prices.
    """
    lines = ["🍽️ 저희 레스토랑 메뉴를 안내해 드립니다.\n"]
    for category, items in MENU.items():
        lines.append(f"【 {category} 】")
        for item in items:
            lines.append(
                f"  • {item['name']} — {item['price']:,}원\n    {item['description']}"
            )
        lines.append("")
    return "\n".join(lines)


@function_tool
def get_menu_by_category(context: RestaurantContext, category: str) -> str:
    """
    Return menu items for a specific category.

    Args:
        category: Menu category (메인, 사이드, 디저트, 음료)
    """
    items = MENU.get(category)
    if not items:
        available = ", ".join(MENU.keys())
        return f"'{category}' 카테고리를 찾을 수 없습니다. 사용 가능한 카테고리: {available}"

    lines = [f"【 {category} 메뉴 】\n"]
    for item in items:
        lines.append(f"• {item['name']} — {item['price']:,}원")
        lines.append(f"  {item['description']}\n")
    return "\n".join(lines)


@function_tool
def check_menu_item(context: RestaurantContext, item_name: str) -> str:
    """
    Get details and price for a specific menu item.

    Args:
        item_name: Name of the menu item
    """
    for category, items in MENU.items():
        for item in items:
            if item_name in item["name"] or item["name"] in item_name:
                return (
                    f"✅ {item['name']}\n"
                    f"카테고리: {category}\n"
                    f"가격: {item['price']:,}원\n"
                    f"설명: {item['description']}"
                )
    return f"'{item_name}' 메뉴를 찾을 수 없습니다. 전체 메뉴를 확인해 드릴까요?"


# =============================================================================
# RESERVATION TOOLS
# =============================================================================


@function_tool
def make_reservation(
    context: RestaurantContext,
    date: str,
    time: str,
    party_size: int,
    special_request: str = "",
) -> str:
    """
    Make a table reservation.

    Args:
        date: Reservation date (YYYY-MM-DD 형식, 예: 2026-04-25)
        time: Reservation time (HH:MM 형식, 예: 19:00)
        party_size: Number of guests
        special_request: Special requests or notes
    """
    reservation_id = f"RES-{random.randint(10000, 99999)}"
    context.reservation_date = date
    context.reservation_time = time

    lines = [
        "✅ 예약이 완료되었습니다!",
        f"📋 예약 번호: {reservation_id}",
        f"👤 고객명: {context.name}",
        f"📅 날짜: {date}",
        f"⏰ 시간: {time}",
        f"👥 인원: {party_size}명",
    ]
    if special_request:
        lines.append(f"📝 특별 요청: {special_request}")
    lines.append("예약 확인은 예약 번호로 문의하실 수 있습니다.")
    return "\n".join(lines)


@function_tool
def check_reservation(context: RestaurantContext, reservation_id: str) -> str:
    """
    Check an existing reservation.

    Args:
        reservation_id: Reservation ID to look up
    """
    if context.reservation_date and context.reservation_time:
        return (
            f"📋 예약 번호: {reservation_id}\n"
            f"👤 고객명: {context.name}\n"
            f"📅 날짜: {context.reservation_date}\n"
            f"⏰ 시간: {context.reservation_time}\n"
            f"상태: ✅ 예약 확정"
        )
    return f"예약 번호 {reservation_id}에 대한 예약 정보를 찾을 수 없습니다."


@function_tool
def cancel_reservation(context: RestaurantContext, reservation_id: str, reason: str = "") -> str:
    """
    Cancel an existing reservation.

    Args:
        reservation_id: Reservation ID to cancel
        reason: Reason for cancellation
    """
    context.reservation_date = None
    context.reservation_time = None
    return (
        f"❌ 예약이 취소되었습니다.\n"
        f"📋 예약 번호: {reservation_id}\n"
        f"{'📝 취소 사유: ' + reason if reason else ''}\n"
        "취소 확인 문자가 전송됩니다. 다음에 또 방문해 주세요!"
    )


# =============================================================================
# ORDER TOOLS
# =============================================================================


@function_tool
def place_food_order(
    context: RestaurantContext,
    items: str,
    special_instructions: str = "",
) -> str:
    """
    Place a food order for the table.

    Args:
        items: Comma-separated list of items to order
        special_instructions: Special preparation instructions
    """
    order_id = f"ORD-{random.randint(10000, 99999)}"
    estimated_time = random.randint(15, 30)

    lines = [
        "✅ 주문이 접수되었습니다!",
        f"🧾 주문 번호: {order_id}",
        f"📋 주문 항목: {items}",
    ]
    if context.table_number:
        lines.append(f"🪑 테이블 번호: {context.table_number}번")
    if special_instructions:
        lines.append(f"📝 특별 요청: {special_instructions}")
    lines.append(f"⏱️ 예상 조리 시간: 약 {estimated_time}분")
    return "\n".join(lines)


@function_tool
def check_order_status(context: RestaurantContext, order_id: str) -> str:
    """
    Check the current status of a food order.

    Args:
        order_id: Order ID to check
    """
    statuses = ["접수됨", "조리 중", "서빙 준비 중", "서빙 완료"]
    current_status = random.choice(statuses)
    return (
        f"🧾 주문 번호: {order_id}\n"
        f"📊 현재 상태: {current_status}\n"
        "추가 문의 사항이 있으시면 알려주세요."
    )


@function_tool
def modify_order(context: RestaurantContext, order_id: str, modification: str) -> str:
    """
    Modify an existing order.

    Args:
        order_id: Order ID to modify
        modification: Description of the modification
    """
    return (
        f"✅ 주문이 수정되었습니다.\n"
        f"🧾 주문 번호: {order_id}\n"
        f"📝 변경 내용: {modification}\n"
        "주방에 수정 내용이 전달되었습니다."
    )


# =============================================================================
# COMPLAINTS TOOLS
# =============================================================================


@function_tool
def submit_complaint(
    context: RestaurantContext,
    complaint_type: str,
    description: str,
) -> str:
    """
    Submit and log a customer complaint.

    Args:
        complaint_type: Type of complaint (음식품질, 서비스, 위생, 대기시간, 기타)
        description: Detailed description of the complaint
    """
    ticket_id = f"CMP-{random.randint(10000, 99999)}"
    return (
        f"📝 불만 사항이 접수되었습니다.\n"
        f"🎫 접수 번호: {ticket_id}\n"
        f"📂 유형: {complaint_type}\n"
        f"📋 내용: {description}\n"
        "매니저가 최대한 빠르게 조치하겠습니다."
    )


@function_tool
def apply_discount(
    context: RestaurantContext,
    discount_percent: int,
    reason: str,
) -> str:
    """
    Apply a discount to the customer's bill as compensation.

    Args:
        discount_percent: Discount percentage (10, 20, 30, 50)
        reason: Reason for applying the discount
    """
    return (
        f"🎁 할인이 적용되었습니다!\n"
        f"💰 할인율: {discount_percent}%\n"
        f"📝 사유: {reason}\n"
        "계산 시 자동으로 적용됩니다. 불편을 드려 진심으로 죄송합니다."
    )


@function_tool
def request_manager_callback(
    context: RestaurantContext,
    issue_summary: str,
    urgency: str = "일반",
) -> str:
    """
    Request a manager to contact the customer directly.

    Args:
        issue_summary: Brief summary of the issue
        urgency: Urgency level (긴급, 일반)
    """
    callback_id = f"MGR-{random.randint(10000, 99999)}"
    wait_time = "10분 이내" if urgency == "긴급" else "30분 이내"
    return (
        f"📞 매니저 콜백이 요청되었습니다.\n"
        f"🔖 요청 번호: {callback_id}\n"
        f"⚡ 긴급도: {urgency}\n"
        f"📋 이슈 요약: {issue_summary}\n"
        f"⏰ 예상 연락 시간: {wait_time}\n"
        "매니저가 직접 연락드릴 예정입니다."
    )


# =============================================================================
# LOGGING HOOKS
# =============================================================================


class AgentToolUsageLoggingHooks(AgentHooks):

    async def on_tool_start(
        self,
        context: RunContextWrapper[RestaurantContext],
        agent: Agent[RestaurantContext],
        tool: Tool,
    ):
        with st.sidebar:
            st.write(f"🔧 **{agent.name}** starting tool: `{tool.name}`")

    async def on_tool_end(
        self,
        context: RunContextWrapper[RestaurantContext],
        agent: Agent[RestaurantContext],
        tool: Tool,
        result: str,
    ):
        with st.sidebar:
            st.write(f"🔧 **{agent.name}** used tool: `{tool.name}`")
            st.code(result)

    async def on_handoff(
        self,
        context: RunContextWrapper[RestaurantContext],
        agent: Agent[RestaurantContext],
        source: Agent[RestaurantContext],
    ):
        with st.sidebar:
            st.write(f"🔄 Handoff: **{source.name}** → **{agent.name}**")

    async def on_start(
        self,
        context: RunContextWrapper[RestaurantContext],
        agent: Agent[RestaurantContext],
    ):
        with st.sidebar:
            st.write(f"🚀 **{agent.name}** activated")

    async def on_end(
        self,
        context: RunContextWrapper[RestaurantContext],
        agent: Agent[RestaurantContext],
        output,
    ):
        with st.sidebar:
            st.write(f"🏁 **{agent.name}** completed")
