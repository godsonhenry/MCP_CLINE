from typing import Any
from mcp.server.fastmcp import FastMCP
import pandas as pd
import numpy as np
from pathlib import Path
# Base directory where our data lives
DATA_DIR = "data"


# Initialize FastMCP server
mcp = FastMCP("bill_merchant_mcc", log_level="ERROR")

def read_in_csv(file_name:str)-> pd.DataFrame:
    """Read a CSV file from the data directory.
    
    Args:   
        file_mname: Name of the CSV file to read (e.g. "bills.csv")"""
    file_path = Path(DATA_DIR) / file_name
    if not file_path.exists():
        raise FileNotFoundError(f"File {file_name} not found in {DATA_DIR}")
    data = pd.read_csv(file_path)
    data["mcc_code"]=data['mcc_code'].astype(int).astype(str).str.zfill(4)
    return data

def find_bill(data: pd.DataFrame) -> str:
    """Find a bill in the MCC Lookup table in Data based on 'bill' column.
    
    args:
        data: DataFrame containing MCC lookup table.
    """
    bill_data=data[data.bill==1]
    bill_data['response']=bill_data['mcc_code'].astype(int).astype(str) + " : " + bill_data['description']
    response = f"Current Bill Related MCC Code has {bill_data.shape[0]} codes. The full list are : \n"
    response = response+ '\n'.join(bill_data['response'].tolist())
    return response

def find_merchant(data: pd.DataFrame) -> str:
    """Find a merchant in the MCC Lookup table in Data based on 'merchant' column.
    
    args:
        data: DataFrame containing MCC lookup table.
    """
    merchant_data=data[data.merchant==1]
    merchant_data['response']=merchant_data['mcc_code'].astype(int).astype(str) + " : " + merchant_data['description']
    response = f"Current Bill Related MCC Code has {merchant_data.shape[0]} codes. The full list are : \n"
    response = response+ '\n'.join(merchant_data['response'].tolist())
    return response

def find_mcc(data : pd.DataFrame, mcc: str) -> str:
    """Find mcc in the MCC Lookup table and confirm if it is a bill mcc or merchant mcc.
    
    args:
        data: DataFrame containing MCC lookup table.
        mcc: MCC code to search for.
    """
    mcc_data=data[data.mcc_code==mcc]
    mcc_data['response']=np.where((mcc_data['bill']==1)&(mcc_data['merchant']==1), f"{mcc} is categorized as Bill and Merchant",
                         np.where(mcc_data['bill']==1, f"{mcc} is categorized as Bill" ,
                         np.where(mcc_data['merchant']==1, f"{mcc} is categorized as Merchant", f"{mcc} is not categorized as Bill or Merchant")))

    return mcc_data['response'].values[0]
print(find_mcc(read_in_csv("mcc.csv"), "1771"))


@mcp.tool()
def get_bill_mcc(file_name: str) -> str:
    """Get all MCC codes related to bills.
    
    Args:
        file_name: Name of the CSV file containing MCC data (e.g. "mcc.csv")
    """

    return find_bill(read_in_csv(file_name))

@mcp.tool()
def get_merchant_mcc(file_name: str) -> str:
    """Get all MCC codes related to merchants.
    
    Args:   
        file_name: Name of the CSV file containing MCC data (e.g. "mcc.csv")
    """

    return find_merchant(read_in_csv(file_name))    

@mcp.tool()
def get_mcc_info(file_name: str, mcc: str) -> str:
    """Get information about a specific MCC code.

    Args:
        file_name: Name of the CSV file containing MCC data (e.g. "mcc.csv")
        mcc: MCC code to search for (e.g. "1771")
    """
    data = read_in_csv(file_name)
    return find_mcc(data, mcc)

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')