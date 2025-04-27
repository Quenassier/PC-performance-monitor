# test_logic.py

from logic import PerformanceAnalyzer

def test_all_problems():
    print("\n=== Тест 1: Все проблемы ===")
    fake_metrics = {
        "CPU": {"temperature": 90.0, "load": 95.0, "frequency": 2800.0},
        "GPU": {"temperature": 88.0, "load": 92.0, "vram_used": 3000, "vram_total": 4000},
        "RAM": {"total": 16, "used": 15, "percent": 94.0},
        "Disks": [{"name": "C:", "usage": 95}, {"name": "D:", "usage": 85}],
        "DiskSMART": {"SMART": "FAILED"},
        "Cooling": {"status": "WARNING", "fan_speed": "Недоступно"}
    }
    analyzer = PerformanceAnalyzer()
    problems = analyzer.analyze(fake_metrics)
    for p in problems:
        print(f"- {p}")

def test_cpu_overload():
    print("\n=== Тест 2: Только высокая загрузка CPU ===")
    fake_metrics = {
        "CPU": {"temperature": 60.0, "load": 95.0, "frequency": 2800.0},
        "GPU": None,
        "RAM": {"total": 16, "used": 6, "percent": 37.5},
        "Disks": [{"name": "C:", "usage": 50}],
        "DiskSMART": {"SMART": "OK"},
        "Cooling": {"status": "OK", "fan_speed": "Недоступно"}
    }
    analyzer = PerformanceAnalyzer()
    problems = analyzer.analyze(fake_metrics)
    for p in problems:
        print(f"- {p}")

def test_disk_failure():
    print("\n=== Тест 3: Только проблема с диском ===")
    fake_metrics = {
        "CPU": {"temperature": 50.0, "load": 20.0, "frequency": 2800.0},
        "GPU": None,
        "RAM": {"total": 16, "used": 5, "percent": 31.25},
        "Disks": [{"name": "C:", "usage": 80}],
        "DiskSMART": {"SMART": "FAILED"},
        "Cooling": {"status": "OK", "fan_speed": "Недоступно"}
    }
    analyzer = PerformanceAnalyzer()
    problems = analyzer.analyze(fake_metrics)
    for p in problems:
        print(f"- {p}")

if __name__ == "__main__":
    test_all_problems()
    test_cpu_overload()
    test_disk_failure()