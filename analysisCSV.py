import pandas as pd
from functions import get_unique_salon_names

csv_path = 'reviews.csv'

unique_salon_names = get_unique_salon_names(csv_path)
print(f"{unique_salon_names}, {len(unique_salon_names)}")

salon_data = pd.read_csv(csv_path)
print(salon_data.shape)

