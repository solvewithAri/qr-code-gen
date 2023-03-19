from flask import Flask, request, jsonify, send_file, render_template
import qrcode
import os
from io import BytesIO
from PIL import Image,ImageDraw
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers.pil import *
from qrcode.image.styles.colormasks import *
import numpy as np
import cv2

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


def hex_to_rgba(hex_code,opacity):
    hex_code = hex_code.lstrip('#')
    rgb = tuple(int(hex_code[i:i+2], 16) for i in (0, 2, 4))
    rgba = rgb + (opacity,)
    return rgba

def get_module_drawer(val):
   if val=="rmd":
        return RoundedModuleDrawer(radius_ratio=1.2)
   elif val=="cmd":
       return CircleModuleDrawer()
   elif val=="smd":
       return GappedSquareModuleDrawer()
   elif val=="vmd":
       return VerticalBarsDrawer()
   elif val=="hmd":
       return HorizontalBarsDrawer()



app = Flask(__name__)

@app.route('/qrcode', methods=['POST'])
def generate_qrcode():
    # Get the data from the request
    data = request.form['data']
    qr_color = hex_to_rgba(request.form['qr_color'],255)
    qr_g_color = hex_to_rgba(request.form['qr_g_color'],255)
    bg_color = hex_to_rgba(request.form['bg_color'],int(request.form['bg_opacity']))

    qr_outer_e_col= hex_to_rgba(request.form['qr_outer_e_col'],255)
    qr_inner_e_col= hex_to_rgba(request.form['qr_inner_e_col'],255)

    inner_eye_md = get_module_drawer(request.form['innereye_md'])
    outer_eye_md = get_module_drawer(request.form['outer_eye_md'])
    qr_md = get_module_drawer(request.form['qr_md'])

    # Get the uploaded image from the request
    image_file = request.files.get('image')   

    # Generate the QR code image with white background
    qr = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_H,
    )
    qr.add_data(data)
    qr.make(fit=True)

    outer_eyes_img = qr.make_image(image_factory=StyledPilImage,
                                eye_drawer=outer_eye_md,
                                color_mask=SolidFillColorMask(back_color=bg_color, front_color=qr_outer_e_col))

    inner_eyes_img = qr.make_image(image_factory=StyledPilImage,
                                eye_drawer=inner_eye_md,
                                color_mask=SolidFillColorMask(back_color=bg_color, front_color=qr_inner_e_col))
    if image_file:
        image = Image.open(image_file) 
        qr_width, qr_height = outer_eyes_img.size
        image.thumbnail((qr_width * 0.3, qr_height * 0.3))
        image_io = BytesIO()
        image.save(image_io,'png')
        image_io.seek(0)
        img = qr.make_image(image_factory=StyledPilImage,
                            module_drawer=qr_md,
                            color_mask=RadialGradiantColorMask(back_color=bg_color,center_color=qr_g_color,edge_color=qr_color),
                            embeded_image_path=image_io)
    else :
       img = qr.make_image(image_factory=StyledPilImage,
                            module_drawer=qr_md,
                            color_mask=RadialGradiantColorMask(back_color=bg_color,center_color=qr_g_color,edge_color=qr_color))
       


    inner_eye_mask = mask_inner_eyes(img)
    outer_eye_mask = mask_outer_eyes(img)
    temp_img = Image.composite(inner_eyes_img, img, inner_eye_mask)
    qr_image = Image.composite(outer_eyes_img, temp_img, outer_eye_mask)

    # Create an in-memory file-like object to hold the image data
    img_io = BytesIO()

    # Save the image data to the in-memory file-like object
    qr_image.save(img_io, 'png')
    qr_image.save('test.png')

    # Set the file position of the in-memory file-like object to the beginning
    img_io.seek(0)

    # Return the image as a Flask response with the appropriate MIME type
    response = send_file(img_io, mimetype='image/png')
    return response

@app.route('/readqrcode', methods=['POST'])
def read_qrcode():


    # Get the uploaded image from the request
    image_file = request.files.get('image')

    # Open the image file as a numpy array using OpenCV
    image = cv2.imdecode(np.fromstring(image_file.read(), np.uint8), cv2.IMREAD_UNCHANGED)

    # Decode the QR code data using OpenCV
    qr_decoder = cv2.QRCodeDetector()
    data, bbox, _ = qr_decoder.detectAndDecode(image)

    # Return the decoded data as JSON
    return jsonify({'data': data})

@app.route('/')
def home():
    return render_template(['index.html','style.css'])


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=True, host='0.0.0.0', port=port)
