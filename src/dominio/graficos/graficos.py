import locale
import logging
import math
from datetime import datetime
from io import BytesIO
from typing import List, TypedDict, Literal, Any, Dict

from plotly import graph_objects as go

from src.dominio.graficos.excecoes import ErroAoCriarGrafico
from src.dominio.transacao.entidade import Transacao, Real

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("graficos")

locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")


class GraficoRetorno(TypedDict):
    nome_arquivo: str
    formato: Literal["png", "svg", "html"]
    dados: bytes
    figura: go.Figure


class GraficoBase:
    def __init__(
        self,
        titulo: str,
        transacoes: List[Transacao],
    ):
        self.titulo = titulo
        self.transacoes = transacoes
        self.formato: Literal["png", "svg", "html"] = "html"

    def _gerar_nome_arquivo(self, prefixo: str = "") -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_base = (
            f"{prefixo}_{timestamp}" if prefixo else f"fluxo_de_caixa_{timestamp}"
        )
        nome_arquivo = "".join(
            c if c.isalnum() or c in ("-", "_") else "_" for c in nome_base
        )
        return nome_arquivo

    def criar_grafico(self, dados, layout) -> GraficoRetorno:
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
            return {
                "nome_arquivo": self._gerar_nome_arquivo("fluxo_de_caixa"),
                "formato": self.formato,
                "dados": self.para_bytes(),
                "figura": fig,
            }
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
                buffer.write(self.figura.to_image())
            buffer.seek(0)
            return buffer.getvalue()
        except Exception as e:
            logger.error(f"Erro ao gerar gráfico em bytes: {str(e)}")
            raise

    def definir_yaxis(self, valores: List[float]):
        valores_numericos = [float(v) for v in valores if isinstance(v, (int, float))]
        min_value = min(valores_numericos)
        max_value = max(valores_numericos)

        # Arredondar para o próximo múltiplo de 2000 acima e abaixo
        y_min = math.floor(min_value / 2000) * 2000
        y_max = math.ceil(max_value / 2000) * 2000

        return y_min, y_max

    def criar_grafico_de_linha(
        self,
        legendas: List[Any],
        valores: List[Any],
        layout: go.Layout,
        hover_texts: List[str] = None,
    ) -> GraficoRetorno:
        valores = [
            go.Scatter(
                x=legendas,
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

        fig = self.criar_grafico(valores, layout)
        return fig

    def criar_grafico_de_pizza(
        self,
        legendas: List[str],
        valores: List[float],
        layout: go.Layout,
        hover_texts: List[str] = None,
    ) -> GraficoRetorno:
        dados = [
            go.Pie(
                labels=legendas,
                values=valores,
                hole=0.3,
                textinfo="percent+label",
                insidetextorientation="radial",
                hovertext=hover_texts,
            )
        ]

        fig = self.criar_grafico(dados, layout)
        return fig

    def criar_grafico_de_barras(
        self,
        legendas: List[str],
        valores: List[float],
        layout: go.Layout,
        hover_texts: List[str] = None,
    ) -> GraficoRetorno:
        y_min, y_max = self.definir_yaxis(valores)

        layout.yaxis.update(
            dtick=2000,
            range=[y_min, y_max],
            tickformat=",d",
        )

        dados = [
            go.Bar(
                x=legendas,
                y=valores,
                text=[str(Real(v)) for v in valores],
                textposition="auto",
                hovertext=hover_texts,
                marker=dict(
                    color=["lightgreen" if v > 0 else "lightcoral" for v in valores],
                ),
            )
        ]

        fig = self.criar_grafico(dados, layout)
        return fig

    def criar_grafico_barra_empilhada(
        self,
        dados: Dict[str, Any],
        periodos: List[str],
        layout: go.Layout = None,
        hover_texts: List[str] = None,
    ) -> GraficoRetorno:
        fig = go.Figure()

        receitas = [dados[periodo]["receitas"] for periodo in periodos]
        despesas = [dados[periodo]["despesas"] for periodo in periodos]

        fig.add_trace(
            go.Bar(
                x=periodos,
                y=receitas,
                text=[str(Real(v)) for v in receitas],
                name="Receitas",
                marker=dict(color="lightgreen"),
            )
        )

        fig.add_trace(
            go.Bar(
                x=periodos,
                y=despesas,
                text=[str(Real(v)) for v in despesas],
                name="Despesas",
                marker=dict(color="lightcoral"),
            )
        )

        fig.update_layout(
            barmode="relative",
            hovermode="closest",
            hoverlabel=dict(bgcolor="white", font_size=12, font_family="Arial"),
            width=1900,
            height=1200,
        )

        return self.criar_grafico(fig, layout)
