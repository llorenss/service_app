from django.conf import settings
from django.core.cache import cache
from django.db.models import Prefetch, Sum
from rest_framework.viewsets import ReadOnlyModelViewSet

from clients.models import Client
from services.models import Subscription
from services.serializers import SubscriptionSerializer


class SubscriptionView(ReadOnlyModelViewSet):
    # Достаём все поля.
    # queryset = Subscription.objects.all().prefetch_related('client').prefetch_related('client__user')

    # Оптимизируем. Только нужные поля получаем. Без учёта PlanSerializer (до его создания). Избегаем n+1.
    # Запросы не будут перемножаться при увеличении количества данных

    # Резюме:
    # Prefetch() - избегаем n+1.
    # only() - получаем только нужные поля.

    # queryset = Subscription.objects.all().prefetch_related(
    #     Prefetch('client', queryset=Client.objects.all().select_related('user').only('company_name', 'user__email')))

    # Оптимизируем. Только нужные поля получаем. C учётом PlanSerializer
    # Использовали class Prefetch
    # queryset = Subscription.objects.all().prefetch_related(
    #     'plan',
    #     Prefetch('client', queryset=Client.objects.all().select_related('user').only('company_name', 'user__email')))

    # Делаем вычисления прям в бд. Мето .annotate()
    # .F() - функция с помощью которой обращаемся к одной из полей бд
    queryset = (
        Subscription.objects.all().prefetch_related(
            "plan",
            Prefetch(
                "client",
                queryset=Client.objects.all()
                .select_related("user")
                .only("company_name", "user__email"),
            ),
        )
        # temp comment annotate 6 lesson for use flower
        # .annotate(
        #     price=F("service__full_price")
        #     - F("service__full_price") * F("plan__discount_percent") / 100.00
        # )
        # 6 lesson for use flower
    )

    serializer_class = SubscriptionSerializer

    # Переопределяем метод вью и формируется новый ответ клиенту.
    # вот этот вариант ничего не помняет.
    # def list(self, request, *args, **kwargs):
    #     response = super().list(request, *args, **kwargs)
    #     return response

    # меняем всю структуру отдаваемых данных
    # крайне не рекомендуется, без острой необходимости.
    # со всеми (фронт, апи пользователи) согласуется.
    # def list(self, request, *args, **kwargs):
    #     response = super().list(request, *args, **kwargs)
    #
    #     response_data = {"result": response.data}
    #     response.data = response_data
    #     return response

    # Зачем всё это?
    # Чтобы к result добавить данных
    # Агрегация - суммарная инфо по всем записям sql
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset((self.get_queryset()))
        response = super().list(request, *args, **kwargs)

        price_cache = cache.get(settings.PRICE_CACHE_NAME)

        if price_cache:
            total_price = price_cache
        else:
            total_price = queryset.aggregate(total=Sum("price")).get("total")
            cache.set(settings.PRICE_CACHE_NAME, total_price, 60 * 60)
        response_data = {
            "result": response.data,
            "total_amount": total_price,
        }
        response.data = response_data
        return response

    # Урок 4 завершён
