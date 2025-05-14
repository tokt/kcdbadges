import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import fitz  # PyMuPDF

def get_position(index_on_page):
    """Calculate x, y coordinates with centered columns and equal margins."""
    # Horizontal positions (0.75" margins on both sides)
    left_x = 0.75 * 72  # 0.75" left margin
    right_x = (0.75 + 3.5) * 72  # 4.25" from left edge
    
    if index_on_page < 5:
        x = left_x
        row = index_on_page
    else:
        x = right_x
        row = index_on_page - 5
        
    # Vertical positions (0.5" bottom margin + 2" per row)
    y = (0.5 + row * 2) * 72
    return x, y

def generate_pdf_and_preview(sticker_folder, output_pdf, output_png, draw_border=False):
    image_files = []
    valid_extensions = ('.png', '.jpg', '.jpeg')
    for f in sorted(os.listdir(sticker_folder)):
        if f.lower().endswith(valid_extensions):
            image_files.append(os.path.join(sticker_folder, f))
            if len(image_files) >= 300:
                break

    c = canvas.Canvas(output_pdf, pagesize=letter)
    for i, img_path in enumerate(image_files):
        if i % 10 == 0 and i != 0:
            c.showPage()
        page_index = i % 10
        x, y = get_position(page_index)
        
        # Draw sticker (3.5"×2")
        c.drawImage(img_path, x, y, 3.5*72, 2*72)
        
        if draw_border:
            c.setStrokeColorRGB(0, 0, 0)
            c.setLineWidth(1)
            c.rect(x, y, 3.5*72, 2*72)

    c.save()

    # Generate preview
    doc = fitz.open(output_pdf)
    page = doc.load_page(0)
    pix = page.get_pixmap()
    pix.save(output_png)

# Usage with equal margins and borders
generate_pdf_and_preview(
    sticker_folder="stickers",
    output_pdf="results.pdf",
    output_png="preview.png",
    draw_border=False
)
