import requests
from bs4 import BeautifulSoup
import smtplib
import ssl
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from pdfminer.high_level import extract_text

# -------------------------------------------
# CONFIGURAÇÕES DO USUÁRIO
# -------------------------------------------

NOME_PROCURADO = "Jefferson dos Santos de Jesus"
EMAIL_DESTINO = "jeffersonjesus.ds@gmail.com"

EMAIL_ORIGEM = "jeffersonjesus.ds@gmail.com"
EMAIL_SENHA = "vcuq wrpn zwrq wajr"  # senha de app

INTERVALO = 3600  # 1 hora


# -------------------------------------------
# FUNÇÃO PARA ENVIAR E-MAIL
# -------------------------------------------
def enviar_email(mensagem):
    msg = MIMEMultipart()
    msg["From"] = EMAIL_ORIGEM
    msg["To"] = EMAIL_DESTINO
    msg["Subject"] = "⚠ ALERTA: Nome encontrado no Diário Oficial da Bahia"

    msg.attach(MIMEText(mensagem, "plain"))

    contexto = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=contexto) as servidor:
        servidor.login(EMAIL_ORIGEM, EMAIL_SENHA)
        servidor.sendmail(EMAIL_ORIGEM, EMAIL_DESTINO, msg.as_string())


# -------------------------------------------
# FUNÇÃO PARA BAIXAR E LER PDFs
# -------------------------------------------
def verificar_pdf(url_pdf):
    try:
        r = requests.get(url_pdf, timeout=15, verify=False)
        if r.status_code != 200:
            return False

        # Salva temporariamente
        with open("temp.pdf", "wb") as f:
            f.write(r.content)

        texto = extract_text("temp.pdf")

        return NOME_PROCURADO.lower() in texto.lower()

    except Exception as e:
        print(f"[ERRO PDF] {e}")
        return False


# -------------------------------------------
# GERA URLs DOS PDFs DOS ÚLTIMOS 7 DIAS
# -------------------------------------------
def gerar_urls_pdf():
    urls = []
    hoje = datetime.now()

    for i in range(7):
        dia = hoje - timedelta(days=i)
        dia_s = dia.strftime("%d")
        mes_s = dia.strftime("%m")
        ano_s = dia.strftime("%Y")

        url = f"https://www.egba.ba.gov.br/wp-content/uploads/{ano_s}/{mes_s}/DOO-{dia_s}-{mes_s}-{ano_s}.pdf"
        urls.append(url)

    return urls


# -------------------------------------------
# FUNÇÃO PRINCIPAL
# -------------------------------------------
def monitorar():
    print("🔍 Verificando PDFs dos últimos 7 dias...")

    urls = gerar_urls_pdf()

    for url in urls:
        print(f"📄 Checando: {url}")

        if verificar_pdf(url):
            print("⚠ NOME ENCONTRADO! Enviando alerta...")
            enviar_email(f"Seu nome apareceu no Diário Oficial da Bahia:\n\n{url}")
            return True

    print("Nenhuma ocorrência encontrada.")
    return False


# -------------------------------------------
# LOOP INFINITO
# -------------------------------------------
print("🔥 Monitor de PDFs do Diário Oficial INICIADO!")

while True:
    monitorar()
    time.sleep(INTERVALO)
