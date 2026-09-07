import pandas as pd
import numpy as np
import pickle
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix


# training fn
def train_and_find_best_model(csv_filename: str='gestures_dataset.csv', model_output:str='gesture_model.pkl'):
    if not os.path.exists(csv_filename):
        print(f"Error: Dataset File '{csv_filename}' not found. Run Data Collector Mode.")
        return

    print("\n === Training === ")

    df = pd.read_csv(csv_filename)

    if df.empty:
        print("Dataset Empty. run  Data Colllector Mode")
        return

    #Features and Target
    X = df.drop('label',axis=1)
    y = df['label']

    test_sizes = [0.15, 0.20, 0.25, 0.30]
    best_accuracy = 0.0
    best_clf = None
    best_params = {}

    print("Running Automated Split Training Experiment...\n")

    for t_size in test_sizes:
        for seed in range(5):
            X_train, X_test, y_train, y_test=train_test_split(
                X,y,test_size=t_size, random_state=seed, stratify=y
            )

            clf = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=seed)
            clf.fit(X_train,y_train)

            y_pred = clf.predict(X_test)
            acc = accuracy_score(y_test, y_pred)

            if(acc>best_accuracy):
                best_accuracy = acc
                best_clf = clf
                best_params = {'test_size': t_size, 'random_state': seed, 'y_test':y_test, 'y_pred': y_pred}

    print(" *** Best Model Selection *** ")
    print(f"""\n
        Highest Accuracy: {best_accuracy * 100:.2f}%; 
        Optimal Test Size: {best_params['test_size'] * 100:.0f}%; 
        Optimal Random State: {best_params['random_state']};
        """
    )

    print("\n\n Confusion Matrix")
    print(confusion_matrix(best_params['y_test'], best_params['y_pred']))

    #Pickle best perfoming model
    with open(model_output, 'wb') as f:
        pickle.dump(best_clf, f)

    print(f"\n\n [SUCCESS] Best Model exoprted to '{model_output}'")

if __name__ == "__main__":
    train_and_find_best_model()