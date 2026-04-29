import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import random

def create_normal_eye(path, size=(64, 64), variant=0):
    """
    Normal eye: smooth, uniform tear film with subtle natural variations.
    Multiple visual strategies for diversity.
    """
    img = np.zeros((size[0], size[1], 3), dtype=np.uint8)
    
    # Base color palettes for healthy eyes (smooth, blueish/greenish tones)
    palettes = [
        (40, 60, 120),   # Blue-tinted healthy
        (50, 70, 110),   # Slightly warmer blue
        (35, 65, 100),   # Muted teal
        (45, 55, 130),   # Deep blue
        (30, 70, 95),    # Aqua tone
        (55, 75, 105),   # Light steel
        (40, 80, 115),   # Cyan-blue
        (50, 60, 90),    # Dark teal
    ]
    
    palette = palettes[variant % len(palettes)]
    
    # Random slight shifts for each image
    r_shift = random.randint(-8, 8)
    g_shift = random.randint(-8, 8)
    b_shift = random.randint(-10, 10)
    
    # Smooth gradient base (simulating healthy, uniform tear film)
    freq_x = random.uniform(8, 14)
    freq_y = random.uniform(6, 12)
    freq_xy = random.uniform(10, 16)
    amp_r = random.randint(10, 20)
    amp_g = random.randint(8, 15)
    amp_b = random.randint(15, 25)
    
    for y in range(size[0]):
        for x in range(size[1]):
            r = palette[0] + r_shift + int(amp_r * np.sin(x / freq_x))
            g = palette[1] + g_shift + int(amp_g * np.cos(y / freq_y))
            b = palette[2] + b_shift + int(amp_b * np.sin((x + y) / freq_xy))
            img[y, x] = [
                np.clip(r, 0, 255),
                np.clip(g, 0, 255),
                np.clip(b, 0, 255)
            ]
    
    pil_img = Image.fromarray(img)
    
    # Apply varying degrees of Gaussian blur for smoothness
    blur_radius = random.choice([1.5, 2, 2.5, 3])
    pil_img = pil_img.filter(ImageFilter.GaussianBlur(radius=blur_radius))
    
    # Random brightness/contrast adjustments
    enhancer = ImageEnhance.Brightness(pil_img)
    pil_img = enhancer.enhance(random.uniform(0.9, 1.15))
    enhancer = ImageEnhance.Contrast(pil_img)
    pil_img = enhancer.enhance(random.uniform(0.85, 1.1))
    
    # Occasionally add a subtle light reflection (healthy tear film reflects light)
    if random.random() < 0.4:
        draw = ImageDraw.Draw(pil_img)
        cx = random.randint(15, 48)
        cy = random.randint(15, 48)
        r = random.randint(2, 5)
        brightness = random.randint(180, 240)
        draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(brightness, brightness, brightness+10))
        pil_img = pil_img.filter(ImageFilter.GaussianBlur(radius=1.5))
    
    pil_img.save(path)


def create_abnormal_eye(path, size=(64, 64), variant=0):
    """
    Abnormal eye: rough texture, dry spots, redness, irregular patterns.
    Multiple visual strategies for diversity.
    """
    strategy = variant % 5
    
    if strategy == 0:
        # Strategy 1: Noisy with red inflammation
        img = np.random.randint(80, 200, size=(size[0], size[1], 3), dtype=np.uint8)
        img[:, :, 0] = np.clip(img[:, :, 0] + random.randint(40, 80), 0, 255)  # Red tint
        
    elif strategy == 1:
        # Strategy 2: Patchy uneven texture
        img = np.zeros((size[0], size[1], 3), dtype=np.uint8)
        for y in range(size[0]):
            for x in range(size[1]):
                noise = random.randint(-30, 30)
                if (x + y) % random.randint(3, 7) == 0:
                    img[y, x] = [160 + noise, 100 + noise, 80 + noise]
                else:
                    img[y, x] = [100 + noise, 70 + noise, 60 + noise]
                    
    elif strategy == 2:
        # Strategy 3: High contrast edges (tear film breakup)
        img = np.random.randint(60, 180, size=(size[0], size[1], 3), dtype=np.uint8)
        # Add sharp edge artifacts
        for _ in range(random.randint(3, 8)):
            y_start = random.randint(0, 50)
            x_start = random.randint(0, 50)
            length = random.randint(5, 20)
            thickness = random.randint(1, 3)
            color = [random.randint(180, 255), random.randint(50, 100), random.randint(30, 80)]
            for t in range(thickness):
                for l in range(length):
                    yy = min(y_start + t, 63)
                    xx = min(x_start + l, 63)
                    img[yy, xx] = color
                    
    elif strategy == 3:
        # Strategy 4: Yellowish dry film
        img = np.zeros((size[0], size[1], 3), dtype=np.uint8)
        for y in range(size[0]):
            for x in range(size[1]):
                base = random.randint(100, 180)
                img[y, x] = [
                    min(base + random.randint(20, 60), 255),
                    min(base + random.randint(10, 40), 255),
                    max(base - random.randint(20, 50), 0)
                ]
    else:
        # Strategy 5: Mixed noise with dark dry zones
        img = np.random.randint(90, 210, size=(size[0], size[1], 3), dtype=np.uint8)
        img[:, :, 0] = np.clip(img[:, :, 0] + 30, 0, 255)  # Mild red
    
    # Add random dark dry spots (common across all strategies)
    num_spots = random.randint(3, 18)
    for _ in range(num_spots):
        cx = random.randint(3, 60)
        cy = random.randint(3, 60)
        r = random.randint(2, 9)
        spot_color = [random.randint(15, 45), random.randint(10, 35), random.randint(5, 25)]
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                if 0 <= cy + dy < 64 and 0 <= cx + dx < 64 and dx * dx + dy * dy <= r * r:
                    # Add some noise to spots too
                    noise = random.randint(-10, 10)
                    img[cy + dy, cx + dx] = [
                        np.clip(spot_color[0] + noise, 0, 255),
                        np.clip(spot_color[1] + noise, 0, 255),
                        np.clip(spot_color[2] + noise, 0, 255)
                    ]
    
    # Random roughness lines (irregular tear film)
    if random.random() < 0.6:
        for _ in range(random.randint(2, 6)):
            y_pos = random.randint(5, 58)
            for x in range(0, 64, random.randint(1, 3)):
                if 0 <= y_pos < 64:
                    img[y_pos, x] = [random.randint(140, 220), random.randint(60, 100), random.randint(40, 70)]
    
    pil_img = Image.fromarray(img)
    
    # Less blur than normal (abnormal = rougher texture)
    if random.random() < 0.5:
        pil_img = pil_img.filter(ImageFilter.GaussianBlur(radius=random.uniform(0.3, 1.0)))
    
    # Random brightness variation
    enhancer = ImageEnhance.Brightness(pil_img)
    pil_img = enhancer.enhance(random.uniform(0.8, 1.2))
    
    # Occasionally sharpen (emphasize roughness)
    if random.random() < 0.4:
        pil_img = pil_img.filter(ImageFilter.SHARPEN)
    
    pil_img.save(path)


def create_dataset():
    base_dir = "dataset"
    
    # 150 train + 50 test per class = 200 images per class = 400 total
    splits = ["train", "test"]
    counts = {"train": 150, "test": 50}
    
    total_created = 0
    
    for split in splits:
        for c in ["normal", "abnormal"]:
            dir_path = os.path.join(base_dir, split, c)
            os.makedirs(dir_path, exist_ok=True)
            
            for i in range(counts[split]):
                path = os.path.join(dir_path, f"img_{i}.jpg")
                if c == "normal":
                    create_normal_eye(path, variant=i)
                else:
                    create_abnormal_eye(path, variant=i)
                total_created += 1
            
            print(f"  [OK] Created {counts[split]} {c} images in {split}/")
    
    print(f"\n{'='*50}")
    print(f"  Dataset Complete: {total_created} total images")
    print(f"  Train: {counts['train']} normal + {counts['train']} abnormal = {counts['train']*2}")
    print(f"  Test:  {counts['test']} normal + {counts['test']} abnormal = {counts['test']*2}")
    print(f"{'='*50}")


if __name__ == "__main__":
    print("=" * 50)
    print("  LacriMetric Data Generator")
    print("  Generating synthetic eye images...")
    print("=" * 50)
    create_dataset()
