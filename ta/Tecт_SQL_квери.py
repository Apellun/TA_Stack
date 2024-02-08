'''== Задание 1.

Написать функцию stack.select_count_pok_by_service. Она получает номера услуг строкой и дату
и возвращает количество показаний по услуге для каждого лицевого 
Результатом вызова
функции должна быть таблица с 4 колонками:
- acc (Лицевой счет)
- serv (Услуга)
- count (Количество показаний)

Примеры вызова функции:

select * from stack.select_count_pok_by_service('300','20230201')
--number|service|count
--111	300	2
--144	300	1
--211	300	2
--222	300	2
--233	300	1
--244	300	1
--255	300	3
--266	300	3
--277	300	2
--288	300	4
--301	300	1 '''

select_count_pok_by_service = '''
    CREATE OR REPLACE FUNCTION stack.select_count_pok_by_service(service_numbers text, pok_date_str text)
    RETURNS TABLE(number int, service int, count bigint) AS $$
    DECLARE
        pok_date date;
    BEGIN
        pok_date := TO_DATE(pok_date_str, 'YYYYMMDD');
        RETURN QUERY
        SELECT
            accounts.number AS acc,
            counters.service AS serv,
            COUNT(meter_pok.row_id) AS count
        FROM
            stack.Accounts accounts
        JOIN
            stack.Counters counters ON accounts.row_id = counters.acc_id
        LEFT JOIN
            stack.Meter_Pok meter_pok ON counters.row_id = meter_pok.counter_id
        WHERE
            counters.service = ANY(string_to_array(service_numbers, ',')::int[])
            AND (meter_pok.date = pok_date OR meter_pok.month = pok_date)
        GROUP BY
            accounts.number, counters.service;
    END;
    $$ LANGUAGE plpgsql;
'''

'''
-------------------------------------------------------------------
== Задание 2

Написать функцию select_value_by_house_and_month. Она получает номер дома
и месяц
и возвращает все лицевые в этом доме , для лицевых выводятся все счетчики с
сумарным расходом за месяц ( суммирую все показания тарифов)
Результатом вызова
функции должна быть таблица с 3 колонками:

- acc (Лицевой счет)
- name (Наименование счетчика)
- value (Расход)

Примеры вызова функции:

select * from stack.select_last_pok_by_service(1,'20230201')
--number|name|value
--111	Счетчик на воду	150
--111	Счетчик на отопление	-50
--111	Счетчик на электричество	80
--122	Счетчик на воду	105
--122	Счетчик на отопление	0
--133	Счетчик на воду	900
--133	Счетчик на отопление	-1
--144	Счетчик на воду	0
--144	Счетчик на отопление	10
--144	Счетчик на электричество	100
'''
# COMMENT не очень поняла условие тут, номера домов вроде отсутствуют в таблице, есть только номера
# строк для счетов, привязанных к дому. я сделала запрос, который будет принимать такой номер
# строки и показывать данные по счетам всех детей (квартир) и детей детей (счетов) строки по "номеру дома"
# + самой строки по переданному номеру.

select_value_by_house_and_month ='''
    CREATE OR REPLACE FUNCTION stack.select_value_by_house_and_month(house_number int, acc_month_str text)
    RETURNS TABLE(acc int, name text, value bigint) AS $$
    BEGIN
    RETURN QUERY
        SELECT
            accounts.number AS acc,
            counters.name,
            SUM(meter_pok.value)
        FROM
            stack.Accounts accounts
        JOIN
            stack.Counters counters ON accounts.row_id = counters.acc_id
        JOIN
            stack.Meter_Pok meter_pok ON counters.row_id = meter_pok.counter_id
        WHERE
            accounts.row_id = house_number
            OR accounts.parent_id = house_number
            OR accounts.parent_id IN (
                SELECT row_id
                FROM stack.Accounts
                WHERE parent_id = house_number
            )
        AND meter_pok.month = TO_DATE(acc_month_str, 'YYYYMMDD')
        GROUP BY
                    accounts.number, counters.name
                ORDER BY acc ASC;
            END;
            $$ LANGUAGE plpgsql;
'''

'''
== Задание 3
Написать функцию stack.select_last_pok_by_acc. Она получает номер лицевого
и возвращает дату,тариф,объем последнего показания по каждой услуге
Результатом вызова
функции должна быть таблица с 5 колонками:
- acc (Лицевой счет)
- serv (Услуга)
- date (Дата показания)
- tarif (Тариф показания)
- value (Объем)
Примеры вызова функции:
select * from select_last_pok_by_acc(144)
--acc|serv|date|tarif|value|
--144	100	2023-02-21	1	0
--144	200	2023-02-27	1	0
--144	300	2023-02-28	1	100
--144	400	2023-02-26	1	10
select * from select_last_pok_by_acc(266)
--266	300	2023-02-27	1	-90
--266	300	2023-02-27	2	0
--266	300	2023-02-27	3	13
'''

select_last_pok_by_acc = '''
    CREATE OR REPLACE FUNCTION stack.select_last_pok_by_acc(account_id integer)
    RETURNS TABLE(acc int, serv int, date date, tarif int, value int) as $$
    BEGIN
        RETURN QUERY
            WITH
            latest_entries AS (
                SELECT counter_id, meter_pok.tarif, MAX(meter_pok.date) as max_date
                FROM stack.meter_pok
                GROUP BY counter_id, meter_pok.tarif
            ),
            serv AS (
                SELECT Counters.service, meter_pok.counter_id
                FROM stack.meter_pok
                JOIN stack.Counters ON meter_pok.counter_id = Counters.row_id
            )
            SELECT
                Accounts.number, serv.service, meter_pok.date, meter_pok.tarif, meter_pok.value
            FROM
                stack.meter_pok
            JOIN
                stack.Accounts ON meter_pok.acc_id = Accounts.row_id
            JOIN
                serv ON meter_pok.counter_id = serv.counter_id
            JOIN
                latest_entries ON meter_pok.counter_id = latest_entries.counter_id 
                AND meter_pok.date = latest_entries.max_date 
                AND meter_pok.tarif = latest_entries.tarif
            WHERE
                Accounts.number = account_id
            GROUP BY
                Accounts.number, serv.service, meter_pok.date, meter_pok.tarif, meter_pok.value;
    END; $$
    LANGUAGE plpgsql;
'''