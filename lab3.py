#Створення веб-додатоку із використанням модуля Streamlit: 


import urllib.request
import datetime
import os
import pandas as pd
import streamlit as st
import altair as alt

PATH_TO_FILES = os.path.join(os.getcwd(), 'Files')


def download_data_of_state(state):
    url = f'https://www.star.nesdis.noaa.gov/smcd/emb/vci/VH/get_TS_admin.php?country=UKR&provinceID={state}&year1=1981&year2=2024&type=Mean'
    wp = urllib.request.urlopen(url)
    now = datetime.datetime.now()
    date_and_time_time = now.strftime("%d%m%Y%H%M%S")

    if not os.path.exists(PATH_TO_FILES):
        os.makedirs(PATH_TO_FILES)

    for file in os.listdir(PATH_TO_FILES):
        if file.startswith('NOAA_' + str(state) + '_'):
            os.remove(os.path.join(PATH_TO_FILES, file))

    out = open(os.path.join(PATH_TO_FILES, 'NOAA_' + str(state) + '_' + date_and_time_time + '.csv'), 'wb')
    out.write(wp.read())
    out.close()

def download_all_states():
    for i in range(1, 28):
        download_data_of_state(i)

def get_files(dir_path=PATH_TO_FILES):
    file_paths = []
    for file in os.listdir(dir_path):
        if file.startswith('NOAA') and file.endswith('.csv'):
            file_paths.append(os.path.join(dir_path, file))
    return file_paths

def load_to_frame(dir_path=PATH_TO_FILES):
    headers = ['Year', 'Week', 'SMN', 'SMT', 'VCI', 'TCI', 'VHI', 'empty']
    dataframes = []
    file_paths = get_files(dir_path)
    for file_path in file_paths:
        df = pd.read_csv(file_path, header=1, names=headers)
        df = df.drop(df.loc[df['VHI'] == -1].index)
        df['Area'] = file_path.split('_')[1]
        dataframes.append(df)
    full_dataframe = pd.concat(dataframes).drop_duplicates()
    full_dataframe = full_dataframe.drop(columns=['empty'])
    full_dataframe['Year'] = full_dataframe['Year'].str.replace('<tt><pre>', '').str.replace('</pre></tt>', '')
    full_dataframe = full_dataframe[full_dataframe['Year'].astype(str).str.strip() != '']
    full_dataframe['Year'] = full_dataframe['Year'].astype(int)
    full_dataframe['Area'] = full_dataframe['Area'].astype(int)
    return full_dataframe

if not os.path.exists(PATH_TO_FILES) or not os.listdir(PATH_TO_FILES):
    download_all_states()
dataframe = load_to_frame()


area_names = {
    1: "Вінницька",
    2: "Волинська",
    3: "Дніпропетровська",
    4: "Донецька",
    5: "Житомирська",
    6: "Закарпатська",
    7: "Запорізька",
    8: "Івано-Франківська",
    9: "Київська",
    10: "Кіровоградська",
    11: "Луганська",
    12: "Львівська",
    13: "Миколаївська",
    14: "Одеська",
    15: "Полтавська",
    16: "Рівненська",
    17: "Сумська",
    18: "Тернопільська",
    19: "Харківська",
    20: "Херсонська",
    21: "Хмельницька",
    22: "Черкаська",
    23: "Чернівецька",
    24: "Чернігівська",
    25: "Республіка Крим"
}


def replace_indexes(df):
    df['Area'] = df['Area'].replace({1:22, 2:24, 3:23, 4:25, 5:3, 6:4, 7:8, 8:19, 9:20, 10:21, 11:9, 13:10, 14:11, 15:12,
                                     16:13, 17:14, 18:15, 19:16, 21:17, 22:18, 23:6, 24:1, 25:2, 26:7, 27:5})
    df['Area'] = df['Area'].map(area_names)
    return df

dataframe = replace_indexes(dataframe)



default_values = {
    "index_type": "VCI",
    "selected_area": sorted(dataframe['Area'].unique())[0],
    "week_range": (1, 52),
    "year_range": (min(dataframe['Year'].unique()), max(dataframe['Year'].unique())),
    "sort_asc": False,
    "sort_desc": False
}

if "index_type" not in st.session_state:
    st.session_state.index_type = default_values['index_type']
if "selected_area" not in st.session_state:
    st.session_state.selected_area = default_values['selected_area']
if "week_range" not in st.session_state:
    st.session_state.week_range = default_values['week_range']
if "year_range" not in st.session_state:
    st.session_state.year_range = default_values['year_range']
if "sort_asc" not in st.session_state:
    st.session_state.sort_asc = default_values['sort_asc']
if "sort_desc" not in st.session_state:
    st.session_state.sort_desc = default_values['sort_desc']

st.title('Lab3')
col1, col2 = st.columns([1, 3])

with col1:

# 1. Створіть dropdown список, який дозволить обрати часовий ряд VCI, TCI, VHI для 
# набору даних із лабораторної роботи 2; 
    st.selectbox(
        "Виберіть індекс",
        options=["VCI", "TCI", "VHI"],
        index=["VCI", "TCI", "VHI"].index(st.session_state.index_type),
        key="index_type"
    )

# 2. Створіть dropdown список, який дозволить вибрати область, для якої буде 
# виконуватись аналіз; 
    areas = sorted(dataframe['Area'].unique())
    st.selectbox(
        "Виберіть область",
        options=areas,
        index=areas.index(st.session_state.selected_area),
        key="selected_area"
    )

# 3. Створіть slider, який дозволить зазначити інтервал тижнів, за які відбираються дані;  
    st.slider(
        "Виберіть діапазон тижнів",
        min_value=1,
        max_value=52,
        value=st.session_state.week_range,
        key="week_range"
    )


# 4. Створіть slider, який дозволить зазначити інтервал років, за які відбираються дані; 
    years = sorted(dataframe['Year'].unique())
    st.slider(
        "Виберіть діапазон років",
        min_value=min(years),
        max_value=max(years),
        value=st.session_state.year_range,
        key="year_range"
    )

# 8. Створіть два checkbox для сортування даних за зростанням та спаданням значень 
# VCI, TCI або VHI (залежно від обраної опції у списку dropdown). Продумайте реакцію 
# програми, якщо увімкнені обидва чекбокси. 
    st.checkbox("Сортувати за зростанням", value=st.session_state.sort_asc, key="sort_asc")
    st.checkbox("Сортувати за спаданням", value=st.session_state.sort_desc, key="sort_desc")


# 5. Створіть button для скидання всіх фільтрів і повернення до початкового стану даних 
# (відповідно інтерактивні елементи повинні мати початкові значення); 
    def reset_filters():
        st.session_state.index_type = default_values["index_type"]
        st.session_state.selected_area = default_values["selected_area"]
        st.session_state.week_range = default_values["week_range"]
        st.session_state.year_range = default_values["year_range"]
        st.session_state.sort_asc = default_values["sort_asc"]
        st.session_state.sort_desc = default_values["sort_desc"]

    st.button("Скинути фільтри", on_click=reset_filters)


filtered_df = dataframe[
    (dataframe['Week'].between(st.session_state.week_range[0], st.session_state.week_range[1])) &
    (dataframe['Year'].between(st.session_state.year_range[0], st.session_state.year_range[1])) &
    (dataframe['Area'] == st.session_state.selected_area)
]


if st.session_state.sort_asc and st.session_state.sort_desc:
    st.warning("Обрано обидва типи сортування.")
elif st.session_state.sort_asc:
    filtered_df = filtered_df.sort_values(st.session_state.index_type)
elif st.session_state.sort_desc:
    filtered_df = filtered_df.sort_values(st.session_state.index_type, ascending=False)


# 6. Створіть три вкладки для відображення таблиці з відфільтрованими даними, 
# відповідного до неї графіка та графіка порівняння даних по областях. 
with col2:
    tab1, tab2, tab3 = st.tabs(["Таблиця", "Графік часового ряду", "Порівняння областей"])
    with tab1:
        st.subheader("Відфільтрована таблиця")
        st.dataframe(filtered_df)

# 7. Перший графік повинен відображати відфільтровані дані (часові ряди за діапазон 
# років, що обмежені інтервалом тижнів). Другий графік має відображати порівняння 
# значень VCI, TCI або VHI (залежно від обраної опції у списку dropdown) для обраної 
# області з усіма іншими областями за вказаний часовий інтервал. Продумайте 
# вигляд цих графіків. 
    with tab2:
        st.subheader(f"{st.session_state.index_type} для {st.session_state.selected_area}")
        chart_data = filtered_df.pivot_table(
            index='Week',
            columns='Year',
            values=st.session_state.index_type
        )
        st.line_chart(chart_data)

    with tab3:
        st.subheader(f"Порівняння {st.session_state.index_type} між областями")
        compare_df = dataframe[
                (dataframe['Week'].between(st.session_state.week_range[0], st.session_state.week_range[1])) &
                (dataframe['Year'].between(st.session_state.year_range[0], st.session_state.year_range[1]))
        ]
        bar_data = compare_df.groupby('Area')[st.session_state.index_type].mean().reset_index()

        bar_data['Color'] = bar_data['Area'].apply(
            lambda x: 'red' if x == st.session_state.selected_area else 'darkgray'
        )

        chart = alt.Chart(bar_data).mark_bar().encode(
            x=alt.X('Area:N').title('Область'),
            y=alt.Y(f'{st.session_state.index_type}:Q').title(f'{st.session_state.index_type} (середнє значення)'),
            color=alt.Color('Color:N', scale=None),
            tooltip=['Area', st.session_state.index_type]
        )
        st.altair_chart(chart)

# streamlit run lab3.py 
#https://github.com/MaxMan0070/Lab3