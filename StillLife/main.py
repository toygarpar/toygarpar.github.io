import os
from jinja2 import Environment, FileSystemLoader
from PIL import Image
from PIL.ExifTags import TAGS

# --- Ayarlar ---
OUTPUT_DIR = "." 
BASE_DIR = "assets/photography"
TEMPLATE_DIR = "templates"
categories = ["events", "portraits", "product", "corporate", "street", "food"]

script_dir = os.path.dirname(os.path.abspath(__file__))
templates_path = os.path.join(script_dir, TEMPLATE_DIR)
base_photography_path = os.path.join(script_dir, BASE_DIR)

def get_exif_data(image_path):
    """Resmin EXIF verisinden teknik detayları çeker."""
    details = {
        "camera": "UNKNOWN CAMERA",
        "iso": "-",
        "shutter": "-",
        "aperture": "-",
        "focal": "-"
    }
    try:
        with Image.open(image_path) as img:
            exif_data = img._getexif()
            if exif_data:
                for tag, value in exif_data.items():
                    tag_name = TAGS.get(tag, tag)
                    
                    if tag_name == "Model":
                        details["camera"] = value
                    elif tag_name == "ISOSpeedRatings":
                        details["iso"] = f"ISO {value}"
                    elif tag_name == "ExposureTime":
                        # Perde hızını rasyonel sayıdan 1/200 gibi okunabilir hale getiriyoruz
                        if isinstance(value, tuple) or hasattr(value, 'numerator'):
                            num, den = value.numerator, value.denominator
                            if num == 1:
                                details["shutter"] = f"1/{den}s"
                            else:
                                details["shutter"] = f"{float(num/den)}s"
                        else:
                            details["shutter"] = f"{value}s"
                    elif tag_name == "FNumber":
                        details["aperture"] = f"f/{float(value):.1f}"
                    elif tag_name == "FocalLength":
                        details["focal"] = f"{int(value)}mm"
    except Exception:
        pass
    return details

if not os.path.exists(templates_path):
    print(f"❌ HATA: '{templates_path}' klasörü bulunamadı!")
else:
    env = Environment(loader=FileSystemLoader(templates_path))

    def generate_portfolio():
        all_data = []
        try:
            portfolio_temp = env.get_template('portfolio_template.html')
            index_temp = env.get_template('index_template.html')
        except Exception as e:
            print(f"❌ Şablon hatası: {e}")
            return

        for cat in categories:
            cat_path = os.path.join(base_photography_path, cat)
            os.makedirs(cat_path, exist_ok=True) 
            
            raw_images = [f for f in os.listdir(cat_path) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]
            
            image_list_with_meta = []
            for img_name in sorted(raw_images):
                full_path = os.path.join(cat_path, img_name)
                # EXIF verilerini çekiyoruz
                meta = get_exif_data(full_path)
                image_list_with_meta.append({
                    "filename": img_name,
                    "camera": meta["camera"],
                    "iso": meta["iso"],
                    "shutter": meta["shutter"],
                    "aperture": meta["aperture"],
                    "focal": meta["focal"]
                })
            
            cat_data = {
                "title": cat.replace("_", " ").title(),
                "slug": cat,
                "images": image_list_with_meta,
                "image_count": len(image_list_with_meta)
            }
            all_data.append(cat_data)

            with open(os.path.join(script_dir, f"{cat}.html"), "w", encoding="utf-8") as f:
                f.write(portfolio_temp.render(category=cat_data))

        with open(os.path.join(script_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(index_temp.render(categories=all_data))
        print("✅ Portfolyo teknik EXIF detaylarıyla güncellendi!")

    if __name__ == "__main__":
        generate_portfolio()