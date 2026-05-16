# Augmenter

Описание проекта
-----------------
Проект "Augmenter" — простой инструмент для просмотра изображений и пакетной аугментации датасетов.
Он включает GUI на PyQt5 (`ImageViewer`) для просмотра/сохранения описаний изображений и вкладку "Mass Processing" для создания набора данных с аугментациями.

Структура репозитория
---------------------
- `main.py` — точка входа запуска GUI-приложения.
- `imageviewer.py` — реализация `ImageViewer` (PyQt5): просмотр, печать, копирование/вставка, сохранение описаний в `info.csv`, поиск.
- `Methods.py` — `AugmentationManager`: перечисление доступных эффектов и пакетная аугментация (с сохранением в целевую папку).
- `Find_image.py` — утилитный скрипт поиска изображений по описанию; использует `pandas` и внешний модуль `MIPT_practice.find_image`.
- `augmenters/__init__.py` — заглушка пакета аугментаций (возвращает список фиктивных методов).
- `info.csv` — таблица метаданных изображений (формат CSV с разделителем `;`: index;path;description).
- `Images/` — папка для хранения копий изображений проекта (используется `ImageViewer`).

Ключевые компоненты и API
-------------------------
- **`ImageViewer` (в `imageviewer.py`)**:
	- `load_file(fileName)` — загрузка изображения в GUI; устанавливает `_current_file` и загружает описание из `info.csv`.
	- `_save_info()` — сохраняет/обновляет запись в `info.csv`, копирует файл в `Images/` при необходимости.
	- `_search_by_description()` — вызывает `Find_image.py` с переданным запросом и открывает первый найденный результат.
	- `_search_by_path()` — локализованный поиск файла по пути/относительному пути.
	- `_create_dataset()` — собирает выбранные методы аугментации (checkboxes) и вызывает `AugmentationManager.batch_augment` или просто копирует файлы при отсутствии методов.

- **`AugmentationManager` (в `Methods.py`)**:
	- `list_effects_for_ui()` — использует `NoiseLoader` (`augmentations_library.Loader`) для перечисления доступных классов-эффектов; возвращает список `(id, label, description)` для UI.
	- `batch_augment(src_dir, dst_dir, methods, use_rng=True)` — пакетная обработка: для каждого изображения последовательно применяются выбранные эффекты; если `use_rng==True`, для каждого изображения/метода бросается PRNG (применяется при r<0.5). Поддерживается secondary_image для эффектов, атомарная запись через staging.
	- Зависит от `ImageLoader` и `NoiseLoader` из `augmentations_library.Loader` (в проекте ожидается соответствующая структура в `Project/augmentations_library`).

- **`Find_image.py`**:
	- CLI-утилита: принимает `query` и возвращает JSON-массив путей найденных изображений.
	- Использует `pandas` для чтения `info.csv` и функцию `find_unique_images` из `MIPT_practice.find_image`.

Взаимодействие компонентов
--------------------------
- GUI (`ImageViewer`) отображает список доступных методов, получая их от `Methods.AugmentationManager.list_effects_for_ui()`.
- При создании датасета GUI вызывает `AugmentationManager.batch_augment(...)`, который использует классы-эффекты из `augmentations_library`.
- Поиск по описанию выполняется отдельным скриптом `Find_image.py`, результат которого GUI парсит и открывает найденный файл.

Формат данных
------------
- `info.csv` — ожидается CSV с `;` как разделителем. Ожидаемые колонки: `index;path;description` (путь обычно относительно `Images/`).


Заметки и ограничения
---------------------
- Аугментации: проект ожидает внешнюю реализацию `augmentations_library.Loader` с классами `ImageLoader` и `NoiseLoader`. В текущем дереве `augmenters/` присутствует только заглушка.
- PRNG-порог в `AugmentationManager.batch_augment` фиксирован (0.5). Можно изменить логику порога в коде для управления долей применений.
- `Find_image.py` полагается на `MIPT_practice.find_image.find_unique_images`.
- Работа с путями в `imageviewer` учитывает переносы на разных дисках и пытается корректно определять, находится ли файл в `Images`.