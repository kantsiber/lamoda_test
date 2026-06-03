import requests
import os
import time
from bs4 import BeautifulSoup

base_link = "https://academy.lamoda.ru"
HEADERS = {"User-Agent": "Mozilla/5.0"}

try:
    main_page = BeautifulSoup(requests.get(base_link, headers=HEADERS).text, "html.parser")
    all_pages_with_links = set()

    for a in main_page.find_all("a", href=True):
        if a['href'].startswith("/articles/"):
            all_pages_with_links.add(a['href'])
except Exception as e:
    print(f"ошибка загрузки страницы: {e}")

for link in list(all_pages_with_links):
    print(f"обрабатываю раздел: {link}")
    try:
        page = BeautifulSoup(requests.get(base_link + link, headers=HEADERS).text, "html.parser")
        for a in page.find_all("a", href=True):
            if a['href'].startswith("/articles/"):
                all_pages_with_links.add(a['href'])
    except Exception as e:
        print(f"ошибка загрузки раздела {link}: {e}")
    time.sleep(0.3)

leaf_pages = []
for link in all_pages_with_links:
    is_section = any(other != link and other.startswith(link) for other in all_pages_with_links)
    if not is_section:
        leaf_pages.append(link)

print(f"найдено статей: {len(leaf_pages)}")

os.makedirs("articles", exist_ok=True)

for link in sorted(leaf_pages):
    try:
        page = BeautifulSoup(requests.get(base_link + link, headers=HEADERS).text, "html.parser")
        article_text = page.find("div", class_="article-detail__text")

        if article_text:
            filename = link.strip("/").replace("/", "_") + ".md"
            with open(f"articles/{filename}", "w", encoding="utf-8") as f:
                f.write(f"Источник: {base_link}{link}\n\n")
                f.write(article_text.get_text(separator="\n", strip=True))
            print(f"страница {link} обработана")
        else:
            print(f"пусто: {link}")

    except Exception as e:
        print(f"ошибка обработки {link}: {e}")

    time.sleep(0.5)

total = os.listdir("articles")
print(f"всего статей: {len(total)}")