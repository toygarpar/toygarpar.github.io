import os
import markdown
from jinja2 import Environment, FileSystemLoader

# Scriptin olduğu klasörü baz alalım
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
POSTS_DIR = os.path.join(SCRIPT_DIR, "rants")
BLOG_DIR = os.path.join(SCRIPT_DIR, "blog") # Bireysel yazılar buraya
TEMPLATES_DIR = os.path.join(SCRIPT_DIR, "templates")

# Klasörleri kontrol et ve oluştur
os.makedirs(BLOG_DIR, exist_ok=True)

env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))

def generate_rants():
    rants_list = []
    
    try:
        post_template = env.get_template('rant_post_template.html')
        index_template = env.get_template('blog_index_template.html')
    except Exception as e:
        print(f"❌ Hata: Şablonlar bulunamadı! {e}")
        return

    # MD dosyalarını tara
    for filename in os.listdir(POSTS_DIR):
        if filename.endswith(".md"):
            with open(os.path.join(POSTS_DIR, filename), "r", encoding="utf-8") as f:
                raw_md = f.read()
                html_content = markdown.markdown(raw_md, extensions=['extra', 'nl2br', 'smarty'])
                
                title = filename.replace(".md", "").replace("-", " ").title()
                summary = (raw_md[:200] + '...') if len(raw_md) > 200 else raw_md
                
                rant_data = {
                    "title": title,
                    "content": html_content,
                    "summary": summary.replace("#", "").replace("*", "").strip(),
                    "slug": f"blog/{filename.replace('.md', '.html')}", # Linkleri 'blog/' klasörüne yönlendir
                    "date": "22 Nisan 2026" 
                }
                rants_list.append(rant_data)

                # Bireysel yazıyı 'blog' klasörüne yazdır
                file_name_only = filename.replace(".md", ".html")
                post_output_path = os.path.join(BLOG_DIR, file_name_only)
                with open(post_output_path, "w", encoding="utf-8") as out:
                    out.write(post_template.render(rant=rant_data))

    
    # index.html dosyasını 'blog' klasörüne değil, scriptin olduğu (Rant) ana klasöre yaz.
    index_output_path = os.path.join(SCRIPT_DIR, "index.html")
    
    with open(index_output_path, "w", encoding="utf-8") as f:
        f.write(index_template.render(rants=rants_list))

    print(f"✅ Başarılı! 'index.html' ana klasörde, yazılar ise 'blog/' içinde oluşturuldu.")

if __name__ == "__main__":
    generate_rants()