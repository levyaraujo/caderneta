import logging
import os
from datetime import datetime
from pathlib import Path
from typing import List
import locale

from plotly import graph_objects as go
import plotly.express as px

from src.dominio.transacao.entidade import Transacao
from src.dominio.transacao.tipos import TipoTransacao
from src.dominio.usuario.entidade import Usuario
from src.libs.tipos import Intervalo
from src.utils.transacoes import criar_transacoes_para_mes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")


class GraficoBase:
    def __init__(
        self, titulo: str, bucket: str = os.getenv("BUCKET_PATH", "/tmp/caderneta")
    ):
        self.titulo = titulo
        self.output_folder = f"{bucket}/graficos"
        logger.info(
            f"Inicializando GraficoBase com pasta de saída: {self.output_folder}"
        )
        self._criar_pasta_se_nao_existe()

    def _criar_pasta_se_nao_existe(self):
        try:
            Path(self.output_folder).mkdir(parents=True, exist_ok=True)
            logger.info(f"Pasta criada/verificada: {self.output_folder}")
        except Exception as e:
            logger.error(f"Erro ao criar pasta {self.output_folder}: {str(e)}")
            raise

    def _gerar_nome_arquivo(self, prefixo: str = "") -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_base = (
            f"{prefixo}_{self.titulo}_{timestamp}"
            if prefixo
            else f"{self.titulo}_{timestamp}"
        )
        nome_arquivo = "".join(
            c if c.isalnum() or c in ("-", "_") else "_" for c in nome_base
        )
        return nome_arquivo

    def criar_grafico(self, dados, layout):
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
            return fig
        except Exception as e:
            logger.error(f"Erro ao criar gráfico: {str(e)}")
            raise

    def salvar_grafico(self, fig, formato: str = "html", prefixo: str = ""):
        try:
            nome_arquivo = self._gerar_nome_arquivo(prefixo)
            caminho_completo = os.path.join(
                self.output_folder, f"{nome_arquivo}.{formato}"
            )
            logger.info(f"Tentando salvar gráfico em: {caminho_completo}")

            if formato == "html":
                fig.write_html(caminho_completo)
            else:
                fig.write_image(caminho_completo)

            logger.info(f"Gráfico salvo com sucesso em: {caminho_completo}")
            return caminho_completo
        except Exception as e:
            logger.error(f"Erro ao salvar gráfico: {str(e)}")
            raise


class GraficoFluxoCaixa(GraficoBase):
    def __init__(self, titulo: str, bucket: str = "/tmp/caderneta"):
        super().__init__(titulo, bucket)

    def criar_grafico_fluxo_caixa(
        self, transacoes: List[Transacao], intervalo: Intervalo
    ):
        try:
            logger.info(
                f"Criando gráfico de fluxo de caixa para intervalo: {intervalo}"
            )

            transacoes_no_periodo = [
                transacao
                for transacao in transacoes
                if intervalo.contem(transacao.caixa)
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
                + f"Valor: R$ {abs(transacao.valor):.2f}<br>"
                + f"Tipo: {transacao.tipo.value}<br>"
                + f"Destino: {transacao.destino}<br>"
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

            self.titulo = f"Fluxo de Caixa de {intervalo.inicio.strftime('%d/%m/%Y')} a {intervalo.fim.strftime('%d/%m/%Y')}"

            fig = self.criar_grafico(dados, layout)
            return fig

        except Exception as e:
            logger.error(f"Erro ao criar gráfico de fluxo de caixa: {str(e)}")
            raise


class GraficoLucro(GraficoBase):
    def __init__(self, titulo: str, bucket: str = "/tmp/caderneta"):
        super().__init__(titulo, bucket)

    def criar_grafico_lucro(self, transacoes: List[Transacao], intervalo: Intervalo):
        try:
            logger.info(f"Criando gráfico de lucro para intervalo: {intervalo}")

            transacoes_no_periodo = [
                transacao
                for transacao in transacoes
                if intervalo.contem(transacao.caixa)
            ]
            logger.info(
                f"Número de transações no período: {len(transacoes_no_periodo)}"
            )
            valores = [
                transacao.valor
                if transacao.tipo == TipoTransacao.CREDITO
                else -transacao.valor
                for transacao in transacoes_no_periodo
            ]
            despesas = sum(valor for valor in valores if valor < 0)
            receitas = sum(valor for valor in valores if valor > 0)

            lucro = sum(valores)
            logger.info(f"Lucro calculado: R$ {lucro:.2f}")

            grafico = px.pie(
                values=[despesas, receitas], names=["Despesas", "Receitas"]
            )
            grafico.show()

        except Exception as e:
            logger.error(f"Erro ao criar gráfico de lucro: {str(e)}")
            raise


# # Exemplo de uso
if __name__ == "__main__":
    try:
        grafico = GraficoLucro("Lucro")
        usuario = Usuario(
            id=1,
            nome="Usuario",
            sobrenome="Teste",
            email="teste@gmail.com",
            senha="123456",
            telefone="94984033357",
        )

        fig = grafico.criar_grafico_lucro(
            criar_transacoes_para_mes(usuario=usuario, ano=2024, mes=9),
            intervalo=Intervalo(datetime(2024, 9, 1), datetime(2024, 9, 30)),
        )

        caminho_arquivo = grafico.salvar_grafico(fig, formato="html")
        logger.info(f"Arquivo salvo em: {caminho_arquivo}")

    except Exception as e:
        logger.error(f"Erro na execução principal: {str(e)}")
