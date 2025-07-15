import argparse
import pandas as pd
from datetime import datetime
from collections import deque

TICKER_COL = 'AsxCode'
ORDER_TYPE_COL = 'Order Type' 
DATE_COL = 'Settlement Date'
PRICE_COL = 'Price'
QUANTITY_COL = 'Quantity'
CONSIDERATION_COL = 'Consideration'
FEE_COLS = ['Brokerage', 'GST', 'Stampduty', 'Application Fee', 'OtherCharge', 'Fee']


def parse_args():
    p = argparse.ArgumentParser(
        description="Compute capital gains using FIFO per-ticker"
    )
    p.add_argument(
        "input_file",
        nargs="?",
        default="Confirmation.csv",
        help="Trade CSV file (default: %(default)s)"
    )
    p.add_argument(
        "--fy-end",
        type=int,
        default=datetime.now().year,
        help="Financial year end year (e.g. 2023 for FY2022-23; defaults to current year)"
    )
    p.add_argument(
        "--splits",
        default="stock_splits.csv",
        help="CSV file with stock splits (format: Date,Ticker,Ratio)"
    )
    p.add_argument(
        "--output",
        default="gains.csv",
        help="Output CSV for per-sale gains (default: %(default)s)"
    )
    return p.parse_args()


def load_stock_splits(split_file):
    if not split_file:
        return {}
    try:
        splits_df = pd.read_csv(split_file, index_col=False)
        splits_df['Date'] = pd.to_datetime(splits_df['Date'])
    except Exception as e:
        print(f"Error reading stock splits file: {e}")
        return {}

    splits = {}
    for _, row in splits_df.iterrows():
        ticker = row['Ticker']
        if ticker not in splits:
            splits[ticker] = []
        splits[ticker].append({
            'date': row['Date'],
            'ratio': float(row['Ratio'])
        })
    return splits


def calc_fees(df_row):
    return sum(df_row.get(col, 0) for col in FEE_COLS)


def main():
    args = parse_args()
    df = pd.read_csv(args.input_file, index_col=False)
    df.columns = df.columns.str.strip()

    df[DATE_COL] = pd.to_datetime(df[DATE_COL])

    # Compute FY window
    fy_start_date = datetime(args.fy_end - 1, 7, 1)
    fy_end_date = datetime(args.fy_end, 6, 30)

    # Clean and tilter order type column
    df[ORDER_TYPE_COL] = df[ORDER_TYPE_COL].astype(str).str.upper()

    # Get a df of all sells within the financial year, sorted in ascending order
    sells_df = df[
        (df[ORDER_TYPE_COL] == 'SELL') &
        (df[DATE_COL] >= fy_start_date) &
        (df[DATE_COL] <= fy_end_date)
    ].copy()
    sells_df.sort_values(DATE_COL, inplace=True)

    # Get a df of all buys, sorted in ascending order
    buys_df = df[df[ORDER_TYPE_COL] == 'BUY'].copy()
    buys_df.sort_values(DATE_COL, inplace=True)

    # Get stock splits from user
    splits = load_stock_splits(args.splits)

    # Build FIFO queues of buys - assume no buy fees
    fifo_queues = {} # ticker: [{buy_date, buy_qty, buy_price}, {} ,...]
    for _, buy_row in buys_df.iterrows():
        ticker = buy_row[TICKER_COL]
        buy_date = buy_row[DATE_COL]
        qty = buy_row[QUANTITY_COL]
        price = buy_row[PRICE_COL]

        # Apply all stock splits before the sell
        if ticker in splits:
            for split in sorted(splits[ticker], key=lambda x: x['date']):
                if buy_date < split['date']:
                    qty *= split['ratio']
                    price /= split['ratio']

        if ticker not in fifo_queues:
            fifo_queues[ticker] = deque()
        fifo_queues[ticker].append({
            'date': buy_date,
            'qty': qty,
            'price': price
        })

    # Match sells to FIFO buys
    gain_rows = []
    total_fees = 0
    for _, sell_row in sells_df.iterrows():
        ticker = sell_row[TICKER_COL]
        sell_qty = sell_row[QUANTITY_COL]
        sell_price = sell_row[PRICE_COL]
        sell_date = sell_row[DATE_COL]
        total_fees += calc_fees(sell_row)

        # Check there is buy data for this stock
        if ticker not in fifo_queues or not fifo_queues[ticker]:
            print(f"No FIFO buy data available for {ticker} before sell on {sell_date}")
            continue
        
        # Check that enough units have been bought for how many are trying to be sold
        total_bought = sum(info_dict['qty'] for info_dict in fifo_queues[ticker] if info_dict['date'] < sell_date)
        if sell_qty > total_bought:
            print(f"Error: Trying to sell {sell_qty} units of {ticker}, but have only bought {total_bought}")
            continue

        while sell_qty > 0 and fifo_queues[ticker]:
            buy = fifo_queues[ticker][0]
            used_qty = min(sell_qty, buy['qty'])
            gain = (sell_price - buy['price']) * used_qty

            gain_rows.append({
                'Ticker': ticker,
                'Sell Date': sell_date,
                'Sell Price': sell_price,
                'Buy Date': buy['date'],
                'Buy Price': buy['price'],
                'Quantity': used_qty,
                'Gain': gain,
            })

            sell_qty -= used_qty
            buy['qty'] -= used_qty
            if buy['qty'] == 0:
                fifo_queues[ticker].popleft()

    # Output to CSV
    gains_df = pd.DataFrame(gain_rows)
    gains_df.to_csv(args.output, index=False)
    print(f"Total capital gain: ${gains_df['Gain'].sum():,.2f}")
    print(f"Total net capital gain (minus fees): ${gains_df['Gain'].sum() - total_fees:,.2f}")
    print(f"Saved capital gains to {args.output}")
    

if __name__ == "__main__":
    main()