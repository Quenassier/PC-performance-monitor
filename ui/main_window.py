# ui/main_window.py
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton, QLabel, QVBoxLayout,
    QHBoxLayout, QStackedWidget, QFileDialog
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon
import pyqtgraph as pg
import collections
import csv
import os
from monitor import get_all_metrics
from logic import PerformanceAnalyzer


class MonitoringPage(QWidget):
    def __init__(self):
        super().__init__()
        self.analyzer = PerformanceAnalyzer()
        # Метки для отображения
        self.cpu_label = QLabel("CPU: —")
        self.gpu_label = QLabel("GPU: —")
        self.ram_label = QLabel("RAM: —")
        self.disk_label = QLabel("Диски: —")
        self.cooling_label = QLabel("Система охлаждения: —")
        self.status_label = QLabel("Статус: —")
        self.recommendations_label = QLabel("Рекомендации: Нет проблем")

        # Кнопка для переключения режима
        self.toggle_mode_button = QPushButton("Переключить режим (Обычный / Расширенный)")
        self.toggle_mode_button.clicked.connect(self.toggle_mode)

        # Графики
        self.cpu_plot = pg.PlotWidget()
        self.cpu_plot.setTitle("Загрузка CPU (%)")
        self.cpu_plot.setYRange(0, 100)
        self.cpu_data = collections.deque(maxlen=30)

        self.gpu_plot = pg.PlotWidget()
        self.gpu_plot.setTitle("Загрузка GPU (%)")
        self.gpu_plot.setYRange(0, 100)
        self.gpu_data = collections.deque(maxlen=30)

        self.ram_plot = pg.PlotWidget()
        self.ram_plot.setTitle("Использование RAM (%)")
        self.ram_plot.setYRange(0, 100)
        self.ram_data = collections.deque(maxlen=30)

        self.extended_mode = True  # Начинаем в расширенном режиме

        layout = QVBoxLayout()
        layout.addWidget(self.toggle_mode_button)
        layout.addWidget(self.cpu_label)
        layout.addWidget(self.gpu_label)
        layout.addWidget(self.ram_label)
        layout.addWidget(self.disk_label)
        layout.addWidget(self.cooling_label)
        layout.addWidget(self.status_label)
        layout.addWidget(self.cpu_plot)
        layout.addWidget(self.gpu_plot)
        layout.addWidget(self.ram_plot)
        layout.addWidget(self.recommendations_label)
        self.setLayout(layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_metrics)
        self.timer.start(2000)

    def toggle_mode(self):
        self.extended_mode = not self.extended_mode
        self.cpu_plot.setVisible(self.extended_mode)
        self.gpu_plot.setVisible(self.extended_mode)
        self.ram_plot.setVisible(self.extended_mode)

    def update_metrics(self):
        metrics = get_all_metrics()
        recommendations = self.analyzer.analyze(metrics)

        cpu = metrics.get("CPU", {})
        gpu = metrics.get("GPU", {})  # GPU может быть None
        ram = metrics.get("RAM", {})
        disks = metrics.get("Disks", [])
        cooling = metrics.get("Cooling", {})

        cpu_temp = cpu.get("temperature")
        cpu_load = cpu.get("load")
        ram_usage = ram.get("percent")
        gpu_load = gpu.get("load") if gpu is not None else None

        # Обновляем метку рекомендаций
        if recommendations:
            self.recommendations_label.setText(f"Рекомендации:\n" + "\n".join(recommendations))
        else:
            self.recommendations_label.setText("Рекомендации: Нет проблем")

        # Формируем строку для дисков
        disk_info = []
        for disk in disks:
            name = disk.get("name", "Нет данных")
            usage = disk.get("usage", "Нет данных")
            disk_info.append(f"{name}: {usage}%")
        disk_text = ", ".join(disk_info) if disk_info else "Данных нет"

        # Формируем строку для системы охлаждения
        cooling_status = cooling.get("status", "Нет данных")
        fan_speed = cooling.get("fan_speed", "Нет данных")
        cooling_text = f"Статус: {cooling_status}, Скорость вентилятора: {fan_speed} RPM"

        # Обновляем метки
        self.cpu_label.setText(
            f"CPU: {cpu_temp if cpu_temp is not None else 'Нет данных'}°C, "
            f"{cpu_load if cpu_load is not None else 'Нет данных'}% загрузка"
        )
        self.gpu_label.setText(f"GPU: {gpu_load:.1f}% загрузка" if gpu_load is not None else "GPU: Нет данных")
        self.ram_label.setText(f"RAM: {ram_usage if ram_usage is not None else 'Нет данных'}% использования")
        self.disk_label.setText(f"Диски: {disk_text}")
        self.cooling_label.setText(f"Система охлаждения: {cooling_text}")

        # Цветовая индикация
        self.colorize_labels(cpu_temp, cpu_load, ram_usage, recommendations)
        self.colorize_gpu(gpu_load)
        self.colorize_disks(disks)
        self.colorize_cooling(cooling_status)

        # Обновление графиков
        if self.extended_mode:
            if isinstance(cpu_load, (int, float)):
                self.cpu_data.append(cpu_load)
                self.cpu_plot.clear()
                self.cpu_plot.plot(list(self.cpu_data), pen=pg.mkPen(color='g', width=2))
            if isinstance(gpu_load, (int, float)):
                self.gpu_data.append(gpu_load)
                self.gpu_plot.clear()
                self.gpu_plot.plot(list(self.gpu_data), pen=pg.mkPen(color='r', width=2))
            if isinstance(ram_usage, (int, float)):
                self.ram_data.append(ram_usage)
                self.ram_plot.clear()
                self.ram_plot.plot(list(self.ram_data), pen=pg.mkPen(color='b', width=2))

    def colorize_labels(self, cpu_temp, cpu_load, ram_usage, recommendations):
        if cpu_temp is not None and cpu_temp > 85 or (cpu_load is not None and cpu_load > 95):
            self.cpu_label.setStyleSheet("color: red;")
        elif cpu_temp is not None and cpu_temp > 75 or (cpu_load is not None and cpu_load > 90):
            self.cpu_label.setStyleSheet("color: orange;")
        else:
            self.cpu_label.setStyleSheet("color: green;")

        if ram_usage is not None and ram_usage > 90:
            self.ram_label.setStyleSheet("color: red;")
        elif ram_usage is not None and ram_usage > 80:
            self.ram_label.setStyleSheet("color: orange;")
        else:
            self.ram_label.setStyleSheet("color: green;")

        if recommendations:
            self.status_label.setText(f"Статус: ПРОБЛЕМЫ ОБНАРУЖЕНЫ!")
            self.status_label.setStyleSheet("color: red;")
        else:
            self.status_label.setText(f"Статус: Всё в норме.")
            self.status_label.setStyleSheet("color: green;")

    def colorize_gpu(self, gpu_load):
        if isinstance(gpu_load, (int, float)):
            if gpu_load > 95:
                self.gpu_label.setStyleSheet("color: red;")
            elif gpu_load > 90:
                self.gpu_label.setStyleSheet("color: orange;")
            else:
                self.gpu_label.setStyleSheet("color: green;")
        else:
            self.gpu_label.setStyleSheet("color: black;")  # Если данных нет

    def colorize_disks(self, disks):
        for disk in disks:
            usage = disk.get("usage")
            if isinstance(usage, (int, float)):
                if usage > 90:
                    self.disk_label.setStyleSheet("color: red;")
                    return
                elif usage > 80:
                    self.disk_label.setStyleSheet("color: orange;")
                    return
        self.disk_label.setStyleSheet("color: green;")  # Если данных нет

    def colorize_cooling(self, cooling_status):
        if cooling_status == "WARNING":
            self.cooling_label.setStyleSheet("color: red;")
        elif cooling_status == "OK":
            self.cooling_label.setStyleSheet("color: green;")
        else:
            self.cooling_label.setStyleSheet("color: black;")  # Если данных нет


class ReportsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.export_button = QPushButton("Экспортировать отчет")
        self.export_button.clicked.connect(self.export_report)
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Экспорт отчетов в CSV"))
        layout.addWidget(self.export_button)
        self.setLayout(layout)

    def export_report(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Сохранить отчет", "", "CSV Files (*.csv)")
        if filename:
            metrics = get_all_metrics()
            with open(filename, mode='w', newline='', encoding='utf-8-sig') as file:
                writer = csv.writer(file)
                writer.writerow(["Компонент", "Показатель", "Значение"])
                cpu = metrics.get("CPU", {})
                ram = metrics.get("RAM", {})
                gpu = metrics.get("GPU", {})
                disks = metrics.get("Disks", [])
                cooling = metrics.get("Cooling", {})
                writer.writerow(["CPU", "Температура (°C)",
                                 cpu.get("temperature") if cpu.get("temperature") is not None else "Нет данных"])
                writer.writerow(
                    ["CPU", "Загрузка (%)", cpu.get("load") if cpu.get("load") is not None else "Нет данных"])
                writer.writerow(["RAM", "Использование (%)",
                                 ram.get("percent") if ram.get("percent") is not None else "Нет данных"])
                if gpu:
                    writer.writerow(
                        ["GPU", "Загрузка (%)", f"{gpu.get('load', 0):.1f}" if gpu.get('load') else "Нет данных"])
                else:
                    writer.writerow(["GPU", "Данных нет", "Нет данных"])
                # Добавляем данные о дисках
                for disk in disks:
                    name = disk.get("name", "Нет данных")
                    usage = disk.get("usage", "Нет данных")
                    writer.writerow(["Диск", name, f"{usage}%" if usage != "Нет данных" else "Нет данных"])
                # Добавляем данные о системе охлаждения
                writer.writerow(["Система охлаждения", "Статус", cooling.get("status", "Нет данных")])
                writer.writerow(
                    ["Система охлаждения", "Скорость вентилятора", f"{cooling.get('fan_speed', 'Недоступно')} RPM"])


class SettingsPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Настройки будут реализованы в следующих версиях"))
        self.setLayout(layout)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PC Performance Monitor")
        self.setWindowIcon(QIcon('ui/icon.ico'))
        self.setGeometry(100, 100, 1000, 700)
        self.stack = QStackedWidget()
        self.monitoring_page = MonitoringPage()
        self.reports_page = ReportsPage()
        self.settings_page = SettingsPage()
        self.stack.addWidget(self.monitoring_page)
        self.stack.addWidget(self.reports_page)
        self.stack.addWidget(self.settings_page)
        self.monitor_button = QPushButton("Мониторинг")
        self.report_button = QPushButton("Отчеты")
        self.settings_button = QPushButton("Настройки")
        self.monitor_button.clicked.connect(lambda: self.stack.setCurrentWidget(self.monitoring_page))
        self.report_button.clicked.connect(lambda: self.stack.setCurrentWidget(self.reports_page))
        self.settings_button.clicked.connect(lambda: self.stack.setCurrentWidget(self.settings_page))
        top_layout = QHBoxLayout()
        top_layout.addWidget(self.monitor_button)
        top_layout.addWidget(self.report_button)
        top_layout.addWidget(self.settings_button)
        main_layout = QVBoxLayout()
        main_layout.addLayout(top_layout)
        main_layout.addWidget(self.stack)
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)