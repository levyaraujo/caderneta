import locale
import logging
from datetime import datetime
from io import BytesIO
from typing import List, TypedDict, Literal, Union

from plotly import graph_objects as go

from src.dominio.graficos.excecoes import ErroAoCriarGrafico
from src.dominio.transacao.entidade import Transacao, Real
from src.dominio.transacao.tipos import TipoTransacao
from src.libs.tipos import Intervalo

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("graficos")

locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")


class GraficoRetorno(TypedDict):
    titulo: str
    formato: Literal["png", "svg", "html"]
    dados: Union[str, bytes]
    tipo_dados: Literal["base64", "bytes"]


class GraficoBase:
    def __init__(
        self,
        titulo: str,
        transacoes: List[Transacao],
        intervalo: Intervalo,
    ):
        self.titulo = titulo
        self.transacoes = transacoes
        self.intervalo = intervalo
        self.figura: go.Figure = None
        self.formato: Literal["png", "svg", "html"] = "html"

    def _gerar_nome_arquivo(self, prefixo: str = "") -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_base = (
            f"{prefixo}_{self.titulo}_{timestamp}"
            if prefixo
            else f"fluxo_de_caixa_{timestamp}"
        )
        nome_arquivo = "".join(
            c if c.isalnum() or c in ("-", "_") else "_" for c in nome_base
        )
        return nome_arquivo

    def criar_grafico(self, dados, layout) -> go.Figure:
        try:
            fig = go.Figure(data=dados, layout=layout)
            fig.update_layout(
                title={
                    "text": self.titulo,
                    "x": 0.5,
                    "xanchor": "center",
                    "yanchor": "top",
                },
                hovermode="closest",
                hoverlabel=dict(bgcolor="white", font_size=12, font_family="Arial"),
            )
            logger.info("Gráfico criado com sucesso")
            self.figura = fig
            return fig
        except Exception as e:
            logger.error(f"Erro ao criar gráfico: {str(e)}")
            raise ErroAoCriarGrafico(
                f"Erro ao criar gráfico de {self.titulo}: {str(e)}"
            )

    def para_bytes(self) -> bytes:
        if self.figura is None:
            raise ValueError("Figura não foi criada. Chame criar_grafico() primeiro.")
        try:
            buffer = BytesIO()
            if self.formato == "html":
                buffer.write(self.figura.to_html().encode("utf-8"))
            else:
                self.figura.write_image(buffer, format=self.formato)
            buffer.seek(0)
            return buffer.getvalue()
        except Exception as e:
            logger.error(f"Erro ao gerar gráfico em bytes: {str(e)}")
            raise


class GraficoFluxoCaixa(GraficoBase):
    def __init__(self, titulo: str, transacoes: List[Transacao], intervalo: Intervalo):
        super().__init__(titulo, transacoes, intervalo)

    def criar_grafico_fluxo_caixa(
        self, formato: Literal["png", "svg", "html"] = ""
    ) -> go.Figure:
        self.formato = formato if formato else self.formato
        try:
            logger.info(
                f"Criando gráfico de fluxo de caixa para intervalo: {self.intervalo}"
            )

            transacoes_no_periodo = [
                transacao
                for transacao in self.transacoes
                if self.intervalo.contem(transacao.caixa)
            ]
            logger.info(
                f"Número de transações no período: {len(transacoes_no_periodo)}"
            )

            datas = [transacao.caixa for transacao in transacoes_no_periodo]
            valores = [
                transacao.valor
                if transacao.tipo == TipoTransacao.CREDITO
                else -transacao.valor
                for transacao in transacoes_no_periodo
            ]

            hover_texts = [
                f"Data: {transacao.caixa.strftime('%d/%m/%Y %H:%M')}<br>"
                + f"Valor: {Real(transacao.valor)}<br>"
                + f"Tipo: {transacao.tipo.value}<br>"
                + f"Destino: {transacao.categoria}<br>"
                + f"Descrição: {transacao.descricao or 'N/A'}"
                for transacao in transacoes_no_periodo
            ]

            dados = [
                go.Scatter(
                    x=datas,
                    y=valores,
                    mode="lines+markers",
                    name="Fluxo de Caixa",
                    hovertext=hover_texts,
                    hoverinfo="text",
                    marker=dict(
                        color=valores,
                        size=12,
                    ),
                    line=dict(color="royalblue", width=2),
                )
            ]

            layout = go.Layout(
                xaxis_title="Data", yaxis_title="Valor (R$)", template="plotly_white"
            )

            self.titulo = f"Fluxo de Caixa de {self.intervalo.inicio.strftime('%d/%m/%Y')} a {self.intervalo.fim.strftime('%d/%m/%Y')}"

            fig = self.criar_grafico(dados, layout)
            return fig

        except Exception as e:
            logger.error(f"Erro ao criar gráfico de fluxo de caixa: {str(e)}")
            raise
