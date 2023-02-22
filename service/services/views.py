from django.db.models import Prefetch, F
from django.shortcuts import render
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
        Subscription.objects.all()
        .prefetch_related(
            "plan",
            Prefetch(
                "client",
                queryset=Client.objects.all()
                .select_related("user")
                .only("company_name", "user__email"),
            ),
        )
        .annotate(
            price=F("service__full_price")
            - F("service__full_price") * F("plan__discount_percent") / 100.00
        )
    )

    serializer_class = SubscriptionSerializer
