from telethon import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest

from config import username, api_id, api_hash


def get_messages(url, limit=100):
    """Get LIMIT messages from Telegram channel with given URL."""
    client = TelegramClient(username, api_id, api_hash)

    async def get_channel_data():
        nonlocal client
        channel = await client.get_entity(url)
        history = await client(GetHistoryRequest(
            peer=channel,
            offset_id=0,
            offset_date=None,
            add_offset=0,
            limit=limit,
            max_id=0,
            min_id=0,
            hash=0
        ))
        return history.messages

    with client:
        return client.loop.run_until_complete(get_channel_data())