import polars as pl
from lightgbm import LGBMClassifier
from sklearn.metrics import accuracy_score


class LGBMClassifierPipeline:
    # class level constants
    PREDICTORS = [
        "Backward_Volatility",
        "Sentiment_lag_1",
        "Sentiment_lag_2",
        "Sentiment_lag_3",
        "Sentiment_lag_4",
        "Sentiment_lag_5",
        "Response_lag_1",
        "Response_lag_2",
        "Response_lag_3",
        "Response_lag_4",
        "Response_lag_5",
        "Sum_of_lagged_response",
    ]
    RESPONSE = "Response"

    def __init__(self, df: pl.DataFrame):
        self.df = df.drop_nulls().with_columns(
            pl.col("Date").str.to_datetime().dt.date()
        )
        self.model = LGBMClassifier()

    def train_validation_split(self, df: pl.DataFrame):
        train = df.filter(pl.col("Date") < pl.date(2022, 8, 1))
        val = df.filter(pl.col("Date") >= pl.date(2022, 8, 1))
        return train, val

    def select_predictors_response(self, train, val):
        X_train = train.select(self.PREDICTORS)
        y_train = train.select(self.RESPONSE)
        X_val = val.select(self.PREDICTORS)
        y_val = val.select(self.RESPONSE)

        return X_train, y_train, X_val, y_val

    def fit_model(self, X_train, y_train):
        self.model.fit(X_train.to_numpy(), y_train.to_numpy().flatten())

    def evaluate_model(self, X_val, y_val):
        y_pred = self.model.predict(X_val)
        accuracy = accuracy_score(y_val, y_pred)
        return accuracy

    def run(self):
        df = self.df.clone()
        train, val = self.train_validation_split(df)
        X_train, y_train, X_val, y_val = self.select_predictors_response(train, val)
        self.fit_model(X_train, y_train)
        accuracy = self.evaluate_model(X_val, y_val)
        print(f"Accuracy: {accuracy}")


if __name__ == "__main__":
    df = pl.read_csv(
        "/Users/hanyuwu/Study/stock-forecasting/data/processed/stock_combined.csv"
    )
    pipeline = LGBMClassifierPipeline(df)
    pipeline.run()
