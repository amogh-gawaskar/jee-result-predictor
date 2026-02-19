# JEE Mains Result Predictor

A comprehensive web application to predict JEE Mains results and recommend eligible colleges based on your performance. Convert between any JEE parameter (marks, percentage, percentile, ranks) and discover which colleges you can target.

## Project Structure

```
JEE Model/
├── backend/                           # Flask backend API
│   ├── app.py                        # Main Flask application
│   └── requirements.txt              # Python dependencies (Flask, pandas)
├── frontend/                         # React + TypeScript frontend
│   ├── src/
│   │   ├── App.tsx                  # Main application component
│   │   └── App.css                  # Styling
│   └── package.json                 # Node dependencies
├── College Databases - JoSAA 2024.csv # College admission data
├── JEE result predictor.ipynb        # Original prediction model
├── CLAUDE.md                         # Development log and version history
└── README.md                         # This file
```

## Features

### 🎯 Result Prediction (v1.0)
- Convert between any JEE Mains parameter: marks, percentage, percentile, All India Rank, or Category Rank
- Supports all categories: OPEN, OBC-NCL, SC, ST, EWS
- Advanced piecewise logistic model for accurate percentile conversion
- Real-time calculation via REST API

### 🔒 Input Validation (v1.1)
- Smart input validation with error messages
- Marks: 0-300 range validation
- Percentage/Percentile: 0-100 range validation
- HTML5 constraints for better UX

### 📊 Advanced Prediction Model (v1.2)
- Three-segment piecewise percentile model for better accuracy:
  - 0-25%: Logistic function
  - 25-40%: Logarithmic function
  - 40%+: Exponential function
- Improved edge case handling

### 🎓 College Recommendations (v2.0)
- **Smart college filtering** based on your predicted rank
- **10% safety margin** for realistic recommendations
- Filter by:
  - Gender (Male/Female with seat-specific logic)
  - Home State (HS/AI quota) vs Other State (OS/AI quota)
  - Special quota handling for Goa and Jammu & Kashmir
- View detailed information:
  - College name and location
  - Course/program name
  - Closing rank for your category
  - Expected salary (NIRF data)
- Responsive table with sticky headers for easy browsing

## Modern UI/UX

- Clean, gradient-based design with purple theme
- Fully responsive (mobile, tablet, desktop)
- Smooth animations and transitions
- Intuitive step-by-step workflow
- Red accent button for college recommendations
- Scrollable college results table

## Setup Instructions

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Start the Flask server:
   ```bash
   python app.py
   ```

   The backend will run on `http://localhost:5001`

   **Note:** Port 5001 is used instead of 5000 due to macOS AirPlay conflicts.

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install Node dependencies:
   ```bash
   npm install
   ```

3. Start the React development server:
   ```bash
   npm start
   ```

   The frontend will run on `http://localhost:3000`

## Usage

### Step 1: Predict Your Results
1. Ensure both backend and frontend servers are running
2. Open `http://localhost:3000` in your browser
3. Select your category (OPEN, OBC-NCL, SC, ST, or EWS)
4. Choose an input type (marks, percentage, percentile, AIR, or category rank)
5. Enter the value (with automatic validation)
6. Click "Predict" to see all calculated results

### Step 2: Find Your Colleges
7. After seeing your predicted results, click the red button "Check your expected college and course"
8. Select your gender (Male/Female)
9. Select your home state (33 Indian states/UTs available)
10. Click "Submit" to see eligible colleges
11. Browse through the table of colleges sorted by closing rank
12. Each entry shows: College name, Course, State, Closing Rank, Expected Salary

## API Endpoints

### POST /api/predict
Predicts JEE results based on input parameters.

**Request Body:**
```json
{
  "category": "OPEN",
  "inputType": "marks",
  "inputValue": 250
}
```

**Response:**
```json
{
  "success": true,
  "results": {
    "marks": 250,
    "percentage": 83.33,
    "percentile": 99.87,
    "allIndiaRank": 1950,
    "categoryRank": 1950
  }
}
```

### POST /api/colleges
Get college recommendations based on rank and preferences.

**Request Body:**
```json
{
  "category": "OPEN",
  "categoryRank": 13050,
  "gender": "Male",
  "state": "Maharashtra"
}
```

**Response:**
```json
{
  "success": true,
  "colleges": [
    {
      "College": "National Institute Of Technology Calicut",
      "Course": "Engineering Physics (4 Years, Bachelor of Technology)",
      "State": "Kerala",
      "Closing Rank": 16218,
      "Expected Salary as per NIRF": 1054944
    },
    ...
  ]
}
```

**Filtering Logic:**
- Only shows JEE Main colleges
- Filters by seat type matching user's category
- Male: Shows Gender-Neutral seats
- Female: Prioritizes Female-only seats per college, falls back to Gender-Neutral
- Home state: Shows HS/AI quota (+ GO for Goa, JK/LA for J&K)
- Other state: Shows OS/AI quota
- 10% safety margin: Shows colleges with closing rank >= 0.9 × your rank

### GET /api/health
Health check endpoint.

## Technologies Used

- **Backend:** Flask 3.0, Flask-CORS, Pandas, Python 3.8+
- **Frontend:** React 18, TypeScript, Create React App
- **Styling:** Custom CSS with gradient design and responsive layouts
- **Data:** JoSAA 2024 college admission database (2.8MB CSV)

## Version History

### v2.0 (Current) - College Recommendations
- Added college recommendation system with JoSAA 2024 data
- Implemented smart filtering by gender, state, and quota
- 10% safety margin for realistic recommendations
- Responsive table UI with college details and expected salaries
- Fixed JSON serialization issues (NaN handling)

### v1.2 - Improved Prediction Model
- Implemented piecewise logistic percentile model (3 segments)
- More accurate percentile calculations across all ranges
- Changed default values from 10 to 1 for edge cases

### v1.1 - Input Validation
- Added client-side validation for marks (0-300)
- Added validation for percentage and percentile (0-100)
- HTML5 constraints for better user experience
- Clear error messages

### v1.0 - Initial Release
- Core prediction functionality
- Support for all 5 categories (OPEN, OBC-NCL, SC, ST, EWS)
- Bidirectional conversion between all parameters
- Modern gradient UI with responsive design

## Key Algorithms

### Percentile to Percentage Conversion
Uses a piecewise model for accuracy across ranges:
- **0-25%**: Logistic sigmoid function
- **25-40%**: Logarithmic growth
- **40%+**: Exponential decay model

### Rank Conversions
- Category-specific piecewise linear functions
- Separate forward (AIR → Category Rank) and inverse (Category Rank → AIR) functions
- Handles all categories: SC, ST, OBC-NCL, EWS, OPEN

## Contributing

This project was built with Claude Code. For questions or issues, please refer to CLAUDE.md for detailed development logs.

## License

This project is for educational purposes.
