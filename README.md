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
- Applies 50% CGT discount for assets held longer than 12 months
- Ignores capital losses when reporting total gains

---

## 📁 Input Format

### 🔹 Trade History CSV

Your input CSV should include at least the following columns (headers must match exactly):

| Column Name        | Description                        |
|--------------------|------------------------------------|
| `AsxCode`          | Ticker symbol (e.g. `AAPL:US`)     |
| `Order Type`       | `BUY` or `SELL`                    |
| `Settlement Date`  | Date of settlement (e.g. `2024-08-01`) |
| `Price`            | Price per share                    |
| `Quantity`         | Number of shares                   |
| `Brokerage`, `GST`, `Stampduty`, `Application Fee`, `OtherCharge`, `Fee` | (Optional) Fees associated with trades |

### 🔹 Stock Splits CSV

To handle stock splits (including reverse splits), provide a separate CSV with this format:

```csv
Date,Ticker,Ratio
2024-06-10,NVDA:US,10
2023-05-01,AAPL:US,0.25
```

---

## 🖥️ Usage

```bash
python3 calculate_capital_gains.py <trades-csv> --fy-end <end-fy> --splits <stock-splits-csv> --output <output-csv>
```

## Arguments
- ```trades-csv```: Path to the CSV file containing trade history (default: Confirmation.csv)

- ```--fy-end```: End year of the financial year (e.g. 2024 for FY2023–24) (default: the current year)

- ```--splits```: Path to stock splits CSV (default: stock_splits.csv)

- ```--output```: Output filename for capital gains report (default: gains.csv)

---

## 📤 Output

The output CSV includes one row per matched sale:

| Ticker | Sell Date | Sell Price | Buy Date | Buy Price | Quantity | Gain | Discounted Gain |
|--------|-----------|------------|----------|-----------|----------|------|-----------------|

The script also prints:

- **Total capital gain** (excluding losses, fees, and CGT discount)
- **Total net capital gain** (after subtracting fees and applying CGT discount)


---

## 📝 Example

```bash
python3 calculate_capital_gains.py Confirmation.csv --fy-end 2025 --splits stock_splits.csv --output gains.csv
```
```
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
- Fees on buy trades are currently ignored — only sell-side fees reduce net gain
- Trades are matched to buys using FIFO order per ticker