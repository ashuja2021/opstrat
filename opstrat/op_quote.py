# Set up pulling data for an option chain
import yfinance as yf
from datetime import datetime, timedelta
import holidays
import pandas as pd
import opstrat as op


def get_nth_business_day(start_date, n, country='US'):
    """
    Returns the date n business days after start_date, skipping weekends and holidays.
    """
    us_holidays = holidays.CountryHoliday(country)
    current_date = start_date
    business_days_count = 0

    while business_days_count < n:
        current_date += timedelta(days=1)
        if current_date.weekday() < 5 and current_date not in us_holidays:
            business_days_count += 1
    return current_date


def get_option_chain(ticker_symbol, expiration_date):
    """
    Fetches the option chain for a given ticker and expiration date.
    Returns a DataFrame with both calls and puts.
    """
    ticker = yf.Ticker(ticker_symbol)
    available_expirations = ticker.options
    if expiration_date not in available_expirations:
        raise ValueError(f"Expiration date {expiration_date} not available. Available dates: {available_expirations}")
    chain = ticker.option_chain(expiration_date)
    # Add a column to distinguish calls and puts
    calls = chain.calls.copy()
    calls['type'] = 'call'
    puts = chain.puts.copy()
    puts['type'] = 'put'
    # Combine into one DataFrame
    options_df = pd.concat([calls, puts], ignore_index=True)
    return options_df

def find_atm_strike(df, spot_price):
    # Only look at unique strikes available in both calls and puts
    strikes = df['strike'].unique()
    # Find the strike closest to the spot price
    atm_strike = min(strikes, key=lambda x: abs(x - spot_price))
    return atm_strike

def get_option_premium(df, strike, opt_type):
    # Filter for the correct strike and type
    row = df[(df['strike'] == strike) & (df['type'] == opt_type)]
    if not row.empty:
        return float(row.iloc[0]['lastPrice'])
    else:
        return None  # Or handle missing data as needed

def plot_iron_butterfly(ticker_symbol, expiration_date, atm_strike, width=10):
    """
    Plots an iron butterfly for the given ticker, expiration, and ATM strike.
    width: distance between ATM and wings
    """
    # Example premiums, you should fetch these from your DataFrame
    # Replace these with actual values from your option chain DataFrame
    premium_atm_call = 5.0
    premium_atm_put = 5.0
    premium_wing_call = 2.0
    premium_wing_put = 2.0

    op_list = [
        {'op_type': 'c', 'strike': atm_strike, 'tr_type': 's', 'op_pr': premium_atm_call},  # Sell ATM Call
        {'op_type': 'p', 'strike': atm_strike, 'tr_type': 's', 'op_pr': premium_atm_put},   # Sell ATM Put
        {'op_type': 'c', 'strike': atm_strike + width, 'tr_type': 'b', 'op_pr': premium_wing_call},  # Buy OTM Call
        {'op_type': 'p', 'strike': atm_strike - width, 'tr_type': 'b', 'op_pr': premium_wing_put},   # Buy OTM Put
    ]
    op.basic_multi.multi_plotter(spot=atm_strike, op_list=op_list)

def main():
    """
    Main function to analyze options and plot iron butterfly strategy.
    Flow:
    1. Get ticker and dates (current + target)
    2. Get available expirations from yfinance
    3. Filter for dates within next 9 business days
    4. Get option chains for target date
    5. Calculate ATM strike based on current spot price
    6. Get option premiums for iron butterfly legs
    7. Plot the strategy
    """
    # 1. Initialize ticker and dates
    ticker_symbol = "KR"  # This will be passed in later
    today = datetime.now().date()
    target_date = get_nth_business_day(today, 9)  # Get date 9 business days ahead
    
    # 2. Get available expiration dates for this ticker
    ticker = yf.Ticker(ticker_symbol)
    available_expirations = ticker.options
    print(f"All available expiration dates for {ticker_symbol}:", available_expirations)
    
    # 3. Filter for dates within next 9 business days
    valid_expirations = [
        date for date in available_expirations
        if datetime.strptime(date, "%Y-%m-%d").date() <= target_date
    ]
    print(f"\nExpiration dates within 9 business days (until {target_date}):", valid_expirations)
    
    # For development/testing - using a specific expiration date
    expiration_date = "2025-06-20"  # This will come from valid_expirations later
    if expiration_date not in available_expirations:
        raise ValueError(f"Expiration date {expiration_date} not available. Available dates: {available_expirations}")
    
    # 4. Get option chain for target expiration date
    df = get_option_chain(ticker_symbol, expiration_date)
    
    # Debug: Print option chains for dates within range (can be commented out later)
    """
    for exp in valid_expirations:
        print(f"\n=== Option Chain for {exp} ===")
        chain = ticker.option_chain(exp)
        print("Calls:")
        print(chain.calls.head())
        print("\nPuts:")
        print(chain.puts.head())
    """
    
    # 5. Get current spot price and calculate ATM strike
    spot_price = yf.Ticker(ticker_symbol).history(period="1d")['Close'].iloc[-1]
    print(f"\nCurrent spot price for {ticker_symbol}: ${spot_price:.2f}")
    
    atm_strike = find_atm_strike(df, spot_price)
    width = 10  # Strike width for butterfly wings
    print(f"ATM Strike: ${atm_strike:.2f}")
    print(f"Wing width: ${width:.2f}")
    
    # 6. Get premiums for each leg of the iron butterfly
    premium_atm_call = get_option_premium(df, atm_strike, 'call')
    premium_atm_put = get_option_premium(df, atm_strike, 'put')
    premium_wing_call = get_option_premium(df, atm_strike + width, 'call')
    premium_wing_put = get_option_premium(df, atm_strike - width, 'put')
    
    print("\nOption Premiums:")
    print(f"ATM Call (sell): ${premium_atm_call:.2f}")
    print(f"ATM Put (sell): ${premium_atm_put:.2f}")
    print(f"OTM Call (buy): ${premium_wing_call:.2f}")
    print(f"OTM Put (buy): ${premium_wing_put:.2f}")
    
    # 7. Plot the iron butterfly
    plot_iron_butterfly(
        ticker_symbol,
        expiration_date,
        atm_strike,
        width=width
    )

# Add this at the bottom of your file to run the script
if __name__ == "__main__":
    main()
