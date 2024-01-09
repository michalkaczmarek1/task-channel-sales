import pandas as pd
import datetime as dt
import os
from datetime import datetime, date
from dateutil import relativedelta

class db:
    def __init__(self):
        self.transactions = db.transation_init()
        self.cc = pd.read_csv(r'db/country_codes.csv', index_col=0)
        self.customers = pd.read_csv(r'db/customers.csv', index_col=0)
        self.cat_prod_info = pd.read_csv(r'db/prod_cat_info.csv')

    @staticmethod
    def transation_init():
        transactions = pd.DataFrame()
        src = r'db/transactions'
        for filename in os.listdir(src):
            transactions = pd.concat(
                [pd.read_csv(os.path.join(src, filename), index_col=0)])

        def convert_dates(x):
            try:
                return dt.datetime.strptime(x, '%d-%m-%Y')
            except:
                return dt.datetime.strptime(x, '%d/%m/%Y')

        transactions['tran_date'] = transactions['tran_date'].apply(
            lambda x: convert_dates(x))

        return transactions

    def merge(self):
        df = self.transactions.join(self.cat_prod_info.drop_duplicates(subset=['prod_cat_code'])
                                    .set_index('prod_cat_code')['prod_cat'], on='prod_cat_code', how='left')

        df = df.join(self.cat_prod_info.drop_duplicates(subset=['prod_sub_cat_code'])
                     .set_index('prod_sub_cat_code')['prod_subcat'], on='prod_subcat_code', how='left')

        df = df.join(self.customers.join(
            self.cc, on='country_code').set_index('customer_Id'), on='cust_id')

        df['DOB'].dropna(inplace=True)
        df['age'] = df.apply(lambda row: self.calculate_age(row), axis=1)

        self.merged = df

    def calculate_age(self, row):
        str_d1 = row['DOB']
        str_d2 = datetime.strftime(date.today(), "%d-%m-%Y")

        d1 = datetime.strptime(str_d1, "%d-%m-%Y")
        d2 = datetime.strptime(str_d2, "%d-%m-%Y")

        delta = relativedelta.relativedelta(d2, d1)
        return delta.years

