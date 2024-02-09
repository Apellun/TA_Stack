from collections import defaultdict
import copy
from const import RECEIPTS_PATH, ACCOUNTS_PATH, SERVICES, MONTHS


class ReceiptManager:
    def __init__(self):
        self.months_list = MONTHS
        self.services_list = SERVICES
        self._default_accounts_dict = None
        self.accounts_dict = None
    
    def _get_default_dict(self) -> None:
        """
        Создает базовый словарь со всеми ожидаемыми платежами по каждому месяцу.
        """
        default_accounts_dict = defaultdict(lambda: defaultdict(str))

        for month in self.months_list:
            for service in self.services_list:
                default_accounts_dict[month][service] = 0
        self._default_accounts_dict = default_accounts_dict
        self.accounts_dict = copy.deepcopy(default_accounts_dict)

    def _get_accounts(self, receipts_file_path: str) -> None:
        """
        Считывает чеки и добавляет информацию о каждом чеке в словарь по ключу месяца и услуги.
        Неоплаченные услуги остаются с пустыми значениями. Создает
        словарь с полной информацией по оплаченным и неоплаченным услугам.
        """
        with open (receipts_file_path, 'r', encoding='utf-8-sig') as receipts:
            for file in receipts:
                service = file.split("_")[0]
                month = file.split("_")[1].split(".")[0]
                
                if not file.endswith("\n"):
                    self.accounts_dict[month][service] = f"{file}\n"
                else:
                    self.accounts_dict[month][service] = file
        
    def _output_accounts(self, accounts_file_path: str) -> None:
        """
        Выводит отсортированную информацию по платежам в файл чеки_по_папкам.
        Неоплаченные в каждом месяце услуги соединяет в строку и прикрепляет в
        концу файла. Я предположила, что итоговый файл "чеки по папкам" создается
        новый для каждого года, поэтому метод каждый раз перезаписывает его.
        """
        with open (accounts_file_path, 'w') as sorted:
            unpaid = f"не оплачены:\n"
            
            for month in self.accounts_dict:
                month_unpaid = f"{month}:\n"
                
                for service in self.accounts_dict[month]:
                    file = self.accounts_dict[month][service]
                    if file:
                        sorted.write(f"/{month}/{file}")
                    else:
                        month_unpaid += f"{service}\n"
                        
                if month_unpaid != f"{month}:\n":
                    unpaid += month_unpaid
            sorted.write(unpaid)
        
    def manage_receipts(self, receipts_file_path: str, accounts_file_path: str) -> None:
        """
        Проверяет наличие базового словаря, если его нет — вызывает метод создания,
        если есть — заменяет словарь с данными по платежам от предыдущего использования
        на базовый. Затем проверяет строки путей и вызывает методы для обработки чеков.
        """
        if not self._default_accounts_dict:
            self._get_default_dict()
        else:
            self.accounts_dict = copy.deepcopy(self.default_accounts_dict)
    
        if not receipts_file_path:
            print("Адрес файла с чеками не может быть пустой строкой")
            return
        if not accounts_file_path:
            print("Адрес файла для вывода не может быть пустой строкой")
            return
        
        try:
            self._get_accounts(receipts_file_path)
        except Exception as e:
            print(f"Ошибка во время обработки чеков: {e}")
        try: 
            self._output_accounts(accounts_file_path)
        except Exception as e:
            print(f"Ошибка во время вывода данных по чекам: {e}")
        

if __name__ == "__main__":
    manager = ReceiptManager()
    manager.manage_receipts(RECEIPTS_PATH, ACCOUNTS_PATH)
        

