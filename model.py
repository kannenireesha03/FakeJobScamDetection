import pandas as pd
import pickle
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Load data
data = pd.read_csv("dataset.csv")
X = data["text"]
y = data["label"]

# Vectorize
vectorizer = TfidfVectorizer(stop_words=stopwords.words('english'))
X_vec = vectorizer.fit_transform(X)

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X_vec, y, test_size=0.2, random_state=42
)

# Models
models = {
    "Logistic Regression": LogisticRegression(max_iter=1000),
    "Naive Bayes": MultinomialNB(),
}

accuracies = {}

for name, model in models.items():
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    accuracies[name] = accuracy_score(y_test, preds)

# Select best model
best_model_name = max(accuracies, key=accuracies.get)
best_model = models[best_model_name]

# Save
pickle.dump(best_model, open("scam_model.pkl", "wb"))
pickle.dump(vectorizer, open("vectorizer.pkl", "wb"))
pickle.dump(accuracies, open("model_accuracy.pkl", "wb"))

print("Model trained successfully")
print("Best model:", best_model_name)
print("Accuracies:", accuracies)

