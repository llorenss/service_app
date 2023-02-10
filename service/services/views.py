from django.db.models import Prefetch
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
    queryset = Subscription.objects.all().prefetch_related(
        'plan',
        Prefetch('client', queryset=Client.objects.all().select_related('user').only('company_name', 'user__email')))

    serializer_class = SubscriptionSerializer
