import logging
import os
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any
from typing import Optional
from typing import Tuple

import joblib
import nltk
import pandas as pd
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from sklearn.exceptions import NotFittedError
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

from const import TRANSACAO_DEBITO, TRANSACAO_CREDITO
from src.dominio.processamento.exceptions import NaoEhTransacao
from src.dominio.transacao.tipos import TipoTransacao
from src.infra.log import setup_logging
from src.utils.datas import ultima_hora

nltk.download("punkt", quiet=True)
nltk.download("stopwords", quiet=True)
nltk.download("wordnet", quiet=True)
nltk.download("punkt_tab", quiet=True)

logger = setup_logging()


class ClassificadorTexto:
    def __init__(self) -> None:
        self.csv_path = os.getenv("CSV_TREINAMENTO", "/opt/caderneta/static/dados_categorizados.csv")
        self.vectorizer_joblib = os.getenv("VECTORIZER_PATH", "/opt/caderneta/static/vectorizer.joblib")
        self.classifier_joblib = os.getenv("CLASSIFIER_PATH", "/opt/caderneta/static/classifier.joblib")
        self.vectorizer = (
            self._carregar_ou_criar_vetorizador(self.vectorizer_joblib)
            if self.vectorizer_joblib
            else TfidfVectorizer(max_features=100, ngram_range=(1, 2))
        )
        self.classifier = (
            self._carregar_ou_criar_classificador(self.classifier_joblib)
            if self.classifier_joblib
            else LogisticRegression(random_state=42)
        )
        self.pipeline = Pipeline([("vectorizer", self.vectorizer), ("classifier", self.classifier)])
        self.stop_words = set(stopwords.words("portuguese"))
        self.lemmatizer = WordNetLemmatizer()
        self.df = self._carregar_dataframe()

    @staticmethod
    def _carregar_ou_criar_vetorizador(path: str) -> Any:
        try:
            return joblib.load(path)
        except FileNotFoundError:
            return TfidfVectorizer(max_features=1000)

    @staticmethod
    def _carregar_ou_criar_classificador(path: str) -> Any:
        try:
            return joblib.load(path)
        except FileNotFoundError:
            return MultinomialNB()

    def _carregar_dataframe(self) -> pd.DataFrame:
        try:
            df = pd.read_csv(self.csv_path, on_bad_lines="skip")
            logger.info(f"Dados carregados com sucesso. Linhas: {len(df)}")
            return df
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            raise

    def pre_processar_texto(self, text: str) -> str:
        tokens = word_tokenize(text.lower())
        tokens = [self.lemmatizer.lemmatize(token) for token in tokens if token not in self.stop_words]
        return " ".join(tokens)

    def treinar_modelo(self) -> str:
        """Train the model using the pipeline"""
        self.df["mensagem"] = self.df["mensagem"].apply(self.pre_processar_texto)

        X_train, X_test, y_train, y_test = train_test_split(
            self.df["mensagem"],
            self.df["classificacao"],
            test_size=0.3,
            random_state=42,
            shuffle=True,
        )

        self.pipeline.fit(X_train, y_train)

        y_pred = self.pipeline.predict(X_test)
        report: str = "\n" + classification_report(y_test, y_pred)
        return report

    def classificar_mensagem(self, mensagem: str, atualizar_df: bool = True) -> Tuple[str, Dict[str, float]]:
        try:
            mensagem_processada = self.pre_processar_texto(mensagem)

            previsao = self.pipeline.predict([mensagem_processada])[0]
            probabilidades = self.pipeline.predict_proba([mensagem_processada])[0]
            probs_dict = dict(zip(self.pipeline.classes_, probabilidades))

            if probs_dict[previsao] < 0.7:
                comando = mensagem.split()[0] if len(mensagem.split(" ")) > 1 else mensagem
                if comando in TRANSACAO_DEBITO:
                    previsao = "debito"
                elif comando in TRANSACAO_CREDITO:
                    previsao = "credito"
                else:
                    raise NaoEhTransacao("O comando informado não é de transação")
                probs_dict = {previsao: 1.0}

            if atualizar_df and previsao != "outros":
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
                logger.info(f"Dataframe atualizado com a nova classificação: {previsao}")

            return previsao, probs_dict

        except NotFittedError as erro:
            logger.info(f"Model not fitted yet: {erro}")
            self.treinar_modelo()
            self.salvar_modelo()
            return self.classificar_mensagem(mensagem, atualizar_df)

    def classificar_todas_as_mensagens(self) -> None:
        results = []
        for message in self.df["mensagem"]:
            prediction, probabilities = self.classificar_mensagem(message, atualizar_df=True)
            results.append(
                {
                    "mensagem": message,
                    "classificacao": prediction,
                    "probabilidade": probabilities[prediction],
                }
            )
        self.df = pd.DataFrame(results).drop_duplicates()

    def salvar_modelo(self) -> None:
        joblib.dump(self.vectorizer, self.vectorizer_joblib)
        joblib.dump(self.classifier, self.classifier_joblib)
        self.df.to_csv(self.csv_path, index=False)
        logger.info(f"Model salvo em {self.vectorizer_joblib} e {self.classifier_joblib}")


@dataclass
class DadosTransacao:
    tipo: TipoTransacao
    valor: float
    metodo_pagamento: Optional[str]
    categoria: Optional[str]
    data: datetime
    mensagem_original: str

    @property
    def data_formatada(self) -> str:
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
        if self.working_message.split()[0] in [*TRANSACAO_DEBITO, *TRANSACAO_CREDITO]:
            self.working_message = " ".join(self.working_message.split()[1:])
        date = self._extract_date()
        value = self._extract_value()
        payment_method = self._extract_payment_method()
        category = self._extract_category()

        return DadosTransacao(
            tipo=self.acao,
            valor=value,
            metodo_pagamento=payment_method,
            categoria=category,
            data=date,
            mensagem_original=message,
        )

    def _extract_date(self) -> datetime:
        data_e_hora = r"\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}"

        if re.search(data_e_hora, self.working_message):
            date_str = re.search(data_e_hora, self.working_message).group()
            self.working_message = self.working_message.replace(date_str, "")
            return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")

        date_pattern = r"\b\d{1,2}/\d{1,2}\b"
        date_match = re.search(date_pattern, self.working_message)
        if not date_match:
            date_str = datetime.now().date().strftime("%d/%m")
        else:
            date_str = date_match.group()

        day, month = map(int, date_str.split("/"))
        self.working_message = self.working_message.replace(date_str, "")
        return datetime.now().replace(day=day, month=month, hour=0, minute=0, second=0, microsecond=0)

    def _extract_value(self) -> float:
        """
        Extract monetary values from the text, handling formats like:
        - 150
        - 520,75
        - 10,500
        - 10.500,15
        - 1,000,000
        - 1.000.000,00
        - 50.46
        - 550.20

        Returns:
            float: Extracted monetary value
        """
        value_pattern = r"\b\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?\b"

        value_match = re.search(value_pattern, self.working_message)
        if not value_match:
            raise ValueError("No value found in message")

        value_str = value_match.group()
        self.working_message = self.working_message.replace(value_str, "")

        # Normalize value string to a float
        if "," in value_str and "." in value_str:
            # Handle cases like "1.000,50"
            value_str = value_str.replace(".", "").replace(",", ".")
        elif "," in value_str:
            # Handle cases like "520,75"
            value_str = value_str.replace(",", ".")
        elif "." in value_str:
            # Handle cases like "550.20"
            value_str = value_str

        return float(value_str)

    def _extract_payment_method(self) -> Optional[str]:
        for method in self.METODOS_PAGAMENTO:
            if method in self.working_message:
                self.working_message = self.working_message.replace(method, "")
                return method
        return None

    def _extract_category(self) -> Optional[str]:
        primeira_palavra = self.working_message.split()[0]
        ultima_palavra = self.working_message.split()[-1]

        if primeira_palavra in self.stop_words:
            self.working_message = " ".join(self.working_message.split()[1:])

        if ultima_palavra in self.stop_words:
            self.working_message = " ".join(self.working_message.split()[:-1])

        palavras_restantes = [
            word
            for word in self.working_message.split()
            if word not in self.METODOS_PAGAMENTO and word not in [*TRANSACAO_DEBITO, *TRANSACAO_CREDITO]
        ]
        category = " ".join(palavras_restantes).strip().replace(",", "|") if len(palavras_restantes) > 0 else "outros"
        return category.strip().upper() if category else None

    def format_transaction(self, transacao: DadosTransacao) -> str:
        """Format a transaction for display."""
        date_str = transacao.data.strftime("%d/%m/%Y")
        parts = [
            f"Action: {transacao.tipo}",
            f"Value: R$ {transacao.valor:.2f}",
            f"Date: {date_str}",
        ]

        if transacao.metodo_pagamento:
            parts.append(f"Payment Method: {transacao.metodo_pagamento}")
        if transacao.categoria:
            parts.append(f"Category: {transacao.categoria}")

        return "\n".join(parts)
