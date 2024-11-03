import logging
import os
from abc import ABC, abstractmethod
from datetime import datetime
from io import BytesIO
from typing import List, TypedDict, Literal, Any, Dict

from PIL import Image, ImageDraw, ImageFont
from plotly import graph_objects as go

from src.dominio.transacao.entidade import Real, Transacao
from src.dominio.transacao.tipos import TipoTransacao
import httpx

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("graficos")
STATIC = os.getenv("BUCKET")


class GraficoConfig:
    def __init__(self, titulo: str, formato: Literal["png", "svg", "html"] = "png"):
        self.titulo = titulo
        self.formato = formato


class GraficoRetorno(TypedDict):
    nome_arquivo: str
    formato: Literal["png", "svg", "html"]
    dados: bytes
    figura: go.Figure | None


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
            width=1000,
            height=700,
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
        hover_texts: List[str] | None = None,
    ):
        super().__init__(config)
        self.legendas: List[datetime] = legendas
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
            marker=dict(
                color=self.valores,
                size=12,
                colorscale=[[0, "red"], [0.5, "royalblue"], [1, "green"]],
            ),
            line=dict(color="royalblue", width=2),
        )

        layout = go.Layout(
            title={
                "text": f"{self.config.titulo} {self.legendas[0].strftime('%m/%Y')}",
                "x": 0.5,
                "xanchor": "center",
                "yanchor": "top",
                "y": 0.95,
            },
            hovermode="closest",
            hoverlabel=dict(bgcolor="white", font_size=12, font_family="Arial"),
            margin=dict(l=50, r=30, t=50, b=50),
            autosize=True,
            plot_bgcolor="rgba(240, 244, 250, 0.8)",
            xaxis=dict(
                showgrid=True,
                gridwidth=1,
                gridcolor="rgba(211, 211, 211, 0.6)",
                zeroline=True,
                zerolinewidth=1,
                zerolinecolor="lightgrey",
                tickformat="%d/%m",
                tickangle=-45,
                dtick="D1",
            ),
            yaxis=dict(
                showgrid=True,
                gridwidth=1,
                gridcolor="rgba(211, 211, 211, 0.6)",
                zeroline=True,
                zerolinewidth=1,
                zerolinecolor="lightgrey",
            ),
            height=500,
            width=800,
        )

        self.figura = go.Figure(data=[trace], layout=layout)

        self.figura.update_xaxes(automargin=True)
        self.figura.update_yaxes(automargin=True)

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

        if len(self.periodos) == 1:
            periodo = [datetime.strptime(self.periodos[0], "%Y-%m").strftime("%m/%Y")]
            largura = 0.5
        else:
            periodo = [datetime.strptime(periodo, "%Y-%m").strftime("%m/%Y") for periodo in self.periodos]
            largura = None

        trace_receitas = go.Bar(
            x=periodo,
            y=receitas,
            hoverinfo="text",
            name="Receitas",
            text=[str(Real(valor)) for valor in receitas],
            marker=dict(color="lightgreen"),
            width=largura,
        )
        trace_despesas = go.Bar(
            x=periodo,
            y=despesas,
            hoverinfo="text",
            name="Despesas",
            text=[str(Real(valor)) for valor in despesas],
            marker=dict(color="lightcoral"),
            width=largura,
        )

        layout = self._criar_layout_base()
        layout.update(
            barmode="relative",
            margin=dict(l=40, r=30, t=40, b=40),
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


class GraficoLucro(GraficoBase):
    def __init__(self, config: GraficoConfig, transacoes: List[Transacao]):
        super().__init__(config)
        self.transacoes = transacoes

    def criar(self) -> GraficoRetorno:
        vendas = sum(t.valor for t in self.transacoes if t.tipo == TipoTransacao.CREDITO)
        custos = sum(t.valor for t in self.transacoes if t.tipo == TipoTransacao.DEBITO)
        resultado = vendas - custos

        width = 800
        height = 700

        # Set the background color to light gray
        image = Image.new("RGBA", (width, height), (240, 240, 240, 255))
        draw = ImageDraw.Draw(image)

        # Attempt to load the font
        try:
            font_path = f"{STATIC}/fonts/InterTight-Bold.ttf"
            font_title = ImageFont.truetype(font_path, 20)
            font_venda_despesa = ImageFont.truetype(font_path, 25)
            font_lucro = ImageFont.truetype(font_path, 40)
        except Exception as erro:
            font_title = ImageFont.load_default()
            font_lucro = font_title
            font_venda_despesa = font_title

        # Center circle position
        center_x = width // 2
        center_y = height // 2 - 50
        radius = 180
        thickness = 40

        # Draw outer white circle as the background for the ring
        draw.ellipse(
            [
                (center_x - radius - thickness, center_y - radius - thickness),
                (center_x + radius + thickness, center_y + radius + thickness),
            ],
            fill="white",
        )

        # Draw the arc for profit and costs
        if vendas > 0:
            cost_angle = (custos / vendas) * 360
            profit_angle = ((vendas - custos) / vendas) * 360
        else:
            cost_angle = 0
            profit_angle = 0

        # Draw cost portion (red)
        if cost_angle > 0:
            draw.arc(
                [
                    (center_x - radius, center_y - radius),
                    (center_x + radius, center_y + radius),
                ],
                -90,
                -90 + cost_angle,
                fill="#ff4d4d",
                width=thickness,
            )

        # Draw profit portion (green)
        if profit_angle > 0:
            draw.arc(
                [
                    (center_x - radius, center_y - radius),
                    (center_x + radius, center_y + radius),
                ],
                -90 + cost_angle,
                -90 + cost_angle + profit_angle,
                fill="#4ade80",
                width=thickness,
            )

        # Draw center text
        title_text = "SEU LUCRO"
        value_text = f"{Real(resultado)}"
        title_bbox = draw.textbbox((0, 0), title_text, font=font_title)
        value_bbox = draw.textbbox((0, 0), value_text, font=font_lucro)
        title_x = center_x - (title_bbox[2] - title_bbox[0]) // 2
        title_y = center_y - 40
        value_x = center_x - (value_bbox[2] - value_bbox[0]) // 2
        value_y = center_y - 10
        draw.text((title_x, title_y), title_text, fill="#065f46", font=font_title)
        draw.text((value_x, value_y), value_text, fill="black", font=font_lucro)

        # Define box dimensions based on "VENDAS" box
        box_width = 200
        box_height = 80
        box_y = height - 150
        vendas_text_y = box_y - 40
        custos_text_y = box_y - 40

        # Vendas box (left)
        vendas_box = [(120, box_y), (120 + box_width, box_y + box_height)]
        draw.rounded_rectangle(vendas_box, fill="#25D364", outline="#d1fae5", radius=15)

        # Center the "VENDAS" text and value in the box
        vendas_center_x = (vendas_box[0][0] + vendas_box[1][0]) // 2
        vendas_center_y = (vendas_box[0][1] + vendas_box[1][1]) // 2
        draw.text(
            (vendas_center_x, vendas_center_y - 45),
            "VENDAS",
            fill="#065f46",
            font=font_title,
            anchor="ms",
        )
        draw.text(
            (vendas_center_x, vendas_center_y + 5),
            f"{Real(vendas)}",
            fill="#ecfdf5",
            font=font_venda_despesa,
            anchor="ms",
        )

        # Custos box (right)
        custos_x = width - 120 - box_width
        custos_box = [(custos_x, box_y), (custos_x + box_width, box_y + box_height)]
        draw.rounded_rectangle(custos_box, fill="#e73760", outline="#fee2e2", radius=15)

        # Center the "CUSTOS" text and value in the box
        custos_center_x = (custos_box[0][0] + custos_box[1][0]) // 2
        custos_center_y = (custos_box[0][1] + custos_box[1][1]) // 2
        draw.text(
            (custos_center_x, custos_center_y - 45),
            "CUSTOS",
            fill="#991b1b",
            font=font_title,
            anchor="ms",
        )
        draw.text(
            (custos_center_x, custos_center_y + 5),
            f"{Real(custos)}",
            fill="white",
            font=font_venda_despesa,
            anchor="ms",
        )

        img_bytes_io: BytesIO = BytesIO()
        image.save(img_bytes_io, format="PNG")
        bytes_imagem: bytes = img_bytes_io.getvalue()
        return self._retorno(bytes_imagem)

    def _retorno(self, img_byte_arr) -> GraficoRetorno:
        return {
            "nome_arquivo": self._gerar_nome_arquivo("lucro"),
            "formato": self.config.formato,
            "dados": img_byte_arr,
            "figura": None,
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
        elif tipo == "lucro":
            return GraficoLucro(config, **kwargs)
        else:
            raise ValueError(f"Tipo de gráfico não suportado: {tipo}")
