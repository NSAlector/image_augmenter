from PIL import Image

def load_image(file):
    try:
        img = Image.open(file)
        img.show()
        return img
    except FileNotFoundError:
        print(f"Файл {file} не найден")
    except Exception as ex:
        print(f"Ошибка при загрузке изображения: {ex}")
    