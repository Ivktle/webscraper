import pandas as pd

df_items = pd.read_csv('C:/Users/Oktyabrina/Desktop/project1/product.csv')
df_review = pd.read_csv('C:/Users/Oktyabrina/Desktop/project1/review.csv')

df_items.to_excel('product.xlsx',
                  sheet_name='Sheet1')
df_review.to_excel('review.xlsx',
                  sheet_name='Sheet1')


data_dict = {
    'Сегодня': '09.07.2025',
    'Вчера': '08.07.2025'
}
df_review['Дата отзыва'] = df_review['Дата отзыва']


print(df_review['Дата отзыва'].unique)