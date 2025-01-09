import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from work.utils import *

# На весь экран
st.set_page_config(page_title="Streamlit Wide Mode", layout="wide")

# Заголовок приложения
st.title("Энергоменеджмент")

# Создаем две колонки: одну для управления (слева), другую для графика (по центру)
col1, col2 = st.columns([1, 3])

with col1:
    # Загрузка датасета
    uploaded_file = st.file_uploader("Загрузите CSV файл", type=["csv"])

    # Проверка наличия загруженного файла
    if uploaded_file is not None:
        # Чтение датасета
        df = pd.read_csv(uploaded_file)

        # Автоматическое определение столбца с датой
        date_columns = df.select_dtypes(include=['object']).apply(pd.to_datetime, errors='coerce').notnull().any()
        date_column = date_columns[date_columns].index[0] if date_columns.any() else None
        
        if date_column:
            st.write(f"Автоматически определенный столбец с датой: {date_column}")
            # Отображение сводки информации о датасете
            st.write("Сводка о предоставленных данных:")
            st.write(df.describe())
        
            # # Выбор столбца с датой
            # date_column = st.selectbox("Выберите столбец с датой", df.columns)

            # Проверка наличия числовых признаков
            numeric_columns = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
            if date_column in numeric_columns:
                numeric_columns.remove(date_column)

            # # Выбор числового признака для графика
            # selected_numeric_column = st.selectbox("Выберите числовой признак для графика", numeric_columns)

            # # Кнопки для выбора типа группировки
            # group_by_options = ['День', 'Неделя', 'Месяц']
            # selected_group_by = st.radio("Выберите тип группировки", group_by_options)

            # Кнопка для формирования отчета (пока заглушка)
            if st.button("Сформировать отчет"):
                output_dir = "reports"  # Директория для сохранения отчетов
                os.makedirs(output_dir, exist_ok=True)  # Создание директории при необходимости
                
                # Генерация отчета
                report_path = generate_report(df, output_dir)
                # st.write("Скачать отчет")
                # Кнопка для скачивания отчета
                with open(report_path, "rb") as f:
                    st.download_button(
                        label="Скачать отчет",
                        data=f,
                        file_name="full_report.pdf",
                        mime="application/pdf"
                    )

with col2:
    # Проверка наличия загруженного файла перед построением графика
    if uploaded_file is not None:

        # Выбор числового признака для графика
        selected_numeric_column = st.selectbox("Выберите числовой признак для просмотра распределения", numeric_columns)

        # Кнопки для выбора типа группировки
        group_by_options = ['День', 'Месяц']
        selected_group_by = st.radio("Выберите тип группировки", group_by_options)

        # Преобразование столбца даты в datetime
        df[date_column] = pd.to_datetime(df[date_column])

        # Группировка данных в зависимости от выбранного типа
        if selected_group_by == 'День':
            # Выбор месяца для отображения
            month_options = df[date_column].dt.month.unique()
            selected_month = st.selectbox("Выберите месяц для анализа", month_options)

            ####
            # Выбор года для отображения
            year_options = df[date_column].dt.year.unique()
            selected_year = st.selectbox("Выберите год для анализа", year_options)
            ####
            
            # Фильтрация данных по выбранному месяцу и году
            df_filtered = df[(df[date_column].dt.month == selected_month) & (df[date_column].dt.year == selected_year)]
            
            # Группировка по дням
            df_grouped = df_filtered.groupby(df_filtered[date_column].dt.date)[selected_numeric_column].sum().reset_index()
            
            # Отображение информации о выбранном месяце и годе
            st.write(f"Данные за месяц: {selected_month}")
            st.write(f"Данные за год: {selected_year}")

        elif selected_group_by == 'Месяц':
            # Группировка по месяцам
            # Выбор года для отображения
            year_options = df[date_column].dt.year.unique()
            selected_year = st.selectbox("Выберите год для анализа", year_options)

            # Фильтрация данных по выбранному месяцу и году
            df_filtered = df[df[date_column].dt.year == selected_year]
            
            # Отображение информации о выбранном годе
            st.write(f"Данные за год: {selected_year}")
            
            df_grouped = df_filtered.groupby(df_filtered[date_column].dt.to_period('M'))[selected_numeric_column].sum().reset_index()
            # df_grouped = df.groupby(df[date_column].dt.to_period('M'))[selected_numeric_column].sum().reset_index()

        # Построение графика
        plt.figure(figsize=(10, 5))
        df_grouped.plot(kind='line')
        plt.title(f'Распределение {selected_numeric_column} по {selected_group_by}')
        plt.xlabel(selected_group_by)
        plt.ylabel(selected_numeric_column)
        plt.xticks(rotation=45)
        st.pyplot(plt)


