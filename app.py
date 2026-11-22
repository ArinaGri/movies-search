
import ast
from pathlib import Path

import pandas as pd
import streamlit as st

from utils.ranking import weighted_rating, LANGUAGE_DICT


st.set_page_config(
    page_title="Что посмотреть?",
    page_icon="🎬",
    layout="wide"
)

DATA_PATH = Path(__file__).parent / "data" / "movies.csv"


# -----------------------------
# Предобработка данных
# -----------------------------

def parse_tmdb_names(value):
    """
    Извлекает названия из полей genres и production_countries.
    В CSV они представлены строками со списками словарей.
    """

    if isinstance(value, list):
        parsed = value
    elif pd.isna(value) or not str(value).strip():
        return []
    else:
        try:
            parsed = ast.literal_eval(value)
        except (ValueError, SyntaxError, TypeError):
            return []

    if not isinstance(parsed, list):
        return []

    return [
        str(item["name"]).strip()
        for item in parsed
        if isinstance(item, dict) and item.get("name")
    ]




@st.cache_data
def load_movies():
    """Загружает и подготавливает TMDB CSV."""

    if not DATA_PATH.exists():
        st.error(
            f"Файл датасета не найден: {DATA_PATH}"
        )
        st.stop()

    try:
        df = pd.read_csv(
            DATA_PATH,
            low_memory=False,
            encoding="utf-8"
        )
    except UnicodeDecodeError:
        df = pd.read_csv(
            DATA_PATH,
            low_memory=False,
            encoding="latin-1"
        )

    # Проверяем наличие необходимых колонок
    required_columns = [
        "title",
        "genres",
        "production_countries",
        "original_language",
        "release_date",
        "vote_average",
        "vote_count",
        "popularity",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        st.error(
            f"В CSV отсутствуют колонки: {missing_columns}"
        )
        st.stop()

    # Убираем фильмы без названия
    df = df.dropna(subset=["title"])
    df["title"] = df["title"].astype(str).str.strip()
    df = df[df["title"] != ""]


    # Разбираем жанры и страны
    df["genres_list"] = df["genres"].apply(
        parse_tmdb_names
    )

    df["countries_list"] = df["production_countries"].apply(
        parse_tmdb_names
    )

    # Текстовые варианты для таблиц
    df["genre_text"] = df["genres_list"].apply(
        lambda items: ", ".join(items)
    )

    df["country_text"] = df["countries_list"].apply(
        lambda items: ", ".join(items)
    )

    # Язык оригинала
    df["original_language"] = (
        df["original_language"]
        .map(LANGUAGE_DICT).fillna("")
        .astype(str)
        .str.strip())

    # Числовые колонки
    numeric_columns = [
        "vote_average",
        "vote_count",
        "popularity"
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        ).fillna(0)

    # Год выпуска
    df["year"] = pd.to_datetime(
        df["release_date"],
        errors="coerce"
    ).dt.year

    df["year"] = df["year"].fillna(0).astype(int)

    # Удаляем дубликаты по ID, если колонка есть
    if "id" in df.columns:
        df = df.drop_duplicates(subset=["id"])

    return df.reset_index(drop=True)


# -----------------------------
# Загружаем фильмы
# -----------------------------

movies = load_movies()

if movies.empty:
    st.warning("В датасете не осталось фильмов с постерами.")
    st.stop()


# -----------------------------
# Заголовок
# -----------------------------

st.title("🎬 Что посмотреть?")

st.write(
    "Найдите фильм по жанру, стране производства "
    "и языку оригинала или откройте рейтинг лучших фильмов."
)

st.caption(
    f"В каталоге: {len(movies):,} фильмов с постерами."
)


# -----------------------------
# Вкладки
# -----------------------------

tab_search, tab_top, tab_about = st.tabs([
    "🔎 Поиск фильма",
    "🏆 Топ фильмов",
    "ℹ️ О проекте"
])


# =====================================================
# ВКЛАДКА 1. ПОИСК ФИЛЬМОВ
# =====================================================

with tab_search:

    st.subheader("Подбор фильма")

    genres = sorted({
        genre
        for items in movies["genres_list"]
        for genre in items
    })

    countries = sorted({
        country
        for items in movies["countries_list"]
        for country in items
    })

    languages = sorted(
        movies.loc[
            movies["original_language"] != "",
            "original_language"
        ].unique()
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        selected_genre = st.selectbox(
            "Жанр",
            ["Любой"] + genres
        )

    with c2:
        selected_country = st.selectbox(
            "Страна производства",
            ["Любая"] + countries
        )

    with c3:
        selected_language = st.selectbox(
            "Язык оригинала",
            ["Любой"] + languages
        )

    title_query = st.text_input(
        "Название содержит"
    )

    min_rating = st.slider(
        "Минимальная оценка",
        min_value=0.0,
        max_value=10.0,
        value=0.0,
        step=0.5
    )

    # Применяем фильтры
    result = movies.copy()

    if selected_genre != "Любой":
        result = result[
            result["genres_list"].apply(
                lambda items: selected_genre in items
            )
        ]

    if selected_country != "Любая":
        result = result[
            result["countries_list"].apply(
                lambda items: selected_country in items
            )
        ]

    if selected_language != "Любой":
        result = result[
            result["original_language"] == selected_language
        ]

    if title_query:
        result = result[
            result["title"].str.contains(
                title_query,
                case=False,
                na=False,
                regex=False
            )
        ]

    result = result[
        result["vote_average"] >= min_rating
    ]

    result = result.sort_values(
        ["vote_average", "vote_count"],
        ascending=False
    )

    st.metric("Найдено фильмов", len(result))

    if result.empty:
        st.info("По выбранным параметрам фильмы не найдены.")

    else:
        # Показываем постеры карточками
        display_result = result.head(30)

        for start in range(0, len(display_result), 3):
            cols = st.columns(3)

            for col, (_, movie) in zip(
                cols,
                display_result.iloc[start:start + 3].iterrows()
            ):
                with col:
            
                    st.markdown(
                        f"**{movie['title']} ({movie['year'] or 'год неизвестен'})**"
                    )

                    st.write(
                        f"⭐ Оценка: {movie['vote_average']:.1f}"
                    )

                    st.write(
                        f"Жанры: {movie['genre_text'] or 'Не указаны'}"
                    )

                    st.write(
                        f"Страны: {movie['country_text'] or 'Не указаны'}"
                    )

                    st.divider()

        if len(result) > 30:
            st.caption(
                "Показаны первые 30 результатов. "
                "Для полного списка скачайте CSV."
            )

    # Скачивание результатов
    csv_data = result.to_csv(
        index=False
    ).encode("utf-8-sig")

    st.download_button(
        "📥 Скачать результаты CSV",
        data=csv_data,
        file_name="movies_search.csv",
        mime="text/csv"
    )


# =====================================================
# ВКЛАДКА 2. ТОП ФИЛЬМОВ
# =====================================================

with tab_top:

    st.subheader("🏆 Рейтинг фильмов")

    a, b = st.columns(2)

    with a:
        amount = st.radio(
            "Количество фильмов",
            [10, 15, 30],
            horizontal=True
        )

        metric = st.selectbox(
            "Сортировать по",
            [
                "Взвешенный рейтинг",
                "Средняя оценка",
                "Популярность",
                "Число голосов"
            ]
        )

    with b:
        min_votes = st.number_input(
            "Минимум голосов",
            min_value=0,
            max_value=100000,
            value=100,
            step=50
        )

        top_genre = st.selectbox(
            "Жанр для топа",
            ["Все жанры"] + genres
        )

    ranked = movies[
        movies["vote_count"] >= min_votes
    ].copy()

    if top_genre != "Все жанры":
        ranked = ranked[
            ranked["genres_list"].apply(
                lambda items: top_genre in items
            )
        ]

    # Средняя оценка каталога
    rated_movies = movies[
        movies["vote_count"] > 0
    ]

    global_mean = (
        rated_movies["vote_average"].mean()
        if not rated_movies.empty
        else 0
    )

    # Рассчитываем взвешенный рейтинг
    ranked["weighted_rating"] = ranked.apply(
        lambda row: weighted_rating(
            row["vote_average"],
            row["vote_count"],
            global_mean,
            min_votes
        ),
        axis=1
    )

    sort_columns = {
        "Взвешенный рейтинг": "weighted_rating",
        "Средняя оценка": "vote_average",
        "Популярность": "popularity",
        "Число голосов": "vote_count"
    }

    sort_column = sort_columns[metric]

    top = ranked.sort_values(
        [sort_column, "vote_count"],
        ascending=False
    ).head(amount)

    if top.empty:
        st.info(
            "Нет фильмов, подходящих под выбранный порог голосов."
        )

    else:
        for index, (_, movie) in enumerate(
            top.iterrows(),
            start=1
        ):
            st.markdown(
                f"### {index}. {movie['title']}"
            )

            st.write(
                f"Год выпуска: {movie['year'] or 'Не указан'}"
            )

            st.write(
                f"Жанры: {movie['genre_text'] or 'Не указаны'}"
            )

            st.write(
                f"Оценка: ⭐ {movie['vote_average']:.2f}"
            )

            st.write(
                f"Количество голосов: {int(movie['vote_count'])}"
            )

            st.write(
                f"Взвешенный рейтинг: "
                f"{movie['weighted_rating']:.2f}"
            )

        st.divider()

    # Скачивание топа
    st.download_button(
        "📥 Скачать топ CSV",
        data=top.to_csv(index=False).encode("utf-8-sig"),
        file_name="top_movies.csv",
        mime="text/csv"
    )


# =====================================================
# ВКЛАДКА 3. О ПРОЕКТЕ
# =====================================================

with tab_about:

    st.subheader("О проекте")

    st.write(
        "Учебное приложение для поиска фильмов "
        "по жанру, стране производства и языку оригинала."
    )

    st.write(
        "Для формирования топа доступны четыре варианта "
        "сортировки: средняя оценка, взвешенный рейтинг, "
        "популярность и число голосов."
    )

    st.latex(
        r"WR = \frac{v}{v+m}R + \frac{m}{v+m}C"
    )

    st.caption(
        "R — оценка фильма; v — число голосов; "
        "C — средняя оценка каталога; "
        "m — минимальный порог голосов."
    )

    st.info(
        "Фильмы без постеров автоматически исключаются "
        "из каталога."
    )
