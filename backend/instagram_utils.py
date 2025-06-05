# Instagrapi ile ilgili yardımcı fonksiyonlar burada tanımlanacaktır.
# Giriş, takip ve beğeni doğrulama fonksiyonları ileride eklenecektir.
# Bu dosya sadece şablon ve açıklama içerir.

from instagrapi import Client
import json

def login_instagram(username: str, password: str):
    cl = Client()
    cl.login(username, password)
    return cl

def get_client_from_settings(settings):
    cl = Client(settings)
    return cl

def save_settings(username: str, settings: dict):
    with open(f"settings_{username}.json", "w") as f:
        json.dump(settings, f)

def load_settings(username: str):
    try:
        with open(f"settings_{username}.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return None
