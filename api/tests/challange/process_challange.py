import pandas as pd
import asyncio
import tqdm.asyncio
import csv
import os
from dotenv import load_dotenv
load_dotenv()
from app.services.ai_analyzer import analyze_text

async def process_csv():
    base_path = os.path.dirname(__file__)

    input_file = os.path.join(base_path, "files", "AMOSTRA_e-SIC.csv")
    output_file = os.path.join(base_path, "files", "analysis_result.csv")

    if not os.path.exists(input_file):
        print(f"Arquivo {input_file} não encontrado!")
        return
    
    
    try:
        df = pd.read_csv(input_file, encoding='utf-8', quotechar='"', on_bad_lines='warn', engine='python')
    except Exception as e:
        print(f"Erro crítico na leitura: {e}")
        return

    coluna_texto = 'Texto Mascarado' if 'Texto Mascarado' in df.columns else 'Texto'
    
    df[coluna_texto] = df[coluna_texto].fillna("").astype(str).str.replace(r'\r+|\n+|\t+', ' ', regex=True).str.strip()

    results = []

    print(f"Analisando {len(df)} registros...")
    for index, row in tqdm.asyncio.tqdm(df.iterrows(), total=len(df)):
        text = row[coluna_texto]
        id_msg = row['ID']
        
        try:
            analysis = await analyze_text(text)
            
            results.append({
                "ID": id_msg,
                "Classificacao": analysis['result'],
                "Detalhes": analysis['details']
            })
        except Exception as e:
            results.append({
                "ID": id_msg,
                "Classificacao": "ERRO",
                "Detalhes": f"Erro no processamento: {str(e)}"
            })

    df_output = pd.DataFrame(results)
    df_output.to_csv(
        output_file, 
        index=False, 
        encoding='utf-8-sig', 
        quoting=csv.QUOTE_ALL,
        sep=','
    )
    
    print(f"\nConcluído! Relatório gerado: {output_file}")

if __name__ == "__main__":
    asyncio.run(process_csv())