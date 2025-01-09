import os
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import streamlit as st

# Регистрация шрифта DejaVu Sans
pdfmetrics.registerFont(TTFont('DejaVuSans', 'fonts/DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', 'fonts/DejaVuSans-Bold.ttf'))

def analyze_data(df):
    """Функция для анализа данных и генерации метрик."""
    metrics = {}
    
    # Предположим, что у нас есть колонка 'Энергопотребление'
    energy_column = 'normal'
    
    # Основные метрики
    metrics['mean'] = df[energy_column].mean()
    metrics['std'] = df[energy_column].std()
    metrics['min'] = df[energy_column].min()
    metrics['max'] = df[energy_column].max()
    
    # Выбросы
    threshold = metrics['mean'] + 2 * metrics['std']
    outliers = df[df[energy_column] > threshold]
    
    return metrics, outliers

def generate_recommendations(metrics):
    """Функция для генерации рекомендаций на основе метрик."""
    recommendations = []
    
    if metrics['mean'] > 100:  # Пример порога
        recommendations.append("Рекомендуется провести аудит оборудования.")
    
    if metrics['std'] > 50:  # Пример порога для стандартного отклонения
        recommendations.append("Рекомендуется установить системы мониторинга.")
    
    recommendations.append("Рассмотрите возможность использования энергосберегающих технологий.")
    
    return recommendations

def generate_report(df, output_dir):
    """Функция для генерации отчета на основе исходного датасета."""

    energy_column = 'normal'
    metrics, outliers = analyze_data(df)
    recommendations = generate_recommendations(metrics)

    # Создаем имя файла
    filename = "full_report.pdf"
    file_path = os.path.join(output_dir, filename)

    # Создаем PDF документ
    c = canvas.Canvas(file_path, pagesize=letter)
    width, height = letter

    # Заголовок
    c.setFont("DejaVuSans-Bold", 16)  # Используем зарегистрированный шрифт
    c.drawString(100, height - 50, "Автоматизированный отчет по энергопотреблению")

    # Добавление метрик
    c.setFont("DejaVuSans", 12)  # Используем зарегистрированный шрифт
    y_position = height - 100
    c.drawString(100, y_position, f"Среднее энергопотребление: {metrics['mean']:.2f}")
    y_position -= 20
    c.drawString(100, y_position, f"Стандартное отклонение: {metrics['std']:.2f}")
    y_position -= 20
    c.drawString(100, y_position, f"Минимальное значение: {metrics['min']:.2f}")
    y_position -= 20
    c.drawString(100, y_position, f"Максимальное значение: {metrics['max']:.2f}")

    # Выбросы
    y_position -= 20
    c.setFont("DejaVuSans-Bold", 16)  # Используем зарегистрированный шрифт
    c.drawString(100, y_position, "Выбросы:")
    
    c.setFont("DejaVuSans", 12)  # Используем зарегистрированный шрифт
    
    if not outliers.empty:
        for index, row in outliers.iterrows():
            y_position -= 20
            c.drawString(100, y_position, f"{row['date']}: {row[energy_column]}")
    else:
        c.drawString(100, y_position - 20, "Нет выбросов.")

    # Рекомендации
    # c.setFont("Helvetica-Bold", 14)
    y_position -= 40
    c.drawString(100, y_position, "Рекомендации:")
    
    for rec in recommendations:
        y_position -= 20
        c.drawString(100, y_position, rec)

    # Завершение и сохранение PDF
    c.save()
    
    return file_path