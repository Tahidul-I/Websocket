import json
from channels.generic.websocket import AsyncWebsocketConsumer
from datetime import datetime

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        if self.room_name == 'admin_group':
            self.room_group_name = 'admin_group'
        else:
            self.room_group_name = f'chat_{self.room_name}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        sender = text_data_json.get('sender', 'Anonymous')
        timestamp = text_data_json.get('timestamp', datetime.now().isoformat())
        is_new_room = text_data_json.get('is_new_room', False)

        print("******************************************************************CHECK UPDATE *************************")
        print(is_new_room)

        # Send the message to the relevant room
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': sender,
                'timestamp': timestamp
            }
        )
        
        # Notify all admins about the new chat room
        await self.channel_layer.group_send(
            'admin_group',  # A common group for all admins
            {
                'type': 'new_chat_room',
                'room_name': self.room_name,
                'timestamp': timestamp
            }
        )

    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']
        timestamp = event['timestamp']
        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender,
            'timestamp': timestamp
        }))

    async def new_chat_room(self, event):
        room_name = event['room_name']
        timestamp = event['timestamp']
        await self.send(text_data=json.dumps({
            'type': 'new_chat_room',
            'room_name': room_name,
            'timestamp': timestamp
        }))
