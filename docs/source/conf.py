import os
import sys
sys.path.insert(0, os.path.abspath('../../'))  # Добавляем корень проекта

extensions = [
    'sphinx.ext.autodoc',     # Автоматическая документация по docstring
    'sphinx.ext.napoleon',    # Поддержка Google и NumPy-стилей docstring
    'sphinx.ext.viewcode',    # Добавляет ссылки на исходный код
    'myst_parser'             # Поддержка Markdown файлов
]

html_theme = 'sphinx_rtd_theme'  # Тема оформления
master_doc = 'index'  # Главный файл документации
