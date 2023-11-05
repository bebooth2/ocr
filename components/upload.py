import base64
from io import BytesIO
from PIL import Image
import tempfile
import datetime
import cv2
import numpy as np
from dash import Dash, dcc, html
import numpy as numpy



def upload(id, style, multiple=False):
    return dcc.Upload(
        id=id,
        children=html.Div(
            [
                "Drag and Drop or ",
                html.A("Select Files"),
            ],
            style=style,
        ),
        multiple=multiple,
    )

def b64_to_pil(string):
    decoded = base64.b64decode(string)
    buffer = BytesIO(decoded)
    im = Image.open(buffer)

    return im

def pil_to_b64(im, enc_format="png", verbose=False, **kwargs):
    """
    Converts a PIL Image into base64 string for HTML displaying
    :param im: PIL Image object
    :param enc_format: The image format for displaying. If saved the image will have that extension.
    :param verbose: Allow for debugging tools
    :return: base64 encoding
    """
    t_start = time.time()

    buff = BytesIO()
    im.save(buff, format=enc_format, **kwargs)
    encoded = base64.b64encode(buff.getvalue()).decode("utf-8")

    t_end = time.time()
    if verbose:
        print(f"PIL converted to b64 in {t_end - t_start:.3f} sec")

    return encoded

def parse_contents(contents,filename, date, color_map, gray_scale, blur, input1=75, input2=75):
    print("This is contents before ", contents[:100])
    print("This is filename ", filename)
    end_file = filename.split(".")[-1]
    print("This is end_file ", end_file)
    if color_map or gray_scale or blur or input1 or input2:
        print("first if")
        string= contents.split(";base64,")[-1]
        im_pil = b64_to_pil(string)
        opencv_image = cv2.cvtColor(np.array(im_pil), cv2.COLOR_RGB2BGR)
        if color_map =="stop":
            process_contents = opencv_image
        elif color_map:
            process_contents = cv2.applyColorMap(opencv_image, int(color_map))
        else:
            process_contents = opencv_image
        if gray_scale:
            process_contents = gray_scale_processer(gray_scale, process_contents)

        if blur or input1 or input2:
            print("This is blur ", blur)
            print("This is input1 ", input1)
            process_contents = blur_processer(blur, process_contents,input1, input2)
        ret, buffer = cv2.imencode(f".{end_file}", process_contents)
         
        if not ret:
            raise Exception('Could not encode image!')
        jpg_as_text = base64.b64encode(buffer).decode('utf-8')
        if end_file == "pdf":
            contents= f"data:application/{end_file};base64,{jpg_as_text}"
        elif end_file == 'svg':
            contents= f"data:image/svg+xml;base64,{jpg_as_text}"
        elif end_file == 'png':
            contents= f"data:text/png;base64,{jpg_as_text}"
        else:
            contents =f"data:image/{end_file.lower()};base64,{jpg_as_text}"
       


    print("This is contents after ", contents[:100])

    return html.Div([

        # HTML images accept base64 encoded strings in the same format
        # that is supplied by the upload
        html.Img(src=contents, style={'margin': 'auto', 'justify-content': 'center', 'max-width':'100%' ,'max-height': 'vh50'}),
        html.Hr(),
    ], style={'display':'flex',"margin": "auto"}), contents

def gray_scale_processer(gray_scale, process_contents):
    if gray_scale == "no_gray":
        # ret, thresh1 = cv2.threshold(process_contents, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)
        return process_contents
    elif gray_scale == "no_gray_dilate":
        # ret, thresh1 = cv2.threshold(process_contents, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)
        rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (18, 18))
        kernel = np.ones((5,5),np.uint8)
        dilation = cv2.dilate(process_contents, kernel, iterations=1)
        return dilation
    elif gray_scale == "gray":
        gray = cv2.cvtColor(process_contents, cv2.COLOR_BGR2GRAY)
        ret, thresh1 = cv2.threshold(gray,120, 255, cv2.THRESH_TOZERO)
        return thresh1
    elif gray_scale == "gray_dilate":
        gray = cv2.cvtColor(process_contents, cv2.COLOR_BGR2GRAY)
        ret, thresh1 = cv2.threshold(gray, 120, 255, cv2.THRESH_TOZERO)
        rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (18, 18))
        kernel = np.ones((5,5),np.uint8)
        dilation = cv2.dilate(thresh1,kernel, iterations=1)
        return dilation
    elif gray_scale == "gray_erode":
        gray = cv2.cvtColor(process_contents, cv2.COLOR_BGR2GRAY)
        ret, thresh1 = cv2.threshold(gray, 120, 255, cv2.THRESH_TOZERO)
        rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (18, 18))
        kernel = np.ones((5,5),np.uint8)
        erode = cv2.erode(thresh1,kernel, iterations=1)
        return erode
    elif gray_scale == "gray_dilate_erode": 
        gray = cv2.cvtColor(process_contents, cv2.COLOR_BGR2GRAY)
        ret, thresh1 = cv2.threshold(gray, 120, 255, cv2.THRESH_TOZERO)
        rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (18, 18))
        kernel = np.ones((5,5),np.uint8)
        dilation = cv2.dilate(thresh1,kernel, iterations=1)
        erode = cv2.erode(dilation,kernel, iterations=1)
        return erode
    elif gray_scale == "gray_erode_dilate":     
        gray = cv2.cvtColor(process_contents, cv2.COLOR_BGR2GRAY)
        ret, thresh1 = cv2.threshold(gray, 120, 255, cv2.THRESH_TOZERO)
        rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (18, 18))
        kernel = np.ones((5,5),np.uint8)
        erode = cv2.erode(thresh1,kernel, iterations=1)
        dilation = cv2.dilate(erode,kernel, iterations=1)
        return dilation
    elif gray_scale == "gray_adaptive": 
        gray = cv2.cvtColor(process_contents, cv2.COLOR_BGR2GRAY)
        thresh1 = cv2.adaptiveThreshold(gray,255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11,2)
        return thresh1
    else:
        return process_contents


def blur_processer(blur, process_contents, input1, input2):
    if blur == "no_blur":
        return process_contents
    elif blur == "average_blur":
        blur = cv2.blur(process_contents, (5, 5))
        return blur
    elif blur == "gaussian_blur":
        blur = cv2.GaussianBlur(process_contents, (7, 7), 0)
        return blur
    elif blur == "median_blur":
        blur = cv2.medianBlur(process_contents, 5)
        return blur
    elif blur == "bilateral_blur":
        print(input1, input2)
        blur = cv2.bilateralFilter(process_contents, 9, input1, input2)
        return blur
    else:
        return process_contents


def convert_contents_to_image(contents):
    string= contents.split(";base64,")[-1]
    im_pil = b64_to_pil(string)
    img = cv2.cvtColor(np.array(im_pil), cv2.COLOR_RGB2BGR)
    return img