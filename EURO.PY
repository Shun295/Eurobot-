import streamlit as st
import requests
import base64
import io
from PIL import Image
import google.generativeai as genai

# Add custom CSS for styling the title and button
st.markdown(
    """
    <style>
    .title {
        color: #4CAF50;
        font-size: 36px;
        font-weight: bold;
        font-family: 'bookman old style', sans-serif;
        text-align: center;
        margin-bottom: 40px;
    }
    
    /* Style for the Streamlit button */
    div.stButton > button {
        background-color: #4CAF50; /* Green background */
        color: white; /* White text */
        font-size: 23px; /* Larger font size */
        padding: 15px 30px; /* Padding inside the button */
        border: none; /* Remove border */
        border-radius: 17px; /* Rounded corners */
        cursor: pointer; /* Pointer cursor on hover */
        transition: background-color 0.3s; /* Smooth transition for hover effect */
    }

    div.stButton > button:hover {
        background-color: #45a049; /* Darker green on hover */
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Load background image
def get_img_as_base64(file):
    with open(file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

img = get_img_as_base64("background2.png")

page_bg_img = f"""
<style>
[data-testid="stAppViewContainer"] > .main {{
background-image: url("data:image/png;base64,{img}");
background-size: cover;
}}
[data-testid="stHeader"] {{
background: rgba(0, 0, 0, 0);
}}
h1 {{
    color: white;
    font-family: 'bookman old style', sans-serif;
    font-size: 60px;
    text-align: center;
    margin-top: 50px;
}}
</style>
"""
st.markdown(page_bg_img, unsafe_allow_html=True)

# Add title at the top
st.markdown('<div class="title">WELCOME TO MY EUROBOT CHAT</div>', unsafe_allow_html=True)

# Initialize the generative model
genai.configure(api_key="AIzaSyAs3B_1ziqP6jBrJdGAVQMPMONue7ujYTg")
model = genai.GenerativeModel('gemini-pro')
chat = model.start_chat(history=[])

# Selection menu
option = st.selectbox(
    "Choose a functionality:",
    ["Chat", "Text to Image Generator", "Image to Text Generator"]
)

if option == "Chat":
    text = st.text_input("Enter your question")

    if st.button("Click Me"):
        if text:
            response = chat.send_message(text)
            st.write(response.text)
        else:
            st.warning("Please enter a question.")

elif option == "Text to Image Generator":
    st.subheader("Text to Image Generator")

    text_prompt = st.text_input("Enter prompt for image generation")

    if st.button('Generate Image'):
        if text_prompt:
            # Hugging Face API details for text-to-image
            API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
            headers = {"Authorization": "Bearer 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"}

            def query(payload):
                try:
                    response = requests.post(API_URL, headers=headers, json=payload)
                    response.raise_for_status()  # Raises an error for bad HTTP status codes
                    return response.content
                except requests.exceptions.RequestException as e:
                    st.error(f"Request failed: {e}")
                    return None

            # Generate the image
            image_bytes = query({"inputs": text_prompt})

            if image_bytes:
                try:
                    # Open the image with PIL
                    image = Image.open(io.BytesIO(image_bytes))
                    st.image(image, caption="Generated Image")

                    # Add download button
                    st.download_button(
                        label="Download Image",
                        data=image_bytes,
                        file_name="generated_image.png",
                        mime="image/png"
                    )
                    
                    # Add reprompt button
                    if st.button("Reprompt"):
                        st.experimental_rerun()

                except IOError:
                    st.error("Failed to generate image. The returned data might not be a valid image.")
        else:
            st.warning("Please enter a prompt.")

elif option == "Image to Text Generator":
    st.subheader("Image Caption Generator")

    # Hugging Face API details for image captioning
    IMAGE_API_URL = "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-large"
    IMAGE_HEADERS = {"Authorization": "Bearer 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"}

    def query_image(image_data):
        try:
            response = requests.post(IMAGE_API_URL, headers=IMAGE_HEADERS, data=image_data)
            response.raise_for_status()  # Raises an error for bad HTTP status codes
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Request failed: {e}")
            return None

    # Image uploader
    uploaded_file = st.file_uploader("Upload an image for captioning", type=["jpg", "jpeg", "png"])

    # If an image is uploaded
    if uploaded_file is not None:
        # Display the uploaded image
        st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)

        # Read the image data from the uploaded file
        image_data = uploaded_file.read()

        # Send the image data to the Hugging Face API
        with st.spinner('Generating caption...'):
            result = query_image(image_data)

        # Display the result (the generated caption)
        if result is not None:
            if "error" in result:
                st.error(f"Error: {result['error']}")
            else:
                st.success(f"Generated Caption: {result[0]['generated_text']}")
