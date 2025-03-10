import cv2
import numpy as np


def remove_background(image_path, output_path):
    # Read the image
    image = cv2.imread(image_path)

    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply a binary threshold to the image
    _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

    # Find contours in the binary image
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Create a mask with the same dimensions as the image
    mask = np.zeros_like(image)

    # Draw the contours on the mask
    cv2.drawContours(mask, contours, -1, (255, 255, 255), thickness=cv2.FILLED)

    # Invert the mask
    mask = cv2.bitwise_not(mask)

    # Apply the mask to the image
    result = cv2.bitwise_and(image, mask)

    # Save the result
    cv2.imwrite(output_path, result)


# Example usage
remove_background('item1.jpg', 'output_image.png')




