data_dict = {
        "clients": {
            "column_mapping": {
                "Client_ID": "ID",
                "Client_Category": "Person_Org",
                "Client_Type": "Type",
                "Product_Mix": "Product_Mix",
                "Name": "Name" ,
                "First_Name": "First_Name", 
                "Last_Name": "Last_Name", 
                "NAICS_CD": "NAICS_CD", 
                "SSN": "SSN", 
                "Employer": "Employer", 
                "Title": "Title", 
                "Street_Address": "Address",
                "Region": "Region", 
                "Birthday": "Birthday", 
                "Start_Date": "Start_Dt", 
                "End_Date": "End_Dt", 
                "Is_Current": "Is_Current",
                "Wealth_Tier": "Wealth_Tier", 
                "Household_ID": "HH_ID"
            },
            "primary_key" : "ID",
            "foreign_keys": [
                {"column": "HH_ID", "references_table": "links", "references_column": "Household_ID"},
            ]
        },
        # add ID as primary key to the accounts table
        # remove client_type, wealth_tier from accounts table
        # primary_banker is at client level
        "accounts": {
            "column_mapping": {
                "ID": "ID",
                "Client_ID": "Client_ID",
                "Account_Category": "Product_Group",
                "Account_Nr": "Acct_Nbr",
                "Account_Type": "Product_Type",
                "Init_Balance": "Balance",
                "Banker_ID": "Banker_ID",
                "Primary_Banker": "Primary_Banker",
                "Open_Date": "Start_Dt",
                "Close_Date": "End_Dt",
                "Is_Current": "Is_Current",
                "Status": "Status"
            },
            "primary_key" : "ID",
            "foreign_keys": [
                {"column": "Client_ID", "references_table": "clients", "references_column": "ID"},
                {"column": "Banker_ID", "references_table": "bankers", "references_column": "ID"},
            ]
        },
        "bankers": {
            "column_mapping": {
                "Banker_ID": "ID",
                "Login": "Login",
                "Banker_Name": "Name",
                "Banker_Type" : "Type",
                "Branch_Number": "Branch_Nbr",
                "Region" : "Region",
            },
            "primary_key" : "ID",
            "foreign_keys": [
                {"column": "Branch_Nbr", "references_table": "branches", "references_column": "Branch_Number"},
            ]
        }, 
        "links": {
            "column_mapping": {
                "Link_ID": "ID",
                "Household_ID": "Household_ID",
                "Client_1": "Client_1",
                "Client_2" : "Client_2",
                "Link_Type": "Link_Type",
            },
            "primary_key" : "ID",
            "foreign_keys": [
                {"column": "Household_ID", "references_table": "clients", "references_column": "HH_ID"},
            ]
        }, 
    }