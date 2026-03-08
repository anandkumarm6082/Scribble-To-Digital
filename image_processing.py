import cv2
import numpy as np

def preprocess_image(image):
    """
    Preprocess the image for better OCR results.
    Args:
        image: PIL Image or numpy array
    Returns:
        numpy array: Preprocessed image ready for OCR
    """
    # Convert PIL Image to OpenCV format if needed
    if not isinstance(image, np.ndarray):
        img = np.array(image)
        # Convert RGB to BGR for OpenCV
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    else:
        img = image.copy()

    # 1. Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 2. Adjust brightness and contrast
    # alpha controls contrast (1.0-3.0), beta controls brightness (0-100)
    alpha = 1.2
    beta = 10
    adjusted = cv2.convertScaleAbs(gray, alpha=alpha, beta=beta)

    # 3. Reduce noise using Gaussian Blur
    blurred = cv2.GaussianBlur(adjusted, (5, 5), 0)

    # 4. Apply thresholding for text clarity
    # Using adaptive thresholding which works better for varying lighting conditions in notes
    thresh = cv2.adaptiveThreshold(
        blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )

    return thresh
