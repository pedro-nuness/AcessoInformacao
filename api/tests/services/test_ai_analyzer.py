import pytest
import asyncio
from app.services.ai_analyzer import analyze_text


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
    ),
    (
        "Amostra ID 2",
        "Gostaria de saber da defensoria se q irão implementar o reajuste no auxílio saúde, pois houve uma mudança na faixa de valores da minha dependente, pois ela mudou de idade. No entanto, não percebi ainda nenhum reajuste no repasse,  mesmo a mensalidade aumentando.",
        "PUBLIC"
    ),
    (
        "Amostra ID 3",
        "Oi estou chateada o meu companheiro está estranho por e-mail passando a empresa ele este queimado ele, na verdade, a consciência de se  cuidar, de sua saúde emocional informado de direitos e deveres, de seu pé, seu cróxis e pé e cuidado de seus filhos pais e respeita ex casa ele promove destruição põe sentir no direito familiar e ameça de perda destruir a companheira e perda causa até agora pela só perdeu e causa está perdida, pois a companheira não e ouvida e ponto de criança pedir para sair ele pegar o talão de energia e quase na cara mesma  ele se apresenta alterado e coloca a empresa a ponto de julgar a estrita e não atenção na ideia colocada e dificuldade que enfrentou para escrita ela esta em causa especial ela fica cansada .",
        "PUBLIC"
    ),
    (
        "Amostra ID 28",
        "Prezados, entro em contato requerendo acesso no autos do processo de nº 0315-000009878/2023-15 conforme procuração em anexo.   Informo que já houve a solicitação anteriormente onde fui orientado a criar um usuário externo, entretanto, até a presente data não fui habilitado a acessar os autos.   Ao entrar em contato com o DF LEGAL fui orientado a requerer novamente a solicitação e informar o usuário externo.  Portanto passo as seguintes informações:  Nome do requerente: Roberto Carlos Pereira Nome da parte representada: Antônio Garcia Soares CPF: 141.161.100-51 E-mail: carlos.prr@ho.con   Atenciosamente,  Roberto Carlos Pereira",
        "PRIVATE"
    ),
    (
        "Amostra ID 30",
        "Solicito informação a respeito da existência bens tombados a nível distrital que possam gerar área envoltória e/ou restrições urbanísticas para novas construções que possam atingir o imóvel de interesse localizado no seguinte endereço: Comercial II, Rua 41, Lo 20, CEP 20031 - 900, com inscrição imobiliária nº 78965412  e matrícula nº 654.789 8ºRI. A informação é para fins de Estudo de Viabilidade Técnica e Legal - EVTL para empreendimento comercial.",
        "PUBLIC"
    ),
    (
        "Amotra ID 99",
        "Denúncia - e-Ouvidoria Canal de comunicação entre o cidadão e a administração pública.  PROTOCOLO: 000254.2012-56   Informações do Pedido Razão Social: gestaojaira_ CNPJ: 48.236.147/0001-89 E-mail: feito10@press.so   Secretaria: Contoladoria Geral Assunto: ASSÉDIO Data Pedido: 31/11/2012 Bairro Hortolândia Prazo de atendimento: 28/03/2024 Localização: Ministério Público do SP   Descrição: CARTA PRECATÓRIA PARA TABOÃO DA SERRA. PARA QUE NÃO EXISTA ESBULHO OU ASSÉDIO MORAL: DENUNCIA LIGAÇÕES TELEFÔNICAS MUDAS. OCORRÊNCIA REGISTRADO NAS DELEGACIAS.   COMUNICADO DO CIDADÃO CPF 551.169.500-18. Eduardo da Costa Barbosa (13/03/1956). Nascimento em Brasília, Distrito Federal. Número do telefone (95)99149-2006 e Whatsapp (97)99201-2009. Nome social (se for o caso); Nome da mãe e do pai; funcionária pública Pablo da Vitória Simões. Endereço residência à Avenida São Luís 333 Taboão da Serra SP CEP 29. 192 - 170. Condomínio Municipal Hélio Silva Campos  * Motivo do pedido: Solicitação de providências após o registro de inúmeros e diversos boletins de ocorrências. VENDA DO IMÓVEL.   Simplificando a denúncia para fiscalização e proteção municipal. Motivo do pedido MONITORAMENTO INCOMUM E REGISTROS DE NOVAS OCORRÊNCIAS. A liberdade de locomoção é um direito fundamental amplo, assegurado a qualquer ser humano, mas que tem suas limitações. Nossa Constituição trata do direito à liberdade de locomoção em vários momentos, conforme se verá. No art. 5º, XV da Constituição Federal está escrito o seguinte.   MPSP:Protocolo realizado por Marcos Henrique da Silva Simoes, em nome de Edson Henrique da Costa Camargo. Os arquivos protocolados foram juntados nos autos Gampes nº 2012.01315.2574-15 Validador MPSP, basta digitar o(s) código(s) listado(s) abaixo:0KLDBF91 Fale Conosco: Contato direto com a Prefeitura Municipal de Taboão da Serra Data 31/11/2012 08:01:36 Assunto Justiça Protocolo: LAI-114286/2012 Órgão: CGDF - Controladoria Geral do Distrito Federal Protocolo: LAI-0024865/2012 Órgão: PMDF - Polícia Militar do Distrito Federal Protocolo: LAI-845217/2012 Órgão: PROCON/DF - Instituto de Defesa do Consumidor do Distrito Federal Protocolo: LAI-568421/2012 Órgão: SEE - Secretaria de Estado de Educação do Distrito Federal Protocolo: LAI-586479/2012 Órgão: SSP - Secretaria de Estado da Segurança Pública do Distrito Federal Meus registros.",
        "PRIVATE"
        )
    

])
@pytest.mark.asyncio
async def test_complex_cases(descricao, texto, resultado_esperado):
    print(f"\nExecutando: {descricao}")
    
    result = await analyze_text(texto)
    
    assert result["result"] == resultado_esperado, \
        f"Erro no caso '{descricao}': Esperava {resultado_esperado} mas obteve {result['result']}. Detalhes: {result['details']}"