<h1>ТЕСТОВОЕ ЗАДАНИЕ на позицию 
Junior Python разработчик 
</h1>
<br>

<h3>📝Реализация веб-сервиса на базе django, предоставляющего REST-api и способного: </h3>
1.	Принимать из POST-запроса .csv файлы для дальнейшей обработки;
2.	Обрабатывать типовые deals.csv файлы, содержащие истории сделок;
3.	Сохранять извлеченные из файла данные в БД проекта;
4.	Возвращать обработанные данные в ответе на GET-запрос.
1.	Данные хранятся в реляционной БД, взаимодействие с ней осуществляется посредством django ORM.
2.	Ранее загруженные версии файла deals.csv не должны влиять на результат обработки новых.
3.	Эндпоинты соответствуют спецификации:

<b>Выдача обработанных данных</b>
Метод: GET
В ответе содержится поле “response” со списком из 5 клиентов, потративших наибольшую сумму за весь период.
Каждый клиент описывается следующими полями:
●	username - логин клиента;
●	spent_money - сумма потраченных средств за весь период;
●	gems - список из названий камней, которые купили как минимум двое из списка "5 клиентов, потративших наибольшую сумму за весь период", и данный клиент является одним из этих покупателей.

