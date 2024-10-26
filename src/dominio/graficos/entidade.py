import logging
from abc import ABC, abstractmethod
from datetime import datetime
from io import BytesIO
from typing import List, TypedDict, Literal, Any, Dict

from plotly import graph_objects as go

from src.dominio.transacao.entidade import Real

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("graficos")


class GraficoConfig:
    def __init__(self, titulo: str, formato: Literal["png", "svg", "html"] = "html"):
        self.titulo = titulo
        self.formato = formato


class GraficoRetorno(TypedDict):
    nome_arquivo: str
    formato: Literal["png", "svg", "html"]
    dados: bytes
    figura: go.Figure


class IGrafico(ABC):
    @abstractmethod
    def criar(self) -> GraficoRetorno:
        pass


class GraficoBase(IGrafico):
    def __init__(self, config: GraficoConfig):
        self.config = config
        self.figura: go.Figure = None

    def _gerar_nome_arquivo(self, prefixo: str = "") -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_base = f"{prefixo}_{timestamp}" if prefixo else f"grafico_{timestamp}"
        return "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in nome_base)

    def _criar_layout_base(self) -> go.Layout:
        return go.Layout(
            title={
                "text": self.config.titulo,
                "x": 0.5,
                "xanchor": "center",
                "yanchor": "top",
            },
            hovermode="closest",
            hoverlabel=dict(bgcolor="white", font_size=12, font_family="Arial"),
        )

    def para_bytes(self) -> bytes:
        if self.figura is None:
            raise ValueError("Figura não foi criada. Chame criar() primeiro.")
        try:
            buffer = BytesIO()
            if self.config.formato == "html":
                buffer.write(self.figura.to_html().encode("utf-8"))
            else:
                buffer.write(self.figura.to_image(format=self.config.formato))
            buffer.seek(0)
            return buffer.getvalue()
        except Exception as e:
            logger.error(f"Erro ao gerar gráfico em bytes: {str(e)}")
            raise

    @abstractmethod
    def criar(self) -> GraficoRetorno:
        pass


class GraficoLinha(GraficoBase):
    def __init__(
        self,
        config: GraficoConfig,
        legendas: List[Any],
        valores: List[Any],
        hover_texts: List[str],
    ):
        super().__init__(config)
        self.legendas = legendas
        self.valores = valores
        self.hover_texts = hover_texts

    def criar(self) -> GraficoRetorno:
        trace = go.Scatter(
            x=self.legendas,
            y=self.valores,
            mode="lines+markers",
            name="Fluxo de Caixa",
            hovertext=self.hover_texts,
            hoverinfo="text",
            marker=dict(color=self.valores, size=12),
            line=dict(color="royalblue", width=2),
        )
        layout = self._criar_layout_base()
        self.figura = go.Figure(data=[trace], layout=layout)
        return self._retorno()

    def _retorno(self) -> GraficoRetorno:
        return {
            "nome_arquivo": self._gerar_nome_arquivo("linha"),
            "formato": self.config.formato,
            "dados": self.para_bytes(),
            "figura": self.figura,
        }


class GraficoPizza(GraficoBase):
    def __init__(
        self,
        config: GraficoConfig,
        legendas: List[str],
        valores: List[float],
        hover_texts: List[str],
    ):
        super().__init__(config)
        self.legendas = legendas
        self.valores = valores
        self.hover_texts = hover_texts

    def criar(self) -> GraficoRetorno:
        trace = go.Pie(
            labels=self.legendas,
            values=self.valores,
            hole=0.3,
            textinfo="percent+label",
            insidetextorientation="radial",
            hovertext=self.hover_texts,
        )
        layout = self._criar_layout_base()
        self.figura = go.Figure(data=[trace], layout=layout)
        return self._retorno()

    def _retorno(self) -> GraficoRetorno:
        return {
            "nome_arquivo": self._gerar_nome_arquivo("pizza"),
            "formato": self.config.formato,
            "dados": self.para_bytes(),
            "figura": self.figura,
        }


class GraficoBarras(GraficoBase):
    def __init__(
        self,
        config: GraficoConfig,
        legendas: List[str],
        valores: List[float],
        hover_texts: List[str],
    ):
        super().__init__(config)
        self.legendas = legendas
        self.valores = valores
        self.hover_texts = hover_texts

    def criar(self) -> GraficoRetorno:
        trace = go.Bar(
            x=self.legendas,
            y=self.valores,
            text=[str(Real(v)) for v in self.valores],
            textposition="auto",
            hovertext=self.hover_texts,
            marker=dict(
                color=["lightgreen" if v > 0 else "lightcoral" for v in self.valores],
            ),
        )
        layout = self._criar_layout_base()
        layout.update(yaxis=dict(tickformat=",d"))
        self.figura = go.Figure(data=[trace], layout=layout)
        return self._retorno()

    def _retorno(self) -> GraficoRetorno:
        return {
            "nome_arquivo": self._gerar_nome_arquivo("barras"),
            "formato": self.config.formato,
            "dados": self.para_bytes(),
            "figura": self.figura,
        }


class GraficoBarraEmpilhada(GraficoBase):
    def __init__(self, config: GraficoConfig, legendas: List, valores: Dict[str, Any]):
        super().__init__(config)
        self.dados = valores
        self.periodos = legendas

    def criar(self) -> GraficoRetorno:
        receitas = [self.dados[periodo]["receitas"] for periodo in self.periodos]
        despesas = [self.dados[periodo]["despesas"] for periodo in self.periodos]

        trace_receitas = go.Bar(
            x=self.periodos,
            y=receitas,
            hoverinfo="text",
            name="Receitas",
            text=[str(Real(valor)) for valor in receitas],
            marker=dict(color="lightgreen"),
        )
        trace_despesas = go.Bar(
            x=self.periodos,
            y=despesas,
            hoverinfo="text",
            name="Despesas",
            text=[str(Real(valor)) for valor in despesas],
            marker=dict(color="lightcoral"),
        )

        layout = self._criar_layout_base()
        layout.update(
            barmode="relative",
        )

        self.figura = go.Figure(data=[trace_receitas, trace_despesas], layout=layout)
        return self._retorno()

    def _retorno(self) -> GraficoRetorno:
        return {
            "nome_arquivo": self._gerar_nome_arquivo("barra_empilhada"),
            "formato": self.config.formato,
            "dados": self.para_bytes(),
            "figura": self.figura,
        }


class GraficoFactory:
    @staticmethod
    def criar_grafico(tipo: str, config: GraficoConfig, **kwargs) -> IGrafico:
        if tipo == "linha":
            return GraficoLinha(config, **kwargs)
        elif tipo == "pizza":
            return GraficoPizza(config, **kwargs)
        elif tipo == "barras":
            return GraficoBarras(config, **kwargs)
        elif tipo == "barra_empilhada":
            return GraficoBarraEmpilhada(config, **kwargs)
        else:
            raise ValueError(f"Tipo de gráfico não suportado: {tipo}")
