from setuptools import setup, find_packages

setup(
    name="augmentations_library",
    version="1.0.0",
    author="Oleg",
    description="Пакет для динамического добавления шумов и фильтров на изображения",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "opencv-python",
    ],
    python_requires='>=3.7',
)