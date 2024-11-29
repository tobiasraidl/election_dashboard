import pandas as pd


### BASE CSV ###

def create_base_dataframe(file_path):
    df = pd.read_csv(file_path)
    df = df.dropna(subset=["hash"]).reset_index(drop=True)
    
    # Drop rows where the image only appears once in the entire dataset
    hash_counts = df['hash'].value_counts()
    df = df[df['hash'].isin(hash_counts[hash_counts > 1].index)]
    
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")

    party_mapping = {
        'DIE LINKE': 'die_linke',
        'FDP': 'fdp',
        'DIE GRÜNEN': 'die_gruenen',
        'SPD': 'spd',
        'AFD': 'afd',
        'CDU/CSU': 'cdu_csu'
    }
    df['party'] = df['party'].map(party_mapping)
    df['party'] = df['party'].fillna('unknown')
    
    platform_mapping = {
        'fb': 'Facebook',
        'ig': 'Instagram',
        'tw': 'Twitter'
    }

    df['platform'] = df['platform'].map(platform_mapping)
    
    df = df[df["hash"] != "0000000000000000"]
    
    # Filter out accounts that have not shared at least one same image as another account
    hash_counts = df.groupby('hash')['user_id'].nunique()
    valid_hashes = hash_counts[hash_counts >= 2].index
    filtered_df = df[df['hash'].isin(valid_hashes)]
    
    return df

df = create_base_dataframe('../data/original_posts.csv')
df.to_csv('../data/base_posts.csv', index=False)


### PARTIES AVAILABLE CSV ###

def df_with_parties(file_path):
    df = pd.read_csv(file_path)
    df = df[df['party'] != 'unknown']
    df = df.reset_index(drop=True)
    return df

df = df_with_parties('../data/base_posts.csv')
df.to_csv('../data/posts_with_party.csv', index=False)


### CROSS PLATOFRM CSV ###

def df_for_cross_platform_images(file_path):
    df = pd.read_csv(file_path)
    hash_platform_counts = df.groupby('hash')['platform'].nunique()
    valid_hashes = hash_platform_counts[hash_platform_counts > 1].index
    df = df[df['hash'].isin(valid_hashes)]
    return df
    
df = df_for_cross_platform_images('../data/base_posts.csv')
df.to_csv('../data/cross_platform_posts.csv', index=False)
print(df.shape[0])
df.head()