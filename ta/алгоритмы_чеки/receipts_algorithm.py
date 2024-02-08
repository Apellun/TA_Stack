from collections import defaultdict
from typing import List, DefaultDict
from const import RECEIPTS_PATH, ACCOUNTS_PATH, SERVICES, MONTHS

#COMMENT: Я предположила, что итоговый файл "чеки по папкам" создается новый для каждого
# года, поэтому алгоритм каждый раз перезаписывает его.
def get_default_dict(months_list: List, services_list: List) -> DefaultDict:
    """
    Возвращает словарь со всеми ожидаемыми платежами по каждому месяцу.
    """
    if not months_list:
        print("Список месяцев не может быть пустым")
        return
    if not services_list:
        print("Список услуг не может быть пустым")
        return
    
    default_accounts_dict = defaultdict(lambda: defaultdict(str))

    for month in months_list:
        for service in services_list:
            default_accounts_dict[month][service] = 0
            
    return default_accounts_dict
    

def get_accounts(default_accounts_dict: DefaultDict, receipts_file_path: str) -> DefaultDict:
    """
    Считывает чеки и добавляет информацию о каждом чеке в словарь по ключу месяца и услуги.
    Неоплаченные услуги остаются с пустыми значениями. Возвращает
    словарь с полной информацией по оплаченным и неоплаченным услугам.
    """
    if not default_accounts_dict:
        print("Список ожидаемых платежей не может быть пустым")
        return
    if not receipts_file_path:
        print("Адрес файла с чеками не может быть пустой строкой")
        return
    
    try:
        with open (receipts_file_path, 'r', encoding='utf-8-sig') as receipts:
            for file in receipts:
                service = file.split("_")[0]
                month = file.split("_")[1].split(".")[0]
                
                if not file.endswith("\n"):
                    default_accounts_dict[month][service] = f"{file}\n"
                else:
                    default_accounts_dict[month][service] = file
                    
        return default_accounts_dict
    
    except Exception as e:
        print(f"Ошибка во время обработки файла: {e}")
        return
    

def output_accounts(accounts_dict: DefaultDict, accounts_file_path: str) -> None:
    """
    Выводит отсортированную информацию по платежам в файл чеки_по_папкам.
    Неоплаченные в каждом месяце услуги соединяет в строку и прикрепляет в
    концу файла.
    """
    if not accounts_dict:
        print("Список платежей не может быть пустым")
        return
    if not accounts_file_path:
        print("Адрес файла для вывода не может быть пустой строкой")
        return
    
    try:
        with open (accounts_file_path, 'w') as sorted:
            unpaid = f"не оплачены:\n"
            
            for month in accounts_dict:
                month_unpaid = f"{month}:\n"
                
                for service in accounts_dict[month]:
                    file = accounts_dict[month][service]
                    if file:
                        sorted.write(f"/{month}/{file}")
                    else:
                        month_unpaid += f"{service}\n"
                
                if month_unpaid != f"{month}:\n":
                    unpaid += month_unpaid
                
            sorted.write(unpaid)
            
    except Exception as e:
        print(f"Ошибка во время обработки платежей: {e}")
        return
        

if __name__ == "__main__":
    
    default_accounts_dict = get_default_dict(MONTHS, SERVICES)
    accounts_dict = get_accounts(default_accounts_dict, RECEIPTS_PATH)
    output_accounts(accounts_dict, ACCOUNTS_PATH)
        

