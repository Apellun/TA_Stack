from pathlib import Path

BASE_PATH = Path(__file__).parent.resolve()
RECEIPTS_PATH = str(BASE_PATH / 'чеки.txt')
ACCOUNTS_PATH = str(BASE_PATH / 'чеки_по_папкам.txt')

MONTHS = (
    'январь', 'февраль', 'март', 'апрель',
    'май', 'июнь', 'июль', 'август',
    'сентябрь', 'октябрь', 'ноябрь', 'декабрь')

SERVICES = [
    'газоснабжение', 'ГВС', 'домофон',
    'капремонт', 'квартплата', 'ТБО',
    'теплоснабжение', 'ХВС', 'электроснабжение'
]