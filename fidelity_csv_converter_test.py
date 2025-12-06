import datetime 
import pytest
import qif_converter
from pathlib import Path
from unittest import mock
import time
import os

_TEST_CSV_DATA = """

Run Date,Action,Symbol,Description,Type,Price ($),Quantity,Commission ($),Fees ($),Accrued Interest ($),Amount ($),Cash Balance ($),Settlement Date
12/04/2025,"DIVIDEND RECEIVED ISHARES ULTRA SHORT-TERM BOND ACTIVE ETF (ICSH) (Cash)",ICSH,"ISHARES ULTRA SHORT-TERM BOND ACTIVE ETF",Cash,,0.000,,,,176.87,3976.60,
12/04/2025,"YOU BOUGHT INVESTMENT MANAGERS SER TR II TRADR ... (MQQQ) (Cash)",MQQQ,"INVESTMENT MANAGERS SER TR II TRADR 2X ",Cash,190.06,1,,,,-190.06,3799.73,12/05/2025
12/04/2025,"YOU SOLD FIDELITY CONTRAFUND (FCNTX) (Cash)",FCNTX,"FIDELITY CONTRAFUND",Cash,25,-155.6,,,,3890,3989.79,12/05/2025
12/03/2025,"YOU SOLD ISHARES ULTRA SHORT-TERM BOND ACTIVE ETF (ICSH) (Cash)",ICSH,"ISHARES ULTRA SHORT-TERM BOND ACTIVE ETF",Cash,50.6,-77,,,,3895.85,99.79,12/04/2025
12/03/2025,"YOU BOUGHT INVESTMENT MANAGERS SER TR II TRADR ... (MQQQ) (Cash)",MQQQ,"INVESTMENT MANAGERS SER TR II TRADR 2X ",Cash,189.9,20,,,,-3798,-3796.06,12/04/2025
12/02/2025,"YOU SOLD ISHARES ULTRA SHORT-TERM BOND ACTIVE ETF (ICSH) (Cash)",ICSH,"ISHARES ULTRA SHORT-TERM BOND ACTIVE ETF",Cash,50.58,-120,,,,6069,1.94,12/03/2025
12/02/2025,"YOU BOUGHT PROSPECTUS UNDER SEPARATE COVER FIDELITY CONTRAFUND (FCNTX) (Cash)",FCNTX,"FIDELITY CONTRAFUND",Cash,24.92,244.382,,,,-6090,-6067.06,12/03/2025
11/28/2025,"REINVESTMENT FIDELITY GOVERNMENT MONEY MARKET (SPAXX) (Cash)",SPAXX,"FIDELITY GOVERNMENT MONEY MARKET",Cash,1,21.45,,,,-21.45,22.94,
11/28/2025,"DIVIDEND RECEIVED FIDELITY GOVERNMENT MONEY MARKET (SPAXX) (Cash)",SPAXX,"FIDELITY GOVERNMENT MONEY MARKET",Cash,,0.000,,,,21.45,22.94,
11/26/2025,"YOU BOUGHT ISHARES ULTRA SHORT-TERM BOND ACTIVE ETF (ICSH) (Cash)",ICSH,"ISHARES ULTRA SHORT-TERM BOND ACTIVE ETF",Cash,50.72,985,,,,-49962.75,1.49,11/28/2025
11/26/2025,"YOU BOUGHT ISHARES ULTRA SHORT-TERM BOND ACTIVE ETF (ICSH) (Cash)",ICSH,"ISHARES ULTRA SHORT-TERM BOND ACTIVE ETF",Cash,50.72,1,,,,-50.72,49964.24,11/28/2025
11/24/2025,"YOU BOUGHT PROSPECTUS UNDER SEPARATE COVER CONF:035795544 AMERICAN NEW ECONOMY CLASS F1 (ANFFX) (Cash)",ANFFX,"AMERICAN NEW ECONOMY CLASS F1",Cash,76.59,765.113,,,,-58600,50014.96,11/25/2025
11/24/2025,"YOU SOLD CAPITAL GROUP GLOBAL GROWTH EQUITY S... (CGGO) (Cash)",CGGO,"CAPITAL GROUP GLOBAL GROWTH EQUITY SHAR",Cash,33.69,-1410,,,,47495.85,108614.96,11/25/2025
11/21/2025,"YOU SOLD ISHARES ULTRA SHORT-TERM BOND ACTIVE ETF (ICSH) (Cash)",ICSH,"ISHARES ULTRA SHORT-TERM BOND ACTIVE ETF",Cash,50.69,-1205,,,,61081.45,61119.11,11/24/2025
11/20/2025,"YOU SOLD ISHARES ULTRA SHORT-TERM BOND ACTIVE ETF (ICSH) (Cash)",ICSH,"ISHARES ULTRA SHORT-TERM BOND ACTIVE ETF",Cash,50.67,-927,,,,46966.46,37.66,11/21/2025
11/20/2025,"YOU BOUGHT CAPITAL GROUP GLOBAL GROWTH EQUITY S... (CGGO) (Cash)",CGGO,"CAPITAL GROUP GLOBAL GROWTH EQUITY SHAR",Cash,33.29,1410,,,,-46944.96,-46928.80,11/21/2025
11/17/2025,"YOU BOUGHT PROSPECTUS UNDER SEPARATE COVER CONF:035795468 AMERICAN NEW ECONOMY CLASS F1 (ANFFX) (Cash)",ANFFX,"AMERICAN NEW ECONOMY CLASS F1",Cash,76.69,5.868,,,,-450,16.16,11/18/2025
11/06/2025,"DIVIDEND RECEIVED ISHARES ULTRA SHORT-TERM BOND ACTIVE ETF (ICSH) (Cash)",ICSH,"ISHARES ULTRA SHORT-TERM BOND ACTIVE ETF",Cash,,0.000,,,,399,466.16,



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
    # Patch Path.home() inside qif_converter to return tmp_path so the lookup happens in our temp Downloads
    with mock.patch("qif_converter.Path.home", return_value=tmp_path):
        qif_converter.convert_csv_file_to_ofx_file(input_csv=None, input_ofx=None, input_account=None, input_start_date=None)
        assert output_ofx_path.exists()
        ofx_content = output_ofx_path.read_text()
        assert len(ofx_content) > 0

# def test_convert_csv_with_start_date():
#     start_date = datetime.date(2025, 12, 1)
#     actual_qif = qif_converter.convert_csv_to_qif(_TEST_CSV_DATA, start_date)
#     print("Generated QIF Data with Start Date:")
#     print(actual_qif)

def test_find_input_file_valid():
    # Test with a valid CSV path
    valid_path = "/path/to/valid_file.csv"
    # Mock the existence of the file for testing
    assert qif_converter.find_input_file(valid_path) == valid_path

def test_find_input_file_not_found(tmp_path: Path):
    # Create an empty Downloads folder under the temporary path
    downloads = tmp_path / "Downloads"
    downloads.mkdir()
    # Patch Path.home() inside qif_converter to return tmp_path so the lookup happens in our temp Downloads
    with mock.patch("qif_converter.Path.home", return_value=tmp_path):
        assert qif_converter.find_input_file(None) is None

def test_find_input_file(tmp_path: Path):
    # Create an empty Downloads folder under the temporary path
    downloads = tmp_path / "Downloads"
    downloads.mkdir()
    csv_file = downloads / "History_for_Account_242530333.csv"
    csv_file.write_text("dummy data")
    # Patch Path.home() inside qif_converter to return tmp_path so the lookup happens in our temp Downloads
    with mock.patch("qif_converter.Path.home", return_value=tmp_path):
        assert qif_converter.find_input_file(None) == str(csv_file)

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

    # Patch Path.home() inside qif_converter to return tmp_path so the lookup happens in our temp Downloads
    with mock.patch("qif_converter.Path.home", return_value=tmp_path):
        assert qif_converter.find_input_file(None) == str(csv_file_2)

def test_get_account_id():
    account_id = qif_converter.get_account_id("/path/to/History_for_Account_242530333.csv", None)
    assert account_id == "242530333"

def test_get_account_id_2():
    account_id = qif_converter.get_account_id("/path/to/History_for_Account_242530333-2.csv", None)
    assert account_id == "242530333"

def test_get_account_id_none():
    account_id = qif_converter.get_account_id("/path/to/blabla.csv", None)
    assert account_id is None

def test_get_ofx_path(tmp_path: Path):
    ofx_path = qif_converter.get_ofx_path(f"{tmp_path}/csv_file.csv", None)
    assert ofx_path == f"{tmp_path}/csv_file.ofx"

def test_get_ofx_path_1(tmp_path: Path):
    already_existing_ofx = tmp_path / "csv_file.ofx"
    already_existing_ofx.write_text("dummy data")
    ofx_path = qif_converter.get_ofx_path(f"{tmp_path}/csv_file.csv", None)
    assert ofx_path == f"{tmp_path}/csv_file_1.ofx"


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__]))