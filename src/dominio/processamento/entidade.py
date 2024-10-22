from enum import Enum
from typing import Tuple, Dict

import pandas as pd
import re
import logging
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import classification_report
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import joblib

from src.dominio.transacao.tipos import TipoTransacao

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger("TextClassifier")

nltk.download("punkt", quiet=True)
nltk.download("stopwords", quiet=True)
nltk.download("wordnet", quiet=True)


class ClassificadorTexto:
    def __init__(self):
        self.data_path = "/home/lev0x/Documents/modelo/dados_categorizados.csv"
        self.vectorizer_joblib = "/home/lev0x/Documents/modelo/vectorizer.joblib"
        self.classifier_joblib = "/home/lev0x/Documents/modelo/classifier.joblib"
        self.vectorizer = (
            self._carregar_ou_criar_vetorizador(self.vectorizer_joblib)
            if self.vectorizer_joblib
            else TfidfVectorizer(max_features=1000)
        )
        self.classifier = (
            self._carregar_ou_criar_classificador(self.classifier_joblib)
            if self.classifier_joblib
            else MultinomialNB()
        )
        self.stop_words = set(stopwords.words("portuguese"))
        self.lemmatizer = WordNetLemmatizer()
        self.df = self._carregar_dataframe()

    @staticmethod
    def _carregar_ou_criar_vetorizador(path: str):
        try:
            return joblib.load(path)
        except FileNotFoundError:
            return TfidfVectorizer(max_features=1000)

    @staticmethod
    def _carregar_ou_criar_classificador(path: str):
        try:
            return joblib.load(path)
        except FileNotFoundError:
            return MultinomialNB()

    def _carregar_dataframe(self) -> pd.DataFrame:
        try:
            df = pd.read_csv(self.data_path, on_bad_lines="skip")
            logger.info(f"Data loaded successfully. Number of samples: {len(df)}")
            return df
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            raise

    def pre_processar_texto(self, text: str) -> str:
        tokens = word_tokenize(text.lower())
        tokens = [
            self.lemmatizer.lemmatize(token)
            for token in tokens
            if token not in self.stop_words
        ]
        return " ".join(tokens)

    @staticmethod
    def categorizar_texto(text: str) -> str:
        if re.search(r"v\s+\d+|recebi|\bvendi\b|\bvender\b", text, re.IGNORECASE):
            return "credito"
        if re.search(r"paguei|gastei|comprei", text, re.IGNORECASE):
            return "debito"
        return "outro"

    def treinar_modelo(self):
        self.df["mensagem"] = self.df["mensagem"].apply(self.pre_processar_texto)
        X_train, X_test, y_train, y_test = train_test_split(
            self.df["mensagem"],
            self.df["classificacao"],
            test_size=0.2,
            random_state=42,
            shuffle=True,
        )
        X_train_vectorized = self.vectorizer.fit_transform(X_train)
        self.classifier.fit(X_train_vectorized, y_train)
        X_test_vectorized = self.vectorizer.transform(X_test)
        y_pred = self.classifier.predict(X_test_vectorized)
        logger.info("\n" + classification_report(y_test, y_pred))

    def classificar_mensagem(
        self, mensagem: str, atualizar_df: bool = True
    ) -> Tuple[str, Dict[str, float]]:
        mensagem_processada = self.pre_processar_texto(mensagem)
        message_vectorized = self.vectorizer.transform([mensagem_processada])
        previsao = self.classifier.predict(message_vectorized)[0]
        probabilidades = self.classifier.predict_proba(message_vectorized)[0]
        probs_dict = dict(zip(self.classifier.classes_, probabilidades))

        if atualizar_df and probs_dict[previsao] > 0.7:
            nova_linha = pd.DataFrame(
                [
                    {
                        "mensagem": mensagem,
                        "classificacao": previsao,
                        "probabilidade": probs_dict[previsao],
                    }
                ]
            )
            self.df = pd.concat([self.df, nova_linha], ignore_index=True)
            self.df.to_csv(self.data_path, index=False)

        self.treinar_modelo()
        return str(previsao).upper(), probs_dict

    def classificar_todas_as_mensagens(self):
        results = []
        for message in self.df["mensagem"]:
            prediction, probabilities = self.classificar_mensagem(
                message, atualizar_df=True
            )
            logger.info(f"Message: {message}")
            logger.info(f"Classification: {prediction}")
            logger.info(f"Probabilities: {probabilities}")
            results.append(
                {
                    "mensagem": message,
                    "classificacao": prediction,
                    "probabilidade": probabilities[prediction],
                }
            )
        df_results = pd.DataFrame(results)
        df_results.to_csv(self.data_path, index=False)

    def treinar_e_salvar_modelo(self):
        self.treinar_modelo()
        joblib.dump(self.vectorizer, self.vectorizer_joblib)
        joblib.dump(self.classifier, self.classifier_joblib)
        self.df.to_csv(self.data_path, index=False)
        logger.info(
            f"Model saved to {self.vectorizer_joblib} and {self.classifier_joblib}"
        )


from dataclasses import dataclass
from datetime import datetime, date
import re
from typing import Optional


@dataclass
class DadosTransacao:
    acao: TipoTransacao
    valor: float
    metodo_pagamento: Optional[str]
    categoria: Optional[str]
    data: date
    mensagem_original: str


class ConstrutorTransacao(ClassificadorTexto):
    def __init__(self, acao: TipoTransacao):
        super().__init__()
        self.acao = acao
        self.mensagem_encolhida = ""

    METODOS_PAGAMENTO = {
        "pix",
        "credito",
        "debito",
        "dinheiro",
        "boleto",
        "transferencia",
    }

    def parse_message(self, message: str) -> DadosTransacao:
        """Parse a financial message by extracting known patterns first."""
        message = message.lower().strip()
        working_message = message  # Create a copy to modify

        # 1. Extract and remove date (DD/MM)
        date_pattern = r"\b\d{1,2}/\d{1,2}\b"
        date_match = re.search(date_pattern, working_message)
        if not date_match:
            date_str = datetime.now().date().strftime("%d/%m")
        else:
            date_str = date_match.group()

        day, month = map(int, date_str.split("/"))
        date = datetime.now().replace(day=day, month=month).date()
        # Remove the date from working message
        working_message = working_message.replace(date_str, "")

        # 2. Extract and remove value
        value_pattern = r"\b\d+(?:\.\d{3})*(?:,\d{2})?\b|\b\d+\b"
        value_match = re.search(value_pattern, working_message)
        if not value_match:
            raise ValueError("No value found in message")

        value_str = value_match.group()
        value = float(value_str.replace(".", "").replace(",", "."))
        # Remove the value from working message
        working_message = working_message.replace(value_str, "")

        # 3. Extract and remove payment method
        payment_method = None
        for method in self.METODOS_PAGAMENTO:
            if method in working_message:
                payment_method = method
                # Remove the payment method from working message
                working_message = working_message.replace(method, "")
                break

        # 4. Clean up remaining text and use as category
        # Remove common words like 'de', 'para', etc
        remaining_words = [
            self.pre_processar_texto(word) for word in working_message.split()
        ]

        # Join remaining words as category, excluding the first word (action)
        category = " ".join(remaining_words[1:]) if len(remaining_words) > 1 else None
        # If category is empty string or only spaces, set to None
        category = category.strip() if category else None

        return DadosTransacao(
            acao=self.acao,
            valor=value,
            metodo_pagamento=payment_method,
            categoria=category,
            data=date,
            mensagem_original=message,
        )

    def format_transaction(self, transacao: DadosTransacao) -> str:
        """Format a transaction for display."""
        date_str = transacao.data.strftime("%d/%m/%Y")
        parts = [
            f"Action: {transacao.acao}",
            f"Value: R$ {transacao.valor:.2f}",
            f"Date: {date_str}",
        ]

        if transacao.metodo_pagamento:
            parts.append(f"Payment Method: {transacao.metodo_pagamento}")
        if transacao.categoria:
            parts.append(f"Category: {transacao.categoria}")

        return "\n".join(parts)
