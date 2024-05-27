# -*- coding: utf-8 -*-
"""Final_Project_Code.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/16EGtmopJaiQvxlZnOW5TjJu2wNMcEF12
"""

# Importing necessary Modules for the Project
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, AdaBoostClassifier, ExtraTreesClassifier
from sklearn.naive_bayes import GaussianNB
from scipy.stats import boxcox

from collections import Counter

import warnings
warnings.filterwarnings("ignore")

# Loading and having an initial look at the data

data = pd.read_csv("/Users/sairahulpadma/Desktop/UNT/SPRING-2024/SDAI/GlassClassification/glassclassification-backend/glass.csv ")
data.head()

# Having a look at statistics of each feature
# Immediately we found out that the Type feature is mislabeled where a class is missing.

print(data.describe())

# Handling the missed class by renaming the class values
# This has been done using the map method of pandas series.
# For more understanding have look at the mapping dictionary.

mapper = {1:0, 2:1, 3:2, 5:3, 6:4, 7:5}
data.Type = data.Type.map(mapper)
data.head()

# This part of the code is used to find the outliers using quartiles.
# We use Q1 and Q3 to find the interquartile range and then create a step size by multiplying it with 1.5.
# We then use then use this as a reference to find out outliers. The formula is presented in the code section.

def process_outliers(data):
  outlier_indices = []
  for column in data.columns.tolist()[:-1]:
    quartile_1 = np.percentile(data[column], 25)
    quartile_3 = np.percentile(data[column], 75)
    inter_quartile_range = quartile_3 - quartile_1
    step_size = inter_quartile_range * 1.5
    indices = data[(data[column] < quartile_1 - step_size) | (data[column] > step_size + quartile_3)].index
    outlier_indices.extend(indices)

  outlier_indices = Counter(outlier_indices)
  outliers = list(index for index, count in outlier_indices.items() if count > 2)
  return outliers

# Using the outlier function to find and drop them.
# Using this function we identified 14 outliers, so we dropped them.

outliers = process_outliers(data.iloc[:, :-1])
data = data.drop(outliers).reset_index(drop=True)
data.shape

"""# Exploratory Data Analysis"""

# Using the pair plot to see how each pair of data is distributed.
# It also provides a distribution plot with a seperate distributiion for each class seperately.
# We can clearly see that the distribution of different classes are intersecting, meaning classes are also intersecting.

sns.pairplot(data, hue="Type")

# Trying to understand the relation between each pair of features numerically.
# The heat map shows the correlation between each feature.
# Some features such as RI and Ca are highly correlated with many other features.

plt.figure(figsize=(8,8))
sns.heatmap(data.corr(), annot=True)

# Checking how the data is distubuted in each feature seperately.
# We have also used the Kernel Density Estimation to produce continuous plot for the distribution.

plt.figure(figsize=(15,15))
plt.tight_layout()
for i, feature in enumerate(data.columns.tolist()[:-1]):
  plt.subplot(int(f"33{i+1}"))
  sns.distplot(data[feature], kde=True)

plt.suptitle("Distribution plot for each feature")

# Implementing box plot to visually see the quartiles and outliers present in each class seperatley.
# This helped us to write the outlier detection algorithm presented in the early section.

plt.figure(figsize=(15,10))
plt.title("Box plot for each feature")
sns.boxplot(data.iloc[:, :-1], orient='h')

# Checking the count of classes.
# This shows that the dataset is imbalanced with very few samples in classes 2, 3, 4 and 5.

types, counts = np.unique(data['Type'].values, return_counts=True)
plt.title("Checking count of each class type")
plt.bar(types, counts)

"""# Training and Evaluating Models"""

# Splitting the dataset into training and testing set using model selection technique.
# Later we have standardized the data using the standard scaler.
# The split for training is 80% and 20% for testing.

X, Y = data.iloc[:, :-1].values, data.iloc[:, -1].values

X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=.2, stratify=Y)
scaler = StandardScaler()
scaler.fit(X_train)
X_train = scaler.transform(X_train)
X_test = scaler.transform(X_test)

# A helper function to reduce the code for training each model seperately
# It takes model, model name, X and Y (both train and test) and trains the model.
def base(model, X, Y, model_name):
  model.fit(X[0], Y[0])
  results = cross_val_score(model, X[0], Y[0], cv=10)
  return results

# Initializing the required models and variables for the training and validation process.
# 7 different models has been tested with one model having differernt variations (Random Forest).

models = {
    "Decision Tree" : DecisionTreeClassifier(),
    "Logistic Regression" : LogisticRegression(),
    "Adaboost Classifier" : AdaBoostClassifier(),
    "Gradient Boosting" : GradientBoostingClassifier(n_estimators=300),
    "Extra Tree Classifier" : ExtraTreesClassifier(),
    "Support Vector Machine" : SVC(),
    "Random Forest 50" : RandomForestClassifier(n_estimators=50),
    "Random Forest 75" : RandomForestClassifier(n_estimators=75),
    "Random Forest 100" : RandomForestClassifier(n_estimators=100)
}
X = [X_train, X_test]
Y = [Y_train, Y_test]

cv_results_train = dict()
for model_name, model in models.items():
  result = base(model, X, Y, model_name)
  cv_results_train[model_name] = result

# Comparing the performance of each model using the cross validation technique
# We have implemented the 10 fold cross validation to check the median performance of each model.
# The test has that proved Gradient Boosting Algorithm is performing better since the median performance is good along with high score.

plt.figure(figsize=(15, 10))
plt.boxplot(cv_results_train.values(), labels=cv_results_train.keys())
plt.xticks(rotation='vertical')
plt.title("Comparing performance of different models")

# Checking the training results of the Gradient Boosting Model
# It has performed very well on the training set and the results are presented below.

print(classification_report(Y[0], models['Gradient Boosting'].predict(X[0])))

# Confusion Matrix for the training set. It clearly has no misclassifications

sns.heatmap(confusion_matrix(Y[0], models['Gradient Boosting'].predict(X[0])), annot=True, cmap='coolwarm')
plt.title("Train Confusion Matrix")

# The model performance on the test set.
# It has a accuracy score of 85% Which is a good score considering the size of the dataset

print(classification_report(Y[1], models['Gradient Boosting'].predict(X[1])))

# Confusion Matrix for test set.

sns.heatmap(confusion_matrix(Y[1], models['Gradient Boosting'].predict(X[1])), annot=True, cmap='coolwarm')
plt.title("Test Confusion Matrix")
