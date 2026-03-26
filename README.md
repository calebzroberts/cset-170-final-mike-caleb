# Flask Basic Application

This is a basic Flask web application with the following pages:
- Main Page (/)
- Login Page (/login)
- Sign Up Page (/signup)
- Admin Page (/admin)
- My Account Page (/account)

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the application:
   ```
   python main.py
   ```

3. Open your browser and go to `http://127.0.0.1:5000/`

## Notes

- This is a basic implementation with static pages.
- Forms on login and signup pages don't perform actual authentication yet.
- No database is used; all data is handled in-memory or not at all.