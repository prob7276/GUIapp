import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime


# Create tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Search Assets", "Input Assets", "Remove Assets", "Reports", "CLEAR ENTIRE INVENTORY"])

# Function to search assets in the database
def search_assets(asset_list):
    placeholders = ', '.join('?' for _ in asset_list)
    query = f'''
    SELECT Inventory.Asset_Tag_Inventory, Inventory.Cart_Number, Inventory.Shelf_Number, Inventory.Last_Scan,
           CMDB_Data.Agency, CMDB_Data.Computer_Model, CMDB_Data.CMDB_Status
    FROM Inventory
    LEFT JOIN CMDB_Data ON Inventory.Asset_Tag_Inventory = CMDB_Data.Asset_Tag_CMDB
    WHERE Inventory.Asset_Tag_Inventory IN ({placeholders})
    '''
    conn = sqlite3.connect('Desktop/inventory.db')
    c = conn.cursor()
    c.execute(query, asset_list)
    results = c.fetchall()
    conn.close()
    
    # Convert results to a DataFrame
    df = pd.DataFrame(results, columns=['Asset Tag', 'Cart Number', 'Shelf Number', 'Last Scan', 'Agency', 'Computer Model', 'CMDB Status'])
    return df

# Streamlit app
with tab1:
    st.title("Search Assets")
    # Create a text area for input
    input_asset = st.text_area("Enter Asset Tags to Search (separated by new line)")

    # Process the input values
    if input_asset:
        asset_list = [value.strip() for value in input_asset.splitlines()]
        st.write("You entered the following Assets to search:")
        st.write(asset_list)

        # Search data in the database
        if st.button('Search Assets in Database'):
            results_df = search_assets(asset_list)
            if not results_df.empty:
                st.write("Search Results:")
                # Display results as a table with custom column headers
                st.table(results_df)
            else:
                st.write("No matching assets found.")



with tab2:
    # Title of the app
    st.title("Input Assets")

    # Input cart number
    Cart_Number = st.text_input("Enter Cart #")

    # Input shelf number
    Shelf_Number = st.text_input("Enter Shelf #")

    # Create a text area for input
    input_asset = st.text_area("Enter Asset Tags (separated by new line)")

    # Process the input values
    if input_asset:
        asset_list = [value.strip() for value in input_asset.splitlines()]
        st.write("You entered the following Assets:")
        st.write(asset_list)

    # Input time stamp
    Last_Scan = st.date_input("Day", value=datetime.today().date())

    # Insert values into the database
    if st.button('Add Assets to Database'):
        # Connect to database
        conn = sqlite3.connect('Desktop/inventory.db')
        c = conn.cursor()

        # To track already existing assets
        existing_assets = []

        for asset in asset_list:
            # Check if asset already exists in the database
            c.execute('SELECT COUNT(*) FROM Inventory WHERE Asset_Tag_Inventory = ?', (asset,))
            if c.fetchone()[0] > 0:
                existing_assets.append(asset)
            else:
                # Insert only if the asset does not exist
                c.execute('''
                INSERT INTO Inventory (Asset_Tag_Inventory, Cart_Number, Shelf_Number, Last_Scan)
                VALUES (?, ?, ?, ?)
                ''', (asset, Cart_Number, Shelf_Number, Last_Scan))

        # Commit the transaction
        conn.commit()

        # Provide feedback
        if existing_assets:
            st.warning(f'The following assets already exist and were not added: {existing_assets}')
        else:
            st.success('All assets added to database!')

        # Close the database connection
        conn.close()

    

    st.title("Clear Cart and/or Shelf")
    # Connect to database
    conn = sqlite3.connect('desktop\inventory.db')
    c = conn.cursor()

    # Input fields for cart number and shelf number
    cart_number = st.text_input("Enter Cart Number to Clear")
    shelf_number = st.text_input("Enter Shelf Number to Clear")

    # Button to clear records
    if st.button('Clear Specific Records'):
        if cart_number and shelf_number:
            c.execute('DELETE FROM Inventory WHERE Cart_Number = ? AND Shelf_Number = ?', (cart_number, shelf_number))
        elif cart_number:
            c.execute('DELETE FROM Inventory WHERE Cart_Number = ?', (cart_number,))
        else:
            st.warning('Please enter at least one criterion to clear records.')
    
        conn.commit()
        st.success('Specified records cleared from the Inventory table!')

    # Close the database connection
    conn.close()


with tab3:
    st.title("Remove Assets")
    # Create a text area for input
    input_asset = st.text_area("Enter Asset Tags to Remove (separated by new line)")

    # Process the input values
    if input_asset:
        asset_list = [value.strip() for value in input_asset.splitlines()]
        st.write("You entered the following Assets to remove:")
        st.write(asset_list)

    # Connect to database
    conn = sqlite3.connect('desktop\inventory.db')
    c = conn.cursor()

    # Create table if it doesn't exist (for demonstration purposes)
    c.execute('''
    CREATE TABLE IF NOT EXISTS Inventory (
        Asset_Tag_Inventory VARCHAR(50) PRIMARY KEY,
        Cart_Number VARCHAR(50),
        Shelf_Number VARCHAR(50),
        Last_Scan TIMESTAMP
    )
    ''')

    # Remove data from the database
    if st.button('Remove Assets from Database'):
        for asset in asset_list:
            c.execute('''
            DELETE FROM Inventory WHERE Asset_Tag_Inventory = ?
            ''', (asset,))
    
        conn.commit()
        st.success('Assets removed from database!')

    # Close the database connection
    conn.close()


with tab4:
    st.title("Reports")

    # Connect to database
    conn = sqlite3.connect('desktop/inventory.db')
    c = conn.cursor()

    # Button to display the entire Inventory table sorted by Cart_Number and Shelf_Number
    if st.button('Show Entire Inventory Table'):
        query = '''
        SELECT Inventory.Asset_Tag_Inventory, Inventory.Cart_Number, Inventory.Shelf_Number, Inventory.Last_Scan,
               CMDB_Data.Agency, CMDB_Data.Computer_Model, CMDB_Data.CMDB_Status
        FROM Inventory
        LEFT JOIN CMDB_Data ON Inventory.Asset_Tag_Inventory = CMDB_Data.Asset_Tag_CMDB
        ORDER BY Inventory.Cart_Number, Inventory.Shelf_Number
        '''
        c.execute(query)
        data = c.fetchall()
        df = pd.DataFrame(data, columns=['Asset_Tag_Inventory', 'Cart_Number', 'Shelf_Number', 'Last_Scan', 'Agency', 'Computer_Model', 'CMDB_Status'])
        st.dataframe(df)

    # Close the database connection
    conn.close()
    
    # Connect to database
    conn = sqlite3.connect('desktop/inventory.db')
    c = conn.cursor()

    # Input fields for cart number and shelf number
    cart_number = st.text_input("Enter Cart Number to Search")
    shelf_number = st.text_input("Enter Shelf Number to Search")

    # Button to search records
    if st.button('Search Inventory'):
        query = '''
        SELECT Inventory.Asset_Tag_Inventory, Inventory.Cart_Number, Inventory.Shelf_Number, Inventory.Last_Scan,
               CMDB_Data.Agency, CMDB_Data.Computer_Model, CMDB_Data.CMDB_Status
        FROM Inventory
        LEFT JOIN CMDB_Data ON Inventory.Asset_Tag_Inventory = CMDB_Data.Asset_Tag_CMDB
        WHERE 1=1
        '''
        params = []
    
        if cart_number:
            query += ' AND Inventory.Cart_Number = ?'
            params.append(cart_number)
    
        if shelf_number:
            query += ' AND Inventory.Shelf_Number = ?'
            params.append(shelf_number)
    
        c.execute(query, params)
        data = c.fetchall()
    
        if data:
            df = pd.DataFrame(data, columns=['Asset_Tag_Inventory', 'Cart_Number', 'Shelf_Number', 'Last_Scan', 'Agency', 'Computer_Model', 'CMDB_Status'])
            st.dataframe(df)
        else:
            st.write("No matching records found.")

    # Close the database connection
    conn.close()


with tab5:
    # Connect to database
    conn = sqlite3.connect('desktop\inventory.db')
    c = conn.cursor()

    if st.button('CLEAR ENTIRE INVENTORY'):
        c.execute('DELETE FROM Inventory')
        conn.commit()
        st.success('Inventory cleared!')

    # Close the database connection
    conn.close()