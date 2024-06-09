REST API сервис для распределения заказов по курьерам. 

Курьеры могут брать и завершать заказы. У курьера есть своя карточка с информацией: среднее выполнение заказа и среднее количество завершенных заказов в день. Курьер может выполнять максимум один заказ одновременно.

Реализованы следующие эндпоинты:
api/couriers:
1) POST /courier
  Регистрация курьера в системе. 
  Поля: name: str - имя курьера 
        districts: list[str] - массив районов. 
  Заказ и курьер должны иметь общий район.
2) GET /courier 
  Получение информации о всех курьеров системе. 
  Ожидаемые поля: id: UUID 
                  name: str - имя курьера.
3) GET /courier/{id} 
  Получение подробной информации о курьере
    id: UUID - уникальный идентификатор.
    name: str - имя курьера
    active_order: dict - информация об активном заказе. Если такого нет, возвращать None {"order_id": ид заказа, "order_name": имя заказа }
    avg_order_complete_time: datetime - среднее время отработки заказа
    avg_day_orders: int - среднее кол-во завершенных заказов в день.
  
api/orders:
4) POST /order 
  Публикация заказа в системе с полями: 
    name: str - имя заказа 
    district: str - район заказа. 
  В случае, если удалось найти подходящего курьера, запрос возвращает order_id (ид заказа) и courier_id( ид курьера). Если подходящего курьера нет, то запрос возвращает ошибку.
  
5) GET /order/{id}
   Получение информации о заказе:
     courier_id: UUID
     status:int - статус заказа. 1 - в работе, 2 - завершен.
6) POST /order/{id}
    Завершить заказ. Должен вернуть ошибку если заказ уже завершен или такого заказа нет.

Для пересчёта среднего кол-ва завершенных заказов в день и среднего времени выполнения используется celery и redis (tasks/tasks).
Релизованы следующие функции: 
1) post_order
   Размещение в ежедневной записи в редисе данных о зарегестрированном заказе
     item: dict
  При этом под item ожидается следующий словарь:
     "courier_id": UUID,
     "start_time": DateTime,
     "lead_time": DateTime,
     "status": int,
     "order_id": UUID

При этом используется функция update_daily_record
   data: dict,
   current_date: str

   В качестве data передаётся item, в качестве current_date передается str(datetime.now().date().isoformat())

2) close_order
   courier_id: UUID,
   order_id: UUID,
   close_time: DateTime
   
  Обновление данных lead_time и status о заказе order_id в ежедневной записи в редисе.
  Обновление данных о курьере courier_id в записи редиса:
    'start_work': str(DateTime),
    'all_time': str(lead_time),
    'avg_time': str(lead_time),
    'all_orders': int,
    'avg_orders_closed': int
  И обновление полей базе данных avg_order_complete_time и avg_day_orders у этого курьера

Отследить процессы celery можно с помощью flower на хосту 5555

#Запуск контейнеров
docker-compose up -d
