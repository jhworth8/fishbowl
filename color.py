from PIL import Image
import colorsys

def change_hue(image, hue_shift):
    """Change the hue of an image while preserving transparency."""
    # Convert the image to RGBA if it's not already
    image = image.convert("RGBA")
    
    # Split the image into its individual bands (R, G, B, A)
    r, g, b, a = image.split()
    
    # Convert the RGB values to HSV
    hsv_data = []
    for r_pixel, g_pixel, b_pixel in zip(r.getdata(), g.getdata(), b.getdata()):
        h, s, v = colorsys.rgb_to_hsv(r_pixel / 255.0, g_pixel / 255.0, b_pixel / 255.0)
        # Shift the hue
        h = (h + hue_shift) % 1.0
        # Convert back to RGB
        r_pixel, g_pixel, b_pixel = colorsys.hsv_to_rgb(h, s, v)
        hsv_data.append((int(r_pixel * 255), int(g_pixel * 255), int(b_pixel * 255)))
    
    # Create a new image with the modified RGB values
    new_image = Image.new("RGB", image.size)
    new_image.putdata(hsv_data)
    
    # Merge the new RGB image with the original alpha channel
    new_image.putalpha(a)
    
    return new_image

def main():
    # Define the list of fish filenames
    fish_filenames = [f"fish_{i}.png" for i in range(7, 15)]  # fish_7.png to fish_14.png
    
    # Define the hue shifts for 8 different colors
    hue_shifts = [i / 8.0 for i in range(8)]
    
    # Process each fish image
    for fish_filename in fish_filenames:
        try:
            # Load the original image
            original_image = Image.open(fish_filename)
            
            # Generate and save the 8 variants for this fish
            for i, hue_shift in enumerate(hue_shifts):
                variant_image = change_hue(original_image, hue_shift)
                # Save the variant with the appropriate filename
                variant_image.save(f"{fish_filename[:-4]}.{i+1}.png")
            print(f"Processed {fish_filename} successfully.")
        except FileNotFoundError:
            print(f"File {fish_filename} not found. Skipping.")

if __name__ == "__main__":
    main()