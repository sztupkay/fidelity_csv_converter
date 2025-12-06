import datetime 
import pytest
import fidelity_csv_converter
from pathlib import Path
from unittest import mock
import time
import os

_TEST_CSV_DATA = """

Run Date,Action,Symbol,Description,Type,Price ($),Quantity,Commission ($),Fees ($),Accrued Interest ($),Amount ($),Cash Balance ($),Settlement Date
11/28/2025,"REINVESTMENT FIDELITY GOVERNMENT MONEY MARKET (SPAXX) (Cash)",SPAXX,"FIDELITY GOVERNMENT MONEY MARKET",Cash,1,21.45,,,,-21.45,22.94,
11/28/2025,"DIVIDEND RECEIVED FIDELITY GOVERNMENT MONEY MARKET (SPAXX) (Cash)",SPAXX,"FIDELITY GOVERNMENT MONEY MARKET",Cash,,0.000,,,,21.45,22.94,
11/26/2025,"YOU BOUGHT ISHARES ULTRA SHORT-TERM BOND ACTIVE ETF (ICSH) (Cash)",ICSH,"ISHARES ULTRA SHORT-TERM BOND ACTIVE ETF",Cash,50.72,985,,,,-49962.75,1.49,11/28/2025
11/26/2025,"YOU BOUGHT ISHARES ULTRA SHORT-TERM BOND ACTIVE ETF (ICSH) (Cash)",ICSH,"ISHARES ULTRA SHORT-TERM BOND ACTIVE ETF",Cash,50.72,1,,,,-50.72,49964.24,11/28/2025



"The data and information in this spreadsheet is provided to you solely for your use and is not for distribution. The spreadsheet is provided for"
"informational purposes only, and is not intended to provide advice, nor should it be construed as an offer to sell, a solicitation of an offer to buy or a"
"recommendation for any security or insurance product by Fidelity or any third party. Data and information shown is based on information known to Fidelity as of the date it was"
"exported and is subject to change. It should not be used in place of your account statements or trade confirmations and is not intended for tax reporting"
"purposes. For more information on the data included in this spreadsheet, including any limitations thereof, go to Fidelity.com."

"Brokerage services are provided by Fidelity Brokerage Services LLC (FBS), 900 Salem Street, Smithfield, RI 02917. Custody and other services provided by National"
"Financial Services LLC (NFS). Both are Fidelity Investment companies and members SIPC, NYSE. Insurance products at Fidelity are distributed by"
"Fidelity Insurance Agency, Inc., and, for certain products, by Fidelity Brokerage Services, Member NYSE, SIPC."

Date downloaded 12/04/2025 9:12 pm"""

def test_convert_csv_file_to_ofx_file(tmp_path: Path):
    downloads = tmp_path / "Downloads"
    downloads.mkdir()
    input_csv_path = downloads / "History_for_Account_242530333.csv"
    output_ofx_path = downloads / "History_for_Account_242530333.ofx"
    input_csv_path.write_text(_TEST_CSV_DATA)
    # Patch Path.home() inside fidelity_csv_converter to return tmp_path so the lookup happens in our temp Downloads
    with mock.patch("fidelity_csv_converter.Path.home", return_value=tmp_path):
        fidelity_csv_converter.convert_csv_file_to_ofx_file(input_csv=None, input_ofx=None, input_account=None, input_start_date=None)
        assert output_ofx_path.exists()
        ofx_content = output_ofx_path.read_text()
        assert len(ofx_content) > 0

# def test_convert_csv_with_start_date():
#     start_date = datetime.date(2025, 12, 1)
#     actual_qif = fidelity_csv_converter.convert_csv_to_qif(_TEST_CSV_DATA, start_date)
#     print("Generated QIF Data with Start Date:")
#     print(actual_qif)

def test_find_input_file_valid():
    # Test with a valid CSV path
    valid_path = "/path/to/valid_file.csv"
    # Mock the existence of the file for testing
    assert fidelity_csv_converter.find_input_file(valid_path) == valid_path

def test_find_input_file_not_found(tmp_path: Path):
    # Create an empty Downloads folder under the temporary path
    downloads = tmp_path / "Downloads"
    downloads.mkdir()
    # Patch Path.home() inside fidelity_csv_converter to return tmp_path so the lookup happens in our temp Downloads
    with mock.patch("fidelity_csv_converter.Path.home", return_value=tmp_path):
        assert fidelity_csv_converter.find_input_file(None) is None

def test_find_input_file(tmp_path: Path):
    # Create an empty Downloads folder under the temporary path
    downloads = tmp_path / "Downloads"
    downloads.mkdir()
    csv_file = downloads / "History_for_Account_242530333.csv"
    csv_file.write_text("dummy data")
    # Patch Path.home() inside fidelity_csv_converter to return tmp_path so the lookup happens in our temp Downloads
    with mock.patch("fidelity_csv_converter.Path.home", return_value=tmp_path):
        assert fidelity_csv_converter.find_input_file(None) == str(csv_file)

def test_find_input_file_2(tmp_path: Path):
    # Create an empty Downloads folder under the temporary path
    downloads = tmp_path / "Downloads"
    downloads.mkdir()
    csv_file_1 = downloads / "History_for_Account_242530333.csv"
    csv_file_1.write_text("dummy data")
    # Set the modified and created time to one hour ago
    one_hour_ago = time.time() - 3600
    os.utime(csv_file_1, (one_hour_ago, one_hour_ago))
    csv_file_2 = downloads / "History_for_Account_242530333-2.csv"
    csv_file_2.write_text("dummy data")

    # Patch Path.home() inside fidelity_csv_converter to return tmp_path so the lookup happens in our temp Downloads
    with mock.patch("fidelity_csv_converter.Path.home", return_value=tmp_path):
        assert fidelity_csv_converter.find_input_file(None) == str(csv_file_2)

def test_get_account_id():
    account_id = fidelity_csv_converter.get_account_id("/path/to/History_for_Account_242530333.csv", None)
    assert account_id == "242530333"

def test_get_account_id_2():
    account_id = fidelity_csv_converter.get_account_id("/path/to/History_for_Account_242530333-2.csv", None)
    assert account_id == "242530333"

def test_get_account_id_none():
    account_id = fidelity_csv_converter.get_account_id("/path/to/blabla.csv", None)
    assert account_id is None

def test_get_ofx_path(tmp_path: Path):
    ofx_path = fidelity_csv_converter.get_ofx_path(f"{tmp_path}/csv_file.csv", None)
    assert ofx_path == f"{tmp_path}/csv_file.ofx"

def test_get_ofx_path_1(tmp_path: Path):
    already_existing_ofx = tmp_path / "csv_file.ofx"
    already_existing_ofx.write_text("dummy data")
    ofx_path = fidelity_csv_converter.get_ofx_path(f"{tmp_path}/csv_file.csv", None)
    assert ofx_path == f"{tmp_path}/csv_file_1.ofx"


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__]))