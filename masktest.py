from PIL import Image, ImageDraw, ImageOps

size = (128, 128)
mask = Image.new('L', size, 0)
draw = ImageDraw.Draw(mask)
draw.ellipse((0, 0) + size, fill=255)
im = Image.open('prof.png')
output = ImageOps.fit(im, mask.size, centering=(0.5, 0.5))
output.putalpha(mask)
img = Image.new("RGBA", (500, 750), (255, 255, 255, 255))
img.alpha_composite(output, (250, 375))
img.save("test.png")