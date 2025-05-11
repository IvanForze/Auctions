import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from django.contrib.auth.models import AnonymousUser
from .models import Listing
from django.contrib.auth.decorators import login_required
from .views import check_session
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User

class ListingConsumer(WebsocketConsumer):
    def connect(self):
        # Получаем сессию из scope
        session = self.scope.get('session', None)
        if session:
            # Пытаемся получить user_id из сессии
            user_id = session.get('_auth_user_id')
            if user_id:
                self.user = User.objects.get(id=user_id)
            else:
                self.user = AnonymousUser()
        else:
            self.user = AnonymousUser()
        
        print(f"Connected user: {self.user}")
        print(f"Session: {session}")
        
        # Получаем название группы по ID листинга
        self.room_group_name = f'listing_{self.scope["url_route"]["kwargs"]["id"]}'
        self.id = self.scope['url_route']['kwargs']['id']
        
        # Добавляем пользователя в группу
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        # Приняли подключение
        self.accept()

        # Получаем текущую цену листинга для отправки клиенту
        listing = Listing.objects.filter(id=self.id).first()
        if listing:
            self.send(text_data=json.dumps({
                'price': str(listing.price)  # Отправляем цену на клиент
            }))
        else:
            self.send(text_data=json.dumps({
                'success': False,
                'message': 'Listing not found'
            }))

    def receive(self, text_data):
        self.user = self.scope["user"]
        print(self.user)

        if isinstance(self.user, AnonymousUser):
            listing = Listing.objects.filter(id=self.id).first()

            self.send(text_data=json.dumps({
                'success': False,
                'price': str(listing.price),
                'message': 'Authentication required'
            }))
            return

        text_data_json = json.loads(text_data)
        price = text_data_json.get('price')

        
        # Получаем листинг и проверяем, можем ли обновить цену
        listing = Listing.objects.filter(id=self.id).first()
        if not listing:
            self.send(text_data=json.dumps({
                'success': False,
                'message': 'Listing not found'
            }))

        try:
            # Преобразуем цену в float и проверяем её
            price = float(price.replace(",", "."))  # Замена запятой на точку, если необходимо
        except ValueError:
            self.send(text_data=json.dumps({
                'success': False,
                'price': str(listing.price),
                'message': 'Invalid price format'
            }))
            return

        
        
        if price > listing.price:  # Если ставка больше текущей, обновляем цену
            listing.price = price
            listing.save()

            # Отправляем обновленную цену всем клиентам в группе
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'price_update',
                    'price': str(listing.price)
                }
            )

            # Подтверждаем успешное обновление
            self.send(text_data=json.dumps({
                'success': True,
                'price': str(listing.price),
                'message': 'Your bid was placed'            
            }))
        else:
            # Если ставка меньше текущей, отправляем сообщение об ошибке
            self.send(text_data=json.dumps({
                'price': str(listing.price),
                'success': False,
                'message': 'Bid must be higher than current price'
            }))
        
            

    def price_update(self, event):
        # Отправка нового значения цены всем подключённым клиентам
        price = event['price']
        self.send(text_data=json.dumps({
            'price': price
        }))
        
    def disconnect(self, close_code):
        # Убираем пользователя из группы при отключении
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )
