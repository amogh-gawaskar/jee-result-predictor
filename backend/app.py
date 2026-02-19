from flask import Flask, request, jsonify
from flask_cors import CORS
import math
import pandas as pd
import os

app = Flask(__name__)
CORS(app)

# Constants
TOTAL_MARKS = 300  # JEE Mains total marks
a = -0.1035 #exponential coefficient
b = 1500000 #number of test takers

# ============================
# Basic Conversion Functions
# ============================

def marks_to_percentage(score: int, total: int = TOTAL_MARKS) -> float:
    return score * 100 / total

def percentage_to_marks(percentage: float, total: int = TOTAL_MARKS) -> int:
    return math.floor(percentage * total / 100)

def percentage_to_percentile(percentage: float) -> float:
    """
    Piecewise logistic model for percentage to percentile conversion.
    - 0 to 25: Logistic function
    - 25 to 40: Logarithmic function
    - 40 and above: Exponential function
    """
    if percentage <= 25:
        # Logistic model
        Lfit = -86.555129
        Ufit = 98.24994
        kfit = 0.153249
        x0_fit = 0.624824
        percentile = Lfit + (Ufit - Lfit) / (1 + math.exp(-kfit * (percentage - x0_fit)))
    elif 25 < percentage <= 40:
        # Logarithmic model
        percentile = 65.1 + 8.95 * math.log(percentage)
    else:  # percentage > 40
        # Exponential model
        percentile = 100 * (1 - math.exp(-0.095 * percentage))
    return percentile

# Calculate exact segment boundaries for inverse function
PERCENTILE_AT_25 = -86.555129 + (98.24994 - (-86.555129)) / (1 + math.exp(-0.153249 * (25 - 0.624824)))  # ~94.417
PERCENTILE_AT_40 = 65.1 + 8.95 * math.log(40)  # ~97.796

def percentile_to_percentage(percentile: float) -> float:
    """
    Inverse of percentage_to_percentile using piecewise model.
    Uses precise segment boundaries.
    """
    if percentile <= PERCENTILE_AT_25:
        # Invert logistic model (segment 1: 0-25%)
        # Using numerical search
        low, high = 0, 25
        for _ in range(50):  # Binary search
            mid = (low + high) / 2
            test_percentile = percentage_to_percentile(mid)
            if abs(test_percentile - percentile) < 0.001:
                return mid
            if test_percentile < percentile:
                low = mid
            else:
                high = mid
        return (low + high) / 2

    elif PERCENTILE_AT_25 < percentile <= PERCENTILE_AT_40:
        # Invert logarithmic model (segment 2: 25-40%)
        # percentile = 65.1 + 8.95 * ln(percentage)
        # ln(percentage) = (percentile - 65.1) / 8.95
        # percentage = exp((percentile - 65.1) / 8.95)
        percentage = math.exp((percentile - 65.1) / 8.95)
        return percentage

    else:  # percentile > PERCENTILE_AT_40
        # Invert exponential model (segment 3: 40+%)
        # percentile = 100 * (1 - exp(-0.095 * percentage))
        # 1 - percentile/100 = exp(-0.095 * percentage)
        # ln(1 - percentile/100) = -0.095 * percentage
        # percentage = -ln(1 - percentile/100) / 0.095
        if percentile >= 100:
            return 100
        percentage = -math.log(1 - percentile / 100) / 0.095
        return percentage

def percentile_to_air(percentile: float) -> int:
    return int(b * (1 - percentile / 100))

def air_to_percentile(air: int) -> float:
    return 100 * (1 - air / b)

# ============================
# Coefficient Declarations (SC)
# ============================

F1_C1_M = 0.0251
F1_C1_B = -19.5
F1_C2_M = 0.0276
F1_C2_B = -51.9
F1_C3_M = 0.0383
F1_C3_B = -373
F1_C4_M = 0.0429
F1_C4_B = -605
F1_C5_M = 0.0515
F1_C5_B = -1297
F1_C6_M = 0.0571
F1_C6_B = -1854
F1_C7_M = 0.0738
F1_C7_B = -4542
F1_C8_M = 0.0892
F1_C8_B = -9217
F1_C9_M = 0.106
F1_C9_B = -17937
F1_C10_M = 0.118
F1_C10_B = -30183

# Function 2 coefficients (OBC-NCL)
F2_C1_M = 0.232
F2_C1_B = -131
F2_C2_M = 0.313
F2_C2_B = -1180
F2_C3_M = 0.351
F2_C3_B = -2833
F2_C4_M = 0.389
F2_C4_B = -7865

# Function 3 coefficients (EWS)
F3_C1_M = 0.129
F3_C1_B = -77.2
F3_C2_M = 0.145
F3_C2_B = -100
F3_C3_M = 0.118
F3_C3_B = 7517
F3_C4_M = 0.098
F3_C4_B = 19862
F3_C5_M = 0.0788
F3_C5_B = 39286

# Function 4 coefficients (ST)
F4_C1_M = 0.00725
F4_C1_B = -32.2
F4_C2_M = 0.0122
F4_C2_B = -326
F4_C3_M = 0.0165
F4_C3_B = -930
F4_C4_M_LINEAR = 0.0136
F4_C4_M_QUAD = 1.76e-8
F4_C4_B = -1146
F4_C5_M = 0.0396
F4_C5_B = -11081

# ST segment coefficients for inverse
C4_S1_A = F4_C1_M
C4_S1_B = F4_C1_B
C4_S2_A = F4_C2_M
C4_S2_B = F4_C2_B
C4_S3_A = F4_C3_M
C4_S3_B = F4_C3_B
C4_S4_A = F4_C4_M_QUAD
C4_S4_B = F4_C4_M_LINEAR
C4_S4_C = F4_C4_B
C4_S5_A = F4_C5_M
C4_S5_B = F4_C5_B

# ============================
# Inverse Coefficients
# ============================

# OBC-NCL
INV1_C1_M = 0.232
INV1_C1_B = 131
INV1_C2_M = 0.313
INV1_C2_B = 1180
INV1_C3_M = 0.351
INV1_C3_B = 2833
INV1_C4_M = 0.389
INV1_C4_B = 7865

# EWS
INV2_C1_M = 0.129
INV2_C1_B = 77.2
INV2_C2_M = 0.145
INV2_C2_B = 100
INV2_C3_M = 0.118
INV2_C3_B = -7517
INV2_C4_M = 0.098
INV2_C4_B = -19862
INV2_C5_M = 0.0788
INV2_C5_B = -39286

# SC
INV4_C1_M = 0.0251
INV4_C1_B = 19.5
INV4_C2_M = 0.0276
INV4_C2_B = 51.9
INV4_C3_M = 0.0383
INV4_C3_B = 373
INV4_C4_M = 0.0429
INV4_C4_B = 605
INV4_C5_M = 0.0515
INV4_C5_B = 1297
INV4_C6_M = 0.0571
INV4_C6_B = 1854
INV4_C7_M = 0.0738
INV4_C7_B = 4542
INV4_C8_M = 0.0892
INV4_C8_B = 9217
INV4_C9_M = 0.106
INV4_C9_B = 17937
INV4_C10_M = 0.118
INV4_C10_B = 30183

# ============================
# AIR to Category Rank Functions
# ============================

def calculate_function1(value: float) -> float:
    """SC category"""
    if value < 10000:
        return F1_C1_M * value + F1_C1_B
    elif 10000 <= value <= 30000:
        return F1_C2_M * value + F1_C2_B
    elif 30000 <= value <= 50000:
        return F1_C3_M * value + F1_C3_B
    elif 50000 <= value <= 75000:
        return F1_C4_M * value + F1_C4_B
    elif 75000 <= value <= 100000:
        return F1_C5_M * value + F1_C5_B
    elif 100000 <= value <= 150000:
        return F1_C6_M * value + F1_C6_B
    elif 150000 <= value <= 300000:
        return F1_C7_M * value + F1_C7_B
    elif 300000 <= value <= 500000:
        return F1_C8_M * value + F1_C8_B
    elif 500000 <= value <= 1000000:
        return F1_C9_M * value + F1_C9_B
    elif value > 1000000:
        return F1_C10_M * value + F1_C10_B
    return 0.0

def calculate_function2(value: float) -> float:
    """OBC-NCL category"""
    if value < 10000:
        return F2_C1_M * value + F2_C1_B
    elif 10000 <= value <= 50000:
        return F2_C2_M * value + F2_C2_B
    elif 50000 <= value <= 100000:
        return F2_C3_M * value + F2_C3_B
    elif value > 100000:
        return F2_C4_M * value + F2_C4_B
    return 0.0

def calculate_function3(value: float) -> float:
    """EWS category"""
    if value <= 10000:
        return F3_C1_M * value + F3_C1_B
    elif 10000 < value <= 300000:
        return F3_C2_M * value + F3_C2_B
    elif 300000 < value <= 600000:
        return F3_C3_M * value + F3_C3_B
    elif 600000 < value <= 1000000:
        return F3_C4_M * value + F3_C4_B
    elif value > 1000000:
        return F3_C5_M * value + F3_C5_B
    return 0.0

def calculate_function4(value: float) -> float:
    """ST category"""
    if value <= 50000:
        return F4_C1_M * value + F4_C1_B
    elif 50000 < value <= 150000:
        return F4_C2_M * value + F4_C2_B
    elif 150000 < value <= 200000:
        return F4_C3_M * value + F4_C3_B
    elif 200000 < value <= 750000:
        return F4_C4_M_QUAD * (value ** 2) + F4_C4_M_LINEAR * value + F4_C4_B
    elif value > 750000:
        return F4_C5_B + F4_C5_M * value
    return 0.0

def air_to_cat(category: str, rank: float) -> int:
    """Convert All India Rank to Category Rank"""
    if category == "SC":
        raw = calculate_function1(rank)
    elif category == "OBC-NCL":
        raw = calculate_function2(rank)
    elif category == "EWS":
        raw = calculate_function3(rank)
    elif category == "OPEN":
        raw = rank
    elif category == "ST":
        raw = calculate_function4(rank)
    else:
        raise ValueError("Invalid category")

    rounded = int(round(raw))
    if rounded <= 0:
        return 1
    return rounded

# ============================
# Category Rank to AIR Functions
# ============================

def inverse_function1(y: float) -> float:
    """OBC-NCL inverse"""
    if y < 2189:
        return (y + INV1_C1_B) / INV1_C1_M
    elif 2189 <= y <= 14470:
        return (y + INV1_C2_B) / INV1_C2_M
    elif 14470 <= y <= 32267:
        return (y + INV1_C3_B) / INV1_C3_M
    elif y > 32267:
        return (y + INV1_C4_B) / INV1_C4_M
    return 0.0

def inverse_function2(y: float) -> float:
    """EWS inverse"""
    if y <= 1212.8:
        return (y + INV2_C1_B) / INV2_C1_M
    elif 1212.8 < y <= 43400:
        return (y + INV2_C2_B) / INV2_C2_M
    elif 43400 < y <= 78317:
        return (y + INV2_C3_B) / INV2_C3_M
    elif 78317 < y <= 117862:
        return (y + INV2_C4_B) / INV2_C4_M
    elif y > 117862:
        return (y + INV2_C5_B) / INV2_C5_M
    return 0.0

def inverse_function3(y: float) -> int:
    """ST inverse - from notebook"""
    # Determine y-ranges of each segment
    y_s1_min = calculate_function4(0.0)
    y_s1_max = calculate_function4(50000.0)
    y_s2_min = calculate_function4(50000.0)
    y_s2_max = calculate_function4(150000.0)
    y_s3_min = calculate_function4(150000.0)
    y_s3_max = calculate_function4(200000.0)
    y_s4_min = calculate_function4(200000.0)
    y_s4_max = calculate_function4(750000.0)
    y_s5_min = calculate_function4(750000.0)

    # Invert per segment by y-range
    if y_s1_min <= y <= y_s1_max:
        x = (y - C4_S1_B) / C4_S1_A
    elif y_s2_min < y <= y_s2_max:
        x = (y - C4_S2_B) / C4_S2_A
    elif y_s3_min < y <= y_s3_max:
        x = (y - C4_S3_B) / C4_S3_A
    elif y_s4_min < y <= y_s4_max:
        # Solve: C4_S4_A * x^2 + C4_S4_B * x + (C4_S4_C - y) = 0
        a = C4_S4_A
        b = C4_S4_B
        c = C4_S4_C - y
        disc = b * b - 4.0 * a * c
        if disc < 0:
            raise ValueError("No real solution for quadratic inverse in segment 4")
        sqrt_disc = math.sqrt(disc)
        x1 = (-b + sqrt_disc) / (2.0 * a)
        x2 = (-b - sqrt_disc) / (2.0 * a)
        # Select the root that lies in (200000, 750000]
        x = None
        for candidate in (x1, x2):
            if 200000.0 < candidate <= 750000.0:
                x = candidate
                break
        if x is None:
            raise ValueError("No valid root in the domain (200000, 750000] for segment 4")
    elif y > y_s5_min:
        x = (y - C4_S5_B) / C4_S5_A
        if x <= 750000.0:
            raise ValueError("Inverse in segment 5 produced x not > 750000")
    else:
        raise ValueError("Input y is outside the range of calculate_function4")

    rounded = int(round(x))
    if rounded <= 0:
        return 1
    return rounded

def inverse_function4(y: float) -> float:
    """SC inverse"""
    if y < 231.6:
        return (y + INV4_C1_B) / INV4_C1_M
    elif 231.6 <= y <= 776.1:
        return (y + INV4_C2_B) / INV4_C2_M
    elif 776.1 <= y <= 1542:
        return (y + INV4_C3_B) / INV4_C3_M
    elif 1542 <= y <= 2612.5:
        return (y + INV4_C4_B) / INV4_C4_M
    elif 2612.5 <= y <= 3853:
        return (y + INV4_C5_B) / INV4_C5_M
    elif 3853 <= y <= 6711:
        return (y + INV4_C6_B) / INV4_C6_M
    elif 6711 <= y <= 17598:
        return (y + INV4_C7_B) / INV4_C7_M
    elif 17598 <= y <= 35483:
        return (y + INV4_C8_B) / INV4_C8_M
    elif 35483 <= y <= 88063:
        return (y + INV4_C9_B) / INV4_C9_M
    elif y > 88063:
        return (y + INV4_C10_B) / INV4_C10_M
    return 0.0

def cat_to_air(category: str, rank: float) -> int:
    """Convert Category Rank to All India Rank"""
    if category == "SC":
        raw = inverse_function4(rank)
    elif category == "OBC-NCL":
        raw = inverse_function1(rank)
    elif category == "EWS":
        raw = inverse_function2(rank)
    elif category == "OPEN":
        raw = rank
    elif category == "ST":
        raw = inverse_function3(rank)
    else:
        raise ValueError("Invalid category")

    rounded = int(round(raw))
    if rounded < 0:
        return 1
    return rounded

# ============================
# API Endpoints
# ============================

@app.route('/api/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        category = data.get('category')
        input_type = data.get('inputType')
        input_value = float(data.get('inputValue'))

        # Initialize results
        results = {
            'marks': None,
            'percentage': None,
            'percentile': None,
            'allIndiaRank': None,
            'categoryRank': None
        }

        # Based on input type, calculate all other values
        if input_type == 'marks':
            results['marks'] = int(input_value)
            results['percentage'] = round(marks_to_percentage(input_value), 2)
            results['percentile'] = round(percentage_to_percentile(results['percentage']), 2)
            results['allIndiaRank'] = percentile_to_air(results['percentile'])
            results['categoryRank'] = air_to_cat(category, results['allIndiaRank'])

        elif input_type == 'percentage':
            results['percentage'] = round(input_value, 2)
            results['marks'] = percentage_to_marks(input_value)
            results['percentile'] = round(percentage_to_percentile(input_value), 2)
            results['allIndiaRank'] = percentile_to_air(results['percentile'])
            results['categoryRank'] = air_to_cat(category, results['allIndiaRank'])

        elif input_type == 'percentile':
            results['percentile'] = round(input_value, 2)
            results['percentage'] = round(percentile_to_percentage(input_value), 2)
            results['marks'] = percentage_to_marks(results['percentage'])
            results['allIndiaRank'] = percentile_to_air(input_value)
            results['categoryRank'] = air_to_cat(category, results['allIndiaRank'])

        elif input_type == 'allIndiaRank':
            results['allIndiaRank'] = int(input_value)
            results['percentile'] = round(air_to_percentile(int(input_value)), 2)
            results['percentage'] = round(percentile_to_percentage(results['percentile']), 2)
            results['marks'] = percentage_to_marks(results['percentage'])
            results['categoryRank'] = air_to_cat(category, int(input_value))

        elif input_type == 'categoryRank':
            results['categoryRank'] = int(input_value)
            results['allIndiaRank'] = cat_to_air(category, int(input_value))
            results['percentile'] = round(air_to_percentile(results['allIndiaRank']), 2)
            results['percentage'] = round(percentile_to_percentage(results['percentile']), 2)
            results['marks'] = percentage_to_marks(results['percentage'])

        return jsonify({'success': True, 'results': results})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/colleges', methods=['POST'])
def get_colleges():
    try:
        data = request.json
        print(f"Received request: {data}")
        category = data.get('category')
        category_rank = int(data.get('categoryRank'))
        gender = data.get('gender')
        state = data.get('state')
        print(f"Parsed: category={category}, rank={category_rank}, gender={gender}, state={state}")

        # Load CSV file - works for both local and Vercel
        current_dir = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(current_dir, '..', 'College Databases - JoSAA 2024.csv')
        csv_path = os.path.abspath(csv_path)
        df = pd.read_csv(csv_path)

        # Filter by Entrance Test = JEE Main
        df = df[df['Entrance Test'] == 'JEE Main']

        # Filter by Seat Type = category
        df = df[df['Seat Type'] == category]

        # Filter by Gender
        if gender == 'Male':
            # Only Gender-Neutral
            df = df[df['Gender'] == 'Gender-Neutral']
        else:  # Female
            # For each College ID, check if Female-only rows exist
            college_ids = df['College ID'].unique()
            filtered_dfs = []

            for college_id in college_ids:
                college_df = df[df['College ID'] == college_id]
                female_only_df = college_df[college_df['Gender'].str.contains('Female-only', na=False)]

                if len(female_only_df) > 0:
                    # Show only Female-only rows for this college
                    filtered_dfs.append(female_only_df)
                else:
                    # Show all eligible rows for this college
                    filtered_dfs.append(college_df)

            if filtered_dfs:
                df = pd.concat(filtered_dfs, ignore_index=True)
            else:
                df = pd.DataFrame()  # Empty dataframe

        # Filter by State and Quota
        college_ids = df['College ID'].unique()
        filtered_dfs = []

        for college_id in college_ids:
            college_df = df[df['College ID'] == college_id]
            college_state = college_df['State'].iloc[0] if len(college_df) > 0 else None

            if college_state == state:
                # Home state - show HS or AI quota
                quota_filter = college_df['Quota'].isin(['HS', 'AI'])

                # Special cases
                if state == 'Goa':
                    quota_filter = college_df['Quota'].isin(['HS', 'AI', 'GO'])
                elif state == 'Jammu and Kashmir':
                    quota_filter = college_df['Quota'].isin(['HS', 'AI', 'JK', 'LA'])

                filtered_college_df = college_df[quota_filter]
            else:
                # Other state - show OS or AI quota
                filtered_college_df = college_df[college_df['Quota'].isin(['OS', 'AI'])]

            if len(filtered_college_df) > 0:
                filtered_dfs.append(filtered_college_df)

        if filtered_dfs:
            df = pd.concat(filtered_dfs, ignore_index=True)
        else:
            df = pd.DataFrame()

        # Convert Closing Rank and Expected Salary to numeric
        df['Closing Rank'] = pd.to_numeric(df['Closing Rank'], errors='coerce')
        df['Expected Salary'] = pd.to_numeric(df['Expected Salary'], errors='coerce')
        df = df.dropna(subset=['Closing Rank'])  # Remove rows with invalid closing ranks

        # Filter by Closing Rank >= 0.9 * category_rank (10% error margin)
        df = df[df['Closing Rank'] >= 0.9 * category_rank]

        # Select and rename columns
        result_df = df[['Institute', 'Academic Program Name', 'State', 'Closing Rank', 'Expected Salary']].copy()
        result_df.sort_values(by='Closing Rank')
        result_df.columns = ['College', 'Course', 'State', 'Closing Rank', 'Expected Salary as per NIRF']

        # Replace NaN values with None for valid JSON
        result_df = result_df.where(pd.notnull(result_df), None)

        # Convert to list of dictionaries, preserving CSV order
        results = result_df.to_dict('records')
        print(f"Returning {len(results)} colleges")

        return jsonify({'success': True, 'colleges': results})

    except Exception as e:
        print(f"ERROR in get_colleges: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5001, use_reloader=False)
