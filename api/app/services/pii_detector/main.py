from scanner import PIIScanner

def main():
    scanner = PIIScanner()

    test_text = """
    O sr. Carlos tem a CNH número 98048995304.
    Ele dirige o caminhão de placa GRA-1234, mas as vezes usa a moto placa MER1C23.
    O RENAVAM do caminhão é 00639884965. 
    Nota: O antigo renavam 11111111111 parece errado (dígito inválido).

    O CPF do titular é 704.167.350-20. 
    Em alguns lugares digitaram sem ponto: 70416735020.
    Cuidado, pois temos um CPF falso na base: 123.456.789-00 (esse não deve passar!).
    O PIS dele para o abono é 120.5235.347-6.
    Título de Eleitor para votação: 063462630329.

    O número do cartão CNS é 700001854833215.
    Favor verificar no cadastro do hospital.

    A empresa contratante é a Google Brasil, CNPJ 06.990.590/0001-23.
    Outro CNPJ que apareceu foi o 33649575000199 (sem formatação).

    O e-mail para login é: admin.suporte@empresa.com.br
    Para o primeiro acesso, a senha é: Segredo@2024!
    Não compartilhar a senha provisória.
    """

    resultados = scanner.analyze_text(test_text)

    for res in resultados:
        texto_encontrado = test_text[res.start:res.end]
        print(f"Tipo: {res.entity_type:15} | Score: {res.score:.2f} | Valor: '{texto_encontrado}'")

    resultado_anonimizado = scanner.anonymize_text(test_text, resultados)
    print(f"\nTEXTO ANONIMIZADO\n{resultado_anonimizado.text}")

if __name__ == "__main__":
    main()