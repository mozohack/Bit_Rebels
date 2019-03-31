import requests



def translate(word):
    base_url = "https://translate.yandex.net/api/v1.5/tr.json/translate?"
    key = 'key=' + "API-KEY"
    text = "text=" + word
    lang = "lang=" + "en-zh"

    url = base_url + key + "&" + text + "&" + lang

    response = requests.get(url)
    data = response.json()
    return data["text"][0]


