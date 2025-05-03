#imports
import cv2
import numpy as np
import streamlit as st
from PIL import Image
import io
from streamlit_image_comparison import image_comparison

#---- Build our filters ---------------------------------------------------------------------------
#RGB --> Gray
def black_white(img):
    gray_image = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    return gray_image

#brightness
def brightness(img, level):
    bright = cv2.convertScaleAbs(img, beta=level)
    return bright

#style image
def style_image(img, sigma_s=10, sigma_r=0.1):
    blur_image = cv2.GaussianBlur(img, (5, 5), 0, 0)
    style_img = cv2.stylization(blur_image, sigma_s=sigma_s, sigma_r=sigma_r)
    return style_img

#HDR filter
def HDR(img, level, sigma_s=10, sigma_r=0.1):
    bright = cv2.convertScaleAbs(img, beta=level)
    hd_image = cv2.detailEnhance(bright, sigma_s=sigma_s, sigma_r=sigma_r)
    return hd_image

#blur filter
def blur_image(img, ksize=5):
    return cv2.GaussianBlur(img, (ksize, ksize), 0)

#sharpen filter
def sharpen_image(img):
    kernel = np.array([[0, -1, 0],
                       [-1, 5,-1],
                       [0, -1, 0]])
    return cv2.filter2D(img, -1, kernel)

# ----- Page Config -----
st.set_page_config(page_title="🎨 Filter App", page_icon="🎨", layout="centered")

# ----- Custom CSS -----
st.markdown("""
    <style>
    body, .main {
        background: linear-gradient(-45deg, #6a82fb, #fc5c7d, #6a82fb, #fc5c7d);
        background-size: 400% 400%;
        animation: gradientMove 15s ease infinite;
        color: #f0f0f0;
    }

    @keyframes gradientMove {
        0% {background-position: 0% 50%;}
        50% {background-position: 100% 50%;}
        100% {background-position: 0% 50%;}
    }

    .block-container {
        background-color: rgba(0, 0, 0, 0.6);
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 0 30px #6a82fb;
    }

    h1 {
        color: #6a82fb;
        text-align: center;
        font-size: 2.8rem;
        font-weight: bold;
    }

    h3 {
        color: #f0f0f0;
        text-align: center;
    }

    .stTextArea textarea {
        background-color: #333;
        color: #f0f0f0;
        border-radius: 12px;
        border: 1px solid #555;
    }

    .stButton>button {
        background-color: #6a82fb;
        color: black;
        font-weight: bold;
        border-radius: 10px;
        transition: 0.3s ease;
        box-shadow: 0 0 10px #6a82fb, 0 0 20px #6a82fb inset;
    }

    .stButton>button:hover {
        background-color: #fc5c7d;
        transform: scale(1.05);
    }
    </style>
""", unsafe_allow_html=True)

#GUI
st.title('🎨 Filter App')

upload = st.file_uploader('📤 Choose an Image', type=['png', 'jpg', 'jpeg'])

if upload is not None:
    # setup my img
    img = Image.open(upload)
    img = np.array(img)

    original_img, output_img = st.columns(2)

    with original_img:
        st.subheader('🖼️ Original Image')
        st.image(img, channels='RGB')
        st.caption(f"🧾 Resolution: {img.shape[1]} x {img.shape[0]}")
        st.caption(f"📁 File Name: {upload.name}")

    st.markdown("### 🧪 Filters List")
    options = st.selectbox('🧰 Select Filter: ', (
        'None', 'black_white', 'brightness', 'style_image', 'HDR', 'blur', 'sharpen'))

    output_flag = True
    color = 'RGB'

    if options == 'None':
        output = img
        output_flag = False

    elif options == 'black_white':
        output = black_white(img)
        color = 'GRAY'

    elif options == 'brightness':
        level = st.slider('💡 Brightness Level', -50, 50, 10, step=5)
        output = brightness(img, level)

    elif options == 'style_image':
        sigma_s = st.slider('🎨 sigma_s (Color)', 0, 200, 100, step=10)
        sigma_r = st.slider('🧵 sigma_r (Details)', 0.0, 1.0, 0.1)
        output = style_image(img, sigma_s, sigma_r)

    elif options == 'HDR':
        level = st.slider('💡 Brightness Level', -50, 50, 10, step=5)
        sigma_s = st.slider('🎯 HDR sigma_s', 0, 200, 100, step=10)
        sigma_r = st.slider('🔍 HDR sigma_r', 0.0, 1.0, 0.1)
        output = HDR(img, level, sigma_s, sigma_r)

    elif options == 'blur':
        ksize = st.slider('💤 Blur Kernel Size (odd number)', 1, 15, 5, step=2)
        output = blur_image(img, ksize)

    elif options == 'sharpen':
        output = sharpen_image(img)

    with output_img:
        st.subheader('🎯 Output Image')
        if color == 'GRAY':
            st.image(output, channels='GRAY')
        else:
            st.image(output, channels='RGB')

        st.success('✅ Filter Applied Successfully!')
        st.info(f"🧰 Applied Filter: {options}")

        # Convert image to PIL for download
        if color != 'GRAY':
            result = Image.fromarray(output)
        else:
            result = Image.fromarray(output).convert("RGB")

        # Save the image to a BytesIO buffer
        img_byte_arr = io.BytesIO()
        result.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()

        # Download button
        st.download_button(
            label="📥 Download Image",
            data=img_byte_arr,
            file_name="filtered_image.png",
            mime="image/png"
        )

    st.markdown("---")
    st.markdown("### 🔀 Compare Before and After")
    image_comparison(img1=img, img2=output, label1="Original", label2="Filtered")

    if st.button("🔁 Reset Filter (Reload Page)"):
        st.experimental_rerun()
