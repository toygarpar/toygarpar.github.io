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

def get_camera_model(image_path):
    """Resmin EXIF verisinden kamera modelini çeker."""
    try:
        with Image.open(image_path) as img:
            exif_data = img._getexif()
            if exif_data:
                for tag, value in exif_data.items():
                    tag_name = TAGS.get(tag, tag)
                    if tag_name == "Model":
                        return value
    except Exception:
        pass
    return "UNKNOWN CAMERA"

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
            
            # Her resim için özel veri oluşturuyoruz
            image_list_with_meta = []
            for img_name in sorted(raw_images):
                full_path = os.path.join(cat_path, img_name)
                camera = get_camera_model(full_path)
                image_list_with_meta.append({
                    "filename": img_name,
                    "camera": camera
                })
            
            cat_data = {
                "title": cat.replace("_", " ").title(),
                "slug": cat,
                "images": image_list_with_meta, # Artık sadece isim değil, bir sözlük listesi
                "image_count": len(image_list_with_meta)
            }
            all_data.append(cat_data)

            with open(os.path.join(script_dir, f"{cat}.html"), "w", encoding="utf-8") as f:
                f.write(portfolio_temp.render(category=cat_data))

        with open(os.path.join(script_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(index_temp.render(categories=all_data))
        print("✅ Portfolyo EXIF verileriyle güncellendi!")

    if __name__ == "__main__":
        generate_portfolio()