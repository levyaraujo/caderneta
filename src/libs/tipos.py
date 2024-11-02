from datetime import datetime
from typing import Optional


class Intervalo:
    def __init__(self, inicio: datetime, fim: datetime):
        """
        Inicializa um novo intervalo.

        Args:
            inicio: Valor inicial do intervalo.
            fim: Valor final do intervalo.

        Raises:
            ValueError: Se o valor inicial for maior que o valor final.
        """
        if inicio > fim:
            raise ValueError("O início deve ser menor ou igual ao fim do intervalo.")
        self.inicio = inicio
        self.fim = fim

    def __repr__(self) -> str:
        """Retorna uma representação em string do intervalo."""
        return f"Intervalo({self.inicio}, {self.fim})"

    def contem(self, valor) -> bool:
        """Verifica se um valor está contido no intervalo.

        Args:
            valor: Valor a ser verificado.

        Returns:
            bool: True se o valor estiver contido, False caso contrário.
        """
        return self.inicio <= valor <= self.fim

    def interseccao(self, outro_intervalo) -> Optional["Intervalo"]:
        """Calcula a interseção entre dois intervalos.

        Args:
            outro_intervalo: Outro objeto Intervalo.

        Returns:
            Intervalo: O intervalo resultante da interseção, ou None se não houver interseção.
        """
        if self.fim < outro_intervalo.inicio or outro_intervalo.fim < self.inicio:
            return None
        return Intervalo(
            max(self.inicio, outro_intervalo.inicio), min(self.fim, outro_intervalo.fim)
        )

    def uniao(self, outro_intervalo) -> Optional["Intervalo"]:
        """Calcula a união entre dois intervalos.

        Args:
            outro_intervalo: Outro objeto Intervalo.

        Returns:
            Intervalo: O intervalo resultante da união, ou None se os intervalos forem disjuntos.
        """
        if self.interseccao(outro_intervalo) is None:
            return None
        return Intervalo(
            min(self.inicio, outro_intervalo.inicio), max(self.fim, outro_intervalo.fim)
        )
