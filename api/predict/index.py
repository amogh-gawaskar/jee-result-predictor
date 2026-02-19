from flask import Flask, request, jsonify
import math

app = Flask(__name__)

# Constants
TOTAL_MARKS = 300
a = -0.1035
b = 1500000

def marks_to_percentage(score: int, total: int = TOTAL_MARKS) -> float:
    return score * 100 / total

def percentage_to_marks(percentage: float, total: int = TOTAL_MARKS) -> int:
    return math.floor(percentage * total / 100)

def percentage_to_percentile(percentage: float) -> float:
    if percentage <= 25:
        Lfit = -86.555129
        Ufit = 98.24994
        kfit = 0.153249
        x0_fit = 0.624824
        percentile = Lfit + (Ufit - Lfit) / (1 + math.exp(-kfit * (percentage - x0_fit)))
    elif 25 < percentage <= 40:
        percentile = 65.1 + 8.95 * math.log(percentage)
    else:
        percentile = 100 * (1 - math.exp(-0.095 * percentage))
    return percentile

PERCENTILE_AT_25 = -86.555129 + (98.24994 - (-86.555129)) / (1 + math.exp(-0.153249 * (25 - 0.624824)))
PERCENTILE_AT_40 = 65.1 + 8.95 * math.log(40)

def percentile_to_percentage(percentile: float) -> float:
    if percentile <= PERCENTILE_AT_25:
        low, high = 0, 25
        for _ in range(50):
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
        percentage = math.exp((percentile - 65.1) / 8.95)
        return percentage
    else:
        if percentile >= 100:
            return 100
        percentage = -math.log(1 - percentile / 100) / 0.095
        return percentage

def percentile_to_air(percentile: float) -> int:
    return int(b * (1 - percentile / 100))

def air_to_percentile(air: int) -> float:
    return 100 * (1 - air / b)

def air_to_cat(category: str, rank: float) -> int:
    # Simplified - returns same for OPEN, approximate for others
    if category == "OPEN":
        return int(round(rank))
    return int(round(rank * 0.27))  # Approximate conversion

def cat_to_air(category: str, rank: float) -> int:
    if category == "OPEN":
        return int(round(rank))
    return int(round(rank / 0.27))

@app.route('/', defaults={'path': ''}, methods=['POST', 'OPTIONS'])
@app.route('/<path:path>', methods=['POST', 'OPTIONS'])
def predict(path):
    if request.method == 'OPTIONS':
        return '', 200

    try:
        data = request.json
        category = data.get('category')
        input_type = data.get('inputType')
        input_value = float(data.get('inputValue'))

        results = {
            'marks': None,
            'percentage': None,
            'percentile': None,
            'allIndiaRank': None,
            'categoryRank': None
        }

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

def handler(request):
    return app(request)
