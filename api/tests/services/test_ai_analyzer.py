import pytest
from app.services.ai_analyzer import analyze_text

@pytest.mark.asyncio
@pytest.mark.parametrize("descricao, texto, resultado_esperado", [
    (
        "CPF sem pontos e endereço",
        "Solicito a documentação de Julio Cesar Rosa (CPF 12918012206) referente ao contrato de locação do imóvel na Rua das Palmeiras 450. O documento é urgente para fins de comprovação de residência conforme solicitado.",
        "PRIVATE"
    ),
    (
        "Email e Celular grudados",
        "Entrar em contato com mariao_silva@gmail.com ou pelo cel 61988776655 para tratar da limpeza do lote vago no Gama-DF. Aguardo retorno o mais breve possível para agendar a visita técnica.",
        "PRIVATE"
    ),
    (
        "RG com erro de dígito",
        "Prezados, informo que meu rg é 3.456.78x expedido pela ssp df. Gostaria de saber se este documento é válido para a retirada da certidão negativa que solicitei na semana passada via portal.",
        "PRIVATE"
    ),
    (
        "Endereço residencial específico",
        "Existe um vazamento na Rua 15 de Novembro, n 10, apto 202, Ed. Horizonte. A água está escorrendo pela escada do prédio e pode atingir a fiação elétrica. Solicito reparo imediato da Caesb.",
        "PUBLIC"
    ),
    (
        "Texto público sem PII",
        "Prezados, favor analisar o processo 001.234/2023 sobre a iluminação pública da Praça do Relógio em Taguatinga. Muitos postes estão apagados, gerando insegurança para os moradores da região.",
        "PUBLIC"
    ),
    (
        "Nome e OAB",
        "Eu, Jorge Luiz, OAB-SP 14123, venho requerer cópia integral dos autos do processo administrativo citado acima. Atuo como representante legal da parte interessada e preciso dos dados para defesa.",
        "PRIVATE"
    ),
    (
        "Sigla e número sem espaço",
        "O consumo registrado no meu cpf12345678901 veio muito alto este mês. Gostaria de uma revisão da leitura do hidrômetro, pois a casa ficou vazia durante todo o período de férias em janeiro.",
        "PRIVATE"
    ),
    (
        "Assinatura com nome completo",
        "Solicito a lista de aprovados no concurso da SES-DF conforme edital 85/2009. Gostaria de saber a nota de corte para o cargo de técnico administrativo. Atenciosamente, Jorge Luiz Pereira Vieira.",
        "PRIVATE"
    ),
    (
        "WhatsApp com gíria",
        "Preciso que mande o boleto atualizado para o zap 89341801890. O e-mail que está cadastrado eu não consigo mais acessar e preciso pagar a conta antes do vencimento para não gerar multa.",
        "PRIVATE"
    ),
    (
        "Nome associado a local",
        "Mudei para a casa da minha tia Maria Silva na quadra 10 do Gama. Preciso transferir a conta de luz para o meu nome e atualizar o endereço de cobrança para que as faturas cheguem corretamente.",
        "PRIVATE"
    )
])
async def test_casos_rigorosos_edital(descricao, texto, resultado_esperado):
    print(f"\nExecutando: {descricao}")
    
    result = await analyze_text(texto)
    
    assert result["result"] == resultado_esperado, \
        f"Erro no caso '{descricao}': Esperava {resultado_esperado} mas obteve {result['result']}. Detalhes: {result['details']}"