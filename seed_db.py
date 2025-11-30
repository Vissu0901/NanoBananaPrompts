from app import app, db, Prompt

with app.app_context():
    # Check if prompt already exists to avoid duplicates
    if not Prompt.query.filter_by(image_filename='test_card.png').first():
        new_prompt = Prompt(
            image_filename='test_card.png',
            prompt_text='This is a test prompt with abstract colors. Verify the card layout and styling.'
        )
        db.session.add(new_prompt)
        db.session.commit()
        print("Prompt added successfully.")
    else:
        print("Prompt already exists.")
