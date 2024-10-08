import threading
import httpx
import asyncio
import schedule
import time
from tenacity import retry, wait_fixed, stop_after_attempt


async def send_telegram_message(text):
    bot_token = '6865909648:AAE00lypiX55PmDV-O36BrH0RqzBfbYJfXo'
    chat_id = '-1002018966301'
    data = {
        'chat_id': chat_id,
        'text': text
    }
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data)
            response.raise_for_status()
    except httpx.RequestError as e:
        print(f"Error sending Telegram message: {e}")


@retry(wait=wait_fixed(5), stop=stop_after_attempt(4))
async def open_shift():
    try:
        async with httpx.AsyncClient() as client:
            open_shift_response = await client.post('http://185.39.79.6:1234/api/Shift/OpenShift?cashierCode=1', timeout=20)
            open_shift_response.raise_for_status()
        await send_telegram_message(f'Смена открыта')
    except httpx.RequestError as e:
        await send_telegram_message(f'Смена не открылась, пожалуйста проверьте. Ошибка {e}')


@retry(wait=wait_fixed(5), stop=stop_after_attempt(4))
async def close_shift():
    try:
        async with httpx.AsyncClient() as client:
            close_shift_response = await client.post('http://185.39.79.6:1234/api/Shift/CloseShift?cashierCode=1', timeout=20)
            close_shift_response.raise_for_status()
        await send_telegram_message(f'Смена закрыта')
    except httpx.RequestError as e:
        await send_telegram_message(f'Смена не закрылась, пожалуйста проверьте. Ошибка {e}')


@retry(wait=wait_fixed(5), stop=stop_after_attempt(4))
async def keep_awake():
    try:
        async with httpx.AsyncClient() as client:
            keep_awake_response = await client.get('http://185.39.79.6:1234/api/Service/State', timeout=20)
            keep_awake_response.raise_for_status()
        await send_telegram_message(f'Проверка ККМ: работает успешно')
    except httpx.RequestError as e:
        await send_telegram_message(f'Проверка ККМ: что-то не так, пожалуйста проверьте. Ошибка {e}')


def run_scheduler():
    schedule.every().day.at("00:00").do(lambda: asyncio.create_task(open_shift()))
    schedule.every().day.at("23:59").do(lambda: asyncio.create_task(close_shift()))
    schedule.every().hour.do(lambda: asyncio.create_task(keep_awake()))

    while True:
        schedule.run_pending()
        time.sleep(1)

scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
scheduler_thread.start()


async def open_ticket(open_ticket_data):
    try:
        print(f"open_ticket_data: {open_ticket_data}")
        async with httpx.AsyncClient() as client:
            resp = await client.post('http://185.39.79.6:1234/api/Ticket/OpenTicket', json=open_ticket_data)
            print(f"Response status: {resp.status_code}")
            print(f"Response headers: {resp.headers}")
            print(f"Response content: {resp.text}")
            resp.raise_for_status()
            if resp.text.strip():
                return resp.json()
            else:
                return {}
    except httpx.RequestError as e:
        print(f"Request failed: {e}")
        return None


async def add_commodity(commodity_data):
    try:
        print(f"add_commodity_data: {commodity_data}")
        async with httpx.AsyncClient() as client:
            resp = await client.post('http://185.39.79.6:1234/api/Ticket/AddCommodity', json=commodity_data)
            print(f"Response status: {resp.status_code}")
            print(f"Response headers: {resp.headers}")
            print(f"Response content: {resp.text}")
            resp.raise_for_status()
            if resp.text.strip():
                return resp.json()
            else:
                return {}
    except httpx.RequestError as e:
        print(f"Request failed: {e}")
        return None


async def close_ticket(close_ticket_data):
    try:
        print(f"close_ticket_data: {close_ticket_data}")
        async with httpx.AsyncClient() as client:
            resp = await client.post('http://185.39.79.6:1234/api/Ticket/CloseTicket', json=close_ticket_data)
            print(f"Response status: {resp.status_code}")
            print(f"Response headers: {resp.headers}")
            print(f"Response content: {resp.text}")
            resp.raise_for_status()
            if resp.text.strip():
                return resp.json()
            else:
                return {}
    except httpx.RequestError as e:
        print(f"Request failed: {e}")
        return None
