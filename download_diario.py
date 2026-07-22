import requests

url = "https://cidadao.saocarlos.sp.gov.br/servicos/jornal/"

html = requests.get(url)

print(html.status_code)