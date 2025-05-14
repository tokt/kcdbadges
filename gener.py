import csv
import os
import sys
from PIL import Image, ImageDraw, ImageFont

# Check for required packages and suggest installation if missing
try:
    import qrcode
except ImportError:
    print("ERROR: Required package 'qrcode' is not installed.")
    print("Please install it using:")
    print("    pip install qrcode[pil]")
    print("or")
    print("    uv pip install qrcode[pil]")
    sys.exit(1)

def generate_stickers(csv_file, output_folder="stickers"):
    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Business card size in inches (3.5 x 2)
    # Using 300 DPI for high quality
    width_px = int(3.5 * 300)
    height_px = int(2 * 300)
    
    # Load fonts - using simpler, more reliable font handling
    try:
        # Try to use the default monospace font that comes with Pillow
        large_font = ImageFont.truetype("DejaVuSansMono.ttf", 90)
        small_font = ImageFont.truetype("DejaVuSansMono.ttf", 45)
        print("Using DejaVuSansMono font")
    except Exception:
        try:
            # Try to use the default font that comes with Pillow
            large_font = ImageFont.truetype("DejaVuSans.ttf", 72)
            small_font = ImageFont.truetype("DejaVuSans.ttf", 32)
            print("Using DejaVuSans font")
        except Exception:
            print("Using default font (may not look as good)")
            large_font = ImageFont.load_default()
            small_font = ImageFont.load_default()
    
    # Check if CSV file exists
    if not os.path.exists(csv_file):
        print(f"Error: CSV file '{csv_file}' not found.")
        sys.exit(1)
    
    # Read CSV file
    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            rows = list(reader)
            
            if not rows:
                print("CSV file contains no data")
                sys.exit(1)
            
            print(f"Found {len(rows)} attendees in the CSV file")
            
            # Process each row
            for i, row in enumerate(rows):
                try:
                    # Get data from row
                    first_name_original = row.get('First Name', '')
                    last_name_original = row.get('Last Name', '')
                    first_name = first_name_original.upper()  # Convert to uppercase for display
                    last_name = last_name_original.upper()    # Convert to uppercase for display
                    email = row.get('Email', '')
                    company = row.get('Company', '')          # Get company for QR code only
                    
                    if not first_name_original or not last_name_original or not email:
                        print(f"Skipping row {i+1} due to missing data")
                        continue
                    
                    # Create QR code with vCard format - using original case for names
                    vcard = [
                        "BEGIN:VCARD",
                        "VERSION:3.0",
                        f"N:{last_name_original};{first_name_original};;;",
                        f"FN:{first_name_original} {last_name_original}"
                    ]
                    
                    # Add email
                    vcard.append(f"EMAIL:{email}")
                    
                    # Add company if present
                    if company:
                        vcard.append(f"ORG:{company}")
                    
                    # End vCard
                    vcard.append("END:VCARD")
                    
                    qr_data = "\n".join(vcard)
                    
                    qr = qrcode.QRCode(
                        version=1,
                        error_correction=qrcode.constants.ERROR_CORRECT_M,  # Medium error correction for vCard
                        box_size=10,
                        border=4,
                    )
                    qr.add_data(qr_data)
                    qr.make(fit=True)
                    qr_img = qr.make_image(fill_color="black", back_color="white")
                    
                    # Resize QR code to fit nicely on the sticker
                    qr_size = int(height_px * 0.5)
                    qr_img = qr_img.resize((qr_size, qr_size))
                    
                    # Create a blank image
                    sticker = Image.new('RGB', (width_px, height_px), color='white')
                    draw = ImageDraw.Draw(sticker)
                    
                    # Get text sizes
                    try:
                        first_name_bbox = draw.textbbox((0, 0), first_name, font=large_font)
                        first_name_width = first_name_bbox[2] - first_name_bbox[0]
                        first_name_height = first_name_bbox[3] - first_name_bbox[1]
                        
                        last_name_bbox = draw.textbbox((0, 0), last_name, font=small_font)
                        last_name_width = last_name_bbox[2] - last_name_bbox[0]
                        last_name_height = last_name_bbox[3] - last_name_bbox[1]
                    except AttributeError:
                        # Fallback for older PIL versions
                        try:
                            first_name_width, first_name_height = draw.textsize(first_name, font=large_font)
                            last_name_width, last_name_height = draw.textsize(last_name, font=small_font)
                        except Exception as e:
                            print(f"Error measuring text size: {e}")
                            # Estimate sizes
                            first_name_width, first_name_height = len(first_name) * 40, 60
                            last_name_width, last_name_height = len(last_name) * 20, 30
                    
                    # Calculate total content height (first name + QR code + last name + spacing)
                    spacing = 20  # Space between elements
                    total_content_height = first_name_height + qr_size + last_name_height + (spacing * 2)
                    
                    # Calculate vertical starting position to center everything
                    start_y = (height_px - total_content_height) // 2
                    
                    # Calculate positions for centered elements
                    # First name (at top of centered content)
                    first_name_position = ((width_px - first_name_width) // 2, start_y)
                    
                    # QR code (in middle of centered content)
                    qr_position = ((width_px - qr_size) // 2, start_y + first_name_height + spacing)
                    
                    # Last name (at bottom of centered content)
                    last_name_position = (
                        (width_px - last_name_width) // 2, 
                        start_y + first_name_height + spacing + qr_size + spacing
                    )
                    
                    # Draw elements on sticker
                    try:
                        draw.text(first_name_position, first_name, font=large_font, fill='black')
                        draw.text(last_name_position, last_name, font=small_font, fill='black')
                        sticker.paste(qr_img, qr_position)
                        
                        # Save the sticker
                        safe_filename = f"{first_name}_{last_name}".replace(" ", "_").replace("/", "_")
                        sticker.save(f"{output_folder}/{safe_filename}_sticker.png")
                        
                        # Report company in console output if present
                        company_info = f" ({company})" if company else ""
                        print(f"Generated sticker for {first_name} {last_name}{company_info}")
                    except Exception as e:
                        print(f"Error creating sticker for {first_name} {last_name}: {e}")
                
                except Exception as e:
                    print(f"Error processing row {i+1}: {e}")
            
            print(f"All stickers have been generated in the '{output_folder}' directory")
    
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("KCD Attendee Badge Generator")
    print("---------------------------")
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
    else:
        csv_file = "data.csv"  # Default filename
        print(f"No CSV file specified, using default: {csv_file}")
    
    # Check if file exists
    if not os.path.isfile(csv_file):
        print(f"Error: File '{csv_file}' not found.")
        print("Usage: python sticker_generator.py [csv_file]")
        sys.exit(1)
    
    # Get output folder
    output_folder = "stickers"
    
    print(f"Processing file: {csv_file}")
    print(f"Output folder: {output_folder}")
    print("---------------------------")
    
    # Generate stickers
    generate_stickers(csv_file, output_folder)
