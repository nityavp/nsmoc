import streamlit as st
import pandas as pd
import random
import zipfile
import os
import requests
from openai import OpenAI

# Text input for API key
api_key = st.text_input("Enter your OpenAI API Key", type="password")

# Categories and options
points = ["tips", "hacks", "news", "guide", "analogy", "joke", "compare", "up and downs", "funfacts"]
time_related = ["latest", "historic", "trends"]
locations = ["culture", "country", "region", "religions", "beliefs"]

# Hooks for personal posts
hooks = [
    "If you're lazy, but still want to do {topic}, try this...",
    "I will never recover from learning about {topic}...",
    "If I died tomorrow, here's everything I'd want you to know about {topic}...",
    "Have you ever had to do {topic} because of this reason?",
    "The one secret experts don't want you to know about {topic}...",
    "Why I stopped doing {topic} and you should too...",
    "The ultimate guide to {topic} that you never knew you needed...",
    "If you could only do one thing to achieve {topic}, it would be this...",
    "How {topic} completely changed my perspective...",
    "The best advice I ever got about {topic}...",
    "5 things nobody tells you about {topic}...",
    "I tried {topic} for 30 days and this is what happened...",
    "Why {topic} is the key to achieving your goals...",
    "You won't believe what {topic} can do for you...",
    "The shocking truth about {topic} that everyone should know...",
    "If you're struggling with {topic}, try this simple trick...",
    "I wish I knew about {topic} sooner...",
    "The top 10 {topic} hacks that will change your life...",
    "How I went from beginner to expert in {topic} in just 30 days...",
    "Why {topic} is more important than you think...",
    "The unexpected benefits of {topic}...",
    "What nobody tells you about {topic}...",
    "The biggest mistake people make with {topic}...",
    "How to master {topic} in 5 easy steps...",
    "The real reason why {topic} is so popular...",
    "What I learned from {topic} that changed my life...",
    "The best way to approach {topic} that you've never heard of...",
    "How to make {topic} work for you...",
    "The surprising connection between {topic} and personal growth...",
    "Why {topic} is the future of self-improvement...",
    "The ultimate {topic} checklist for success...",
    "How to get started with {topic} even if you're a complete beginner...",
    "The most important thing to remember about {topic}...",
    "Why you should start focusing on {topic} today...",
    "The one thing you need to know about {topic}...",
    "How {topic} can help you achieve your dreams...",
    "The best-kept secret in {topic}...",
    "How to avoid the biggest mistake with {topic}...",
    "Why {topic} is the best investment you can make...",
    "The real story behind my journey with {topic}...",
    "What {topic} taught me about life...",
    "The most effective way to approach {topic}...",
    "Why {topic} is worth the hype...",
    "How to turn {topic} into your biggest advantage...",
    "The truth about {topic} that nobody wants to admit...",
    "Why {topic} is more powerful than you think...",
    "How to tackle {topic} like a pro...",
    "The secret to success with {topic}...",
    "Why {topic} is the best thing I've ever done...",
    "What you need to know about {topic} before you start..."
]


# Initialize session state for posts data
if 'posts_data' not in st.session_state:
    st.session_state['posts_data'] = pd.DataFrame(columns=['Date', 'Content', 'Platform', 'Status'])

# Function to generate posts using the OpenAI API
def generate_posts(api_key, platform, topic, style, num_posts, user_type):
    posts = []
    for _ in range(num_posts):
        chosen_points = random.choice(points) if random.random() > 0.5 else ""
        chosen_time = random.choice(time_related) if random.random() > 0.5 else ""
        chosen_location = random.choice(locations) if random.random() > 0.5 else ""
        
        if user_type == "Personal":
            chosen_hook = random.choice(hooks)
            custom_prompt = f"Generate a unique {platform} post that contains interesting {chosen_points} with the {chosen_hook} for my followers about {topic} in {style} style"
        else:
            custom_prompt = f"Generate a unique {platform} post that contains interesting {chosen_points} in {chosen_time} for {chosen_location} for my followers about {topic} in {style} style"

        messages = [{"role": "system", "content": custom_prompt}]
        try:
            client = OpenAI(api_key=api_key)
            completions = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages
            )
            response = completions.choices[0].message.content
            posts.append(response)
        except Exception as e:
            st.error(f"Failed to generate posts: {e}")
            return []
    return posts

# User interface for selecting user type, platform, entering topic, style, and number of posts
user_type = st.radio('Select User Type', ['Company', 'Personal'])
platform = st.selectbox('Select Social Media Platform', ['Twitter', 'LinkedIn'])
topic = st.text_input('Enter Topic')
style = st.text_input('Enter Writing Style')
num_posts = st.number_input('Number of Posts', min_value=1, max_value=20, value=1)
generate_btn = st.button('Generate Posts')

# Generate posts when button is clicked
if generate_btn:
    generated_posts = generate_posts(api_key, platform, topic, style, num_posts, user_type)
    new_rows = [{'Date': pd.Timestamp('now'), 'Content': post, 'Platform': platform, 'Status': 'Pending'} for post in generated_posts]
    st.session_state.posts_data = pd.concat([st.session_state.posts_data, pd.DataFrame(new_rows)], ignore_index=True)

# Display and edit the DataFrame containing generated posts
edited_data = st.dataframe(st.session_state.posts_data, num_rows='dynamic', use_container_width=True)

# Update session state with edited data
st.session_state.posts_data = edited_data

# Function to generate an image based on selected row
def generate_image(api_key, style, content):
    try:
        client = OpenAI(api_key=api_key)
        response = client.images.generate(
            model="dall-e-3",
            prompt=f"{style} {content}",
            size="1024x1024",
            quality="standard",
            n=1,
        )
        image_url = response.data[0].url
        return image_url
    except Exception as e:
        st.error(f"Failed to generate image: {e}")
        return None

# Function to create a zip file with content and image
def create_zip(content, image_url):
    zip_path = '/mnt/data/final_posts.zip'
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        # Save the content
        content_path = '/mnt/data/content.txt'
        with open(content_path, 'w') as f:
            f.write(content)
        zipf.write(content_path, 'content.txt')
        os.remove(content_path)
        
        # Download and save the image
        image_path = '/mnt/data/image.png'
        img_data = requests.get(image_url).content
        with open(image_path, 'wb') as f:
            f.write(img_data)
        zipf.write(image_path, 'image.png')
        os.remove(image_path)
    
    return zip_path

# Allow user to select a row
selected_row = st.selectbox('Select a row to generate an image', edited_data.index)
selected_style = st.text_input('Enter Image Style for Selected Row')
if st.button('Generate Image for Selected Row'):
    selected_content = edited_data.loc[selected_row, 'Content']
    image_url = generate_image(api_key, selected_style, selected_content)
    if image_url:
        st.image(image_url, caption='Generated Image')
        zip_path = create_zip(selected_content, image_url)
        with open(zip_path, "rb") as file:
            st.download_button('Download Content and Image in Zip', file, file_name='final_posts.zip')

