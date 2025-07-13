# 📈 Capital Gains Calculator

This Python script calculates **capital gains** on stock trades using a **FIFO (First-In, First-Out)** cost basis. It supports:
- Transaction filtering by financial year
- Fee inclusion
- Multiple and reverse stock splits

The result is written to a CSV file with detailed per-lot gain calculations.

---

## 🔧 Features

- Parses trade history from a CSV file
- Calculates gains using FIFO for each security
- Filters only **SELL** transactions within a given financial year
- Handles **multiple stock splits**, including **reverse splits**
- Includes **brokerage and related fees**
- Outputs per-sale details and total capital gain

---

## 📁 Input Format

Your input CSV should include at least the following columns (headers must match):

| Column Name        | Description                        |
|--------------------|------------------------------------|
| AsxCode            | Ticker symbol (e.g. `AAPL:US`)     |
| Order Type         | `BUY` or `SELL`                    |
| Settlement Date    | Date of settlement (e.g. `2024-08-01`) |
| Price              | Price per share                    |
| Quantity           | Number of shares                   |
| Brokerage, GST, Stampduty, Application Fee, OtherCharge, Fee | (Optional) Fees associated with trades |

---

## 🖥️ Usage

```bash
python3 calculate_capital_gains.py <trades-csv> --fy-end <end-fy> --output <output-csv>
```

## Arguments
- ```trades-csv```: Path to the CSV file containing trade history (default: Confirmation.csv)

- ```--fy-end```: End year of the financial year (e.g. 2024 for FY2023–24) (default: the current year)

- ```--output```: Output filename for capital gains report (default: gains.csv)

---

## 🧮 Stock Splits
At runtime, the script will prompt you to enter any stock splits:
1. Ticker (e.g., AAPL:US)
2. Split Date (e.g., 2024-08-30)
3. Split Ratio:
    - Use 2 for a 2-for-1 split
    - Use 0.1 for a 1-for-10 reverse split

You can enter multiple splits per stock. Press Enter without a ticker to finish.

---

## 📤 Output

The output CSV includes one row per matched sale:

| Ticker | Sell Date | Sell Price | Buy Date | Buy Price | Quantity | Gain |
|--------|-----------|------------|----------|-----------|----------|------|

The script also prints:

- **Total gross capital gain**
- **Total net capital gain** (after subtracting fees)

---

## 📝 Example

```bash
python3 calculate_capital_gains.py Confirmation.csv --fy-end 2024 --output gains.csv
```
```
Enter stock splits (press Enter to skip):
Ticker (e.g. AAPL:US): AAPL:US
Split date for AAPL:US (YYYY-MM-DD): 2024-08-30
Split ratio (e.g. 2 for 2-for-1, 0.1 for 1-for-10): 4
Registered split for AAPL:US: 4.0-for-1 on 2024-08-30
Ticker (e.g. AAPL:US): 
Total capital gain: $12,450.70
Total net capital gain (minus fees): $12,126.90
Saved capital gains to gains.csv
```

---

## 📦 Requirements
- Python 3.x
- pandas

Install dependencies with:
```
pip install pandas
```

---

## 📌 Notes
- Only settled trades (Settlement Date) are used for gain calculation
- All quantities and prices are adjusted for splits prior to sale
- Fees on buy trades are currently ignored — only sale-side fees reduce net gain