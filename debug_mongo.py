from app import app, mongo, fs

with app.app_context():
    print("--- Prompts Collection ---")
    prompts = list(mongo.db.prompts.find())
    for p in prompts:
        print(f"Prompt: {p.get('prompt_text')}, Image: {p.get('image_filename')}")

    print("\n--- GridFS Files ---")
    # Access collection using dictionary notation to avoid attribute errors
    files = list(mongo.db['fs.files'].find())
    for f in files:
        print(f"Filename: {f.get('filename')}, ContentType: {f.get('contentType')}, Length: {f.get('length')}")
