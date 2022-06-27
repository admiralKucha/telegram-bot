import logging
from database import signIn, orders, openOrders, promo, openPromo, menu, nextMenu, product, createPromo
from joke import joke
#основа
from aiogram import Bot
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.utils import executor

from aiogram.types import ReplyKeyboardRemove #кнопки

from aiogram.types import ParseMode, Message #обработка сообщения

from aiogram.contrib.fsm_storage.memory import MemoryStorage #состояния

#файловый импорт
from config import TOKEN
from states import TestStates
from buttons import greet, greet_menu, greet_post_login, greet_acc, greet_order, greet_product_menu, greet_promo, greet_product_menu_w_l, greet_product_menu_w_n, greet_product_menu_w_n_l
from stringPizza import success_str_log, fail_str_log, password_str, help_string, login_string, acc_string
from stringPizza import start1, start2, start3, miss

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

#Cловари
dic_id = dict()
dict_log = dict()
dict_user = dict()
dict_menu = dict()

logging.basicConfig(filename="log_error_telegram.log", filemode='a', level=logging.ERROR, format = "%(asctime)s - %(levelname)s - %(funcName)s: %(lineno)d - %(message)s")

@dp.message_handler(state=TestStates.TEST_STATE_PASSWORD)
async def state_password(message: Message):
    state = dp.current_state()
    msg_us_id = message.from_user.id
    msg_id = message.message_id
    #сразу для безопасности удаляем пароль, после проверяем: можем ли мы удалить прошлое сообщение бота?
    await bot.delete_message(message_id = msg_id, chat_id = msg_us_id)
    smth = dic_id[msg_us_id] 
    flag = signIn(dict_log[msg_us_id], message.text)
    del dict_log[msg_us_id]
    del dic_id[msg_us_id]
    try:
        await bot.delete_message(message_id = smth, chat_id = msg_us_id)
    except:
        for i in range  (smth, msg_id):
            try:
                await bot.delete_message(message_id = i, chat_id = msg_us_id)
            except:
                continue
            if flag != (): 
                dict_user[msg_us_id] = flag
                await message.answer(success_str_log, reply_markup = greet_post_login)
                await state.set_state(TestStates.all()[2])
            else:               
                await message.answer("НЕВЕРНО", reply_markup = greet)
                await state.reset_state()
            break

        else:   
            await message.answer(fail_str_log,  reply_markup = greet)
            await state.reset_state()

    else:
        if flag != ():
            await message.answer(success_str_log, reply_markup = greet_post_login)
            dict_user[msg_us_id] = flag
            await state.set_state(TestStates.all()[2])
        else:
            await message.answer("НЕВЕРНО", reply_markup = greet)
            await state.reset_state()

@dp.message_handler(state=TestStates.TEST_STATE_LOGIN)
async def state_login(message: Message):
    state = dp.current_state()
    msg_us_id = message.from_user.id
    msg_id = message.message_id
     #сразу для безопасности удаляем логин, после проверяем: можем ли мы удалить прошлое сообщение бота?
    await bot.delete_message(message_id = msg_id, chat_id = msg_us_id)
    smth = dic_id[msg_us_id] 
    dic_id[msg_us_id] = msg_id + 1
    dict_log[msg_us_id] = message.text

    try:
        await bot.delete_message(message_id = smth, chat_id = msg_us_id)
    except:
        for i in range  (smth, msg_id):
            try:
                await bot.delete_message(message_id = i, chat_id = msg_us_id)
            except:
                continue

            await state.set_state(TestStates.all()[4])
            await message.answer(password_str)
            break

        else: 
            await message.answer(fail_str_log,  reply_markup = greet)
            await state.reset_state()
            
    else:
        await state.set_state(TestStates.all()[4])
        await message.answer(password_str)


@dp.message_handler(state=TestStates.TEST_STATE_ACC)
async def state_acc(message: Message):
    state = dp.current_state()
    if message.text == "exit":
        state = dp.current_state()
        string = "Успешно выполнен выход из аккаунта"
        del dict_user[message.from_user.id]
        await state.reset_state()
        await message.answer(string, reply_markup = greet)

    elif message.text == 'помощь':
        await state.set_state(TestStates.all()[2])
        await message.answer(help_string,  reply_markup = greet_post_login, parse_mode=ParseMode.MARKDOWN)

    elif message.text == 'заказы':
        res = orders(dict_user[message.from_user.id])
        if res == ():
            await message.answer("Ошибка, попробуйте позже", reply_markup = greet_acc)
        elif res == -1:
            await message.answer("Заказов нет(((", reply_markup = greet_acc)
        else:
            await state.set_state(TestStates.all()[1])
            await message.answer(res, reply_markup = greet_order)
        
    elif message.text == 'акции':
        res = promo(dict_user[message.from_user.id])
        if res == ():
            await message.answer("Ошибка, попробуйте позже", reply_markup = greet_acc)
        elif res == -1:
            await message.answer("Акции закончились(((", reply_markup = greet_promo)
            await state.set_state(TestStates.all()[5])
        else:
            await state.set_state(TestStates.all()[5])
            await message.answer(res, reply_markup = greet_promo)
    else:
        await message.answer(miss,  reply_markup = greet_acc)


@dp.message_handler(state=TestStates.TEST_STATE_ACC_ORDER)
async def state_acc_order(message: Message):
    state = dp.current_state()
    if message.text == 'помощь':
        await state.set_state(TestStates.all()[2])
        await message.answer(help_string,  reply_markup = greet_post_login, parse_mode=ParseMode.MARKDOWN)
        return

    elif  message.text == 'аккаунт':
        state = dp.current_state()
        await state.set_state(TestStates.all()[0])
        await message.answer(acc_string, reply_markup = greet_acc, parse_mode=ParseMode.MARKDOWN) 
        return
    elif message.text[0] == "/":
        res = openOrders(message.text[1:], dict_user[message.from_user.id])
        if res == ():
            await message.answer("Ошибка, попробуйте позже", reply_markup = greet_acc)
        else:
            await message.answer(res, reply_markup = greet_order)
    elif message.text[0] in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]:
        res = openOrders(message.text, dict_user[message.from_user.id])
        if res == ():
            await message.answer("Ошибка, попробуйте позже", reply_markup = greet_acc)
        else:
            await message.answer(res, reply_markup = greet_order)
    else :
        await message.answer(miss,  reply_markup = greet_order)

@dp.message_handler(state=TestStates.TEST_STATE_PROMO)
async def state_acc_order(message: Message):
    state = dp.current_state()
    if message.text == 'помощь':
        await state.set_state(TestStates.all()[2])
        await message.answer(help_string,  reply_markup = greet_post_login, parse_mode=ParseMode.MARKDOWN)
        return

    elif  message.text == 'аккаунт':
        state = dp.current_state()
        await state.set_state(TestStates.all()[0])
        await message.answer(acc_string, reply_markup = greet_acc, parse_mode=ParseMode.MARKDOWN) 
        return
    elif message.text == "создать акцию":
        res  = createPromo(dict_user[message.from_user.id])
        await message.answer(res,  reply_markup = greet_promo)

    elif message.text[0] == "/":
        res = openPromo(message.text[1:], dict_user[message.from_user.id])
        if res == ():
            await message.answer("Ошибка, попробуйте позже", reply_markup = greet_acc)
        else:
            await message.answer(res, reply_markup = greet_order)
    elif message.text[0] in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]:
        res = openPromo(message.text, dict_user[message.from_user.id])
        if res == ():
            await message.answer("Ошибка, попробуйте позже", reply_markup = greet_acc)
        else:
            await message.answer(res, reply_markup = greet_order)
    else :
        await message.answer(miss,  reply_markup = greet_order)

@dp.message_handler(state=TestStates.TEST_STATE__MENU)
async def state_acc_order(message: Message):
    state = dp.current_state()
    if message.text == 'помощь':
        if dict_user.get(message.from_user.id) == None:
            await state.reset_state()
            await message.answer(help_string,  reply_markup = greet, parse_mode=ParseMode.MARKDOWN)
        else:
            await state.set_state(TestStates.all()[2])
            await message.answer(help_string,  reply_markup = greet_post_login, parse_mode=ParseMode.MARKDOWN)
        return

    elif  message.text == 'меню':
        string = menu()
        if string == ():
            await message.answer("Ошибка, попробуйте позже",  reply_markup = greet_menu)
            return
        dict_menu[message.from_user.id] = 0
        await state.set_state(TestStates.all()[6])
        await message.answer(string,  reply_markup = greet_menu) 
        return

    #ТУТ НАДО ПРОВЕРКУ ПОСТАВИТЬ ЧТО ДАЛИ КОРЕКТНОЕ ЧИСЛО
    elif message.text[0] == "/":
        res, flag = nextMenu(message.text[1:], dict_menu[message.from_user.id])
        if res == ():
            await message.answer("Ошибка, попробуйте позже", reply_markup = greet_menu)
        elif res == "":
            await message.answer("Неправильная позиция", reply_markup = greet_menu)
        else:
            if flag == -1:
                greet_now = greet_product_menu_w_l
                await state.set_state(TestStates.all()[8])
            elif flag == 0:
                greet_now = greet_product_menu
                await state.set_state(TestStates.all()[7])
            elif flag == 2:
                greet_now = greet_product_menu_w_n_l
                await state.set_state(TestStates.all()[10])
            else:
                greet_now = greet_product_menu_w_n
                await state.set_state(TestStates.all()[9])

            dict_menu[message.from_user.id] = [message.text[1:], dict_menu[message.from_user.id]]
            await message.answer(res, reply_markup = greet_now)
    elif message.text[0] in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]:
        res, flag = nextMenu(message.text, dict_menu[message.from_user.id])
        if res == ():
            await message.answer("Ошибка, попробуйте позже", reply_markup = greet_menu)
        elif res == "":
            await message.answer("Неправильная позиция", reply_markup = greet_menu)
        else:
            if flag == -1:
                greet_now = greet_product_menu_w_l
                await state.set_state(TestStates.all()[8])
            elif flag == 0:
                greet_now = greet_product_menu
                await state.set_state(TestStates.all()[7])
            elif flag == 2:
                greet_now = greet_product_menu_w_n_l
                await state.set_state(TestStates.all()[10])
            else:
                greet_now = greet_product_menu_w_n
                await state.set_state(TestStates.all()[9])

            dict_menu[message.from_user.id] = [message.text[1:], dict_menu[message.from_user.id]]
            await message.answer(res, reply_markup = greet_now)
    else:
        await message.answer(miss,  reply_markup = greet_menu)

@dp.message_handler(state=TestStates.TEST_STATE__MENU_PRODUCT)
async def state_acc_order(message: Message):
    state = dp.current_state()
    if message.text == 'помощь':
        if dict_user.get(message.from_user.id) == None:
            await state.reset_state()
            await message.answer(help_string,  reply_markup = greet, parse_mode=ParseMode.MARKDOWN)
        else:
            await state.set_state(TestStates.all()[2])
            await message.answer(help_string,  reply_markup = greet_post_login, parse_mode=ParseMode.MARKDOWN)
        return

    elif  message.text == 'меню':
        string = menu()
        if string == ():
            await message.answer("Ошибка, попробуйте позже",  reply_markup = greet_menu)
            return
        dict_menu[message.from_user.id] = 0
        await state.set_state(TestStates.all()[6])
        await message.answer(string,  reply_markup = greet_menu) 
        return
    elif len(message.text) > 10:
        if message.text == 'следующая страница':
            dict_menu[message.from_user.id][1] = dict_menu[message.from_user.id][1] + 1
            res, flag = nextMenu(dict_menu[message.from_user.id][0], dict_menu[message.from_user.id][1])

        elif message.text == 'прошлая страница':
            dict_menu[message.from_user.id][1] = dict_menu[message.from_user.id][1] - 1
            res, flag = nextMenu(dict_menu[message.from_user.id][0], dict_menu[message.from_user.id][1])
        if res == ():
            await message.answer("Ошибка, попробуйте позже", reply_markup = greet_menu)
        else:
            if flag == -1:
                greet_now = greet_product_menu_w_l
                await state.set_state(TestStates.all()[8])
            elif flag == 0:
                greet_now = greet_product_menu
                await state.set_state(TestStates.all()[7])
            elif flag == 2:
                greet_now = greet_product_menu_w_n_l
                await state.set_state(TestStates.all()[10])
            else:
                greet_now = greet_product_menu_w_n
                await state.set_state(TestStates.all()[9])

            await message.answer(res, reply_markup = greet_now)
    
    elif message.text[0] == "/":
        res = product(message.text[1:], dict_menu[message.from_user.id][0])
        await message.answer(res, reply_markup = greet_product_menu)
    elif message.text[0] in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]:
        res = product(message.text, dict_menu[message.from_user.id][0])
        await message.answer(res, reply_markup = greet_product_menu)
    else:
        res, flag = nextMenu(dict_menu[message.from_user.id][0], dict_menu[message.from_user.id][1])
        if flag == -1:
            greet_now = greet_product_menu_w_l
            await state.set_state(TestStates.all()[8])
        elif flag == 0:
            greet_now = greet_product_menu
            await state.set_state(TestStates.all()[7])
        elif flag == 2:
            greet_now = greet_product_menu_w_n_l
            await state.set_state(TestStates.all()[10])
        else:
            greet_now = greet_product_menu_w_n
            await state.set_state(TestStates.all()[9])
        await message.answer(miss,  reply_markup = greet_now)

@dp.message_handler(state=TestStates.TEST_STATE__MENU_PRODUCT_W_L)
async def state_acc_order(message: Message):
    state = dp.current_state()
    if message.text == 'помощь':
        if dict_user.get(message.from_user.id) == None:
            await state.reset_state()
            await message.answer(help_string,  reply_markup = greet, parse_mode=ParseMode.MARKDOWN)
        else:
            await state.set_state(TestStates.all()[2])
            await message.answer(help_string,  reply_markup = greet_post_login, parse_mode=ParseMode.MARKDOWN)
        return

    elif  message.text == 'меню':
        string = menu()
        if string == ():
            await message.answer("Ошибка, попробуйте позже",  reply_markup = greet_menu)
            return
        dict_menu[message.from_user.id] = 0
        await state.set_state(TestStates.all()[6])
        await message.answer(string,  reply_markup = greet_menu) 
        return

    elif message.text == 'следующая страница':
        dict_menu[message.from_user.id][1] = dict_menu[message.from_user.id][1] + 1
        res, flag = nextMenu(dict_menu[message.from_user.id][0], dict_menu[message.from_user.id][1])
        if res == ():
            await message.answer("Ошибка, попробуйте позже", reply_markup = greet_menu)
        else:
            if flag == -1:
                greet_now = greet_product_menu_w_l
                await state.set_state(TestStates.all()[8])
            elif flag == 0:
                greet_now = greet_product_menu
                await state.set_state(TestStates.all()[7])
            elif flag == 2:
                greet_now = greet_product_menu_w_n_l
                await state.set_state(TestStates.all()[10])
            else:
                greet_now = greet_product_menu_w_n
                await state.set_state(TestStates.all()[9])

            await message.answer(res, reply_markup = greet_now)

    elif message.text[0] == "/":
        res = product(message.text[1:], dict_menu[message.from_user.id][0])
        await message.answer(res, reply_markup = greet_product_menu_w_l)

    elif message.text[0] in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]:
        res = product(message.text, dict_menu[message.from_user.id][0])
        await message.answer(res, reply_markup = greet_product_menu_w_l)
    else:
        await message.answer(miss,  reply_markup = greet_product_menu_w_l)


@dp.message_handler(state=TestStates.TEST_STATE__MENU_PRODUCT_W_N)
async def state_acc_order(message: Message):
    state = dp.current_state()
    if message.text == 'помощь':
        if dict_user.get(message.from_user.id) == None:
            await state.reset_state()
            await message.answer(help_string,  reply_markup = greet, parse_mode=ParseMode.MARKDOWN)
        else:
            await state.set_state(TestStates.all()[2])
            await message.answer(help_string,  reply_markup = greet_post_login, parse_mode=ParseMode.MARKDOWN)
        return

    elif  message.text == 'меню':
        string = menu()
        if string == ():
            await message.answer("Ошибка, попробуйте позже",  reply_markup = greet_menu)
            return
        dict_menu[message.from_user.id] = 0
        await state.set_state(TestStates.all()[6])
        await message.answer(string,  reply_markup = greet_menu) 
        return

    elif message.text == 'прошлая страница':
        dict_menu[message.from_user.id][1] = dict_menu[message.from_user.id][1] - 1
        res, flag = nextMenu(dict_menu[message.from_user.id][0], dict_menu[message.from_user.id][1])
        if res == ():
            await message.answer("Ошибка, попробуйте позже", reply_markup = greet_menu)
        else:
            if flag == -1:
                greet_now = greet_product_menu_w_l
                await state.set_state(TestStates.all()[8])
            elif flag == 0:
                greet_now = greet_product_menu
                await state.set_state(TestStates.all()[7])
            elif flag == 2:
                greet_now = greet_product_menu_w_n_l
                await state.set_state(TestStates.all()[10])
            else:
                greet_now = greet_product_menu_w_n
                await state.set_state(TestStates.all()[9])

            await message.answer(res, reply_markup = greet_now)

    elif message.text[0] == "/":
        res = product(message.text[1:], dict_menu[message.from_user.id][0])
        await message.answer(res, reply_markup = greet_product_menu_w_n)

    elif message.text[0] in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]:
        res = product(message.text, dict_menu[message.from_user.id][0])
        await message.answer(res, reply_markup = greet_product_menu_w_n)
    else:
        await message.answer(miss,  reply_markup = greet_product_menu_w_n)  

@dp.message_handler(state=TestStates.TEST_STATE__MENU_PRODUCT_W_N_L)
async def state_acc_order(message: Message):
    state = dp.current_state()
    if message.text == 'помощь':
        if dict_user.get(message.from_user.id) == None:
            await state.reset_state()
            await message.answer(help_string,  reply_markup = greet, parse_mode=ParseMode.MARKDOWN)
        else:
            await state.set_state(TestStates.all()[2])
            await message.answer(help_string,  reply_markup = greet_post_login, parse_mode=ParseMode.MARKDOWN)
        return

    elif  message.text == 'меню':
        string = menu()
        if string == ():
            await message.answer("Ошибка, попробуйте позже",  reply_markup = greet_menu)
            return
        dict_menu[message.from_user.id] = 0
        await state.set_state(TestStates.all()[6])
        await message.answer(string,  reply_markup = greet_menu) 
        return

    elif message.text[0] == "/":
        res = product(message.text[1:], dict_menu[message.from_user.id][0])
        await message.answer(res, reply_markup = greet_product_menu_w_n_l)

    elif message.text[0] in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]:
        res = product(message.text, dict_menu[message.from_user.id][0])
        await message.answer(res, reply_markup = greet_product_menu_w_n_l)
    else:
        await message.answer(miss,  reply_markup = greet_product_menu_w_n_l)

@dp.message_handler(state='*')
async def main(message: Message, state: FSMContext):
    state = await state.get_state()
    if TestStates.all()[2] == state:
        greet_now = greet_post_login
    else:
        greet_now = greet

    with open('log_telegram.log','a') as f:
        log_msg = str(message.date)  + "  id: " + str(message.from_user.id)
        log_msg = log_msg + " text: " + message.text + "\n"
        f.write(log_msg)

    if message.text == '/start' :
        await message.answer(start1)
        await message.answer(start2)
        await message.answer(start3,  reply_markup = greet_now)

    elif message.text == 'помощь':
        await message.answer(help_string,  reply_markup = greet_now, parse_mode=ParseMode.MARKDOWN)

    elif message.text == "меню":
        string = menu()
        if string == ():
            await message.answer("Ошибка, попробуйте позже",  reply_markup = greet_menu)
            return
        state = dp.current_state()
        dict_menu[message.from_user.id] = 0
        await state.set_state(TestStates.all()[6])
        await message.answer(string,  reply_markup = greet_menu) 

    elif message.text == 'анекдот':
        await message.answer(joke(),  reply_markup = greet_now)

    elif message.text == 'login' and state != TestStates.all()[2]:
        dic_id[message.from_user.id] = message.message_id+1
        state = dp.current_state()
        await state.set_state(TestStates.all()[3])
        await message.answer(login_string, reply_markup = ReplyKeyboardRemove())

    elif  message.text == 'аккаунт' and state == TestStates.all()[2]:
        state = dp.current_state()
        await state.set_state(TestStates.all()[0])
        await message.answer(acc_string, reply_markup = greet_acc, parse_mode=ParseMode.MARKDOWN)
        
    else:  
        await message.answer(miss,  reply_markup = greet_now)

if __name__ == '__main__':
    executor.start_polling(dp)