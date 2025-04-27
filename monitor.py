# monitor.py
import psutil
import GPUtil
import platform
import subprocess
from pprint import pprint
import time

def get_cpu_info():
    temp = None
    try:
        temps = psutil.sensors_temperatures()
        for key in ['coretemp', 'cpu-thermal', 'k10temp']:
            if key in temps:
                temp = temps[key][0].current
                break
    except (AttributeError, NotImplementedError):
        print("Ошибка: Температура CPU недоступна.")  # Логирование
        temp = None

    return {
        "temperature": round(temp, 1) if temp else None,
        "load": round(psutil.cpu_percent(interval=1), 1),
        "frequency": round(psutil.cpu_freq().current, 1)
    }

def get_gpu_info():
    try:
        gpus = GPUtil.getGPUs()
        if not gpus:
            print("GPU не найдено.")  # Логирование
            return None
        gpu = gpus[0]
        return {
            "temperature": round(gpu.temperature, 1),
            "load": round(gpu.load * 100, 1),
            "vram_used": round(gpu.memoryUsed, 1),
            "vram_total": round(gpu.memoryTotal, 1)
        }
    except Exception as e:
        print(f"Ошибка при получении данных GPU: {e}")  # Логирование
        return None

def get_ram_info():
    mem = psutil.virtual_memory()
    return {
        "total": round(mem.total / (1024 ** 3), 1),
        "used": round(mem.used / (1024 ** 3), 1),
        "percent": round(mem.percent, 1)
    }

def get_disk_usage():
    disks = []
    for partition in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            disks.append({
                "name": partition.device,
                "usage": round(usage.percent, 1)
            })
        except PermissionError:
            continue
    return disks

def get_disk_smart_status():
    try:
        if platform.system() == "Windows":
            cmd = ["smartctl", "-H", "C:"]
        else:
            cmd = ["sudo", "smartctl", "-H", "/dev/sda"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if "PASSED" in result.stdout:
            return "OK"
        elif "FAILED" in result.stdout:
            return "FAILED"
        else:
            return "UNKNOWN"
    except Exception:
        return "UNAVAILABLE"

def get_cooling_system_status():
    #пример: если температура CPU выше порога то система охлаждения работает плохо
    cpu_temp = get_cpu_info()["temperature"]
    if cpu_temp and cpu_temp > 80:
        return {"status": "WARNING", "fan_speed": "Недоступно"}
    return {"status": "OK", "fan_speed": "Недоступно"}

def get_all_metrics():
    return {
        "CPU": get_cpu_info(),
        "GPU": get_gpu_info(),
        "RAM": get_ram_info(),
        "Disks": get_disk_usage(),
        "DiskSMART": {"SMART": get_disk_smart_status()},
        "Cooling": get_cooling_system_status()
    }

if __name__ == "__main__":
    while True:
        pprint(get_all_metrics())
        print("-" * 50)
        time.sleep(1)  # Пауза 1 секунда между обновлениями