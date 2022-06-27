from aiogram.utils.helper import Helper, HelperMode, Item
class TestStates(Helper):
    mode = HelperMode.snake_case

    TEST_STATE_LOGIN = Item()
    TEST_STATE_PASSWORD = Item()
    TEST_STATE_IN = Item()
    TEST_STATE_ACC = Item()
    TEST_STATE_ACC_ORDER = Item()
    TEST_STATE_PROMO = Item()
    TEST_STATE__MENU = Item()
    TEST_STATE__MENU_PRODUCT = Item()
    TEST_STATE__MENU_PRODUCT_W_L = Item()
    TEST_STATE__MENU_PRODUCT_W_N = Item()
    TEST_STATE__MENU_PRODUCT_W_N_L = Item()