import glob
import os

import fitz
from PIL import Image

pdf_local_directory = f"{os.getcwd()}/PDF"


def select_pdf_files(directory: str) -> list[str]:
    files = glob.glob(os.path.join(directory, "*.pdf"))

    if not files:
        print("В директории нет файлов формата PDF.")
        return []
    else:
        print("Доступные файлы:")
        for i, file_path in enumerate(files):
            print(f"{i+1}. {file_path}")

        selected_files = []  # Список для хранения выбранных файлов
        while True:
            try:
                choice = input(
                    "Введите номер файла, который хотите выбрать (или 'all' для выбора всех файлов, или '0' для выхода): ")
                if choice == '0':
                    print("Отмена операции")
                    break
                elif choice == 'all':
                    selected_files = files
                    print(f"Выбраны все файлы: {selected_files}")
                    return [os.path.basename(file) for file in selected_files]
                else:
                    choice = int(choice)
                    if choice < 1 or choice > len(files):
                        print("Некорректный выбор. Попробуйте еще раз.")
                    else:
                        selected_file = files[choice - 1]
                        print(f"Выбран файл: {selected_file}")
                        # Добавляем выбранный файл в список выбранных файлов
                        selected_files.append(selected_file)
            except ValueError:
                print("Некорректный выбор. Попробуйте еще раз.")
    return [os.path.basename(file) for file in selected_files]


def convert_pdf_to_image(pdf_files, zoom_x=2.0, zoom_y=2.0):
    pdf_folder = "PDF"  # Имя папки с PDF-файлами
    png_folder = "IMAGES"

    if not os.path.exists(png_folder):
        os.makedirs(png_folder)

    for pdf_file in pdf_files:
        # Соединяем имя файла с путем к папке "PDF"
        pdf_path = os.path.join(pdf_folder, pdf_file)
        if not os.path.exists(pdf_path):
            print(f"Файл {pdf_file} не найден в папке 'PDF'. Пропускаем...")
            continue  # Пропускаем файл, если он не существует
        pdf = fitz.open(pdf_path)
        for page_idx in range(pdf.page_count):
            page = pdf.load_page(page_idx)
            pix = page.get_pixmap(matrix=fitz.Matrix(zoom_x, zoom_y))
            image = Image.frombytes(
                "RGB", [pix.width, pix.height], pix.samples).convert("RGB")
            # Изменяем имя файла для каждой страницы
            output_filename = f"{os.path.splitext(pdf_file)[0]}.png"
            output_path = os.path.join(png_folder, output_filename)
            image.save(output_path)
        pdf.close()


def cut_image(image_path):
    # Формируем полный путь к файлу в папке IMAGES
    image_path = os.path.join("IMAGES", image_path)
    image = Image.open(image_path).convert("RGB")

    # Определяем размеры исходного изображения
    width, height = image.size

    # Вычисляем ширину, на которую нужно обрезать справа (3.69 % от ширины)
    cut_width = int(width * 0.0369)

    # Определяем ширину и высоту каждой из 16 равных картинок
    cropped_width = (width - cut_width) // 4
    cropped_height = (height * 0.975) // 4

    # Получаем название начального файла без расширения
    base_name = os.path.splitext(image_path)[0]

    # Создаем папку с именем начального файла без расширения, если ее нет
    folder_name = os.path.basename(base_name)
    if not os.path.exists(folder_name):
        os.makedirs(folder_name, exist_ok=True)

    # Нарезаем исходное изображение на 16 равных картинок
    for i in range(4):
        for j in range(4):
            # Вычисляем координаты для вырезания фотографии
            left = i * cropped_width
            top = j * cropped_height
            right = (i + 1) * cropped_width
            bottom = (j + 1) * cropped_height

            # Вырезаем фотографию из исходного изображения
            photo = image.crop((left, top, right, bottom))

            # Формируем имя файла для сохранения
            file_name = f"{folder_name}/{folder_name}_photo_{i + 1}_{j + 1}.png"

            # Сохраняем фотографию в отдельный файл
            photo.save(file_name)

            if is_white_image(file_name, white_threshold=30):
                os.remove(file_name)

    print("Файл успешно нарезан на 16 равных картинок.")


def is_white_image(image_path, white_threshold=30):
    # Открываем изображение
    image = Image.open(image_path)

    # Получаем пиксели изображения
    pixels = image.load()

    # Проверяем наличие пикселей, отличных от белого
    is_white = True
    for x in range(image.width):
        for y in range(image.height):
            # Получаем значения красного, зеленого и синего цветов пикселя
            r, g, b = pixels[x, y]
            if abs(r - 255) > white_threshold or abs(g - 255) > white_threshold or abs(b - 255) > white_threshold:
                # Проверяем отклонение значений цветов от белого с порогом
                is_white = False
                break
        if not is_white:
            break

    return is_white


def main():
    pdf_file = select_pdf_files(pdf_local_directory)
    if pdf_file != None:
        convert_pdf_to_image(pdf_file)
        for png in pdf_file:
            # Обрезаем окончание ".pdf"
            if png.endswith(".pdf"):
                png = png[:-4]
            png += ".png"
            cut_image(png)
    else:
        print("PDF-файл не найден")


if __name__ == "__main__":
    main()
