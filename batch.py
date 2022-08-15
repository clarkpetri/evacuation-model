from mesa.batchrunner import batch_run
from multiprocessing import freeze_support
import os
import model
from model import Evacuation
import pandas as pd
import numpy as np

params = {"width": 20, "height": 20, "seed": 1, "density": [.25,.50,.75], "hero_prob": np.arange(0, 0.51, 0.10), "malevolent": [0,1,2,3], "tipping_point": np.arange(0, 1.01, 0.2), "agi_gain": np.arange(0, 1.01, 0.2)}
# 2592 dimensions
if __name__ == '__main__':

    results = batch_run(Evacuation,parameters=params,iterations=5,max_steps=500,
                        number_processes=None,data_collection_period=1,display_progress=True,)

    df = pd.DataFrame(results)
    results_df = df.drop(['width', 'height', 'seed'], axis=1)

    # To export a csv of the results
    cwd = os.getcwd()
    path = cwd + "/filename.csv"
    results_df.to_csv(path)