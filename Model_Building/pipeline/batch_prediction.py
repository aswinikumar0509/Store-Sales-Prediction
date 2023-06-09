from Model_Building.exception import MartException
from Model_Building.logger import logging
from Model_Building.predictor import ModelResolver
import pandas as pd
import numpy as np
import os, sys
from Model_Building.utils import load_object
from datetime import datetime
PREDICTION_DIR = "prediction"

def start_batch_prediction(input_file_path):
    try:
        os.makedirs(PREDICTION_DIR,exist_ok=True)
        logging.info(f"Creating Model resolver config")
        model_resolver = ModelResolver(model_registry="saved_models")
        logging.info(f"Reading file : {input_file_path}")
        df = pd.read_csv(input_file_path)
        df.replace({"na":np.NAN},inplace = True)

        # validation

        logging.info(f"loading transformer to transform dataset")
        transformer = load_object(file_path=model_resolver.get_latest_save_transformer_path())

        input_feature_names = list(transformer.feature_names_in)
        input_arr = transformer.transform(df[input_feature_names])

        logging.info(f"Loading model for Prediction")
        model = load_object(file_path=model_resolver.get_latest_save_model_path())
        prediction = model.predict(input_arr)

        df["prediction"] = prediction

        prediction_file_name = os.path.basename(input_file_path).replace(".csv",f"{datetime.now().strftime('%m%d%Y__%H%M%S')}.csv")
        prediction_file_path = os.path.join(PREDICTION_DIR,prediction_file_name)
        df.to_csv(prediction_file_path,index = False , header=True)
        return prediction_file_path

    except Exception as e:
        raise MartException(e,sys)
