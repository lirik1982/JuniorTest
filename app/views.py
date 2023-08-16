import base64
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Sum, Count
from django.db import transaction

from datetime import datetime
from collections import defaultdict
import csv
import io

from .models import Deal
import redis
import pickle


class EnterPoint(APIView):

    REDIS_CONN_POOL = redis.ConnectionPool(
        host='redislocal', port=6379, decode_responses=True)

    @transaction.non_atomic_requests
    def post(self, request, format=None):
        # если ниже ошибка, то атомик откатит изменени
        Deal.objects.all().delete()

        file = request.FILES.get('file')
        if not file:
            return Response('Ошибка в оформлении запроса',
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)

        try:
            file_wrapper = io.TextIOWrapper(file, encoding='utf-8')
            reader = csv.DictReader(file_wrapper)
            for row in reader:
                customer = row['customer']
                item = row['item']
                total = int(row['total'])
                quantity = int(row['quantity'])
                date = datetime.strptime(row['date'], '%Y-%m-%d %H:%M:%S.%f')
                deal = Deal(
                    customer=customer,
                    item=item,
                    total=total,
                    quantity=quantity,
                    date=date,
                )
                deal.save()

            try:
                r = redis.Redis(connection_pool=self.REDIS_CONN_POOL)
                r.delete('clients')
            except ConnectionError as e:
                print(f'Redis Connection Error, Desc: {str(e)}')
            except KeyError:
                pass

            return Response({'status': "OK"}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                f'Status: Error, Desc: {str(e)}',
                status=status.HTTP_400_BAD_REQUEST,
            )

    def get(self, request):
        # Проверяем есть ли решение в кэше, если да то берем его
        try:
            r = redis.Redis(connection_pool=self.REDIS_CONN_POOL)
            list_clients = r.get('clients')
            if list_clients:
                decoded = base64.b64decode(list_clients)
                list_clients = pickle.loads(decoded)
                return Response(
                    {'response': list_clients},
                    status=status.HTTP_200_OK
                )
        except ConnectionError as e:
            print(f'Redis Connection Error, Desc: {str(e)}')

        except KeyError:
            pass

        if not Deal.objects.all():
            return Response({'response': None},
                            status=status.HTTP_204_NO_CONTENT)

        # добавляем новое поле, суммируем траты, сортируем и срезаем 5
        best_of = (
            Deal.objects.values('customer')
            .annotate(
                spent_money=Sum('total')
            )
            .order_by('-spent_money')[: 5]
        )

        # имена лучших 5
        best_names = [client.get('customer') for client in best_of]

        best_gems = (
            # выборка сделок с лучшими покупателями
            Deal.objects.filter(customer__in=best_names)
            # среди лучших создаем словарь по полю item
            .values('item')
            # создаем новое поле с подсчетом customer без дублей
            .annotate(count=Count('customer', distinct=True))
            # фильтр больше либо равно 2
            .filter(count__gte=2)
            # получаем итоговый кортеж моделм
            .values_list('item', flat=True)
        )

        repeated_gems = (
            # выборка элементов из лучших
            Deal.objects.filter(item__in=best_gems)
            # словарь из лучших элементов и клиентов
            .values('customer', 'item')
            # сортируем по клиентам
            .order_by('customer')
            # убираем дубли
            .distinct()
        )

        # определяем словарь со значениями по умолчанию
        repeated_gems_by_customers = defaultdict(list)

        # наполняем словарь парой заказчик и товар
        for row in repeated_gems:
            customer, item = row['customer'], row['item']
            repeated_gems_by_customers[customer].append(item)

        best_out = []
        for client in best_of:
            username = client['customer']
            spent_money = client['spent_money']
            best_out.append(
                {
                    'username': username,
                    'spent_money': spent_money,
                    'gems': repeated_gems_by_customers[username],
                }
            )

        # сохраняем решение в кэш
        try:
            encoded = base64.b64encode(pickle.dumps(best_out))
            r.set('clients', encoded)
        except ConnectionError as e:
            print(f'Redis Connection Error, Desc: {str(e)}')

        return Response({'response': best_out}, status=status.HTTP_200_OK)
