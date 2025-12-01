import requests
import os

# Configuration
BASE_URL = 'http://127.0.0.1:5000'
LOGIN_URL = f'{BASE_URL}/admin'
DASHBOARD_URL = f'{BASE_URL}/dashboard'
USERNAME = 'Admin'
PASSWORD = 'Admin@1998'
IMAGE_PATH = 'static/uploads/test_card.png'

# Create a session to persist cookies
session = requests.Session()

# 1. Login
print(f"Logging in to {LOGIN_URL}...")
login_payload = {'username': USERNAME, 'password': PASSWORD}
response = session.post(LOGIN_URL, data=login_payload)

if response.url == DASHBOARD_URL or 'Upload New Prompt' in response.text:
    print("Login successful!")
else:
    print("Login failed!")
    print(response.text)
    exit(1)

# 2. Upload Image
print(f"Uploading image from {IMAGE_PATH}...")
if not os.path.exists(IMAGE_PATH):
    print(f"Error: File {IMAGE_PATH} not found.")
    # Create a dummy file if needed
    with open(IMAGE_PATH, 'wb') as f:
        f.write(b'dummy image content')
    print("Created dummy file.")

with open(IMAGE_PATH, 'rb') as f:
    files = {'image': ('test_card.png', f, 'image/png')}
    data = {'prompt_text': 'Test prompt from script'}
    response = session.post(DASHBOARD_URL, files=files, data=data)

if response.status_code == 200:
    print("Upload request completed.")
    if 'Prompt uploaded successfully!' in response.text:
        print("Upload success message found.")
    else:
        print("Upload success message NOT found.")
else:
    print(f"Upload failed with status code {response.status_code}")
