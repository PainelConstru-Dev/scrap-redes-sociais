import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from bs4 import BeautifulSoup
import pandas as pd
import random
import os

driver = webdriver.Firefox()

def get_last_email():
    output = 'TAB1_WHO.csv'
    if os.path.exists(output) and os.path.getsize(output) > 0:
        with open(output, "r", encoding="utf-8") as csv_file:
            try:
                data = pd.read_csv(csv_file)
                if len(data) == 0:
                    return 0
                last_number = data.iloc[-1]["Numero"]
                return last_number
            except (pd.errors.EmptyDataError, KeyError):
                return 0
    else:
        return 0

input_csv = "TAB1.csv" 
output_csv = "TAB1_WHO.csv"

try:
    df = pd.read_csv(input_csv)
except Exception as e:
    print(f"Erro ao ler o arquivo CSV de entrada: {str(e)}")
    driver.quit()
    exit()

last_email = get_last_email()
filtered_df = df[df['numero'] > last_email]

# Obter lista de emails e números correspondentes
# Aqui usamos zip para iterar sobre ambos simultaneamente
email_number_pairs = filtered_df[['correio_eletronico', 'numero']].dropna().values.tolist()

if not email_number_pairs:
    print("Nenhum novo email para processar.")
    driver.quit()
    exit()

try:
    driver.get("https://registro.br/tecnologia/ferramentas/whois/")
    time.sleep(5)

    file_exists = os.path.exists(output_csv) and os.path.getsize(output_csv) > 0

    with open(output_csv, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        
        if not file_exists:
            writer.writerow(["Email", "Domínio", "Responsáveis", "Owner", "Criado em", 
                            "Atualizado em", "Status", "Emails", "Numero"])

        for email, numero in email_number_pairs:   
            domain = email.split('@')[-1]
            
            try:
                search_field = driver.find_element(By.ID, "whois-field")
                search_field.clear()  
                search_field.send_keys(domain)
                search_field.send_keys(Keys.RETURN)

                time.sleep(random.randint(5, 10))

                page_source = driver.page_source
                soup = BeautifulSoup(page_source, 'html.parser')

                owner_info = soup.find('td', {'class': 'cell-owner'})
                createdat_info = soup.find('td', {'class': 'cell-createdat'})
                updatedat_info = soup.find('td', {'class': 'cell-updatedat'})
                status_info = soup.find('td', {'class': 'cell-status'})
                email_info = soup.find_all('td', {'class': 'cell-emails'})
                persons_info = soup.find_all('td', {'class': 'cell-persons'})

                owner_name = owner_info.get_text(strip=True) if owner_info else "Owner não encontrado"
                createdat_name = createdat_info.get_text(strip=True) if createdat_info else "Data de criação não encontrada"
                updatedat_name = updatedat_info.get_text(strip=True) if updatedat_info else "Data de atualização não encontrada"
                status_name = status_info.get_text(strip=True) if status_info else "Status não encontrado"

                persons = [person.get_text(strip=True) for person in persons_info]
                persons_name = ", ".join([f"Responsável {i+1}: {p}" for i, p in enumerate(persons)]) if persons else "Pessoas não encontradas"

                emails_found = [email_found.get_text(strip=True) for email_found in email_info]
                email_name = ", ".join([f"Email {i+1}: {e}" for i, e in enumerate(emails_found)]) if emails_found else "Email(s) não encontrado(s)"

                writer.writerow([email, domain, persons_name, owner_name, createdat_name, 
                               updatedat_name, status_name, email_name, numero])

                print(f"Email: {email}, Número: {numero}, Domínio: {domain}, {persons_name}, Owner: {owner_name}, "
                      f"Created at: {createdat_name}, Updated at: {updatedat_name}, Status: {status_name}, {email_name}")
            
            except Exception as e:
                print(f"Erro ao processar {email}: {str(e)}")
                writer.writerow([email, domain, "NULL", "NULL", "NULL", "NULL", "NULL", f"Erro: {str(e)}", numero])
                continue

except Exception as e:
    print(f"Erro geral no processamento: {str(e)}")
finally:
    driver.quit()

print(f"Os dados foram salvos no arquivo '{output_csv}'.")