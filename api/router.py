from api.health.health import health_router
from api.users.users_controller import users_router
from utils.oauth.auth import auth_router
from api.orders.orders_controller import orders_router
from api.employees.employees_controller import employees_router
from api.restaurants.restaurants_controller import restaurants_router
from api.tables.tables_controller import tables_router
from api.menus.menus_controller import menus_router
from api.rooms.rooms_controller import rooms_router
from api.stock.stock_controller import stock_router
from api.daily_menu.daily_menu_controller import daily_menu_router
from api.final_articles.final_articles_controller import final_articles_router
from api.components.components_controller import components_router
from api.options.options_controller import options_router
from api.general_menu.general_menu_controller import general_menu_router
from api.ingredients.ingredients_controller import ingredients_router
from api.categories_menu.categories_menu_controller import categories_menu_router

ACTIVE_ROUTERS = [
    health_router,
    users_router,
    auth_router,
    orders_router,
    employees_router,
    restaurants_router,
    tables_router,
    menus_router,
    daily_menu_router,
    rooms_router,
    stock_router,
    final_articles_router,
    components_router,
    options_router,
    general_menu_router,
    ingredients_router,
    categories_menu_router
]
