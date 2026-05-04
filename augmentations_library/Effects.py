import cv2
import numpy as np
from abc import ABC, abstractmethod

class BaseEffect(ABC):
    """Единый интерфейс для всех эффектов"""
    @abstractmethod
    def apply(self, image: np.ndarray) -> np.ndarray:
        pass

class GaussianNoise(BaseEffect):
    def __init__(self, mean=0, sigma=25):
        self.mean = mean
        self.sigma = sigma

    def apply(self, image: np.ndarray) -> np.ndarray:
        noise = np.random.normal(self.mean, self.sigma, image.shape)
        noisy = image.astype(np.float32) + noise
        return np.clip(noisy, 0, 255).astype(np.uint8)

class SaltPepperNoise(BaseEffect):
    def __init__(self, prob=0.02):
        self.prob = prob

    def apply(self, image: np.ndarray) -> np.ndarray:
        noisy = image.copy()
        random_mask = np.random.random(image.shape[:2])
        noisy[random_mask < (self.prob / 2)] = 0    # Pepper
        noisy[random_mask > (1 - self.prob / 2)] = 255 # Salt
        return noisy
    
class GaussianBlur(BaseEffect):
    def __init__(self, kernel_size=(5, 5), sigma=0):
        self.kernel_size = kernel_size
        self.sigma = sigma

    def apply(self, image: np.ndarray) -> np.ndarray:
        return cv2.GaussianBlur(image, self.kernel_size, self.sigma)

class MedianFilter(BaseEffect):
    def __init__(self, kernel_size=5):
        self.kernel_size = kernel_size

    def apply(self, image: np.ndarray) -> np.ndarray:
        return cv2.medianBlur(image, self.kernel_size)

class HistogramEqualization(BaseEffect):
    """Улучшение контраста через эквализацию"""
    def apply(self, image: np.ndarray) -> np.ndarray:
        if len(image.shape) == 3:
            img_yuv = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
            # Эквализируем только канал яркости (Y)
            img_yuv[:,:,0] = cv2.equalizeHist(img_yuv[:,:,0])
            return cv2.cvtColor(img_yuv, cv2.COLOR_YUV2BGR)
        return cv2.equalizeHist(image)
    
class SwirlEffect(BaseEffect):
    def __init__(self, intensity=0.5, radius=None):
        self.strength = intensity * 5
        self.radius = radius

    def apply(self, image: np.ndarray) -> np.ndarray:
        h, w = image.shape[:2]
        center = (w // 2, h // 2)
        radius = self.radius or min(w, h) * 0.8
        
        x, y = np.meshgrid(np.arange(w), np.arange(h))
        dx, dy, r = x - center[0], y - center[1], np.sqrt((x-center[0])**2 + (y-center[1])**2)
        theta = np.arctan2(dy, dx) + np.maximum(0, self.strength * (1 - r / radius))
        
        x_map = (center[0] + r * np.cos(theta)).astype(np.float32)
        y_map = (center[1] + r * np.sin(theta)).astype(np.float32)
        return cv2.remap(image, x_map, y_map, cv2.INTER_LINEAR)
    
class WaveEffect(BaseEffect):
    """
    Геометрическое искажение 'Волна'.
    Создает волнообразное смещение пикселей по горизонтали или вертикали.
    """
    def __init__(self, amplitude=10, frequency=0.05, direction='horizontal'):
        """
        Args:
            amplitude (int): Сила волны (смещение в пикселях). 
                             Чем больше, тем сильнее искажение.
            frequency (float): Частота волны. Чем больше, тем больше "волн" на изображении.
            direction (str): Направление волны. 'horizontal' (по умолчанию) или 'vertical'.
        """
        self.amplitude = amplitude
        self.frequency = frequency
        self.direction = direction

    def apply(self, image: np.ndarray) -> np.ndarray:
        """Применяет волновое искажение к изображению"""
        h, w = image.shape[:2]
        
        x, y = np.meshgrid(np.arange(w), np.arange(h))
        
        x_map = x.astype(np.float32)
        y_map = y.astype(np.float32)

        if self.direction == 'horizontal':
            # Смещаем X координату в зависимости от Y координаты
            deviation = self.amplitude * np.sin(2 * np.pi * y * self.frequency)
            x_map += deviation
        elif self.direction == 'vertical':
            # Смещаем Y координату в зависимости от X координаты
            deviation = self.amplitude * np.sin(2 * np.pi * x * self.frequency)
            y_map += deviation
        else:
            raise ValueError("Direction must be 'horizontal' or 'vertical'")
        return cv2.remap(image, x_map, y_map, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT_101)

class ChessboardBlend(BaseEffect):
    """Смешивает текущее изображение со вторым в шахматном порядке"""
    def __init__(self, secondary_image: np.ndarray, cell_size=50):
        self.secondary_image = secondary_image
        self.cell_size = cell_size

    def apply(self, image: np.ndarray) -> np.ndarray:
        h, w = image.shape[:2]
        img2 = cv2.resize(self.secondary_image, (w, h))
        
        mask = np.zeros((h, w), dtype=np.float32)
        for i in range(h):
            for j in range(w):
                if ((i // self.cell_size) + (j // self.cell_size)) % 2 != 0:
                    mask[i, j] = 1.0
        
        if len(image.shape) == 3:
            mask = np.repeat(mask[:, :, np.newaxis], 3, axis=2)
            
        result = image * (1 - mask) + img2 * mask
        return result.astype(np.uint8)