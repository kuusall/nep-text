import os
import pandas as pd
from datetime import date

def save_to_csv(df, directory, file_name):
    
    if not isinstance(df, pd.DataFrame):
        raise ValueError("Input must be a pandas DataFrame")
    
    if not file_name:
        file_name=date.today().strftime("%Y-%m-%d") + ".csv"
    else:
        file_name= file_name+ ".csv"
        
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError as e:
        print(f"Error creating directory {directory}: {e}")
        return
    file_path = f'{directory}/{file_name}'
    if os.path.exists(file_path):
        df.to_csv(file_path, mode='a', index=False, header=False)
    else:
        df.to_csv(file_path, index=False)
        
    # return df