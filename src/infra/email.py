import os
import resend
import dotenv
from resend import Email

from src.dominio.usuario.entidade import Usuario

# Carregar variáveis de ambiente do arquivo .env
dotenv.load_dotenv("../../.env")

# HTML completo para o e-mail
html_content = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Obrigado por se cadastrar</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      background-color: #0d1321;
      color: #ffffff;
      margin: 0;
      padding: 0;
    }
    .button {
      display: inline-block;
      padding: 15px 30px;
      background-color: #2ed573; /* Cor de fundo do botão */
      color: #ffffff; /* Cor do texto */
      font-size: 16px;
      font-weight: bold;
      border: none;
      border-radius: 8px; /* Bordas arredondadas */
      text-align: center;
      text-decoration: none;
      cursor: pointer;
      box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1); /* Sombra para destacar */
      transition: background-color 0.3s ease, transform 0.2s ease; /* Animação ao interagir */
    }

    .button:hover {
      background-color: #28cc69; /* Cor de fundo ao passar o mouse */
      transform: scale(1.02); /* Leve aumento ao passar o mouse */
    }

    .button:active {
      background-color: #24b861; /* Cor de fundo ao clicar */
      transform: scale(0.98); /* Leve redução ao clicar */
    }
    .container {
      max-width: 600px;
      margin: 0 auto;
      padding: 20px;
      background-color: #17203a;
      border-radius: 10px;
    }
    .header {
      text-align: center;
      margin-bottom: 20px;
    }
    .header img {
      max-width: 150px;
    }
    .header h1 {
      color: #56db6b;
      font-size: 24px;
      margin-top: 10px;
    }
    .content {
      text-align: center;
      line-height: 1.6;
    }
    .content h2 {
      font-size: 20px;
      color: #ffffff;
    }
    .content p {
      font-size: 16px;
      color: #b0c4de;
    }
    .button {
      display: inline-block;
      margin-top: 20px;
      padding: 10px 20px;
      background-color: #56db6b;
      color: #ffffff;
      text-decoration: none;
      border-radius: 5px;
      font-size: 16px;
    }
    .footer {
      text-align: center;
      margin-top: 30px;
      font-size: 12px;
      color: #b0c4de;
    }
    .footer a {
      color: #56db6b;
      text-decoration: none;
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <img src="https://i.ibb.co/j8cs8W9/logo100.png" alt="Logo do Caderneta">
      <h1>Bem-vindo ao Caderneta!</h1>
    </div>
    <div class="content">
      <h2>Obrigado por se cadastrar!</h2>
      <p>Estamos muito felizes por ter você conosco, %s! A partir de agora, você terá acesso a uma maneira prática e intuitiva de gerenciar suas finanças pelo WhatsApp.</p>
      <p>Explore as funcionalidades que preparamos para você e comece a tomar controle das suas finanças de forma simples e eficiente.</p>
      <a class="button" href="https://wa.me/5594984033357">
        Comece agora!
      </a>
    </div>
    <div class="footer">
      <p>Se precisar de ajuda ou tiver dúvidas, estamos à disposição! Fale com a gente pelo e-mail <a href="mailto:cadernetapp@gmail.com">cadernetapp@gmail.com</a>.</p>
      <p>&copy; 2024 Caderneta. Todos os direitos reservados.</p>
    </div>
  </div>
</body>
</html>
"""

# Configurar a API key
resend.api_key = os.getenv("RESEND_API_KEY")


def enviar_email_boas_vindas(usuario: Usuario) -> Email:
    # Configurar parâmetros do e-mail
    params: resend.Emails.SendParams = {
        "from": "Caderneta <contato@caderneta.chat>",
        f"to": [{usuario.email}],
        "subject": "Bem-vindo à Caderneta!",
        "html": html_content % usuario.nome,
    }

    # Enviar e-mail
    email = resend.Emails.send(params)

    return email
