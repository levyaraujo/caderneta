import logging
import os
from typing import Tuple, Dict

import joblib
import nltk
import pandas as pd
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB

from const import COMANDOS_TRANSACAO
from src.dominio.transacao.tipos import TipoTransacao

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger("TextClassifier")

nltk.download("punkt", quiet=True)
nltk.download("stopwords", quiet=True)
nltk.download("wordnet", quiet=True)


class ClassificadorTexto:
    def __init__(self):
        self.csv_path = os.getenv("CSV_TREINAMENTO")
        self.vectorizer_joblib = os.getenv("VECTORIZER_PATH")
        self.classifier_joblib = os.getenv("CLASSIFIER_PATH")
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
            df = pd.read_csv(self.csv_path, on_bad_lines="skip")
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
            self.df.to_csv(self.csv_path, index=False)

        self.treinar_e_salvar_modelo()
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
        df_results.to_csv(self.csv_path, index=False)

    def treinar_e_salvar_modelo(self):
        self.treinar_modelo()
        joblib.dump(self.vectorizer, self.vectorizer_joblib)
        joblib.dump(self.classifier, self.classifier_joblib)
        self.df.to_csv(self.csv_path, index=False)
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

    @property
    def data_formatada(self):
        return self.data.strftime("%d/%m/%Y")


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
        self.working_message = message.lower().strip()
        if self.working_message.split()[0] in COMANDOS_TRANSACAO:
            self.working_message = " ".join(self.working_message.split()[1:])
        date = self._extract_date()
        value = self._extract_value()
        payment_method = self._extract_payment_method()
        category = self._extract_category()

        return DadosTransacao(
            acao=self.acao,
            valor=value,
            metodo_pagamento=payment_method,
            categoria=category,
            data=date,
            mensagem_original=message,
        )

    def _extract_date(self) -> date:
        date_pattern = r"\b\d{1,2}/\d{1,2}\b"
        date_match = re.search(date_pattern, self.working_message)
        if not date_match:
            date_str = datetime.now().date().strftime("%d/%m")
        else:
            date_str = date_match.group()

        day, month = map(int, date_str.split("/"))
        self.working_message = self.working_message.replace(date_str, "")
        return datetime.now().replace(day=day, month=month).date()

    def _extract_value(self) -> float:
        value_pattern = r"\b\d+(?:\.\d{3})*(?:,\d{2})?\b|\b\d+\b"
        value_match = re.search(value_pattern, self.working_message)
        if not value_match:
            raise ValueError("No value found in message")

        value_str = value_match.group()
        self.working_message = self.working_message.replace(value_str, "")
        return float(value_str.replace(".", "").replace(",", "."))

    def _extract_payment_method(self) -> Optional[str]:
        for method in self.METODOS_PAGAMENTO:
            if method in self.working_message:
                self.working_message = self.working_message.replace(method, "")
                return method
        return None

    def _extract_category(self) -> Optional[str]:
        palavras_restantes = [
            self.pre_processar_texto(word)
            for word in self.working_message.split()
            if self.pre_processar_texto(word) and word not in self.METODOS_PAGAMENTO
        ]
        category = (
            " ".join(palavras_restantes).strip().replace(",", "|")
            if len(palavras_restantes) > 0
            else "outros"
        )
        return category.strip() if category else None

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
