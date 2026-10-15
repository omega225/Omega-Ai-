from flask import Flask, render_template, jsonify
import requests

app = Flask(__name__)

def get_absolute_vector(symbol):
    # Fetch high-frequency 1m data
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1m&range=1d"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        data = requests.get(url, headers=headers).json()
        ohlc = data['chart']['result'][0]['indicators']['quote'][0]
        
        # Current Price Point
        last_close = ohlc['close'][-1]
        last_open = ohlc['open'][-1]
        
        # Calculate Vector Force (Pressure)
        # If closing > opening, force is positive. 
        force = last_close - last_open
        
        future_candles = []
        current_cursor = last_close
        
        # PROJECT 3 FUTURE CANDLES (100% VECTOR LOCK)
        for i in range(1, 4):
            f_open = current_cursor
            # The Vector Projection: Momentum + Harmonic Decay
            # We predict the candle will follow the current force with 90% follow-through
            move = force * (1.1 - (i * 0.1)) 
            f_close = f_open + move
            
            # Absolute Wick Projection (High/Low)
            f_high = max(f_open, f_close) + (abs(move) * 0.2)
            f_low = min(f_open, f_close) - (abs(move) * 0.2)
            
            future_candles.append({
                "o": f_open, "h": f_high, "l": f_low, "c": f_close
            })
            current_cursor = f_close
            
        return {
            "symbol": symbol.replace("=X", ""),
            "price": last_close,
            "future": future_candles
        }
    except:
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/vector/<symbol>')
def vector(symbol):
    return jsonify(get_absolute_vector(symbol))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
