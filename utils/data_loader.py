import pandas as pd
import numpy as np

def load_data(file_path, config):
    df = pd.read_csv(file_path)
    df = df.dropna(subset=["hash"]).reset_index()
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")
    
    values = ["afd", "spd", "gruene", "linke", "cdu", "fdp", "linke", "unknown"]
    df["party"] = np.random.choice (values, size=len(df))
    
    party_color_map = {
        "afd":      config["party_color_map"]["afd"],     # Light Blue
        "spd":      config["party_color_map"]["spd"],     # Light Red
        "gruene":    config["party_color_map"]["gruene"],   # Light Green
        "linke":    config["party_color_map"]["linke"],   # Thistle (Light Purple)
        "cdu":      config["party_color_map"]["cdu"],     # Gray (Light Black)
        "fdp":      config["party_color_map"]["fdp"],     # Light Yellow
        "unknown":  config["party_color_map"]["unknown"]  # Light Gray
    }
    df['color'] = df['party'].map(party_color_map)
    return df