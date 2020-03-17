from viber.utils.common import ViberCommon
from viber.utils.api.msg_types import ViberMessageTypes
from viber.utils.api.request_sender import ViberApiRequestSender
from viber.utils.database.majilis_collection import MajilisCollection
from viber.utils.database.gazette_collections import GazetteCollection
from viber.utils.helpers.unsplash import UnsplashPhotos
from viber.utils.helpers.pixabay import PixbayVideos
from viber.utils.api.keyboards import ViberKeyboards


class ViberCommands:
    def __init__(self):
        self.auth_token = ViberCommon.viber_auth_token
        self.sender_name = ViberCommon.viber_name
        self.sender_avatar = ViberCommon.viber_avatar

    async def text_validator(self, data):
        message = data['message']['text']
        receiver = data["sender"]["id"]
        if 'tracking_data' in data['message']:
            tracking_data = data['message']['tracking_data']
            await ViberCommands().tracking_data_attendant(tracking_data, message, receiver)
        else:
            if str(message).startswith('!'):
                await ViberCommands().commands_checker(message, receiver)

    async def commands_checker(self, command, receiver):
        command = command[1:]
        if command == "bills":
            bills = await MajilisCollection().majilis_return_collection('bills_collection')
            message = await ViberMessageTypes().rich_media(receiver, bills)
            payload = await ViberCommands().prepare_payload(message=message,
                                                            sender_name=self.sender_name,
                                                            sender_avatar=self.sender_avatar,
                                                            sender=None,
                                                            receiver=receiver,
                                                            chat_id=None)
            await ViberApiRequestSender().post('send_message', payload)
        elif command == "resolutions":
            resolutions = await MajilisCollection().majilis_return_collection('resolutions_collection')
            message = await ViberMessageTypes().rich_media(receiver, resolutions)
            payload = await ViberCommands().prepare_payload(message=message,
                                                            sender_name=self.sender_name,
                                                            sender_avatar=self.sender_avatar,
                                                            sender=None,
                                                            receiver=receiver,
                                                            chat_id=None)
            await ViberApiRequestSender().post('send_message', payload)
        elif command == "emergency_debates":
            emergency_debates = await MajilisCollection().majilis_return_collection('emergency_debates_collection')
            message = await ViberMessageTypes().rich_media(receiver, emergency_debates)
            payload = await ViberCommands().prepare_payload(message=message,
                                                            sender_name=self.sender_name,
                                                            sender_avatar=self.sender_avatar,
                                                            sender=None,
                                                            receiver=receiver,
                                                            chat_id=None)
            await ViberApiRequestSender().post('send_message', payload)
        elif command == "approvals":
            approvals = await MajilisCollection().majilis_return_collection('approvals_collection')
            message = await ViberMessageTypes().rich_media(receiver, approvals)
            payload = await ViberCommands().prepare_payload(message=message,
                                                            sender_name=self.sender_name,
                                                            sender_avatar=self.sender_avatar,
                                                            sender=None,
                                                            receiver=receiver,
                                                            chat_id=None)
            await ViberApiRequestSender().post('send_message', payload)
        elif command == "others":
            others = await MajilisCollection().majilis_return_collection('others_collection')
            message = await ViberMessageTypes().rich_media(receiver, others)
            payload = await ViberCommands().prepare_payload(message=message,
                                                            sender_name=self.sender_name,
                                                            sender_avatar=self.sender_avatar,
                                                            sender=None,
                                                            receiver=receiver,
                                                            chat_id=None)
            await ViberApiRequestSender().post('send_message', payload)
        elif command == "gazette":
            gazette = await GazetteCollection().gazette_return_collection()
            keyboard = await ViberKeyboards().gazette_keyboard(gazette)
            message = await ViberMessageTypes().text_message(
                receiver,
                'Here are the Latest 10 Articles from Gazettes',
                'gazette',
                keyboard
            )
            payload = await ViberCommands().prepare_payload(message=message,
                                                            sender_name=self.sender_name,
                                                            sender_avatar=self.sender_avatar,
                                                            sender=None,
                                                            receiver=receiver,
                                                            chat_id=None)
            await ViberApiRequestSender().post('send_message', payload)
        elif command == "photo":
            photo = await UnsplashPhotos().random_photo()
            message = await ViberMessageTypes().picture_message(
                receiver,
                f"{photo['title']} by {photo['username']} on Unsplash",
                photo['link'],
                photo['thumb'],
                None,
                None
            )
            payload = await ViberCommands().prepare_payload(message=message,
                                                            sender_name=self.sender_name,
                                                            sender_avatar=self.sender_avatar,
                                                            sender=None,
                                                            receiver=receiver,
                                                            chat_id=None)
            await ViberApiRequestSender().post('send_message', payload)
        elif command == 'video':
            video = await PixbayVideos().get_random_video()
            message = await ViberMessageTypes().video_message(
                receiver,
                video['url'],
                video['size'],
                video['thumb'],
                video['duration'],
                None,
                None
            )
            payload = await ViberCommands().prepare_payload(message=message,
                                                            sender_name=self.sender_name,
                                                            sender_avatar=self.sender_avatar,
                                                            sender=None,
                                                            receiver=receiver,
                                                            chat_id=None)
            await ViberApiRequestSender().post('send_message', payload)

    async def tracking_data_attendant(self, tracking_data, message, receiver):
        if tracking_data == 'gazette':
            gazette = await GazetteCollection().gazette_return_collection()
            if str(message).isnumeric():
                tracked_gazette = gazette[int(message)]
                message = await ViberMessageTypes().file_message(receiver, tracked_gazette['link'], None, None)
                payload = await ViberCommands().prepare_payload(message=message,
                                                                sender_name=self.sender_name,
                                                                sender_avatar=self.sender_avatar,
                                                                sender=None,
                                                                receiver=receiver,
                                                                chat_id=None)
                await ViberApiRequestSender().post('send_message', payload)

    async def prepare_payload(self, message, sender_name, sender_avatar, sender=None, receiver=None, chat_id=None):
        payload = message
        payload.update({
            'auth_token': self.auth_token,
            'from': sender,
            'receiver': receiver,
            'sender': {
                'name': sender_name,
                'avatar': sender_avatar
            },
            "chat_id": chat_id
        })

        return await ViberCommands()._remove_empty_fields(payload)

    async def _remove_empty_fields(self, message):
        return {k: v for k, v in message.items() if v is not None}
