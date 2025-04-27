class PerformanceAnalyzer:
    def __init__(self):
        self.cpu_temp_limit = 80.0  # °C
        self.gpu_temp_limit = 85.0  # °C
        self.ram_usage_limit = 90.0  # %
        self.disk_usage_limit = 90.0  # %

    def analyze_cpu(self, cpu_data):
        advice = []
        if isinstance(cpu_data.get("temperature"), (int, float)) and cpu_data["temperature"] > self.cpu_temp_limit:
            advice.append("Перегрев процессора. Проверьте состояние системы охлаждения (очистка от пыли, замена термопасты).")
            advice.append("Рекомендуется уменьшить нагрузку на процессор: закройте ресурсоёмкие приложения.")
        if isinstance(cpu_data.get("load"), (int, float)) and cpu_data["load"] > 90:
            advice.append("Высокая загрузка процессора. Проверьте наличие фоновых процессов в диспетчере задач.")
            advice.append("При продолжительной высокой нагрузке рекомендуется обновить драйверы или рассмотреть модернизацию оборудования.")
        return advice

    def analyze_gpu(self, gpu_data):
        advice = []
        if gpu_data:
            if isinstance(gpu_data.get("temperature"), (int, float)) and gpu_data["temperature"] > self.gpu_temp_limit:
                advice.append("Перегрев видеокарты. Проверьте вентиляцию корпуса и очистите кулеры от пыли.")
                advice.append("Рекомендуется снизить настройки графики в требовательных приложениях для уменьшения нагрева.")
                advice.append("При постоянном перегреве обратитесь в сервисный центр для диагностики системы охлаждения GPU.")
            if isinstance(gpu_data.get("load"), (int, float)) and gpu_data["load"] > 90:
                advice.append("Высокая загрузка видеокарты. Возможно, текущие приложения используют её на пределе возможностей.")
                advice.append("Проверьте наличие обновлений драйверов видеокарты через официальный сайт производителя.")
        return advice

    def analyze_ram(self, ram_data):
        advice = []
        if isinstance(ram_data.get("percent"), (int, float)) and ram_data["percent"] > self.ram_usage_limit:
            advice.append("Высокое использование оперативной памяти. Закройте лишние программы и вкладки в браузере.")
            advice.append("При систематической нехватке ОЗУ рекомендуется увеличить объём оперативной памяти устройства.")
        return advice

    def analyze_disks(self, disk_data):
        advice = []
        for disk in disk_data:
            if isinstance(disk.get("usage"), (int, float)) and disk["usage"] > self.disk_usage_limit:
                advice.append(f"Диск {disk['name']} заполнен на {disk['usage']}%. Освободите место на диске.")
        return advice

    def analyze_disk_smart(self, disk_smart):
        advice = []
        smart_status = disk_smart.get("SMART")
        if smart_status and smart_status != "OK":
            advice.append("Внимание: состояние накопителя нестабильное. Немедленно создайте резервную копию важных данных.")
            advice.append("Рекомендуется провести полную проверку диска с помощью утилит диагностики (например, Victoria, CrystalDiskInfo).")
        return advice

    def analyze(self, metrics):
        recommendations = []
        recommendations.extend(self.analyze_cpu(metrics.get("CPU", {})))
        recommendations.extend(self.analyze_gpu(metrics.get("GPU", {})))
        recommendations.extend(self.analyze_ram(metrics.get("RAM", {})))
        recommendations.extend(self.analyze_disks(metrics.get("Disks", [])))
        recommendations.extend(self.analyze_disk_smart(metrics.get("DiskSMART", {})))

        if recommendations:
            recommendations.append("Если проблема сохраняется, рекомендуется обратиться к специалисту.")
        return recommendations