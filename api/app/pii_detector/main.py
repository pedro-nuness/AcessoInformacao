from scanner import PIIScanner

def main():
    scanner = PIIScanner()

    test_text = """
    Relatório de Incidente:
    Ocorreu um acidente com o veículo de placa ABC-1234.
    O suspeito fugiu no Fiat Uno, placa ABC1C34.
    O CPF do envolvido é 123.456.789-00
    Contato: joao.silva@email.com.
    Para acessar o sistema, a senha: SuperSecreta123!. Mas essa parte aaqui não é uma senha ok?
    Para acessar o sistema: ph050206
    O nome do solicitante é Maria Souza.
    """

    resultados = scanner.analyze_text(test_text)

    for res in resultados:
        texto_encontrado = test_text[res.start:res.end]
        print(f"Tipo: {res.entity_type:15} | Score: {res.score:.2f} | Valor: '{texto_encontrado}'")

    resultado_anonimizado = scanner.anonymize_text(test_text, resultados)
    print(f"\nTEXTO ANONIMIZADO\n{resultado_anonimizado.text}")

if __name__ == "__main__":
    main()