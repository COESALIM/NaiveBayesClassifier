from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn import model_selection, preprocessing
from sklearn import datasets
from sklearn.model_selection import train_test_split

import psycopg2 as psql

import time
import datetime


import string

import pandas as pd

class products:
    def __init__(self, dbname, user, password, port):
        try:
            # Connect to database:
            conn = psql.connect(f"dbname ={dbname} user = {user} password = {password} port = {port}")
            cur = conn.cursor()
            print("completed connecting to Database")
        except:
            print("Error, connect to Database")
            exit()
        #exit()
        # Function to clean all data stored in data frame by make it lowercase
        def preprocess_data(data):
            data['sellables_descriptions'] = data['sellables_descriptions'].str.strip().str.lower()
            data['product_name'] = data['product_name'].str.strip().str.lower()
            return data

        def remove_punctuations(text):
            for punctuation in string.punctuation:
                text = text.replace(punctuation, '')
            return text

        # Function to clearn string from special character
        def clean_string(txt):
            txt = str(txt)
            txt = txt.replace(']', '')
            txt = txt.replace('[', '')
            txt = txt.replace("'", '')
            txt = txt.title()
            return txt
        # Fetch data from sellables table and products table to create train, test dataset
        # Without null values

        queryOne = '''
        Select sellables.description, products.name
        from sellables 
        full outer join products
        on sellables.product_id = products.id
        where 
        (sellables.product_id  is not null)
        and (products.id  is not null)
        and (sellables.description  is not null)
        and (products.name  is not null)
        ;
        '''

        try:
            sellables_products = cur.execute(queryOne)
            sellables_products = cur.fetchall()
            print("Completed fetch data from sellables & products tables")
        except:
            print("Error, fetch data from sellables & products tables")
            exit()

        # Put data in Dataframe formate
        df = pd.DataFrame.from_records(sellables_products, columns=['sellables_descriptions', 'product_name'])

        data = preprocess_data(df)

        # Set witch column want to X axis and y axis
        x = df['sellables_descriptions'].apply(remove_punctuations)
        y = df['product_name'].apply(remove_punctuations)

        # Split  data frame to train and test data set note: test tata set=20%  , train tata set=80%
        x, x_test, y, y_test = train_test_split(x, y, test_size=0.20, random_state=0)

        # Vectorize text reviews to numbers
        vec = CountVectorizer(stop_words='english')
        x = vec.fit_transform(x).toarray()
        x_test = vec.transform(x_test).toarray()

        # Train data
        model = MultinomialNB()
        model.fit(x, y)

        score = model.score(x_test, y_test)
        ScorePercentage = round((float(score) * 100), 2)
        print(f"score = {ScorePercentage}%")

        queryTwo = '''
        Select id, description from sellables 
        where (product_id is null)
        and (description is not null)
        ;
        '''

        sellables_list = cur.execute(queryTwo)
        sellables_list = cur.fetchall()

        for sku in sellables_list:
            sku_id = str(sku[0])
            sku_description = str(sku[1])
            desc = f'{sku_description}'
            print(f"corrent SKU:{sku_id}\nDescription:{sku_description}")

            product_name = model.predict(vec.transform([desc]))
            product_name = clean_string(product_name)

            fetch_product_id = f'''
            Select products.id, products.name from products
            where (name = '{product_name}')
            and (name is not null)
            and (id is not null)
            '''

            try:
                products_list = cur.execute(fetch_product_id)
                products_list = cur.fetchall()
                print("completed fetch data from Products table")

            except:
                print("Error fetch data from Prodcut table")
                exit()

            for products in products_list:
                products_id = str(products[0])
                products_name = str(products[1])
                print(f"product_name:{products_name}\nproduct_id:{products_id}")

                try:
                    curr_time = datetime.datetime.now()
                    curr_time = curr_time.strftime("%Y-%m-%d %H:%M:%S.%f")
                    UpdateData = f'''
                    UPDATE sellables SET product_id = '{products_id}', 
                    updated_at = '{curr_time}' WHERE id = '{sku_id}'; 
                    '''
                    cur.execute(UpdateData)
                    conn.commit()
                    print(f"completed update product_id for {sku_id} ")

                except:
                    print(f"Error, update product id for {sku_id}")

        cur.close()
        conn.close()