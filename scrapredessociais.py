import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pandas
import re
import os
import csv

import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup

def encontrar_redes_sociais(company):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        if '@' in company['correio_eletronico']:
            domain = company['correio_eletronico'].split('@')[1]
        else:
            domain = company['correio_eletronico']
        url = f"https://{domain}"
        response = requests.get(url, headers=headers, timeout=10, verify=False)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        page_text = soup.get_text()
        
        contact_types = {
            'facebook': set(),
            'twitter': set(),
            'instagram': set(),
            'linkedin': set(),
            'youtube': set(),
            'tiktok': set(),
            'telefone': set(),
            'cep': set()
        }
        
        for link in soup.find_all('a', href=True):
            href = link['href'].lower()
            link_completo = urljoin(url, href)
            
            if len(link_completo) < 70:
                if 'facebook.com' in href:
                    contact_types['facebook'].add(link_completo)
                elif 'twitter.com' in href or 'x.com/' in href:
                    contact_types['twitter'].add(link_completo)
                elif 'instagram.com' in href:
                    if 'instagram.com/p/' in href or 'instagram.com/reel' in href:
                        continue
                    else:
                        contact_types['instagram'].add(link_completo)
                elif 'linkedin.com' in href:
                    contact_types['linkedin'].add(link_completo)
                elif 'youtube.com' in href or 'youtu.be' in href:
                    contact_types['youtube'].add(link_completo)
                elif 'tiktok.com' in href:
                    contact_types['tiktok'].add(link_completo)
                elif 'tel:' in href or 'whatsapp' in href:
                    numeros = re.findall(r'\d+', href)
                    if numeros:
                        telefone = ''.join(numeros)
                        contact_types['telefone'].add(telefone)               
            else:
                continue
            
            ceps_no_texto = re.findall(r'\b\d{5}-?\d{3}\b', page_text)
            for cep in ceps_no_texto:
                contact_types['cep'].add(cep)
        file_path = 'data/TAB2.csv'
        file_exists = os.path.exists(file_path) and os.path.getsize(file_path) > 0
        with open(file_path, mode="a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(["cnpj_basico", "cnpj_dv", "cnpj_ordem", "razao_social", "correio_eletronico", "tipo_contato", "contato", "numero"])

            for type in contact_types:
                for contact in contact_types[type]:
                    writer.writerow([company['cnpj_basico'], company['cnpj_dv'], company['cnpj_ordem'], company['razao_social'], company['correio_eletronico'], type, contact, company['numero']])
            return 
    
    except Exception as e:
        print(f"Erro ao processar {company['correio_eletronico']}: {str(e)}")
        return company

    
def load_info_from_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        search_info = pandas.read_csv(file)
    last_company = get_last_company()
    companies = [] 
    for _, company in search_info.iterrows():
        if int(company["numero"]) <= last_company:
            continue
        else:
            company = {
                'cnpj_basico' : company["cnpj_basico"],
                'cnpj_dv' : company["cnpj_dv"],
                'cnpj_ordem' : company["cnpj_ordem"],
                'razao_social' : company["razao_social"],
                'correio_eletronico' : company["correio_eletronico"],
                'tipo_contato' : '',
                'contato' : '',
                'numero' : company["numero"]
            }
            companies.append(company)
    return companies

def save_load(file_path):
    # Lendo o arquivo CSV
    search_info = pandas.read_csv(file_path, encoding='utf-8')
    
    companies = []
    for _, row in search_info.iterrows():  # Note o uso de _ para o índice que não será usado
        company = {
            'cnpj_basico': row["cnpj_basico"],
            'cnpj_dv': row["cnpj_dv"],
            'cnpj_ordem': row["cnpj_ordem"],
            'razao_social': row["razao_social"],
            'correio_eletronico': row["correio_eletronico"],
            'tipo_contato': row["tipo_contato"],
            'contato': row["contato"],
            'numero': row["numero"]
        }
        companies.append(company)
    
    # Invertendo a lista
    companies = companies[::-1]
    
    # Escrevendo de volta no arquivo
    with open(file_path, "w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=companies[0].keys())
        writer.writeheader()
        writer.writerows(companies)
        
def save_redes_sociais_to_csv(empresa):
    output = 'data/TAB2.csv'
    os.makedirs(os.path.dirname(output), exist_ok=True)
    existing_data = []
    if os.path.exists(output) and os.path.getsize(output) > 0:
        with open(output, "r", encoding="utf-8", newline='') as csv_file:
            reader = csv.DictReader(csv_file)
            existing_data = list(reader)
    
    if isinstance(empresa, list):
        existing_data.extend(empresa)
    else:
        existing_data.append(empresa)
    
    with open(output, "w", encoding="utf-8", newline='') as csv_file:
        if existing_data:
            fieldnames = existing_data[0].keys()
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(existing_data)
        print("Data saved")

def get_last_company():
    output = 'data/TAB2.csv'
    if os.path.exists(output) and os.path.getsize(output) > 0:
        with open(output, "r", encoding="utf-8") as csv_file:
            try:
                data = pandas.read_csv(csv_file)
                if len(data) == 0:
                    return 0
                last_number = data.iloc[-1]["numero"]
                return last_number
            except pandas.errors.EmptyDataError:
                return 0
    else:
        return 0
    
def add_number_to_companies():
    input = 'TAB1.csv'
    output = 'TAB1.csv'
    if os.path.exists(input) and os.path.getsize(input) > 0:
        with open(input, "r", encoding="utf-8") as csv_file:
            reader = csv.DictReader(csv_file)
            data = list(reader)
    number = 1
    for row in data:
        row["numero"] = number
        number += 1
    with open(output, "w", encoding="utf-8", newline='') as csv_file:
        fieldnames = data[0].keys()
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

def main():
    
    companies = load_info_from_file("TAB1.csv")
        
    for company in companies:
        print(f"\nRedes sociais para {company['razao_social']}:")
        encontrar_redes_sociais(company)
        
if __name__ == "__main__":
    main()