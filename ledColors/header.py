import math

import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Function to convert HSL to RGB
def hsl_to_rgb(hue, saturation, lightness):
    # Convert HSL (hue in degrees, saturation/lightness in percentage) to RGB (0-255)
    saturation /= 100.0
    lightness /= 100.0

    c = (1 - abs(2 * lightness - 1)) * saturation
    x = c * (1 - abs((hue / 60.0) % 2 - 1))
    m = lightness - c / 2

    r_prime, g_prime, b_prime = 0, 0, 0

    if 0 <= hue < 60:
        r_prime, g_prime, b_prime = c, x, 0
    elif 60 <= hue < 120:
        r_prime, g_prime, b_prime = x, c, 0
    elif 120 <= hue < 180:
        r_prime, g_prime, b_prime = 0, c, x
    elif 180 <= hue < 240:
        r_prime, g_prime, b_prime = 0, x, c
    elif 240 <= hue < 300:
        r_prime, g_prime, b_prime = x, 0, c
    elif 300 <= hue < 360:
        r_prime, g_prime, b_prime = c, 0, x

    r = int((r_prime + m) * 255)
    g = int((g_prime + m) * 255)
    b = int((b_prime + m) * 255)

    return (r,g,b)

# Function to convert HSV to RGB
def hsv_to_rgb(hue, saturation, value):
    # Convert HSV (hue in degrees, saturation/value in percentage) to RGB (0-255)
    saturation /= 100.0
    value /= 100.0

    c = value * saturation
    x = c * (1 - abs((hue / 60.0) % 2 - 1))
    m = value - c

    r_prime, g_prime, b_prime = 0, 0, 0

    if 0 <= hue < 60:
        r_prime, g_prime, b_prime = c, x, 0
    elif 60 <= hue < 120:
        r_prime, g_prime, b_prime = x, c, 0
    elif 120 <= hue < 180:
        r_prime, g_prime, b_prime = 0, c, x
    elif 180 <= hue < 240:
        r_prime, g_prime, b_prime = 0, x, c
    elif 240 <= hue < 300:
        r_prime, g_prime, b_prime = x, 0, c
    elif 300 <= hue < 360:
        r_prime, g_prime, b_prime = c, 0, x

    r = int((r_prime + m) * 255)
    g = int((g_prime + m) * 255)
    b = int((b_prime + m) * 255)

    return (r, g, b)


# Function to generate the hues and saturations
def generate_hue_saturation(i):
    # Calculate hue
    hue_step = 360 / 128
    hue = i * hue_step

    # Determine saturation based on index
    if i % 2 == 0:
        saturation = 100  # Max saturation
    elif i % 4 == 1:
        saturation = (100 / 7) * 6
    elif i % 8 == 3:
        saturation = (100 / 7) * 5
    elif i % 16 == 7:
        saturation = (100 / 7) * 4
    elif i % 32 == 15:
        saturation = (100 / 7) * 3
    elif i % 64 == 31:
        saturation = (100 / 7) * 2
    elif i % 128 == 63:
        saturation = (100 / 7) * 1
    else:
        saturation = 0  # Minimum saturation

    return hue, saturation

# Function to generate the color for each pressure and velocity value
def generate_c_array(filename):
    with open(filename, 'w') as f:
        f.write("#include <stdint.h>\n\n")
        f.write("static const uint32_t LedColor[128][128] = {\n")

        for pressure in range(128):
            f.write("    {")
            for velocity in range(128):
                # Map velocity (0-127) to lightness (0-100)
                lightness = (velocity / 127.0) * 100.0

                # Get hue and saturation for this pressure index
                hue, saturation = generate_hue_saturation(pressure)

                # Convert HSL to RGB
                (r,g,b) = hsl_to_rgb(hue, saturation, lightness)
                color = (r << 16) | (g << 8) | b  # Combine RGB into 0xRRGGBB 

                # Write the color in hex format
                f.write(f"0x{color:06X}")
                if velocity < 127:
                    f.write(", ")
            f.write("},\n")
        
        f.write("};\n")

def generate_header_file(filename):
    with open(filename, 'w') as f:
        f.write("#ifndef LED_COLORS_H\n")
        f.write("#define LED_COLORS_H\n\n")
        f.write("#include <stdint.h>\n\n")
        f.write("extern const uint32_t LedColor[128][128];\n\n")
        f.write("#endif // LED_COLORS_H\n")

# Generate the header file
generate_header_file("led_colors.h")

# Generate the C file with the LedColor array
generate_c_array("led_colors.c")

from PIL import Image

# Function to generate a 128x128 PNG image
def generate_png_image(filename):
    # Create a new image (128x128) with RGB mode
    img = Image.new("RGB", (128, 128))
    pixels = img.load()

    for pressure in range(128):
        for velocity in range(128):
            # Map velocity (0-127) to lightness (0-100)
            lightness = (velocity / 127.0) * 100.0

            # Get hue and saturation for this pressure index
            hue, saturation = generate_hue_saturation(pressure)

            # Convert HSL to RGB
            r, g, b = hsl_to_rgb(hue, saturation, lightness)

            # Set the pixel in the image
            pixels[velocity, pressure] = (r, g, b)

    # Save the image to the file
    img.save(filename)

# Generate the PNG image
generate_png_image("led_colors.png")
