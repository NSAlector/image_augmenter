from noise_lab import ImageLoader, GaussianNoise, MedianFilter, WaveEffect

loader = ImageLoader()
img = loader.load("download.jpeg")

effects = [
    WaveEffect(amplitude=15, frequency=0.02, direction='horizontal'),
    GaussianNoise(sigma=10),
    MedianFilter(kernel_size=3)
]

for effect in effects:
    img = effect.apply(img)
    
loader.save("Pictires/result.png", img)