# -*- coding: utf-8 -*-
"""
Created on Fri Nov  1 09:50:52 2024

@author: fabio
"""

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn import svm
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score
import warnings

# Suppress warnings
warnings.filterwarnings('ignore')

# Load the dataset
iris = pd.read_csv(r'C:\Users\TRAPPIST\Desktop\CARPETA DATABASES\CSV\IRIS\Iris.csv')


# Drop the 'Id' column as specified
iris = iris.drop(columns=['Id'], errors='ignore')

# Check data structure and show the first few rows
print(iris.info())
print(iris.head())

# Rename columns to more descriptive names
iris = iris.rename(columns={
    'SepalLengthCm': 'sepal_length',
    'SepalWidthCm': 'sepal_width',
    'PetalLengthCm': 'petal_length',
    'PetalWidthCm': 'petal_width',
    'Species': 'species'
})

# Visualize the distribution of species in the dataset
print("Species count:\n", iris['species'].value_counts())

# Plot Sepal Length vs Sepal Width
sns.set_style("whitegrid")
sns.FacetGrid(iris, hue="species", height=4).map(plt.scatter, "sepal_length", "sepal_width").add_legend()
plt.show()

# Data summary and checking for null values
print(iris.describe())
print("Shape of dataset:", iris.shape)
print("Null values:\n", iris.isnull().sum())

# Splitting data into features and labels
X = iris[['sepal_length', 'sepal_width', 'petal_length', 'petal_width']]
y = iris['species']

# Scaling the features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Splitting the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.4, random_state=42)

# SVM Classifier
clf = svm.SVC(kernel='rbf')
clf.fit(X_train, y_train)

# Making predictions on the test set
y_pred = clf.predict(X_test)

# Evaluating the classifier accuracy
accuracy = accuracy_score(y_test, y_pred)
print('Accuracy:', accuracy)
