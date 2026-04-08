import requests
import time
import sys


def search_torrent(query):
    print(f"Ищем торренты по запросу: '{query}'...")
    # Используем публичный API
    url = f"https://apibay.org/q.php?q={query}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        results = response.json()

        # Если API вернул пустой результат, первый элемент обычно имеет id '0'
        if not results or results[0].get('id') == '0':
            print("Ничего не найдено.")
            return []

        torrents = []
        # Берем топ-5 результатов
        for item in results[:5]:
            name = item.get('name')
            info_hash = item.get('info_hash')
            seeders = item.get('seeders')
            # Формируем магнет-ссылку
            magnet = f"magnet:?xt=urn:btih:{info_hash}&dn={requests.utils.quote(name)}"

            torrents.append({
                'name': name,
                'hash': info_hash,
                'seeders': seeders,
                'magnet': magnet
            })

            print(f"\nНазвание: {name}")
            print(f"Сиды: {seeders}")
            print(f"Magnet: {magnet}")
            print(info_hash)
        return torrents

    except Exception as e:
        print(f"Ошибка при поиске: {e}")
        return []


# def download_from_magnet(magnet_link, save_path='./downloads'):
#     print(f"\nИнициализация клиента BitTorrent...")
#
#     # Создаем сессию с дефолтными портами
#     ses = lt.session({'listen_interfaces': '0.0.0.0:6881'})
#
#     # Включаем DHT (Критически важно для магнет-ссылок!)
#     ses.add_dht_router("router.bittorrent.com", 6881)
#     ses.add_dht_router("router.utorrent.com", 6881)
#     ses.add_dht_router("dht.transmissionbt.com", 6881)
#     ses.start_dht()
#
#     params = {
#         'save_path': save_path,
#         'storage_mode': lt.storage_mode_t(2)
#     }
#
#     print("Добавляем магнет-ссылку в сессию...")
#     handle = lt.add_magnet_uri(ses, magnet_link, params)
#
#     print("Ищем пиров через DHT для получения метаданных (это может занять минуту)...")
#     # Магнет-ссылка не содержит файлов, она содержит только хэш.
#     # Ждем, пока клиент скачает метаданные (список файлов) у других пиров.
#     while not handle.has_metadata():
#         time.sleep(1)
#         sys.stdout.write('.')
#         sys.stdout.flush()
#
#     print("\nМетаданные получены! Начинаем загрузку.")
#
#     # Получаем информацию о торренте
#     info = handle.get_torrent_info()
#     print(f"Скачиваем: {info.name()}")
#     print(f"Общий размер: {info.total_size() / (1024 * 1024):.2f} MB")
#
#     # Основной цикл мониторинга загрузки
#     while handle.status().state != lt.torrent_status.seeding:
#         s = handle.status()
#
#         state_str = ['queued', 'checking', 'downloading metadata', 'downloading', 'finished', 'seeding', 'allocating', 'checking fastresume']
#
#         print(f"\rСостояние: {state_str[s.state]} | "
#               f"Прогресс: {s.progress * 100:.2f}% | "
#               f"Пиры: {s.num_peers} | "
#               f"Скорость: {s.download_rate / 1000:.1f} kB/s", end="")
#
#         time.sleep(1)
#
#     print("\n\nЗагрузка завершена! Файлы сохранены в:", save_path)


# Пример использования (связываем шаг 1 и шаг 2)
if __name__ == "__main__":
    query = input("Что будем искать? (например 'arch linux'): ")
    results = search_torrent(query)

    if results:
        choice = input("\nВведите номер торрента для скачивания (от 1 до 5) или 'q' для выхода: ")
        if choice.isdigit() and 1 <= int(choice) <= len(results):
            selected_magnet = results[int(choice) - 1]['magnet']
            print(selected_magnet)
            # Запускаем загрузку (убедитесь, что папка ./downloads существует или создастся)
            # download_from_magnet(selected_magnet, save_path='./downloads')

