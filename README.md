# trip_planner
# Check out a short video depicting the project here:
```
https://youtu.be/h0lBoGhmCvc
```
This project is a full-stack application developed with FastAPI and Next.js, designed to help users plan trips by providing destination options, flight and hotel information, and generating daily plans and images using OpenAI's DALL-E.

# Features
1. Search for trip destination options based on user input.
2. Fetch flight and hotel information.
3. Generate daily plans for the selected destination.
4. Generate images for the daily plans using OpenAI's DALL-E.

# Technologies used

1. Backend: FastAPI
2. Frontend: Next.js
3. API: OpenAI API, SerpAPI
4. Styling: CSS Modules

# Installation
Clone:
```
git clone https://github.com/yourusername/tripplanner.git
cd tripplanner
```
# Backend setup
Create a '.env' in the backend directory:
```
TRIP_PLANNER_API_KEY=your_openai_api_key_here
SERPAPI_API_KEY_MIKE=your_serpapi_key_here

```
Install dependencies:
```

cd backend
pip install -r requirements.txt
uvicorn main:app --reload

```

# Frontend setup
```
cd frontend
npm install
npm run dev
```

#Usage
1. Start backend server:
```
cd backend
uvicorn main:app --reload
```
2. Start frontend server:
```
cd frontend
npm run dev
```

3. open the browser and go to localhost:3000

# Project structure

```
tripplanner/
│
├── backend/
│   ├── __pycache__/
│   ├── .pytest_cache/
│   ├── .env
│   ├── main.py
│   ├── trip_planner_backend.py
│   ├── requirements.txt
│   └── README.md
│
├── frontend/
│   ├── .next/
│   ├── app/
│   │   ├── favicon.ico
│   │   ├── globals.css
│   │   ├── layout.tsx
│   │   ├── pages/
│   │   │   ├── _app.js
│   │   │   └── index.js
│   │   ├── public/
│   │   └── styles/
│   │       ├── table.module.css
│   ├── node_modules/
│   ├── .eslintrc.json
│   ├── .gitignore
│   ├── next-env.d.ts
│   ├── next.config.mjs
│   ├── package-lock.json
│   ├── package.json
│   └── postcss.config.mjs
│
├── README.md
└── .gitignore

```

# Commit history
```
* 2859d13 (HEAD -> master, origin/master) Better CSS
* 73e81ac finished next.js, need to work on CSS
* afcef86 working get_destination_daily_plan on next.js
* adc3e5e search_options working in next.js
* 31c2717 started working on frontend
* c006cab fixed get dalle issue
* dccd946 working FASTAPI
* cdf840a working python user interaction
* e8a6d77 DNS issue with return_flights
* 98fae43 with one dict for all destinations
* eb47bf8 working get_hotels
* 222c990 need to fix the hotels s.t it will be less than the budget remaining
* 563a71a finished get_flights
* 30f1ff3 returning flight, need to parse better
* 239eddf get_options, get_daily_plan working
* 5c30f18 initial commit
```

# Contributing

I welcome contributions to this project! Whether you want to add new features, improve existing functionality, or fix bugs, your help is appreciated. Please feel free to fork the repository and submit pull requests.

Thank you for checking out this project. If you have any questions or suggestions, please feel free to open an issue or contact us directly. Happy coding!
