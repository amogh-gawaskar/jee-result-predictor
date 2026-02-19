import React, { useState } from 'react';
import './App.css';

interface PredictionResults {
  marks: number | null;
  percentage: number | null;
  percentile: number | null;
  allIndiaRank: number | null;
  categoryRank: number | null;
}

interface College {
  College: string;
  Course: string;
  State: string;
  'Closing Rank': number;
  'Expected Salary as per NIRF': number;
}

function App() {
  // API Base URL - uses relative path in production (Vercel serverless), localhost in development
  const API_BASE_URL = process.env.NODE_ENV === 'development'
    ? 'http://localhost:5001'
    : ''; // Relative path for Vercel

  const [category, setCategory] = useState<string>('OPEN');
  const [inputType, setInputType] = useState<string>('marks');
  const [inputValue, setInputValue] = useState<string>('');
  const [results, setResults] = useState<PredictionResults | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>('');

  // College recommendations state
  const [showCollegeForm, setShowCollegeForm] = useState<boolean>(false);
  const [gender, setGender] = useState<string>('Male');
  const [state, setState] = useState<string>('');
  const [colleges, setColleges] = useState<College[]>([]);
  const [loadingColleges, setLoadingColleges] = useState<boolean>(false);
  const [collegeError, setCollegeError] = useState<string>('');

  const inputTypes = [
    { value: 'marks', label: 'Raw Marks (out of 300)' },
    { value: 'percentage', label: 'Percentage Marks (%)' },
    { value: 'percentile', label: 'Percentile' },
    { value: 'allIndiaRank', label: 'All India Rank' },
    { value: 'categoryRank', label: 'Category Rank' },
  ];

  const categories = [
    { value: 'OPEN', label: 'OPEN' },
    { value: 'OBC-NCL', label: 'OBC-NCL' },
    { value: 'SC', label: 'SC' },
    { value: 'ST', label: 'ST' },
    { value: 'EWS', label: 'EWS' },
  ];

  const indianStates = [
    'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh',
    'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh', 'Jharkhand',
    'Karnataka', 'Kerala', 'Madhya Pradesh', 'Maharashtra', 'Manipur',
    'Meghalaya', 'Mizoram', 'Nagaland', 'Odisha', 'Punjab',
    'Rajasthan', 'Sikkim', 'Tamil Nadu', 'Telangana', 'Tripura',
    'Uttar Pradesh', 'Uttarakhand', 'West Bengal', 'Jammu & Kashmir',
    'Delhi', 'Puducherry', 'Chandigarh', 'Ladakh'
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    // Validate input values
    const value = parseFloat(inputValue);

    if (inputType === 'marks') {
      if (value < 0 || value > 300) {
        setError('Enter a value between 0 and 300');
        return;
      }
    } else if (inputType === 'percentage' || inputType === 'percentile') {
      if (value < 0 || value > 100) {
        setError('Enter a value between 0 and 100');
        return;
      }
    }

    setLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/api/predict`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          category,
          inputType,
          inputValue: parseFloat(inputValue),
        }),
      });

      const data = await response.json();

      if (data.success) {
        setResults(data.results);
      } else {
        setError(data.error || 'An error occurred');
      }
    } catch (err) {
      setError('Failed to connect to the backend. Please ensure the Flask server is running on port 5001.');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setInputValue('');
    setResults(null);
    setError('');
    setShowCollegeForm(false);
    setColleges([]);
    setCollegeError('');
  };

  const handleShowCollegeForm = () => {
    setShowCollegeForm(true);
    setCollegeError('');
  };

  const handleFetchColleges = async (e: React.FormEvent) => {
    e.preventDefault();
    setCollegeError('');
    setLoadingColleges(true);

    if (!state) {
      setCollegeError('Please select a state');
      setLoadingColleges(false);
      return;
    }

    if (!results || !results.categoryRank) {
      setCollegeError('Category rank not available');
      setLoadingColleges(false);
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/api/colleges`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          category,
          categoryRank: results.categoryRank,
          gender,
          state,
        }),
      });

      const data = await response.json();
      console.log('Received data:', data);

      if (data.success) {
        setColleges(data.colleges);
        console.log('Set colleges:', data.colleges.length);
      } else {
        console.log('Error from backend:', data.error);
        setCollegeError(data.error || 'An error occurred');
      }
    } catch (err) {
      console.error('Fetch error:', err);
      setCollegeError(`Failed to fetch college recommendations: ${err instanceof Error ? err.message : 'Unknown error'}`);
    } finally {
      setLoadingColleges(false);
    }
  };

  const getInputPlaceholder = () => {
    switch (inputType) {
      case 'marks':
        return 'Enter marks (0-300)';
      case 'percentage':
        return 'Enter percentage (0-100)';
      case 'percentile':
        return 'Enter percentile (0-100)';
      case 'allIndiaRank':
        return 'Enter All India Rank';
      case 'categoryRank':
        return 'Enter Category Rank';
      default:
        return 'Enter value';
    }
  };

  const getInputMin = () => {
    if (inputType === 'marks' || inputType === 'percentage' || inputType === 'percentile') {
      return 0;
    }
    return undefined;
  };

  const getInputMax = () => {
    if (inputType === 'marks') {
      return 300;
    } else if (inputType === 'percentage' || inputType === 'percentile') {
      return 100;
    }
    return undefined;
  };

  return (
    <div className="App">
      <div className="container">
        <h1>JEE Mains Result Predictor</h1>
        <p className="subtitle">Predict your JEE Mains results using any input parameter</p>

        <form onSubmit={handleSubmit} className="prediction-form">
          <div className="form-group">
            <label htmlFor="category">Category</label>
            <select
              id="category"
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="form-control"
            >
              {categories.map((cat) => (
                <option key={cat.value} value={cat.value}>
                  {cat.label}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="inputType">Input Type</label>
            <select
              id="inputType"
              value={inputType}
              onChange={(e) => {
                setInputType(e.target.value);
                setInputValue('');
                setResults(null);
              }}
              className="form-control"
            >
              {inputTypes.map((type) => (
                <option key={type.value} value={type.value}>
                  {type.label}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="inputValue">
              {inputTypes.find((t) => t.value === inputType)?.label}
            </label>
            <input
              id="inputValue"
              type="number"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder={getInputPlaceholder()}
              className="form-control"
              required
              step="any"
              min={getInputMin()}
              max={getInputMax()}
            />
          </div>

          {error && <div className="error-message">{error}</div>}

          <div className="button-group">
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? 'Calculating...' : 'Predict'}
            </button>
            <button type="button" className="btn btn-secondary" onClick={handleReset}>
              Reset
            </button>
          </div>
        </form>

        {results && (
          <div className="results-container">
            <h2>Predicted Results</h2>
            <div className="results-grid">
              <div className="result-item">
                <span className="result-label">Raw Marks:</span>
                <span className="result-value">{results.marks} / 300</span>
              </div>
              <div className="result-item">
                <span className="result-label">Percentage:</span>
                <span className="result-value">{results.percentage}%</span>
              </div>
              <div className="result-item">
                <span className="result-label">Percentile:</span>
                <span className="result-value">{results.percentile}</span>
              </div>
              <div className="result-item">
                <span className="result-label">All India Rank:</span>
                <span className="result-value">{results.allIndiaRank}</span>
              </div>
              <div className="result-item">
                <span className="result-label">Category Rank ({category}):</span>
                <span className="result-value">{results.categoryRank}</span>
              </div>
            </div>

            {!showCollegeForm && (
              <div className="college-button-container">
                <button
                  onClick={handleShowCollegeForm}
                  className="btn btn-college"
                >
                  Check your expected college and course
                </button>
              </div>
            )}
          </div>
        )}

        {showCollegeForm && results && (
          <div className="college-form-container">
            <h2>College Recommendations</h2>
            <form onSubmit={handleFetchColleges} className="college-form">
              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="gender">Gender</label>
                  <select
                    id="gender"
                    value={gender}
                    onChange={(e) => setGender(e.target.value)}
                    className="form-control"
                  >
                    <option value="Male">Male</option>
                    <option value="Female">Female</option>
                  </select>
                </div>

                <div className="form-group">
                  <label htmlFor="state">State</label>
                  <select
                    id="state"
                    value={state}
                    onChange={(e) => setState(e.target.value)}
                    className="form-control"
                    required
                  >
                    <option value="">Select your state</option>
                    {indianStates.map((s) => (
                      <option key={s} value={s}>
                        {s}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              {collegeError && <div className="error-message">{collegeError}</div>}

              <button type="submit" className="btn btn-primary" disabled={loadingColleges}>
                {loadingColleges ? 'Loading...' : 'Submit'}
              </button>
            </form>
          </div>
        )}

        {colleges.length > 0 && (
          <div className="colleges-container">
            <h2>Eligible Colleges & Courses</h2>
            <p className="colleges-info">
              Showing {colleges.length} options based on your rank with 10% safety margin
            </p>
            <div className="table-container">
              <table className="colleges-table">
                <thead>
                  <tr>
                    <th>College</th>
                    <th>Course</th>
                    <th>State</th>
                    <th>Closing Rank</th>
                    <th>Expected Salary (NIRF)</th>
                  </tr>
                </thead>
                <tbody>
                  {colleges.map((college, index) => (
                    <tr key={index}>
                      <td>{college.College}</td>
                      <td>{college.Course}</td>
                      <td>{college.State}</td>
                      <td>{college['Closing Rank']}</td>
                      <td>₹{college['Expected Salary as per NIRF']?.toLocaleString('en-IN') || 'N/A'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
