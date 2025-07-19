# To Do

Build a basic API service for shortening URLs. You’re free to make reasonable assumptions about requirements.

## Requirements

Please build a simple API with:

1. `POST /shorten` – Accepts a long URL, returns a shortened one (e.g., (`https://jkwlsn.dev/abc123`)
2. `GET /{code}` – Redirects to the original long URL
3. Basic persistence between requests (e.g., save data to a file or use SQLite)

## 📦 What to Include

- A clear README with setup/run instructions
- Logical, clean code structure
- Good naming and meaningful organisation
- Error handling and appropriate HTTP responses

## 💡 Optional Extras (Not Required)

- Feel free to go above and beyond, but only if time allows, to:
- Add expiry times to links
- Show how you’d write tests
- Include a CLI or simple web interface
- Deploy the project somewhere publicly

## 🛠️ Tech Guidelines

- Use any language or framework you’re comfortable with
- Lightweight persistence only (file storage, SQLite, etc.)
- No need for full production infrastructure - focus on clarity, not DevOps

## 🔍 What We Assess

| Category | What to look for |
-----------|--------------------
| Structured Thinking | Clean separation of concerns, modular functions, REST design |
| Autonomy | Good README, sensible defaults, initiative in implementation |
| Curiosity & Stretch | Optional features attempted, insightful comments |
| Technical Fundamentals | Routing, HTTP codes, simple persistence, validation, clean code |
