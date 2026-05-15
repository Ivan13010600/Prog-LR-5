import csv
import os
import random
CAR_BRANDS = [
    "Toyota", "BMW", "Mercedes", "Audi", "Volkswagen",
    "Ford", "Hyundai", "Kia", "Lada", "Renault"
]
def generate_car_data(filepath="L5.csv", target_bytes=1_073_741_824, callback=None):
    CHECK_INTERVAL = 50000
    cnt = 0
    with open(filepath, "w", encoding="utf-8-sig", newline="", buffering=1 << 20) as file:
        writer = csv.writer(file)
        writer.writerow(["Марка автомобиля", "Пробег", "Год выпуска", "Количество владельцев"])
        fileno = file.fileno()

        while True:
            writer.writerow([
                CAR_BRANDS[random.randint(0, 9)],
                random.randint(1000, 500000),
                random.randint(1980, 2026),
                random.randint(1, 10)
            ])
            cnt += 1

            if cnt % CHECK_INTERVAL == 0:
                current_size = os.fstat(fileno).st_size
                percent = min(int((current_size / target_bytes) * 100), 100)
                if callback:
                    callback(f"Генерация {percent}%", percent)
                if current_size >= target_bytes:
                    break

    if callback:
        total_size = os.path.getsize(filepath)
        stats = {
            "count": cnt,
            "size_gb": total_size / (1024 ** 3),
            "avg_record": total_size / cnt if cnt > 0 else 0
        }
        callback(100, "Готово!")