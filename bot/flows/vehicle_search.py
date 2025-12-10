from bot.state_manager import StateManager
from services.woocommerce_service import WooCommerceService
from utils.logger import logger

state_mgr = StateManager()
wc = WooCommerceService()

def start(platform, platform_id):
    s = state_mgr.get_state(platform, platform_id)
    s.current_flow = "vehicle_search"
    s.step = "ask_brand"
    s.data = {}
    state_mgr.save_state(s)
    return "¿Cuál es la marca del vehículo?"

def handle(platform, platform_id, text):
    s = state_mgr.get_state(platform, platform_id)
    if s.current_flow != "vehicle_search":
        return start(platform, platform_id)
    if s.step == "ask_brand":
        s.data["brand"] = text.strip()
        s.step = "ask_model"
        state_mgr.save_state(s)
        return "Perfecto. ¿Cuál es la línea o modelo?"
    if s.step == "ask_model":
        s.data["model"] = text.strip()
        results = wc.search_by_brand_model(s.data.get("brand"), s.data.get("model"))
        state_mgr.clear_state(platform, platform_id)
        if not results:
            return "No encontré resultados para esa combinación. ¿Quieres intentar otra marca o modelo?"
        lines = [f"Encontré {len(results)} productos:"]
        for p in results[:5]:
            lines.append(f"- {p.get('name')} — {p.get('price')}")
        return "\n".join(lines)
