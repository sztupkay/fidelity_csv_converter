from __future__ import annotations
import csv
import datetime
import io
import math
from typing import List, Optional
import argparse
import sys
import hashlib
import xml.etree.ElementTree as ET
import os
from pathlib import Path
import re

#!/usr/bin/env python3
"""
Simple CLI for converting Fidelity CSV transactions to OFX format.

This script can be saved as /Users/{username}/Documents/scripts/qif_convert.py
and executed with the command: python /Users/{username}/Documents/scripts/qif_convert.py

# This script converts Fidelity CSV transactions to OFX format.
# It first checks for an input CSV file, either provided directly or by finding the most recent one in the Downloads folder.
# It extracts the account ID from the CSV filename or uses a provided account ID.
# The script then reads the CSV data, processes each transaction, and converts it into OFX format.
# Finally, it saves the OFX output to a specified file or generates a default output path based on the CSV filename.

The output will be an OFX file containing transaction data structured as follows:

<OFX>
    <INVSTMTMSGSRSV1>
        <INVSTMTTRNRS>
            <INVSTMTRS>
                <INVACCTFROM>
                    <ACCTID>242530437</ACCTID>
                </INVACCTFROM>
                <INVTRANLIST>
                    <DTSTART>20250101</DTSTART>
                    <DTEND>20251231</DTEND>
                    <BUYSTOCK>
                        <INVBUY>
                            <INVTRAN>
                                <FITID>T32D2266EE0C7</FITID>
                                <DTTRADE>20251204</DTTRADE>
                                <MEMO>Market Buy Order</MEMO>
                            </INVTRAN>
                            <SECID>
                                <UNIQUEID>SPY</UNIQUEID>
                                <UNIQUEIDTYPE>CUSIP</UNIQUEIDTYPE>
                            </SECID>
                            <UNITS>1.00</UNITS>
                            <UNITPRICE>190.06</UNITPRICE>
                            <TOTAL>-190.06</TOTAL>
                            <BUYTYPE>BUY</BUYTYPE>
                        </INVBUY>
                    </BUYSTOCK>
                </INVTRANLIST>
            </INVSTMTRS>
        </INVSTMTTRNRS>
    </INVSTMTMSGSRSV1>
</OFX>

"""
_REQUIRED_FIELDS = [
    'Run Date',
    'Action',
    'Symbol',
    'Description',
    'Type',
    'Price ($)',
    'Quantity',
    'Commission ($)',
    'Fees ($)',
    'Amount ($)',
]


# Mapping of security symbols to their corresponding names in Moneydance.
# This mapping is only used for QIF conversion. The name must match the name of the security in Moneydance.
_SYMBOL_NAME_MAP = {
    "SPY": "SPDR S&P 500 ETF TRUST",
}

def security_name_for(symbol: Optional[str]) -> str:

    """Return mapped security name for a symbol, or the trimmed symbol if no mapping."""
    if symbol is None or symbol.strip().upper() not in _SYMBOL_NAME_MAP:
        raise ValueError(f"Symbol {symbol} needs to be configured in _SYMBOL_NAME_MAP")
    key = symbol.strip().upper()
    return _SYMBOL_NAME_MAP.get(key, symbol.strip())

def parse_action(action: str, is_ofx: bool) -> str:
    """Normalize Fidelity 'Action' text to a QIF action code."""
    if not action:
        return ""
    a = action.strip().lower()
    if any(kw in a for kw in ("bought", "buy", "purchase", "reinvestment")):
        return "BUYSTOCK" if is_ofx else "Buy"
    if any(kw in a for kw in ("sold", "sell")):
        return "SELLSTOCK" if is_ofx else "Sell"
    if any(kw in a for kw in ("dividend")):
        return "INCOME" if is_ofx else "Div"
    # fallback: return original trimmed value (capitalized)
    return action.strip().title()

def parse_amount(amount_str: Optional[str]) -> Optional[str]:
    """Parse amount string to float, or None if empty."""
    if amount_str is None or amount_str.strip() == "":
        return None
    try:
        return str(math.fabs(float(amount_str.replace(",", ""))))
    except ValueError:
        raise ValueError(f"Amount string {amount_str!r} is not a valid float.")

def parse_date(date_str: str | None) -> Optional[datetime.date]:
    """Parse a date string in various formats to a date object."""
    if date_str is None:
        return None
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%m-%d-%Y"):
        try:
            return datetime.datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Date string {date_str!r} is not in a recognized format.")

def get_row_id(row: dict[str, str]) -> str:
    """Generate a stable unique ID for a transaction row based on its content."""
    parts: List[str] = []
    for k in sorted(row.keys()):
        v = row.get(k) or ""
        parts.append(f"{k}={v}")
    digest = hashlib.sha1("||".join(parts).encode("utf-8")).hexdigest()[:12].upper()
    return digest

# Note: This function is defined but not used in the current implementation.
def convert_csv_to_qif(csv_data: str, start_date: Optional[datetime.date] = None) -> str:
    """Convert Fidelity CSV data to QIF format."""
    csv_data = "\n".join(line for line in csv_data.splitlines() if line.strip())
    reader = csv.DictReader(io.StringIO(csv_data))
    output = io.StringIO()
    output.write("!Type:Invst\n")

    # Simple check for missing columns
    if reader.fieldnames is None or not all(field in reader.fieldnames for field in _REQUIRED_FIELDS):
        raise ValueError(
            f"CSV is missing required fields. Expected fields: {_REQUIRED_FIELDS}. "
            f"Found: {reader.fieldnames}"
        )

    for row in reader:
        # skip rows that contain 1 or fewer populated fields (e.g., blank lines or stray single-column lines)
        non_empty_fields = sum(1 for v in row.values() if v is not None and str(v).strip())
        if non_empty_fields <= 1:
            continue
        # Simple example conversion logic
        row_date = parse_date(row['Run Date'])
        if start_date and row_date and row_date < start_date:
            continue  # skip transactions before start_date
        output.write("D" + row['Run Date'] + "\n")  # Date
        output.write("N" + parse_action(row['Action'], is_ofx=False) + "\n")  # Action
        output.write("Y" + security_name_for(row['Symbol']) + "\n")  # Symbol
        output.write("I" + row['Price ($)'] + "\n")  # Price
        output.write("Q" + row['Quantity'] + "\n")  # Quantity
        amount = parse_amount(row['Amount ($)'])
        if amount is not None:
            output.write("T" + str(amount) + "\n")  # Total Amount
        output.write("M" + row.get('Description', '') + "\n")  # Description
        output.write("O" + row.get('Fees ($)', '') + "\n")  # Fees
        output.write("^\n")  # End of transaction

    return output.getvalue()

def convert_csv_to_ofx(csv_data: str, account_id: str, start_date: Optional[datetime.date] = None) -> str:
    """Convert Fidelity CSV data to a simple OFX-like XML using ElementTree."""

    csv_data = "\n".join(line for line in csv_data.splitlines() if line.strip())
    reader = csv.DictReader(io.StringIO(csv_data))    

    root = ET.Element("OFX")
    invstmtmsgsrsv1 = ET.SubElement(root, "INVSTMTMSGSRSV1")
    invstmttrnrs = ET.SubElement(invstmtmsgsrsv1, "INVSTMTTRNRS")
    invstmtrs = ET.SubElement(invstmttrnrs, "INVSTMTRS")
    invacctfrom = ET.SubElement(invstmtrs, "INVACCTFROM")
    ET.SubElement(invacctfrom, "ACCTID").text = account_id
    invtranlist = ET.SubElement(invstmtrs, "INVTRANLIST")

    if reader.fieldnames is None or not all(field in reader.fieldnames for field in _REQUIRED_FIELDS):
        raise ValueError(
            f"CSV is missing required fields. Expected fields: {_REQUIRED_FIELDS}. "
            f"Found: {reader.fieldnames}"
        )
    
    for row in reader:
        non_empty_fields = sum(1 for v in row.values() if v is not None and str(v).strip())
        if non_empty_fields <= 1:
            continue
        row_date = parse_date(row['Run Date'])
        if start_date and row_date and row_date < start_date:
            continue
        action = parse_action(row['Action'], is_ofx=True)
        transaction = ET.SubElement(invtranlist, action)

        if action == "BUYSTOCK":
            transaction = ET.SubElement(transaction, "INVBUY")
        if action == "SELLSTOCK":
            transaction = ET.SubElement(transaction, "INVSELL")

        
        invtran = ET.SubElement(transaction, "INVTRAN")
        ET.SubElement(invtran, "FITID").text = f"T{get_row_id(row)}"
        ET.SubElement(invtran, "DTTRADE").text = row_date.strftime("%Y%m%d") if row_date else ""
        ET.SubElement(invtran, "MEMO").text = row.get('Description', '')

        invsecid = ET.SubElement(transaction, "SECID")
        ET.SubElement(invsecid, "UNIQUEID").text = row['Symbol']
        ET.SubElement(invsecid, "UNIQUEIDTYPE").text = "CUSIP"

        unit_price = row['Price ($)']
        amount = parse_amount(row['Amount ($)'])

        if amount is not None:
            ET.SubElement(transaction, "TOTAL").text = str(amount)

        if action in ("BUYSTOCK", "SELLSTOCK"):
            ET.SubElement(transaction, "UNITS").text = row['Quantity']
            ET.SubElement(transaction, "UNITPRICE").text = unit_price
        if action == "INCOME":
            ET.SubElement(transaction, "INCOMETYPE").text = "DIVIDEND"
    ET.indent(root, space="  ")
    return ET.tostring(root, encoding="unicode")

def find_input_file(input_csv_path: Optional[str]) -> Optional[str]:
    """Find the most recent Fidelity CSV file in the Downloads folder."""
    if input_csv_path:
        return input_csv_path
    download_folder = Path.home() / "Downloads"
    csv_files = list(download_folder.glob("History_for_Account_*.csv"))
    if not csv_files:
        return None
    latest_file = max(csv_files, key=os.path.getmtime)
    return str(latest_file)

def get_account_id(csv_path: str, input_account_id: Optional[str]) -> Optional[str]:
    """Determine account ID from CSV data if possible."""
    if input_account_id:
        return input_account_id
    filename = Path(csv_path).name
    # Matches 'History_for_Account_242530333.csv' or 'History_for_Account_242530333-2.csv'
    match = re.search(r'History_for_Account_(\d+)(?:-\d+)?\.csv', filename)
    account_id = match.group(1) if match else None
    return account_id

def get_ofx_path(csv_input_path: str, ofx_path: Optional[str]) -> Optional[str]:
    """Determine OFX output path based on OFX path."""
    if ofx_path is not None:
        return ofx_path
    base, _ = os.path.splitext(csv_input_path)
    ofx_path = f"{base}.ofx"
    counter = 1
    while os.path.exists(ofx_path):
        ofx_path = f"{base}_{counter}.ofx"
        counter += 1
    return ofx_path

def convert_csv_file_to_ofx_file(input_csv: str | None, input_ofx: str | None, input_account: str | None, input_start_date: str | None):
    csv_input_path = find_input_file(input_csv)
    if csv_input_path is None:
        print("No input CSV file found in Downloads folder and none provided via --csv", file=sys.stderr)
        return 1
    account_id = get_account_id(csv_input_path, input_account)
    if account_id is None:
        print("Could not determine account ID from CSV filename and none provided via --account", file=sys.stderr)
        return 1
    ofx_output_path = get_ofx_path(csv_input_path, input_ofx)
    if ofx_output_path is None:
        print(f"No output OFX file path could be determined from CSV path {csv_input_path}", file=sys.stderr)
        return 1
    print(f"CSV input: {csv_input_path}")
    print(f"OFX output: {ofx_output_path}")
    print(f"Account ID: {account_id}")
    start_date = parse_date(input_start_date)
    print(f"Start date filter: {start_date}")
    # Read CSV file from the path provided
    with open(csv_input_path, "r", encoding="utf-8-sig", newline="") as csvfile:
        csv_content = csvfile.read()
        ofx_output = convert_csv_to_ofx(csv_content, account_id=account_id, start_date=start_date)

        with open(ofx_output_path, "w") as f:
            f.write(ofx_output)

def main(argv: Optional[List[str]] = None) -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Convert Fidelity CSV transactions to a QIF file"
    )
    parser.add_argument("--csv", help="path to the Fidelity CSV file. If none provided, the last file in the Download folder will be used", required=False)
    parser.add_argument("--ofx", dest="ofx", help="path to the output OFX file to create", required=False)
    parser.add_argument(
        "--start-date",
        dest="start_date",
        help="transactions after this date will be ignored",
        required=False,
        type=str,
    )
    parser.add_argument(
        "--account",
        dest="account",
        help="account identifier in moneydance",
        required=False,
        type=str,
    )
    args = parser.parse_args(argv)
    convert_csv_file_to_ofx_file(
        input_csv=args.csv,
        input_ofx=args.ofx,
        input_account=args.account,
        input_start_date=args.start_date,
    )
    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

