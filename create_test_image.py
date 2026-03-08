from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random
import os

def create_sample_image(filename="sample_note.jpg"):
    # Create a white background image
    width, height = 800, 600
    img = Image.new('RGB', (width, height), color=(240, 240, 230))
    d = ImageDraw.Draw(img)
    
    # Try to load a generic font, or fallback to default
    try:
        # Many Windows systems have comic sans or similar
        font = ImageFont.truetype("arial.ttf", 36)
        header_font = ImageFont.truetype("arial.ttf", 48)
    except IOError:
        font = ImageFont.load_default()
        header_font = font
        
    # Draw some text
    text = """
Project Meeting Notes
- Discussed the new OCR feature
we ned to implmt the img preprocsng soon
- Get feedback from the client by friday
Also remmber to by groceries: milk, eqqs, bred
Todos:
* Fix the styling bug on main page
* Email John about the new requrements
"""
    
    # Draw text with slight random offsets to simulate handwriting messiness
    y_text = 50
    for line in text.split('\n'):
        x_text = 50 + random.randint(-5, 5)
        d.text((x_text, y_text), line, fill=(20, 20, 40), font=font)
        y_text += 50 + random.randint(-2, 5)
        
    # Add some noise/artifacts to simulate bad lighting/camera
    for _ in range(2000):
        x = random.randint(0, width-1)
        y = random.randint(0, height-1)
        d.point((x, y), fill=(100, 100, 100))
        
    # Apply a slight blur
    img = img.filter(ImageFilter.GaussianBlur(radius=0.5))
    
    # Save image
    img.save(filename)
    print(f"Created sample test image: {filename}")

if __name__ == "__main__":
    create_sample_image()
