import os
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import io
from PIL import Image
import google.ai.generativelanguage as glm
import re
import time

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-pro-vision')
extracted_results = []

# Dictionary for mapping animals to emojis
animal_emojis = {
    "dog": "🐕",
    "bird": "🐦",
    "cat": "🐈",
    "elephant": "🐘",
    "fish": "🐟",
    "fox": "🦊",
    "horse": "🐎",
    "lion": "🦁",
    "monkey": "🐒",
    "mouse": "🐁",
    "owl": "🦉",
    "panda": "🐼",
    "rabbit": "🐇",
    "snake": "🐍",
    "tiger": "🐅",
    "unicorn": "🦄",
    "dragon": "🐉",
    "swan": "🦢",
    # Add more as needed
}

def prepare_image(uploaded_file):
    image = Image.open(uploaded_file)
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    return img_byte_arr

def process_analysis_text(text):
    # Regex pattern to extract items and their similarities
    pattern = re.compile(r"(\w+): (\d+)%")
    matches = pattern.findall(text)
    extracted_results = [(match[0], int(match[1])) for match in matches]
    return extracted_results

def upload_image():
    uploaded_file = st.file_uploader("Upload Your Cloud Photo", type=["jpg", "jpeg", "png"], key="image_uploader")
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption='Uploaded Cloud Photo', width=200)
    return uploaded_file

def main():
    st.set_page_config(page_title="Cloud Riddle Game", layout="centered", initial_sidebar_state="collapsed")

    if 'page' not in st.session_state:
        st.session_state['page'] = "Landing Page"
        st.toast("A new cloud is available ☁️")
        time.sleep(4)  # Keeping the toast for 4 seconds

    if st.session_state['page'] == "Landing Page":
        if st.button("👀 Check my new cloud ☁️"):
            st.session_state['page'] = "Image Upload"
            st.experimental_rerun()

    elif st.session_state['page'] == "Image Upload":
        uploaded_image = upload_image()
        if uploaded_image is not None:
            if st.button("Confirm and Reveal the Riddle"):
                st.session_state['uploaded_image'] = uploaded_image
                st.session_state['page'] = "Riddle Reveal"
                st.experimental_rerun()

    elif st.session_state['page'] == "Riddle Reveal":
        if 'uploaded_image' not in st.session_state or st.session_state['uploaded_image'] is None:
            st.warning("Please upload an image first on the 'Image Upload' page.")
            st.session_state['page'] = "Image Upload"
            st.experimental_rerun()
        else:
            uploaded_image = st.session_state['uploaded_image']
            st.image(uploaded_image, caption='Uploaded Cloud Photo', width=200)

            user_response = st.text_input("What objects do you think the cloud looks like?")
            if st.button("Submit and Reveal the Riddle"):
                with st.spinner("Analyzing..."):
                    try:
                        img_byte_arr = prepare_image(uploaded_image)
                        content = glm.Content(parts=[
                            glm.Part(text="What top 5 objects does this cloud resemble? and say the corresponding degree of similarity, for example, dog: 60%, bird: 30%."),
                            glm.Part(inline_data=glm.Blob(mime_type="image/png", data=img_byte_arr)),
                        ])
                        response = model.generate_content(content)
                        analysis_text = response.text
                        #st.write("Raw response:", analysis_text)  # Optionally keep this line for debugging

                        extracted_results = process_analysis_text(analysis_text)
                        st.session_state['extracted_results'] = extracted_results
                    except Exception as e:
                        st.error(f"An error occurred: {e}")

            # Display the results, avoiding repetition
            if 'extracted_results' in st.session_state:
                extracted_results = st.session_state['extracted_results']
                if extracted_results:
                    st.subheader("Top 5 Similarities:")
                    for index, (item, similarity) in enumerate(extracted_results, start=1):
                        emoji = animal_emojis.get(item.lower(), "")
                        st.write(f"{index}. {emoji} {item}: {similarity}%")

                    # Add "Check Next Cloud" button
                    if st.button("Check Next Cloud ☁️"):
                        # Reset state and go to the image upload page
                        st.session_state['page'] = "Image Upload"
                        st.session_state.pop('uploaded_image', None)
                        st.session_state.pop('extracted_results', None)
                        st.experimental_rerun()

if __name__ == "__main__":
    main()
