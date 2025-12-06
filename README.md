# Fidelity CSV Converter

Convert Fidelity investment account transaction exports to OFX format for use in financial management software like Moneydance.

## What This Does

This tool takes CSV files exported from Fidelity and converts them into OFX format, making it easy to import your investment transactions into other financial software.

## Installation

1. Open **Terminal** (on Mac: press `Cmd + Space`, type "Terminal", press Enter)
2. Create a folder and download the script:

```bash
mkdir fidelity_csv_converter
cd fidelity_csv_converter
curl -o fidelity_csv_converter.py https://raw.githubusercontent.com/sztupkay/fidelity_csv_converter/refs/heads/main/fidelity_csv_converter.py
```

## Prerequisites

You need Python 3.9 or later installed on your computer. To check if you have Python:

1. Open **Terminal** (on Mac: press `Cmd + Space`, type "Terminal", press Enter)
2. Type the following command and press Enter:
   ```
   python3 --version
   ```
3. You should see something like `Python 3.9.x` or higher. If you see "command not found", you need to install Python from [python.org](https://www.python.org/downloads/)

## How to Use

### Step 1: Prepare Your CSV File

1. Log into your [Fidelity account](https://www.fidelity.com)
2. Go to your investment account
3. Find and download the transaction history as CSV format
4. Save the CSV file to your **Downloads** folder. By default, the script searches for files in the 'Downloads' folder.

### Step 2: Run the Converter

#### Option A: Automatic (Recommended)

If your CSV file is in your Downloads folder and has the standard Fidelity naming format (`History_for_Account_XXXXXXXXX.csv`):

```bash
# Run the converter
python3 fidelity_csv_converter.py
```

The tool will automatically find your latest CSV file and create an OFX file in the same folder.

#### Option B: Specify File Paths

If you want more control over input/output paths:

```bash
python3 fidelity_csv_converter.py \
  --csv "/path/to/your/History_for_Account_242530437.csv" \
  --ofx "/path/to/output/transactions.ofx"
```

#### Option C: Filter by Date

To only convert transactions after a specific date:

```bash
python3 fidelity_csv_converter.py \
  --csv "/path/to/your/csv/file.csv" \
  --start-date "2025-01-01"
```

### Step 3: Import into Financial Software

2. Open your financial software (Moneydance, etc.)
3. Use the import function to import the OFX file
4. Choose the appropriate account for importing transactions. If the account ID is correct, you may select "Remember" for future imports.
5. Review the imported transactions and, if necessary, update any "MiscInc" entries to "Div" for accurate categorization.

## Command Line Options

| Option | Description | Example |
|--------|-------------|---------|
| `--csv` | Path to input CSV file. If omitted, uses latest from Downloads | `--csv "/Users/you/Downloads/History_for_Account_242530437.csv"` |
| `--ofx` | Path for output OFX file. If omitted, creates one in the same folder as CSV | `--ofx "/Users/you/Desktop/transactions.ofx"` |
| `--start-date` | Only convert transactions on/after this date (YYYY-MM-DD format) | `--start-date "2025-01-01"` |
| `--account` | Account ID. Usually auto-detected from filename | `--account "242530437"` |

## Troubleshooting

### "Python not found" error
- Make sure Python 3.9+ is installed (see Prerequisites section)
- Try using `python3` instead of `python`

### "No input CSV file found"
- Make sure your CSV file is in your Downloads folder OR specify the full path with `--csv`
- Check that the filename contains "History_for_Account_"

### "Could not determine account ID"
- Rename your CSV file to match the format: `History_for_Account_XXXXXXXXX.csv` where XXXXXXXXX is your account number
- OR use the `--account` option to specify it: `--account "242530437"`

## File Structure

```
fidelity_csv_converter/
├── fidelity_csv_converter.py      # Main converter script
├── fidelity_csv_converter_test.py # Tests (optional)
├── requirements.txt                # Python dependencies
├── .gitignore                       # Files to ignore in git
└── README.md                        # This file
```

## What You Need to Know

- **CSV Format**: The script expects standard Fidelity CSV exports. If your CSV looks different, it may not work.
- **OFX Format**: OFX (Open Financial Exchange) is a standard format supported by most financial software.

## Running Tests (Optional)

If you want to verify everything is working:

```bash
pytest fidelity_csv_converter_test.py -v
```

## Support

If something isn't working:
1. Check the "Troubleshooting" section above
2. Make sure Python 3.9+ is installed
3. Make sure the virtual environment is activated (you should see it in your terminal prompt)
4. Review the error message carefully—it often tells you what's wrong
