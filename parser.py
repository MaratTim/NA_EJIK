import requests
import json
import time
import re

db = {}
months_days = {1:31, 2:29, 3:31, 4:30, 5:31, 6:30, 7:31, 8:31, 9:30, 10:31, 11:30, 12:31}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

print("Начинаю сбор данных...")

for month in range(1, 13):
    for day in range(1, months_days[month] + 1):
        # ОПРЕДЕЛЯЕМ date_key В САМОМ НАЧАЛЕ ЦИКЛА
        date_key = f"{month:02d}-{day:02d}"
        url = f"https://na-russia.org/m-meditation?m={month}&d={day}"
        
        try:
            response = requests.get(url, headers=headers, timeout=15)
            text = response.text
            
            # Простейший поиск заголовка
            title = "Без заголовка"
            if "<h1>" in text:
                title = text.split("<h1>")[1].split("</h1>")[0].strip()
            
            # Ищем контент
            if 'class="item-page' in text:
                content_part = text.split('class="item-page')[1]
                clean_text = re.sub('<[^>]*>', '|||', content_part)
                parts = [p.strip() for p in clean_text.split('|||') if p.strip()]
                lines = [p for p in parts if len(p) > 10]
                
                if len(lines) >= 3:
                    db[date_key] = {
                        "title": title,
                        "quote": lines[0],
                        "source": lines[1] if "(" in lines[1] or "стр" in lines[1] else "",
                        "body": "<p>" + "</p><p>".join(lines[2:-1]) + "</p>",
                        "jft": lines[-1]
                    }
                    print(f"[{date_key}] Ок")
                else:
                    print(f"[{date_key}] Недостаточно текста")
            else:
                print(f"[{date_key}] Страница пуста")
            
            # Небольшая пауза, чтобы Гитхаб не забанили
            time.sleep(0.2)
            
        except Exception as e:
            print(f"Ошибка на {date_key}: {e}")

# Сохраняем результат
with open("daily_db.js", "w", encoding="utf-8") as f:
    f.write("window.dailyData = ")
    json.dump(db, f, ensure_ascii=False, indent=2)
    f.write(";")

print("\nВСЁ ГОТОВО!")
