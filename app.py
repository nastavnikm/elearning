import asyncio
import aiohttp
from flask import Flask, render_template, request, jsonify
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

app = Flask(__name__)

# Funkcija za skidanje vesti sa B92
async def get_b92_news(session):
    url = "https://www.b92.net/najnovije-vesti"
    headers = {"User-Agent": "Mozilla/5.0"}

    async with session.get(url, headers=headers) as response:
        soup = BeautifulSoup(await response.text(), "html.parser")

    news_items = soup.find_all("div", class_="news-item-data")
    vesti = []
    for item in news_items:
        title_tag = item.find("h2", class_="news-item-title").find("a")
        title = title_tag.find("span").text.strip() if title_tag else None
        time_tag = item.find("span", class_="before-time-number")
        time_text = item.find("span", class_="before-time-text")

        if title and time_tag and time_text:
            text = f"***B92*** [{time_tag.text.strip()} {time_text.text.strip()}] {title}"
            vesti.append(text)

    return vesti


# Funkcija za skidanje vesti sa N1
async def get_n1_news(session):
    url = "https://n1info.rs/najnovije/"
    headers = {"User-Agent": "Mozilla/5.0"}

    async with session.get(url, headers=headers) as response:
        soup = BeautifulSoup(await response.text(), "html.parser")

    news_items = soup.find_all("h3", class_="uc-block-post-grid-title")
    vesti = []

    now = datetime.now()

    for item in news_items:
        title_tag = item.find("a")
        title = title_tag.text.strip() if title_tag else None
        time_tag = item.find_previous("time")
        time_text = time_tag.text.strip() if time_tag else "Nepoznato vreme"

        try:
            if "pre" in time_text:
                time_parts = time_text.split()
                quantity = int(time_parts[1])
                unit = time_parts[2]
                if unit in ["minuta", "minut"]:
                    delta = timedelta(minutes=quantity)
                elif unit in ["sat", "sati"]:
                    delta = timedelta(hours=quantity)
                elif unit in ["dan", "dana"]:
                    delta = timedelta(days=quantity)
                else:
                    delta = timedelta(hours=24)

                news_time = now - delta
            else:
                news_time = datetime.strptime(time_text, "%d. %m. %Y.")

            if now - news_time <= timedelta(days=1):
                if title:
                    text = f"***N1*** [{time_text}] {title}"
                    vesti.append(text)
        except Exception as e:
            print(f"Greška u procesu vremena: {e}")

    return vesti


# Funkcija za skidanje vesti sa Danas
async def get_danas_news(session):
    url = "https://www.danas.rs/najnovije-vesti/"
    headers = {"User-Agent": "Mozilla/5.0"}

    async with session.get(url, headers=headers) as response:
        soup = BeautifulSoup(await response.text(), "html.parser")

    news_items = soup.find_all("h3", class_="article-post-title")
    vesti = []

    now = datetime.now()

    for item in news_items:
        title_tag = item.find("a")
        title = title_tag.text.strip() if title_tag else None
        time_tag = item.find_previous("span", class_="published")
        time_text = time_tag.text.strip() if time_tag else "Nepoznato vreme"

        try:
            if "danas" in time_text.lower():
                time_str = time_text.split("danas")[1].strip()
                post_time = datetime.strptime(time_str, "%H:%M").replace(year=now.year, month=now.month, day=now.day)
            else:
                post_time = datetime.strptime(time_text, "%d. %m. %Y.")

            if now - post_time <= timedelta(days=1):
                if title:
                    text = f"***Danas*** [{time_text}] {title}"
                    vesti.append(text)
        except Exception as e:
            print(f"Greška u procesu vremena: {e}")

    return vesti


# Asinhrona funkcija za pretragu svih vesti
async def fetch_all_news(sites):
    async with aiohttp.ClientSession() as session:
        tasks = []
        if "B92" in sites:
            tasks.append(get_b92_news(session))
        if "N1" in sites:
            tasks.append(get_n1_news(session))
        if "Danas" in sites:
            tasks.append(get_danas_news(session))

        results = await asyncio.gather(*tasks)
        return results


# Ruta za vesti
@app.route("/get_news", methods=["POST"])
def get_news():
    data = request.json
    sites = data.get("sites", [])

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    results = loop.run_until_complete(fetch_all_news(sites))

    sve_vesti = []
    if results:
        for site_results in results:
            sve_vesti.extend(site_results)

    return jsonify(sve_vesti)


# Home ruta
@app.route("/")
def home():
    return render_template("index.html")


# Istraživanje ruta
@app.route("/istrazivanje")
def istrazivanje():
    return render_template("istrazivanje.html")

# Ruta za aplikacije
@app.route("/aplikacije")
def aplikacije():
    return render_template("aplikacije.html")

# Ruta za e-learning
@app.route("/elearning")
def elearning():
    return render_template("elearning.html")

# Ruta za about stranu
@app.route("/about")
def about():
    return render_template("about.html")


if __name__ == "__main__":
    app.run(debug=True)
