# cv_utils.py

import cv2
import fitz


def extract_page_text(page_info):
    pdf_path, page_number = page_info
    with fitz.open(pdf_path) as doc:
        page = doc.load_page(page_number)
        text = page.get_text()
    return text


def convert_grayscale(image_path):
    try:
        image = cv2.imread(image_path)
        if image is None:
            raise FileNotFoundError("L'immagine specificata non è stata trovata.")

        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image_gray = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2GRAY)

        return {
            "image_path": image_path,
            "image": image_gray
        }

    except Exception as e:
        print(f"Si è verificato un errore durante la conversione dell'immagine: {e}")
        return None


def increase_contrast(output_previous_function):
    image_path = output_previous_function["image_path"]
    image = output_previous_function["image"]

    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    image_clahe = clahe.apply(image)

    cv2.imwrite(image_path, image_clahe)

    return {
        "image_path": image_path,
        "image": image_clahe
    }


def thresholding(output_previous_function):
    image_path = output_previous_function["image_path"]
    image = output_previous_function["image"]

    _, image_otsu = cv2.threshold(
        image,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )

    image_adaptive = cv2.adaptiveThreshold(
        image,
        255,
        cv2.ADAPTIVE_THRESH_MEAN_C,
        cv2.THRESH_BINARY,
        19,  # Block Size: 15, 17, 19
        10  # C-Value: 5, 10
    )

    cv2.imwrite(image_path, image_otsu)

    return {
        "image_path": image_path,
        "image": image_otsu
    }