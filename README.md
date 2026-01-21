# FindMyBud

#### [Watch Video Demo](https://youtu.be/MwTNoe_C-zU?si=rKKaIOwnB04q1lhj)

## Project Overview:

FindMyBud is a web-based platform designed to help people report lost earbuds or return found earbuds.
Users can register, verify their email, create lost or found reports, browse reports posted by others, and manage their own reports securely.

This project was built as the final project for CS50x, focusing on real-world problem solving, clean code structure, security practices, and full-stack web development fundamentals.

## Features:

1. User registration & login system
1. Email verification using Gmail SMTP
1. Create Lost or Found earbud reports
1. Upload images for reports
1. View all public reports on the homepage
1. View detailed report information
1. Personal dashboard (My Reports)
1. Mark reports as Resolved
1. Delete own reports
1. Secure routes using login protection
1. Reusable UI components (report cards)
1. SQLite database for persistence

## Technologies Used:

- Python
- Flask
- SQLite
- HTML / Jinja2
- CSS
- Bootstrap
- SMTP (Gmail)
- itsdangerous (email verification tokens)

## Project Structure:

```
project/
│
├── app.py
├── helpers.py
├── requirements.txt
├── README.md
│
├── instance/
│   └── findmybud.db
│
├── static/
│   ├── styles.css
│   ├── images/
|   |   └── background.jpg   ✅ main background image
│   └── uploads/
│
└── templates/
    ├── layout.html
    ├── index.html
    ├── form.html
    ├── login.html
    ├── register.html
    ├── report.html
    ├── report_details.html
    ├── my_reports.html
    └── partials/
        └── report_card.html
        └── _footer.html
```

## How It Works:

1. Users register with an email and password
1. A verification email is sent
1. After verification, users can log in
1. Users can create lost or found reports
1. Reports appear publicly on the homepage
1. Owners can manage their reports via My Reports
1. Anyone can view detailed report information

## Installation & Setup:

### Step 1. Clone the repository

    git clone <your-repo-url>
    cd project

### Step 2. Create a virtual environment:

    python -m venv venv

### Step 3. Activate virtual environment:

For Linux / Mac

    source venv/bin/activate

For Windows

    venv\Scripts\activate

Step 4. Install dependencies

    pip install -r requirements.txt

Step 5. Run the application

    flask run

Then open:

http://127.0.0.1:5000


## Email Configuration:

This project uses Gmail SMTP for email verification.

### Recommended Setup

Set credentials using environment variables:

    export EMAIL_ADDRESS="your_email@gmail.com"
    export EMAIL_PASSWORD="your_app_password"


### Security Considerations

- Passwords are hashed using Werkzeug
- Email verification prevents fake accounts
- Users can only modify or delete their own reports
- Protected routes using login_required
- Sensitive credentials stored in environment variables
- Graceful fallback when email configuration is unavailable

## AI Assistance Disclosure:

Some parts of the project design, security considerations, and implementation guidance were assisted ChatGPT.
All code was reviewed, understood, and implemented by the author.

## Author:

### Muhammad Fazal Ur Rehman
CS50 Student
Pakistan 🇵🇰

## Final Notes:

This project demonstrates:

- Backend logic

- Database design

- Authentication & authorization

- Email verification workflows

- Security best practices

- Clean, reusable templates

- Real-world application structure
