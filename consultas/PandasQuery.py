from DbConnection import DbConnection
import pandas as pd

class PandasQuery:
    def __init__(self, db_connection):
        self.db_connection = db_connection

    def query_to_dataframe(self, query, params=None):
        return self.db_connection.execute_query_df(query, params)
    
    def dataframe_to_excel(self, dataframe, path):
        try: 
            dataframe.to_excel(path, index=False)
            print(f"Dataframe exportado a {path}")
        except Exception as e:
            print(f"Error al exportar el dataframe: {e}")
    

if __name__ == "__main__":
    #db = DbConnection("localhost", "pubs", "root", "docker")
    db = DbConnection("localhost", "northwind", "root", "docker")
    db.connect()
    pandas_query = PandasQuery(db)

    orders_df = pandas_query.query_to_dataframe("SELECT * FROM Orders")
    order_details_df = pandas_query.query_to_dataframe("SELECT * FROM OrderDetails")
    customers_df = pandas_query.query_to_dataframe("SELECT * FROM Customers")
    products_df = pandas_query.query_to_dataframe("SELECT * FROM Products")
    categories_df = pandas_query.query_to_dataframe("SELECT * FROM Categories")

    orders_df['OrderDate'] = pd.to_datetime(orders_df['OrderDate'])
    recent_years = orders_df['OrderDate'].dt.year.unique()
    recent_years = sorted(recent_years, reverse=True)[:3]
    recent_orders_df = orders_df[orders_df['OrderDate'].dt.year.isin(recent_years)]

    product_earnings_df = recent_orders_df.merge(order_details_df, on="OrderID") \
        .merge(customers_df, on="CustomerID") \
        .merge(products_df, on="ProductID") \
        .merge(categories_df, on="CategoryID")

    product_earnings_df['CustomerEarnings'] = product_earnings_df['Quantity'] * product_earnings_df['UnitPrice_x']
    product_earnings_df['Years'] = product_earnings_df['OrderDate'].dt.year

    product_earnings_agg_df = product_earnings_df.groupby(
        ['CompanyName', 'Years', 'ProductID', 'ProductName', 'CategoryName']
    ).agg({'CustomerEarnings': 'sum'}).reset_index()

    product_rankings_df = recent_orders_df.merge(order_details_df, on="OrderID") \
        .merge(products_df, on="ProductID") \
        .merge(categories_df, on="CategoryID")

    product_rankings_df['Earnings'] = product_rankings_df['Quantity'] * product_rankings_df['UnitPrice_x']
    product_rankings_df['Years'] = product_rankings_df['OrderDate'].dt.year

    product_rankings_agg_df = product_rankings_df.groupby(
        ['Years', 'ProductID', 'ProductName', 'CategoryName']
    ).agg({'Earnings': 'sum'}).reset_index()

    product_rankings_agg_df['RankNum'] = product_rankings_agg_df.groupby(
        ['Years', 'CategoryName']
    )['Earnings'].rank(method='dense', ascending=False).astype(int)
    top_products_df = product_rankings_agg_df[product_rankings_agg_df['RankNum'] == 1]

    ranked_customers_df = top_products_df.merge(
        product_earnings_agg_df,
        on=['Years', 'ProductID', 'ProductName', 'CategoryName']
    )

    ranked_customers_df['RankDesc'] = ranked_customers_df.groupby(
        ['Years', 'ProductID', 'CategoryName']
    )['CustomerEarnings'].rank(method='dense', ascending=False).astype(int)
    ranked_customers_df['RankAsc'] = ranked_customers_df.groupby(
        ['Years', 'ProductID', 'CategoryName']
    )['CustomerEarnings'].rank(method='dense', ascending=True).astype(int)

    filtered_ranked_customers_df = ranked_customers_df[
        (ranked_customers_df['RankDesc'] == 1) | (ranked_customers_df['RankAsc'] == 1)
    ]

    filtered_ranked_customers_df['FormatCust'] = filtered_ranked_customers_df.apply(
        lambda row: f"{row['CompanyName']} - ${row['CustomerEarnings']}", axis=1
    )

    grouped_customers_df = filtered_ranked_customers_df.groupby(
        ['Years', 'ProductName', 'CategoryName', 'Earnings']
    ).agg({
        'FormatCust': lambda x: ' || '.join(sorted(x, key=lambda y: float(y.split(' - $')[1]), reverse=True))
    }).reset_index()

    grouped_customers_df['SortedFormatCust'] = grouped_customers_df.groupby(
        ['Years', 'ProductName', 'CategoryName']
    )['FormatCust'].transform(lambda x: ' || '.join(x[:2] + x[-2:] if len(x) >= 4 else x))

    grouped_customers_df['Product'] = grouped_customers_df.apply(
        lambda row: f"{row['ProductName']} // {row['SortedFormatCust']}", axis=1
    )

    pivot_df = grouped_customers_df.pivot_table(
        index='CategoryName',
        columns='Years',
        values='Product',
        aggfunc=lambda x: ' || '.join(x[:3]) if len(x) >= 3 else ' || '.join(x)
    ).reset_index()

    pivot_df.columns.name = None
    pivot_df.sort_values(by='CategoryName', inplace=True)
    pivot_df.columns = ['Categoría', recent_years[2], recent_years[1], recent_years[0]]
    print(pivot_df)
    pandas_query.dataframe_to_excel(pivot_df, "exam_query.xlsx")


    # Primera query
    '''sales_query = "SELECT * FROM sales"
    titles_query = "SELECT * FROM titles"
    titleauthor_query = "SELECT * FROM titleauthor"

    sales_df = pandas_query.query_to_dataframe(sales_query)
    titles_df = pandas_query.query_to_dataframe(titles_query)
    titleauthor_df = pandas_query.query_to_dataframe(titleauthor_query)

    merged_df = sales_df.merge(titles_df, on="title_id", how="inner").merge(titleauthor_df, on="title_id", how="inner")
    merged_df["earnings"] = merged_df["price"] * merged_df["qty"] * merged_df["royaltyper"] / 100.0
    earnings = merged_df.groupby("au_id")["earnings"].sum().reset_index()

    royalties_df = titles_df.merge(titleauthor_df, on="title_id", how="left").groupby(["title_id", "price"], as_index=False).agg({"royaltyper": "sum"})
    royalties_df["royaltiess"] = 100 - royalties_df["royaltyper"].fillna(0)
    royalties_df = royalties_df[royalties_df["royaltiess"] > 0]

    anonymous_df = sales_df.merge(royalties_df, on="title_id", how="inner")
    anonymous_df["earnings"] = anonymous_df["royaltiess"] * anonymous_df["price"] * anonymous_df["qty"] / 100.0
    anonymous_earnings = pd.DataFrame({"au_id": ["anonymous"], "earnings": [anonymous_df["earnings"].sum()]})

    result = pd.concat([earnings, anonymous_earnings], ignore_index=True)'''

    # Segunda query
    '''orders_query = "SELECT * FROM Orders"
    order_details_query = "SELECT * FROM OrderDetails"
    employee_territories_query = "SELECT * FROM EmployeeTerritories"
    territories_query = "SELECT * FROM Territories"
    region_query = "SELECT * FROM Region"
    customers_query = "SELECT * FROM Customers"

    orders_df = pandas_query.query_to_dataframe(orders_query)
    order_details_df = pandas_query.query_to_dataframe(order_details_query)
    employee_territories_df = pandas_query.query_to_dataframe(employee_territories_query)
    territories_df = pandas_query.query_to_dataframe(territories_query)
    region_df = pandas_query.query_to_dataframe(region_query)
    customers_df = pandas_query.query_to_dataframe(customers_query)

    orders_df['OrderDate'] = pd.to_datetime(orders_df['OrderDate'])

    subquery_df = orders_df.merge(employee_territories_df, on="EmployeeID", how="inner")
    subquery_df = subquery_df.merge(territories_df, on="TerritoryID", how="inner")
    subquery_df = subquery_df[['OrderID', 'RegionID']].drop_duplicates()

    merged_df = order_details_df.merge(orders_df, on="OrderID", how="inner")
    merged_df = merged_df.merge(subquery_df, on="OrderID", how="inner")
    merged_df = merged_df.merge(region_df, on="RegionID", how="inner")
    merged_df = merged_df.merge(customers_df, on="CustomerID", how="inner")

    merged_df['Cantidad'] = merged_df['Quantity'] * merged_df['UnitPrice']
    merged_df['Año'] = merged_df['OrderDate'].dt.year
    
    grouped_df = merged_df.groupby(['Año', 'RegionDescription', 'CompanyName', 'ContactName'])['Cantidad'].sum().reset_index()
    grouped_df['RankNum'] = grouped_df.groupby(['Año', 'RegionDescription'])['Cantidad'].rank(ascending=False, method='dense').astype(int)

    filtered_df = grouped_df[grouped_df['RankNum'] == 1]
    filtered_df['CustomerInfo'] = filtered_df.apply(lambda x: f"{x['CompanyName']}, {x['ContactName']}, {x['Cantidad']}", axis=1)
    agg_df = filtered_df.groupby(['Año', 'RegionDescription'])['CustomerInfo'].apply(lambda x: '; '.join(x)).reset_index()

    pivot_df = agg_df.pivot(index='Año', columns='RegionDescription', values='CustomerInfo').reset_index()
    pivot_df.columns.name = None'''

    # Tercera query
    ''' orders_query = "SELECT * FROM Orders"
    order_details_query = "SELECT * FROM OrderDetails"
    employee_territories_query = "SELECT * FROM EmployeeTerritories"
    territories_query = "SELECT * FROM Territories"
    region_query = "SELECT * FROM Region"

    orders_df = pandas_query.query_to_dataframe(orders_query)
    order_details_df = pandas_query.query_to_dataframe(order_details_query)
    employee_territories_df = pandas_query.query_to_dataframe(employee_territories_query)
    territories_df = pandas_query.query_to_dataframe(territories_query)
    region_df = pandas_query.query_to_dataframe(region_query)

    subquery_df = orders_df.merge(employee_territories_df, on="EmployeeID", how="inner")
    subquery_df = subquery_df.merge(territories_df, on="TerritoryID", how="inner")
    subquery_df = subquery_df[['OrderID', 'RegionID']].drop_duplicates()

    merged_df = order_details_df.merge(orders_df, on="OrderID", how="inner")
    merged_df = merged_df.merge(subquery_df, on="OrderID", how="inner")
    merged_df = merged_df.merge(region_df, on="RegionID", how="inner")

    merged_df['Ventas'] = merged_df['Quantity'] * merged_df['UnitPrice']
    grouped_df = merged_df.groupby(['RegionDescription'])['Ventas'].sum().reset_index()'''                                          

