import os

import ydb

YDB_ENDPOINT = os.getenv("YDB_ENDPOINT")
YDB_DATABASE = os.getenv("YDB_DATABASE")


def get_ydb_pool(ydb_endpoint, ydb_database, timeout=30):
    ydb_driver_config = ydb.DriverConfig(
        ydb_endpoint,
        ydb_database,
        credentials=ydb.credentials_from_env_variables(),
        root_certificates=ydb.load_ydb_root_certificate(),
    )

    ydb_driver = ydb.Driver(ydb_driver_config)
    ydb_driver.wait(fail_fast=True, timeout=timeout)
    return ydb.SessionPool(ydb_driver)


def _format_kwargs(kwargs):
    return {"${}".format(key): value for key, value in kwargs.items()}


# Заготовки из документации
# https://ydb.tech/en/docs/reference/ydb-sdk/example/python/#param-prepared-queries
def execute_update_query(pool, query, **kwargs):
    def callee(session):
        prepared_query = session.prepare(query)
        session.transaction(ydb.SerializableReadWrite()).execute(
            prepared_query, _format_kwargs(kwargs), commit_tx=True
        )

    return pool.retry_operation_sync(callee)


# Заготовки из документации
# https://ydb.tech/en/docs/reference/ydb-sdk/example/python/#param-prepared-queries
def execute_select_query(pool, query, **kwargs):
    def callee(session):
        prepared_query = session.prepare(query)
        result_sets = session.transaction(ydb.SerializableReadWrite()).execute(
            prepared_query, _format_kwargs(kwargs), commit_tx=True
        )
        return result_sets[0].rows

    return pool.retry_operation_sync(callee)


# Зададим настройки базы данных 
pool = get_ydb_pool(YDB_ENDPOINT, YDB_DATABASE)

# Структура квиза
quiz_data = [
    {
        'question': 'Что такое Python?',
        'options': ['Язык программирования', 'Тип данных', 'Музыкальный инструмент', 'Змея на английском'],
        'correct_option': 0
    },
    {
        'question': 'Какой тип данных используется для хранения целых чисел?',
        'options': ['int', 'float', 'str', 'natural'],
        'correct_option': 0
    }
    ,
    {
        'question': 'Требуется ли использовать ГОСТы при оформлении документации на программный продукт?',
        'options': ['Да', 'Нет'],
        'correct_option': 0
    },
    {
        'question': 'Какая структура данных наиболее часто используется в Pandas?',
        'options': ['Tuple', 'Collection', 'DataFrame', 'List'],
        'correct_option': 2
    },
    {
        'question': 'Выберите правильное название переменной в Python.',
        'options': ['iAmVariable', '123_data', 'im_variable', 'save_data_'],
        'correct_option': 2
    },
    {
        'question': 'Изменяемый ли тип данных String в Python?',
        'options': ['Да', 'Нет'],
        'correct_option': 1
    },
    {
        'question': 'Какая коллекция отсутствует в Python?',
        'options': ['Tuple', 'List', 'Dictionary', 'MutableSet'],
        'correct_option': 3
    },
    {
        'question': 'Какую задачу решает обучение с учителем?',
        'options': ['Регрессии', 'Кластеризации', 'Поиска аномалий', 'Получения максимальной выгоды'],
        'correct_option': 0
    },
    {
        'question': 'Для чего используется библиотка NumPy в Python?',
        'options': ['Построение графиков', 'Проведение вычислений', 'Машинное обучение'],
        'correct_option': 1
    },
    {
        'question': 'Для чего используется библиотка scikit-learn в Python?',
        'options': ['Построение графиков', 'Проведение вычислений', 'Машинное обучение'],
        'correct_option': 2
    },
]
