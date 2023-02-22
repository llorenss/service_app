from rest_framework import serializers

from services.models import Subscription, Plan


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = ('__all__')


class SubscriptionSerializer(serializers.ModelSerializer):
    plan = PlanSerializer()
    client_name = serializers.CharField(source='client.company_name')
    email = serializers.CharField(source='client.user.email')

    # Метод соглашения имён. Переменная price по ней программа сама
    # разыскивает функцию ожидая перед названием переменной get_ .
    price = serializers.SerializerMethodField()

    def get_price(self, instance):
        # instance - конкретная модель подписки, которую будет обрабатывать
        # api все модели показывает
        return (instance.service.full_price -
                instance.service.full_price * (instance.plan.discount_percent / 100))

    class Meta:
        model = Subscription
        fields = ('id', 'plan_id', 'client_name', 'email', 'plan', 'price')