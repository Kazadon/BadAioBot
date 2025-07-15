from dotenv import dotenv_values
import asyncio
import logging
import sys
from typing import Dict, Any

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, CallbackQuery, Message

from expdate_calc import ExpDateCalc
from get_customer import CostumerFeatures

class AIOBotConfig:
    config = dotenv_values('.env')
    token = config['AIOBOTTOKEN']

class Form(StatesGroup):
    # states for calculator
    mfg_date = State()
    exp_date = State()
    # states for costumer features. Workin...
    costumer_handler = State()
    get_feature = State()



class AIOBot:
    def __init__(self, config = AIOBotConfig):
        self.config = config
        print(self.config)
    dp = Dispatcher()

    #start message
    @dp.message(CommandStart()) 
    async def command_start_handler(message: Message) -> None:
        await message.answer(f'Бот-утилита\n'
                             f'Тестовые функции, расчет ОСГ, особенности и правила отгрузки товаров контрагентам, остальное на доработке\n'
                             f'/help для списка команд:\n')
    
    #help handler
    @dp.message(Command('help')) 
    async def command_help_handler(message: Message) -> None:
        await message.answer('Список команд:\n'
                            '/help - Помощь\n'
                            '/expdatecalc - Калькулятор срока годности\n'
                            '/costumer_features - Особенности отгрузки клиентов\n'
                            '/hello - Бот с Вами поздоровается\n'
                            '/start - Приветственное сообщение\n'
                            '/cancel - Отмена')
    # /cancel handler
    @dp.message(Command('cancel'))
    async def command_cancel_handler(message: Message) -> None:
        await message.answer('Отменено. \n/help для списка команд')

    # callback 'cancel' handler
    @dp.callback_query(F.data =='cancel')
    async def cancel_callback_handler(call: CallbackQuery) -> None:
        await call.message.answer('Отменено. \n/help для списка команд')
    
    # /hello command handler
    @dp.message(Command('hello')) 
    async def command_hello_handler(message: Message) -> None:
        await message.answer(f'Привет, {message.from_user.first_name} \U0001F643\U0001FAE0'
                                        f'\U0001F636\U0000200D\U0001F32B\U0000FE0F')


    # Starting expdate calc handler
    @dp.message(Command('expdatecalc'))
    async def expdatecalc_handler(message: Message, state: FSMContext) -> None:
        await state.set_state(Form.mfg_date)
        await message.answer('Введите дату производства в формате ДД.ММ.ГГГГ')

    # Getting mfg date and requesting exp date value
    @dp.message(Form.mfg_date)
    async def get_mfgdate(message: Message, state: FSMContext) -> None:
        await state.update_data(mfg_date=message.text)
        await state.set_state(Form.exp_date)
        await message.answer('Введите дату окончания срока годности в формате ДД.ММ.ГГГГ')
 
    # Getting exp date and calling calc method
    @dp.message(Form.exp_date)
    async def get_expdate(message: Message, state: FSMContext) -> None:
        await state.update_data(exp_date=message.text)
        data = await state.get_data()
        await state.clear()
        # await message.answer(f"MFG Date: {data.get("mfg_date")}")
        # await message.answer(f"EXP Date: {data.get("exp_date")}")
        await AIOBot.expdate_calculation(message=message, data=data) 

    # Calculation dates
    async def expdate_calculation(message: Message, data: Dict[str, Any]) -> None:
        try:
            calc = ExpDateCalc.life_as_percent(data.get("mfg_date"), data.get("exp_date"))
            await message.answer(f'{calc}\n/expdatecalc')
        except ValueError:
            await message.answer('Неверный формат даты.\nДата должна быть в формате ДД.ММ.ГГГГ\nПопробуйте еще раз. /expdatecalc')
            return


    # Costumer features methods 

    def mode_inline_keyboard(list: list):
        kb_builder = InlineKeyboardBuilder()
        for list_item in list:
            kb_builder.row(InlineKeyboardButton(text=list_item, callback_data=f'mode_{list_item}'))

        kb_builder.row(InlineKeyboardButton(text='Отмена', callback_data='cancel'))
        kb_builder.adjust(1)
        return kb_builder.as_markup()

    def customer_inline_keyboard(list: list):
        kb_builder = InlineKeyboardBuilder()
        for list_item in list:
            kb_builder.row(InlineKeyboardButton(text=list_item, callback_data=f'costumer_{list_item}'))

        kb_builder.row(InlineKeyboardButton(text='Отмена', callback_data='cancel'))
        kb_builder.adjust(1)
        return kb_builder.as_markup()
    
    # Enter costumer feauters method
    @dp.message(Command('costumer_features'))
    async def costumer_features_handler(message: Message, state: FSMContext) -> None:
        await message.answer("Выберите режим: ", reply_markup=AIOBot.mode_inline_keyboard(['Все особенности контрагентов', 'Поиск по названию контрагента']))

    # show all costumer features
    @dp.callback_query(F.data == 'mode_Все особенности контрагентов')
    async def show_all_costumer_features(call: CallbackQuery) -> None:
        await call.message.answer(CostumerFeatures('customer_features.docx').show_all_features())

    # Enter searching by name method
    @dp.callback_query(F.data == 'mode_Поиск по названию контрагента') 
    async def searching_customers(call: CallbackQuery, state: FSMContext) -> None:
        await call.message.answer('Введите наименование контрагента, для которого требуется список особенностей по отгрузке')
        await state.set_state(Form.costumer_handler)

    # Get costumer name
    @dp.message(Form.costumer_handler)
    async def choose_customer(message: Message, state: FSMContext) -> None:
        await state.update_data(costumer_name=message.text)
        data = await state.get_data()
        costumer_list = CostumerFeatures('customer_features.docx').find_costumer_list(data.get('costumer_name'))
        await state.clear()
        print(costumer_list)
        if not costumer_list:
            await message.answer('Нет совпадений. Проверьте наименование.\nВозможно нет такого контрагента или для него не указаны особенности \n/costumer_features')
        else:
            await message.answer(f'Выберите контрагента:\n', reply_markup=AIOBot.customer_inline_keyboard(costumer_list))

    @dp.callback_query(F.data.startswith('costumer_'))
    async def get_costumer_feature(call: CallbackQuery) -> None:
        costumer_name = call.data.replace('costumer_', '')
        await call.message.answer(f'Выбрано: {costumer_name}\n{CostumerFeatures("customer_features.docx").get_costumer_feature(costumer_name)}\n')
        await call.message.answer('/costumer_features - для другого наименования\n/cancel - для отмены')


    # Сделать функцию выводящую особенности по приемке сроков годности по договору от поставщика и условия по договору с клиентом


    


    
    async def main(self, dp=dp) -> None:
        bot = Bot(token=self.config.token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
        await dp.start_polling(bot)
    
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    new_bot = AIOBot()
    asyncio.run(new_bot.main())
        

