#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Автозагрузка дистрибутива ТАБ:Библиотека искусственного интеллекта (ТАБ:БИИ) с tab-store.ru.

Ссылки на файлы в карточке товара имеют вид /upload/iblock/<hash>/<hash>.zip и меняются
при каждой публикации новой версии, поэтому URL не зашивается в код: скрипт разбирает
страницу товара и берёт ссылку по видимой подписи ("ТАБ_БИИ" — дистрибутив,
"ТАБ БИИ. Описание функций библиотеки" — документация).

Примеры:
    python3 scripts/fetch-tab-bii.py --url-only
    python3 scripts/fetch-tab-bii.py --dest .tmp/tab-bii
    python3 scripts/fetch-tab-bii.py --what doc --dest .tmp/tab-bii

Успешный вывод последней строкой — абсолютный путь к .cfe (для --what dist)
или к загруженному файлу документации (для --what doc).
"""

import argparse
import html
import os
import re
import sys
import zipfile
from html.parser import HTMLParser
from urllib.parse import urljoin
from urllib.request import Request, urlopen

PRODUCT_PAGE = (
    "https://tab-store.ru/product/blok_ii/"
    "tab-biblioteka-iskusstvennogo-intellekta/"
)
UA = "Mozilla/5.0 (compatible; onec-vibecoding/1.0; +https://github.com/TAB1C/onec-vibecoding)"
DIST_EXT = (".zip", ".cfe", ".rar", ".7z")
DOC_EXT = (".docx", ".pdf")


class LinkCollector(HTMLParser):
    """Собирает пары (href, видимый текст ссылки)."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links = []
        self._depth = 0
        self._href = None
        self._text = []

    def handle_starttag(self, tag, attrs):
        if tag != "a":
            return
        if self._depth:
            self._depth += 1
            return
        href = dict(attrs).get("href")
        if href:
            self._depth = 1
            self._href = href
            self._text = []

    def handle_endtag(self, tag):
        if tag != "a" or not self._depth:
            return
        self._depth -= 1
        if self._depth == 0:
            text = re.sub(r"\s+", " ", "".join(self._text)).strip()
            self.links.append((self._href, text))
            self._href = None
            self._text = []

    def handle_data(self, data):
        if self._depth:
            self._text.append(data)


def get(url, binary=False):
    req = Request(url, headers={"User-Agent": UA, "Accept-Language": "ru,en;q=0.8"})
    with urlopen(req, timeout=120) as resp:
        data = resp.read()
    return data if binary else data.decode("utf-8", "replace")


def pick_link(page_html, page_url, what):
    parser = LinkCollector()
    parser.feed(page_html)
    wanted_ext = DIST_EXT if what == "dist" else DOC_EXT
    candidates = []
    for href, text in parser.links:
        if not href.lower().endswith(wanted_ext):
            continue
        label = html.unescape(text)
        if not re.search(r"ТАБ[ _]?БИИ", label, re.IGNORECASE):
            continue
        is_doc = "описание" in label.lower()
        if what == "dist" and is_doc:
            continue
        if what == "doc" and not is_doc:
            continue
        # .docx предпочтительнее .pdf: из него проще извлечь текст
        rank = 0 if href.lower().endswith((".zip", ".cfe", ".docx")) else 1
        candidates.append((rank, urljoin(page_url, href), label))
    if not candidates:
        raise SystemExit(
            "Не найдена ссылка на {} в карточке товара {}.\n"
            "Скорее всего изменилась вёрстка страницы — открой её в браузере, "
            "скачай файл вручную и передай путь к нему.".format(
                "дистрибутив ТАБ_БИИ" if what == "dist" else "описание функций ТАБ БИИ",
                page_url,
            )
        )
    candidates.sort(key=lambda c: c[0])
    return candidates[0][1], candidates[0][2]


def download(url, dest_dir, force):
    os.makedirs(dest_dir, exist_ok=True)
    name = os.path.basename(url.split("?", 1)[0])
    path = os.path.join(dest_dir, name)
    if os.path.exists(path) and not force:
        print("Уже загружено: {}".format(path), file=sys.stderr)
        return path
    data = get(url, binary=True)
    with open(path, "wb") as f:
        f.write(data)
    print("Загружено {} байт -> {}".format(len(data), path), file=sys.stderr)
    return path


def extract_cfe(path, dest_dir):
    if path.lower().endswith(".cfe"):
        return path
    if not zipfile.is_zipfile(path):
        raise SystemExit(
            "Файл {} не .cfe и не zip-архив. Распакуй его вручную "
            "(нужен .rar/.7z распаковщик) и укажи путь к .cfe.".format(path)
        )
    out_dir = os.path.join(dest_dir, "unpacked")
    with zipfile.ZipFile(path) as zf:
        for member in zf.namelist():
            if member.startswith("/") or ".." in member.replace("\\", "/").split("/"):
                raise SystemExit("Небезопасное имя в архиве: {}".format(member))
        zf.extractall(out_dir)
    cfe = []
    for root, _dirs, files in os.walk(out_dir):
        for f in files:
            if f.lower().endswith(".cfe"):
                cfe.append(os.path.join(root, f))
    if not cfe:
        raise SystemExit(
            "В архиве {} нет файла .cfe. Содержимое распаковано в {} — "
            "посмотри, что внутри (возможно, вложенный архив или инструкция).".format(path, out_dir)
        )
    cfe.sort(key=lambda p: (len(p), p))
    return cfe[0]


def main():
    ap = argparse.ArgumentParser(description="Скачать дистрибутив или описание ТАБ:БИИ с tab-store.ru")
    ap.add_argument("--what", choices=("dist", "doc"), default="dist",
                    help="dist — расширение .cfe (по умолчанию), doc — описание функций")
    ap.add_argument("--dest", default=os.path.join(".tmp", "tab-bii"), help="куда складывать файлы")
    ap.add_argument("--page", default=PRODUCT_PAGE, help="URL карточки товара")
    ap.add_argument("--url-only", action="store_true", help="только показать найденную ссылку, не качать")
    ap.add_argument("--force", action="store_true", help="перекачать, даже если файл уже есть")
    args = ap.parse_args()

    url, label = pick_link(get(args.page), args.page, args.what)
    print("Найдено: {} -> {}".format(label, url), file=sys.stderr)
    if args.url_only:
        print(url)
        return

    dest = os.path.abspath(args.dest)
    path = download(url, dest, args.force)
    print(os.path.abspath(extract_cfe(path, dest) if args.what == "dist" else path))


if __name__ == "__main__":
    main()
