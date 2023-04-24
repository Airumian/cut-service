import glob
import os

import fitz
from PIL import Image

pdf_local_directory = f"{os.getcwd()}/PDF"


def select_pdf_files(directory: str) -> list[str]:
    """
    Позволяет пользователю выбрать один или несколько PDF-файлов из заданной директории.

    Аргументы:
    - directory: строка с путем к локальной директории, в которой нужно выбрать PDF-файлы.

    Возвращает:
    - Список с выбранными файлами (названия файлов).
      Если пользователь выбрал все файлы, то возвращается список со всеми файлами в директории.
      Если пользователь не выбрал ни одного файла, возвращается пустой список.
    """
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
    """
    Конвертирует PDF в изображения формата JPEG.

    Аргументы:
    pdf_files (List[str]): Имена PDF-файлов в папке "PDF".
    zoom_x (float): Масштаб по оси X (по умолчанию 2.0).
    zoom_y (float): Масштаб по оси Y (по умолчанию 2.0).
    """
    pdf_folder = "PDF"  # Имя папки с PDF-файлами
    jpeg_folder = "IMAGES"  # Имя папки для сохранения JPEG-изображений

    if not os.path.exists(jpeg_folder):
        # Создаем папку "JPEG", если она не существует
        os.makedirs(jpeg_folder)

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
                "RGB", [pix.width, pix.height], pix.samples)
            # Изменяем имя файла для каждой страницы
            output_filename = f"{os.path.splitext(pdf_file)[0]}.jpeg"
            # Соединяем имя файла с путем к папке "JPEG"
            output_path = os.path.join(jpeg_folder, output_filename)
            image.save(output_path)
        pdf.close()


def cut_image(image_path):
    """
    Функция для нарезания исходного изображения на отдельные фотографии.

    Аргументы:
        - image_path (str): Путь к исходному JPEG-файлу.
    """

    # Формируем полный путь к файлу в папке IMAGES
    image_path = os.path.join("IMAGES", image_path)

    # Открываем исходный JPEG-файл
    image = Image.open(image_path)

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
        os.makedirs(folder_name)

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
            file_name = f"{folder_name}/{base_name}_photo_{i + 1}_{j + 1}.jpg"

            # Сохраняем фотографию в отдельный файл
            photo.save(file_name)

    print("Файл успешно нарезан на 16 равных картинок.")


def main():
    pdf_file = select_pdf_files(pdf_local_directory)
    if pdf_file != None:
        convert_pdf_to_image(pdf_file)
        for jpeg in pdf_file:
            # Обрезаем окончание ".pdf"
            if jpeg.endswith(".pdf"):
                jpeg = jpeg[:-4]
            # Добавляем новое окончание ".jpeg"
            jpeg += ".jpeg"
            cut_image(jpeg)
    else:
        print("PDF-файл не найден")


if __name__ == "__main__":
    main()
