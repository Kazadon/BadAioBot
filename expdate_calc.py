from datetime import datetime

# Return remaining shelf life as a percentage
class ExpDateCalc:
    def life_as_percent(mfg_date: str, exp_date: str) -> str:
        mfg_date = datetime.strptime(mfg_date, '%d.%m.%Y')
        exp_date = datetime.strptime(exp_date, '%d.%m.%Y')
        current_date = datetime.now()
        if mfg_date > current_date:
            return "Дата производства не может быть больше текущей даты. Проверьте введенные данные и попробуйте заново"
        elif mfg_date > exp_date:
            return "Дата производства не может быть больше даты окончания срока годности. Проверьте введенные данные и попробуйте заново"
        elif mfg_date == exp_date:
            return 'Дата производства и окончания срока годности не может быть одинаковой. Попробуйте другие данные.'
        else: 
            diff_days_exp_mfg = (exp_date - mfg_date)
            diff_days_exp_now = (exp_date - current_date)
            result = diff_days_exp_now/diff_days_exp_mfg*100
            return f'Остаточный срок годности на сегодняшний день: {result:.2f}%' if result >= 0 else f"Товар уже просрочен"