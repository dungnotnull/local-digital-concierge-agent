import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import io

class ImagePreprocessor:
    @staticmethod
    def preprocess_image(image_bytes: bytes) -> bytes:
        """
        Preprocess an image for better OCR results.
        Steps:
        1. Convert to grayscale
        2. Denoise
        3. Increase contrast
        4. Deskew (if needed)
        5. Return processed image as bytes
        """
        # Convert bytes to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            # If OpenCV fails, try PIL
            pil_img = Image.open(io.BytesIO(image_bytes))
            img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Denoise
        denoised = cv2.fastNlMeansDenoising(gray, h=10)
        
        # Increase contrast using CLAHE
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        contrasted = clahe.apply(denoised)
        
        # Deskew: estimate skew angle and correct
        coords = np.column_stack(np.where(contrasted > 0))
        if len(coords) > 0:
            angle = cv2.minAreaRect(coords)[-1]
            if angle < -45:
                angle = -(90 + angle)
            else:
                angle = -angle
            # Rotate the image to deskew
            (h, w) = contrasted.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            rotated = cv2.warpAffine(contrasted, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        else:
            rotated = contrasted
        
        # Encode back to bytes
        _, buffer = cv2.imencode('.png', rotated)
        return buffer.tobytes()
    
    @staticmethod
    def check_image_quality(image_bytes: bytes) -> dict:
        """
        Check image quality: blur, darkness, resolution.
        Returns a dict with quality metrics and a boolean if usable.
        """
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
        if img is None:
            return {"usable": False, "reason": "Could not decode image"}
        
        # Check resolution
        height, width = img.shape
        if width < 300 or height < 300:
            return {"usable": False, "reason": f"Resolution too low: {width}x{height}", "width": width, "height": height}
        
        # Check blur using Laplacian variance
        laplacian_var = cv2.Laplacian(img, cv2.CV_64F).var()
        if laplacian_var < 100:  # threshold
            return {"usable": False, "reason": f"Image too blurry: {laplacian_var}", "blur": laplacian_var}
        
        # Check darkness
        mean_brightness = np.mean(img)
        if mean_brightness < 50:  # too dark
            return {"usable": False, "reason": f"Image too dark: {mean_brightness}", "brightness": mean_brightness}
        if mean_brightness > 200:  # too washed out
            return {"usable": False, "reason": f"Image too bright: {mean_brightness}", "brightness": mean_brightness}
        
        return {"usable": True, "blur": laplacian_var, "brightness": mean_brightness, "width": width, "height": height}
