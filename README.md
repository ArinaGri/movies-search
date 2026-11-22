# 🎬 Что посмотреть? — упрощённая версия

Учебное Streamlit-приложение для поиска фильмов и просмотра топа.

## Функции
- Поиск по жанру, стране производства и языку оригинала.
- Дополнительные фильтры: часть названия и минимальная оценка.
- Топ-10 или топ-15 по выбранному критерию: взвешенный рейтинг, средняя оценка, популярность или число голосов.
- Ограничение минимального числа голосов и фильтр жанра для топа.
- Экспорт результатов в CSV.

## Важно про данные
`data/movies.csv` — небольшой демонстрационный набор для проверки интерфейса, а не полный каталог. Для большого каталога замените файл CSV, сохранив столбцы:
`title, year, genres, countries, original_language, vote_average, vote_count, popularity`.
Жанры и страны внутри ячеек разделяются символом `|`.

## Запуск на macOS
```bash
python3 --version
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
pytest
streamlit run app.py
```
Откройте http://localhost:8501. Остановка: Ctrl+C.

## Docker
```bash
docker build -t movie-finder .
docker run --rm -p 8501:8501 movie-finder
```
Откройте http://localhost:8501. Остановка: Ctrl+C.

## Работа командой из трёх человек
Роли (пример):
1. Участник A — поиск и фильтры (`app.py`, поиск, проверка CSV).
2. Участник B — топ рейтингов и формула (`app.py`, логика рейтинга, тесты).
3. Участник C — Docker, README, проверка запуска и презентация.

Чтобы коммиты действительно были от каждого:
- каждый участник работает под своим GitHub-аккаунтом;
- каждый настраивает собственное имя и email Git:
  `git config user.name "Имя Фамилия"`
  `git config user.email "email, подтверждённый в GitHub"`
- каждый создаёт свою ветку, делает реальные изменения и коммиты, затем открывает Pull Request;
- не делайте все коммиты с одного аккаунта и не меняйте автора задним числом ради количества коммитов.

### Общий Git-процесс
Один участник создаёт пустой репозиторий на GitHub (без README и .gitignore), затем:
```bash
git init
git add .
git commit -m "Initial project structure"
git branch -M main
git remote add origin https://github.com/USERNAME/movie-finder.git
git push -u origin main
```
Каждый из двух остальных участников:
```bash
git clone https://github.com/USERNAME/movie-finder.git
cd movie-finder
git switch -c feature/my-task
# вносит свои изменения
git add .
git commit -m "Add my feature"
git push -u origin feature/my-task
```
Затем на GitHub — Compare & pull request → Create pull request. Владелец проверяет и нажимает Merge. Перед новой задачей:
```bash
git switch main
git pull
git switch -c feature/next-task
```

## Рекомендуемое распределение задач
- Участник A: жанр/страна/язык, поиск по названию, проверка фильтрации.
- Участник B: выбор топ-10/15, критерии сортировки, порог голосов, тесты.
- Участник C: Dockerfile, запуск контейнера, README, демонстрационные скриншоты.
Каждый должен внести содержательные изменения в своей зоне и сделать минимум несколько осмысленных коммитов.
