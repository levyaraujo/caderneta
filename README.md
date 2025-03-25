# Caderneta

Caderneta is a Python-based financial transaction processing and classification system. It extracts, categorizes, and formats financial transaction data from textual messages, leveraging natural language processing (NLP) and machine learning techniques.

## Features

- **Transaction Parsing**: Extracts key details such as date, value, payment method, and category from financial messages.
- **Text Classification**: Uses a machine learning pipeline to classify messages into predefined categories.
- **Data Persistence**: Updates and saves classified data to a CSV file for future use.
- **Customizable**: Supports training and retraining of the classification model with new data.
- **Invoice Image Processing**: Allows users to upload an invoice image, which is stored in an S3 bucket. This triggers an AWS Lambda function that extracts text from the image and sends it to Amazon Bedrock for further processing.

## How It Works

1. **Message Parsing**:
   - The `ConstrutorTransacao` class processes financial messages to extract transaction details.
   - It identifies dates, monetary values, payment methods, and categories using regex patterns and predefined rules.

2. **Text Classification**:
   - The `ClassificadorTexto` class preprocesses messages using tokenization, lemmatization, and stopword removal.
   - A machine learning pipeline (TF-IDF vectorizer + classifier) predicts the category of the message.
   - If the model is not confident, fallback rules are applied to classify the message.

3. **Data Management**:
   - Classified messages are stored in a CSV file for persistence.
   - The model and vectorizer are saved as `.joblib` files for reuse.

4. **Transaction Formatting**:
   - The `format_transaction` method formats transaction details into a human-readable string for display.

## Setup
⚠ Under Construction ⚠
