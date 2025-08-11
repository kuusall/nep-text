import pandas as pd
def add_to_df( headline, paragraph):
    """Add article data to DataFrame"""
    data={
        'शीर्षक': [],
        'विवरण': [],
    }
    df = pd.DataFrame(data)
    # title = clean_text(article.find('h2').get_text(strip=True))
    # content = clean_text(article.find('div', class_='content').get_text(strip=True))
    
    if headline and paragraph:
        df.loc[len(df)] = [headline, paragraph]
    
    return df  