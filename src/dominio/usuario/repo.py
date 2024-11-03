from src.dominio.usuario.entidade import Usuario
from src.infra.database.repo import RepoLeitura, RepoEscrita


class RepoUsuarioLeitura(RepoLeitura):
    def buscar_por_email(self, email: str):
        return self.session.query(Usuario).filter(Usuario.email == email).first()

    def buscar_por_telefone(self, telefone: str):
        return self.session.query(Usuario).filter(Usuario.telefone == telefone).first()

    def buscar_por_id(self, id: int):
        return self.session.query(Usuario).filter(Usuario.id == id).first()

    def buscar_por_email_e_senha(self, email: str, senha: str):
        return self.session.query(Usuario).filter(Usuario.email == email, Usuario.senha == senha).first()
