import qrcode
from PIL import Image,ImageDraw
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers.pil import *
from qrcode.image.styles.colormasks import *

def mask_inner_eyes(img):
  img_size = img.size[0]
  eye_size = 70 #default
  quiet_zone = 40 #default
  mask = Image.new('L', img.size, 0)
  draw = ImageDraw.Draw(mask)
  draw.rectangle((60, 60, 90, 90), fill=255) #top left eye
  draw.rectangle((img_size-90, 60, img_size-60, 90), fill=255) #top right eye
  draw.rectangle((60, img_size-90, 90, img_size-60), fill=255) #bottom left eye
  return mask

def mask_outer_eyes(img):
  img_size = img.size[0]
  eye_size = 70 #default
  quiet_zone = 40 #default
  mask = Image.new('L', img.size, 0)
  draw = ImageDraw.Draw(mask)
  draw.rectangle((40, 40, 110, 110), fill=255) #top left eye
  draw.rectangle((img_size-110, 40, img_size-40, 110), fill=255) #top right eye
  draw.rectangle((40, img_size-110, 110, img_size-40), fill=255) #bottom left eye
  draw.rectangle((60, 60, 90, 90), fill=0) #top left eye
  draw.rectangle((img_size-90, 60, img_size-60, 90), fill=0) #top right eye
  draw.rectangle((60, img_size-90, 90, img_size-60), fill=0) #bottom left eye  
  return mask 


qr = qrcode.QRCode(
    error_correction=qrcode.constants.ERROR_CORRECT_H,
)

qr.add_data('https://www.youtube.com/@SolveWithAriP')
qr.make(fit=True)

outer_eyes_img = qr.make_image(image_factory=StyledPilImage,
                            eye_drawer=RoundedModuleDrawer(radius_ratio=1.2),
                            color_mask=SolidFillColorMask(back_color=(255, 255, 255), front_color=(255, 110, 0)))

inner_eyes_img = qr.make_image(image_factory=StyledPilImage,
                            eye_drawer=RoundedModuleDrawer(radius_ratio=1.2),
                            color_mask=SolidFillColorMask(back_color=(255, 255, 255), front_color=(59, 89, 152)))

img = qr.make_image(image_factory=StyledPilImage,
                       module_drawer=CircleModuleDrawer(),
                       color_mask=RadialGradiantColorMask(back_color=(255, 255, 255),center_color=(59, 89, 152),edge_color=(59, 89, 152)),
                       embeded_image_path="yt-logo.png")

inner_eye_mask = mask_inner_eyes(img)
outer_eye_mask = mask_outer_eyes(img)
temp_img = Image.composite(inner_eyes_img, img, inner_eye_mask)
final_img = Image.composite(outer_eyes_img, temp_img, outer_eye_mask)

final_img.save("my_qr_code.png")
