import csv  # para ler e escrever arquivo csv
import os  # para checar se o arquivo existe e limpar o terminal
import datetime
from tabulate import tabulate  # pra formatar a tabela na hora de mostrar
from collections import defaultdict


nome_arquivo = "registros.csv"
# Inicia o dict de dicts lancamentos vazio.

lancamentos = {}
# O dict lancamentos tem essa estrutura {'id': 'n', 'data': 'dd/mm/aaaa', 'tipo': 'Receita/Despesa/Investimento', 'valor': 'RR.CC', 'taxa_de_juros': 'x.x', 'data_investimento': 'dd/mm/aaaa', 'investimento_atualizado': 'RR.CC'}
# Chamamos de "lancamentos" o dict 'maior'.
# Chamamos de "lancamento" os valores armazenados em cada 'chave' ID do dict lancamentos.


def limpar_terminal():  # Verifica o sistema operacional e faz o comando adequado.
    if os.name == "nt":  # Se for Windows
        os.system("cls")
    else:  # Se for Linux ou macOS
        os.system("clear")


def taxa_mensal_para_diaria(taxa_mensal): # Faz a conversão da taxa de juros coletada, mensal para diária.
    # Converte a taxa mensal para decimal
    taxa_decimal = taxa_mensal / 100
    # Aplica a fórmula para converter para a taxa diária
    taxa_diaria = (1 + taxa_decimal) ** (1 / 30) - 1
    # Converte a taxa diária de volta para porcentagem
    return taxa_diaria * 100


def is_number(s):  # Tentar converter o valor para float, retorna True ou False. Chamamos em outras funções para verificar se uma entrada poderá ser convertida para número.
    try:
        float(s)
        return True
    except ValueError:
        return False


def criar_data(dia: int, mes: int, ano: int):  # Tenta criar uma data, retorna a data criada (datetime.datetime) ou False.
    try:
        data = datetime.datetime(ano, mes, dia)
        return data
    except:
        return False


def carrega_de_arquivo(): # Carrega os dados do arquivo "nome_arquivo = registros.csv" para o dict "lancamentos".
    with open(nome_arquivo, mode="r", newline="", encoding="utf-8") as file:  # Abre o arquivo, ele fecha sozinho quando acaba o with.
        reader = csv.DictReader(file)  # Serve para ler o arquivo csv e transformar num dict.

        # Lê cada linha e adiciona ao dicionário 'lancamentos'.
        for row in reader: # Cada row é um dict que nem esse: {'id': '1', 'data': '14/08/2024', 'tipo': 'Investimento', 'valor': '55.40', 'taxa_de_juros': '5.0', 'data_investimento': '14/08/2024', 'investimento_atualizado': '50.00'}
            id_ = int(row.pop("id")) # Isso retorna o id e remove ele do dicionário, pq id vai ser a chave no 'lancamentos', e o resto da linha vai ser um dict com os 'valores' da chave 'id'.
            row["valor"] = float(row["valor"])
            if row.get("taxa_de_juros"): # tenta acessar a chave 'taxa_de_juros' do dicionário. Se não existir, retorna None, ou seja, False.
                row["taxa_de_juros"] = float(row["taxa_de_juros"])
            if row.get("investimento_atualizado"):
                row["investimento_atualizado"] = float(row["investimento_atualizado"])
            lancamentos[id_] = row

    return lancamentos


def salva_em_arquivo(): # Essa função salva os dados alterados no arquivo CSV, ela é executada ao final de cada lançamento do usuário, digitando "Salvar" ou "S" ao final.
    # Obter os nomes das colunas a partir do primeiro item do dicionário
    colunas = ["id", "data", "tipo", "valor", "taxa_de_juros", "data_investimento", "investimento_atualizado"]

    # Abrir o arquivo para escrita:
    with open(nome_arquivo, mode="w", newline="", encoding="utf-8") as file: # O argumento newline="" é usado para evitar linhas em branco extras no arquivo CSV. E encoding="utf-8" garante que o arquivo seja salvo com codificação UTF-8, que suporta caracteres especiais.
        writer = csv.DictWriter(file, fieldnames=colunas)

        # Escrever o cabeçalho
        writer.writeheader()

        # Escrever os dados
        for id_, valores in lancamentos.items(): # Cria um novo dicionário linha que combina o ID do lançamento com os detalhes do lançamento.
            linha = {"id": id_, **valores}  # Inicia o dicionário linha com uma chave "id" cujo valor é id_ (o identificador do lançamento). **valores: Desempacota o dicionário valores e insere todas as suas chaves e valores no dicionário linha.
            writer.writerow(linha)

    print(f"Dados salvos em {nome_arquivo}!")


def checa_arquivo_csv(): # Verifica se o arquivo CSV 'nome_arquivo = "registros.csv"' já existe, se sim, carrega as informações contidas nele, do contrário cria um arquivo "registros.csv".
    if os.path.exists(nome_arquivo):
        print(f"Arquivo {nome_arquivo} encontrado, carregando informações!")
        carrega_de_arquivo()
    else:
        # criar o arquivo
        print(f"Criando arquivo {nome_arquivo}!")
        arquivo = open(f"./{nome_arquivo}", "w")
        arquivo.close()


def atualizar_rendimento(): # Essa função faz a atualização do valor dos investimentos. Chamada no menu principal do programa, pela opção 4.
    data_atual = datetime.date.today()

    for id_, lancamento in lancamentos.items():
        if lancamento['tipo'] == 'Investimento':
            # Converte as datas de string para objeto datetime
            data_investimento = datetime.datetime.strptime(lancamento['data_investimento'], "%d/%m/%Y").date()

            # Calcula a quantidade de dias entre o investimento e a data atual
            dias = (data_atual - data_investimento).days

            # Calcula a taxa diária com base na taxa de juros mensal
            taxa_diaria = taxa_mensal_para_diaria(lancamento['taxa_de_juros']) # Chamada da função que converte taxa de juros mensal para taxa diária.

            # Calcula o montante atual
            montante = lancamento['valor'] * (1 + (taxa_diaria / 100)) ** dias

            # Atualiza o valor no dicionário
            lancamento['investimento_atualizado'] = round(montante, 2)

    print("Rendimentos atualizados com sucesso!")


# Função para criar novos registros financeiros no dict lancamentos, é chamada na função coleta_lancamento.
def criar_registro(tipo, valor, data_registro=None, taxa_de_juros=None, data_investimento=None, investimento_atualizado=None):
    if data_registro is None:  # Se o usuário informar a data, não entra nesse if.
        data_registro = datetime.date.today()
    if data_investimento is None:  # Se o usuário informar a data, não entra nesse if.
        data_investimento = datetime.date.today()

    if tipo == "Despesa":
        valor = -abs(valor)  # Converte o valor para negativo

    # ver o máximo valor do dicionário e adicionar 1
    if lancamentos: # verifica se o dicionário tem elementos
        id_transacao = max(lancamentos.keys()) + 1
    else:
        id_transacao = 1

    lancamentos[id_transacao] = {
        "data": data_registro.strftime("%d/%m/%Y"),#strftime transforma a data datetime.datetime em string "dd/mm/yyyy"
        "tipo": tipo,
        "valor": valor,
    }

    if tipo == "Investimento":
        lancamentos[id_transacao]["taxa_de_juros"] = taxa_de_juros
        lancamentos[id_transacao]["data_investimento"] = data_investimento.strftime("%d/%m/%Y")
        lancamentos[id_transacao]["valor"] = valor  # Armazena o valor original do investimento, para ver o montante autalizado, precisará chamar a opção 4 no menu principal.

    print(f"Registro {id_transacao} criado com sucesso!")


# Mostrar Menu e pedir para o usuário escolher uma opção
def recebe_opcao_do_menu():
    texto_menu = """
===================================
    EcoBalance - Menu Principal
===================================
Digite um número para acessar a função correspondente:
    1) Inserir Lançamento
    2) Consultar Lançamentos
    3) Editar Lançamento
    4) Atualiza Rendimentos
    5) Remover Lançamento
    6) Calcular Resultado Mensal
    7) Exportar Relatório dos Lançamentos

    Para salvar, digite 'SALVAR' ou 'S'. Será exportado um arquivo .csv com os registros.
    Para sair, digite 'X'
    """
    print(texto_menu)
    opcao_usuario = input(">> ")
    return opcao_usuario


# Função para perguntar a data. faz as verificações para criação da data a escolha do usuário, insere o dia, o mês e o ano, separadamente.
# Caso o usuário digite algo diferente de 's' ou 'n", o usuário terá que digitar a data.
def pergunta_data():
    print("Deseja utilizar a data de hoje? [S/N]")
    resposta = input(">> ")
    if resposta.upper() == "S":
        return datetime.date.today()
    while True:  # pergunta a data
        print("Entre com a data, será pedido dia, depois mês, depois ano.")
        while True:  # pergunta o dia
            print("Digite o dia:")
            dia_digitado = input(">> ")
            if dia_digitado.isdigit():  # verifica se é um número
                dia = int(dia_digitado)
                if 1 <= dia <= 31:
                    break
                else:
                    print("Dia inválido...")
            else:
                print("Dia inválido...")

        while True:  # pergunta o mês
            print("Digite o mês:")
            mes_digitado = input(">> ")
            if mes_digitado.isdigit():  # verifica se é um número
                mes = int(mes_digitado)
                if 1 <= mes <= 12:
                    break
                else:
                    print("Mês inválido...")
            else:
                print("Mês inválido...")

        while True:  # pergunta o ano
            print("Digite o ano:")
            ano_digitado = input(">> ")
            if ano_digitado.isdigit():  # verifica se é um número
                ano = int(ano_digitado)
                if 1900 <= ano <= 9999:
                    break
                else:
                    print("Ano inválido...")
            else:
                print("Ano inválido...")
        # tentar criar a data para ver se é válida
        data = criar_data(dia, mes, ano)
        if data == False:  # se data for str, quer dizer que deu erro
            print(f"Data inválida, não existe o dia {dia}/{mes}/{ano}!")
        else:
            break
    return data


def coleta_lancamento():  # Essa função coleta as informações/detalhes do lançamento, um após o outro.

    while True:  # pergunta o tipo de lançamento
        print("Digite o tipo de lançamento que deseja criar: 'r' para receita, 'i' para investimento, 'd' para despesa.")
        opcao_tipo = input(">> ")
        if opcao_tipo.upper() == "R":
            tipo = "Receita"
            break
        elif opcao_tipo.upper() == "I":
            tipo = "Investimento"
            break
        elif opcao_tipo.upper() == "D":
            tipo = "Despesa"
            break
        else:
            print("Opção de tipo de lançamento inválida...")

    while True:  # pergunta o valor
        print(f"Digite o valor em Reais da(o) {tipo} sem sinal, exemplo 18.25:")
        valor_digitado = input(">> ")
        if is_number(valor_digitado):  # verifica se é possível converter para float
            valor = float(valor_digitado)
            break
        else:
            print("Valor de lançamento inválido...")

    print("Data do lançamento: ")
    data = pergunta_data()  # pergunta a data do lançamento. Caso o usuário digite algo diferente de 's' ou 'n", o usuário terá que digitar a data.

    taxa = None
    data_investimento = None
    investimento_atualizado = None

    if tipo == "Investimento":  # pergunta os campos de investimento
        while True:  # pergunta a taxa de juro
            print(f"Digite o valor percentual da taxa de juros mensal, exemplo: '5' seria 5% ao mês.")
            taxa_digitada = input(">> ")
            if is_number(taxa_digitada):  # verifica se é possível converter para float
                taxa = float(taxa_digitada)
                break
            else:
                print("Valor de taxa inválido...")

        print("Data do investimento: ")
        data_investimento = pergunta_data()  # pergunta a data do investimento. Caso o usuário digite algo diferente de 's' ou 'n", o usuário terá que digitar a data.

    criar_registro(tipo, valor, data, taxa, data_investimento, investimento_atualizado)


def listar_lancamentos(): # Função para listar os registros e exibir no terminal. É chamada em outras funções.
    # lista de cabeçalhos
    colunas = ["ID", "Data do Lançamento", "Tipo", "Valor", "Tx Juros (mês)", "Data Investimento", "Investimento Atualizado"]

    # lista para armazenar as linhas da tabela
    tabela = []

    # Preenche a tabela com os dados de 'lancamentos'
    for id_, lancamento in lancamentos.items():
        linha = [id_,
            lancamento.get("data", ""),  # tenta acessar a chave 'data' do dicionário. Se não existir, retorna "" (string vazia).
            lancamento.get("tipo", ""),
            lancamento.get("valor", ""),
            str(lancamento.get("taxa_de_juros", "")) + "%" if lancamento.get("taxa_de_juros") else "",
            lancamento.get("data_investimento", ""),
            lancamento.get("investimento_atualizado", ""),
        ]
        tabela.append(linha)

    # Exibe a tabela de forma visual mais amigável para o usuário.
    print(tabulate(tabela, headers=colunas, tablefmt="fancy_grid"))


def editar_lancamento(): # Função para editar os lançamentos, para gravar a edição no CSV, precisa "Salvar" ao final, quando retorna ao menu.
    listar_lancamentos()  # Mostrar os lançamentos para que o usuário escolha qual editar
    while True:
        print("Digite o ID do lançamento que deseja editar:")
        id_digitado = input(">> ")

        if id_digitado.isdigit():
            id_lancamento = int(id_digitado)
            if id_lancamento in lancamentos:
                break
            else:
                print("ID não encontrado. Por favor, tente novamente.")
        else:
            print("ID inválido. Por favor, insira um número válido.")

    # Recupera os dados do lançamento selecionado
    lancamento = lancamentos[id_lancamento]

    # Perguntar pelo novo tipo de lançamento
    while True:
        print(f"Tipo atual: {lancamento['tipo']}")
        print("Digite o novo tipo de lançamento: 'r' para receita, 'i' para investimento, 'd' para despesa (ou pressione Enter para manter o tipo atual).")
        opcao_tipo = input(">> ")

        if opcao_tipo.upper() == "R":
            novo_tipo = "Receita"
            break
        elif opcao_tipo.upper() == "I":
            novo_tipo = "Investimento"
            break
        elif opcao_tipo.upper() == "D":
            novo_tipo = "Despesa"
            break
        elif opcao_tipo == "":  # Manter o tipo atual
            novo_tipo = lancamento["tipo"]
            break
        else:
            print("Opção de tipo de lançamento inválida...")

    # Perguntar pelo novo valor
    while True:
        print(f"Valor atual: {lancamento['valor']}")
        print("Digite o novo valor (ou pressione Enter para manter o valor atual):")
        valor_digitado = input(">> ")

        if valor_digitado == "":  # Manter o valor atual
            novo_valor = float(lancamento["valor"])
            break
        elif is_number(valor_digitado):
            novo_valor = float(valor_digitado)
            break
        else:
            print("Valor de lançamento inválido...")

    # Aplicar a regra de negócio ao novo valor
    if novo_tipo == "Despesa":
        novo_valor = -abs(novo_valor)  # Converte o valor para negativo
    else: # Se o tipo for Receita ou Investimento, o valor deve ser positivo
        novo_valor = abs(novo_valor)

    if novo_tipo == "Investimento":
        while True:  # pergunta a taxa de juro
            print(f"Taxa de juros atual: {lancamento.get('taxa_de_juros', 'não especificada')}")
            print("Digite o novo valor percentual da taxa de juros mensal (ou pressione Enter para manter a taxa atual):")
            taxa_digitada = input(">> ")

            if taxa_digitada == "":  # Manter a taxa de juros atual
                nova_taxa = lancamento.get("taxa_de_juros", None)
                break
            elif is_number(taxa_digitada):  # verifica se é possível converter para float
                nova_taxa = float(taxa_digitada)
                break
            else:
                print("Valor de taxa inválido...")

        print(f"Data de investimento atual: {lancamento.get('data_investimento', 'não especificada')}")
        print("Digite a nova data do investimento (ou pressione Enter para manter a data atual):")
        data_investimento = pergunta_data()

        if not data_investimento:  # Se o usuário não alterar a data, manter a atual
            data_investimento = datetime.datetime.strptime(lancamento.get('data_investimento', datetime.date.today().strftime("%d/%m/%Y")), "%d/%m/%Y")

        lancamento['taxa_de_juros'] = nova_taxa
        lancamento['data_investimento'] = data_investimento.strftime("%d/%m/%Y")
        lancamento['valor'] = lancamento['valor'] if 'valor' in lancamento else novo_valor
    else:
        nova_taxa = None
        lancamento.pop('taxa_de_juros', None)  # Remove a taxa de juros se não for mais um investimento
        lancamento.pop('data_investimento', None)  # Remove a data de investimento se não for mais um investimento
        lancamento.pop('investimento_atualizado', None)  # Remove o valor atualizado se não for mais um investimento

    # Atualizar o lançamento
    lancamento['tipo'] = novo_tipo
    lancamento['valor'] = novo_valor
    lancamento['data'] = datetime.date.today().strftime("%d/%m/%Y")  # Atualiza a data de edição

    lancamentos[id_lancamento] = lancamento

    print(f"Lançamento {id_lancamento} atualizado com sucesso!")


def filtrar_lancamentos(): # Essa função é chamada na opção consultar lançamentos, caso o usuário não deseje filtrar, serão exibidos todos os lançamentos.
    limpar_terminal()
    print("Escolha e digite uma opção para o critério de filtro:")
    print("1) Filtrar por Data")
    print("2) Filtrar por Tipo")
    print("3) Filtrar por Valor")
    print("Ou pressione ENTER para exibir todos os registros")
    opcao = input(">> ")
    if not opcao:
        listar_lancamentos()
        return

    resultados = []

    if opcao == "1":
        print("Digite a data no formato dd/mm/yyyy:")
        data_filtro = input(">> ")
        for id_, lancamento in lancamentos.items():
            if lancamento.get("data") == data_filtro:
                resultados.append([id_, lancamento])

    elif opcao == "2":
        print("Digite o tipo de lançamento ('Receita', 'Despesa' ou 'Investimento'):")
        tipo_filtro = input(">> ")
        for id_, lancamento in lancamentos.items():
            if lancamento.get("tipo").lower() == tipo_filtro.lower():
                resultados.append([id_, lancamento])

    elif opcao == "3":
        print("Digite o valor mínimo:")
        valor_minimo = input(">> ")
        print("Digite o valor máximo:")
        valor_maximo = input(">> ")

        # Verifica se os valores são números e os converte para float
        if is_number(valor_minimo) and is_number(valor_maximo):
            valor_minimo = float(valor_minimo)
            valor_maximo = float(valor_maximo)

            for id_, lancamento in lancamentos.items():
                valor = lancamento.get("valor", 0)
                if valor_minimo <= valor <= valor_maximo:
                    resultados.append([id_, lancamento])
        else:
            print("Valores inválidos para o filtro de valor.")
            return

    else:
        print("Opção de filtro inválida.")
        return

    # Exibe os resultados do filtro
    if resultados:
        print(f"\nLançamentos encontrados para o critério escolhido ({len(resultados)} resultados):")
        colunas = ["ID", "Data do Lançamento", "Tipo", "Valor", "Taxa de Juros", "Data Investimento", "Investimento Atualizado"]
        tabela = []
        for id_, lancamento in resultados:
            linha = [
                id_,
                lancamento.get("data", ""),
                lancamento.get("tipo", ""),
                lancamento.get("valor", ""),
                lancamento.get("taxa_de_juros", ""),
                lancamento.get("data_investimento", ""),
                lancamento.get("investimento_atualizado", ""),
            ]
            tabela.append(linha)
        print(tabulate(tabela, headers=colunas, tablefmt="fancy_grid"))
    else:
        print("Nenhum lançamento encontrado para o critério escolhido.")



def excluir_lancamento_por_id(): # Função chamada dentro da função remover_lancamento, quando for necessário excluir pelo ID do registro.
    listar_lancamentos()

    while True:
        print("Digite o ID do lançamento que deseja excluir:")
        id_exclusao = input(">> ")

        if id_exclusao.isdigit():
            id_exclusao = int(id_exclusao)
            if id_exclusao in lancamentos:
                # Confirmação antes de excluir
                confirmacao = input(f"Tem certeza que deseja excluir o lançamento {id_exclusao}? (S/N): ")
                if confirmacao.upper() == 'S':
                    del lancamentos[id_exclusao]
                    print(f"Lançamento {id_exclusao} excluído com sucesso!")
                else:
                    print("Exclusão cancelada.")
                break
            else:
                print("ID não encontrado. Por favor, tente novamente.")
        else:
            print("ID inválido. Por favor, insira um número válido.")


def remover_lancamento():
    listar_lancamentos()  # Mostrar os lançamentos para o usuário escolher qual excluir

    while True:  # Pergunta ao usuário se ele quer consultar o lançamento a ser excluído por data ou por ID
        print("Digite 'D' para excluir por data ou 'I' para excluir por ID, digite 'S' para sair e voltar ao menu:")
        opcao_exclusao = input("> ").upper()

        if opcao_exclusao == 'D':  # Se o usuário digitar D, vai ter que informar a data para localizar o registro
            data_exclusao = pergunta_data()
            lancamentos_a_excluir = [id_ for id_, lancamento in lancamentos.items() if lancamento.get('data') == data_exclusao.strftime("%d/%m/%Y")]

            if len(lancamentos_a_excluir) > 1:  # Se naquela data tiver mais de um registro, ele vai ter que informar o ID do registro a excluir
                print("Há mais de um lançamento nessa data. Informe o ID do lançamento a ser excluído:")
                for id_ in lancamentos_a_excluir:
                    print(f"ID: {id_}, Tipo: {lancamentos[id_]['tipo']}, Valor: {lancamentos[id_]['valor']}")

                while True:
                    print("Digite o ID do lançamento que deseja remover:")
                    id_exclusao = input("> ")

                    if id_exclusao.isdigit():
                        id_lancamentos = int(id_exclusao)
                        confirmacao = input(f"Tem certeza que deseja remover o lançamento de ID {id_lancamentos}? [S/N]").upper()

                        if confirmacao == 'S':
                            del lancamentos[id_lancamentos]
                            print(f"Lançamento {id_lancamentos} removido com sucesso!")
                            break  # Sai do loop após a exclusão
                        else:
                            print("Operação cancelada.")
                            break  # Sai do loop após cancelar a exclusão.
                    else:
                        print("ID não encontrado. Por favor, tente novamente.")
                break  # Sai do loop principal após a exclusão ou cancelamento.

            elif len(lancamentos_a_excluir) == 1:
                id_lancamentos = lancamentos_a_excluir[0]
                confirmacao = input(f"Tem certeza que deseja remover o lançamento de ID {id_lancamentos}? [S/N]").upper()

                if confirmacao == 'S':
                    del lancamentos[id_lancamentos]
                    print(f"Lançamento {id_lancamentos} removido com sucesso!")
                else:
                    print("Operação cancelada.")
                break  # Sai do loop principal após a exclusão ou cancelamento.
            else:
                print("Nenhum lançamento encontrado para a data fornecida.")
                break  # Sai do loop principal se não houver lançamentos para excluir.

        elif opcao_exclusao == 'I':
            excluir_lancamento_por_id()

        elif opcao_exclusao == 'S':
            break # Cancela a exclusão e sai do loop.

        else:
            print("Opção inválida. Por favor, tente novamente.")
            break # Sai do loop principal.


# Calcula resultado mensal - essa função calcula o resultado das operações no perído de um mês. Considerando receitas, despesas e investimentos do período. Exibe os resultados por mês no terminal.
from collections import defaultdict
import datetime
from tabulate import tabulate

def calcular_resultado_mensal(): # Exibe no terminal os resultados por mês, considerando os registros existentes no registros.csv
    resultados_mensais = defaultdict(lambda: {"Receita": 0, "Despesa": 0, "Resultado": 0})

    for lancamento in lancamentos.values():
        # Extrai o mês e o ano do lançamento
        data_lancamento = datetime.datetime.strptime(lancamento["data"], "%d/%m/%Y")
        mes_ano = data_lancamento.strftime("%m/%Y")

        if lancamento["tipo"] == "Receita":
            resultados_mensais[mes_ano]["Receita"] += lancamento["valor"]
        elif lancamento["tipo"] == "Despesa":
            resultados_mensais[mes_ano]["Despesa"] += lancamento["valor"]
        elif lancamento["tipo"] == "Investimento":
            # Verifica se o valor do investimento foi atualizado
            if lancamento.get("investimento_atualizado") is None:
                print(f"Atenção: O investimento realizado em {lancamento['data']} não foi atualizado.")
                print("Por favor, atualize os investimentos antes de calcular o resultado mensal.")
                return
            resultados_mensais[mes_ano]["Receita"] += lancamento["investimento_atualizado"] - lancamento["valor"]

        # Atualiza o resultado do mês (receitas - despesas)
        resultados_mensais[mes_ano]["Resultado"] = (resultados_mensais[mes_ano]["Receita"] + resultados_mensais[mes_ano]["Despesa"])

    # Exibe os resultados mensais
    print("\nResultados Mensais:")
    colunas = ["Mês/Ano", "Receita Total", "Despesa Total", "Resultado"]
    tabela = []

    for mes_ano, resultado in sorted(resultados_mensais.items()):
        linha = [mes_ano,
            f"R$ {resultado['Receita']:.2f}",
            f"R$ {resultado['Despesa']:.2f}",
            f"R$ {resultado['Resultado']:.2f}",]

        tabela.append(linha)

    print(tabulate(tabela, headers=colunas, tablefmt="fancy_grid"))



def exportar_relatorio(lancamentos, nome_relatorio='meu_relatorio.csv'): # Exporta o relatório com as informações guardadas no dict lancamentos.

    if not lancamentos:
        print('Não há dados para exportar.')
        return

    colunas = list(next(iter(lancamentos.values())).keys()) # Obtém os nomes das colunas a partir das chaves do primeiro dicionário dentro de lancamentos.

    with open(nome_relatorio, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=colunas)

        writer.writeheader()

        for registro in lancamentos.values():
            writer.writerow(registro)

    print(f"Relatório exportado com sucesso para {nome_relatorio}!")


def roda_programa():
    limpar_terminal()
    checa_arquivo_csv()  # se não existir, essa função cria o arquivo. Se existir, carrega as informações dele.

    while True:
        opcao = recebe_opcao_do_menu()
        if opcao == "1":
            # print(f"Opção {opcao} selecionada.")
            coleta_lancamento()
        elif opcao == "2":
            # print(f"Opção {opcao} selecionada.")
            filtrar_lancamentos()
        elif opcao == "3":
            # print(f"Opção {opcao} selecionada.")
            editar_lancamento()
        elif opcao == "4":
            # print(f"Opção {opcao} selecionada.")
            atualizar_rendimento()
        elif opcao == "5":
            # print(f"Opção {opcao} selecionada.")
            remover_lancamento()
        elif opcao == "6":
            # print(f"Opção {opcao} selecionada.")
            calcular_resultado_mensal()
        elif opcao == "7":
            # print(f"Opção {opcao} selecionada.")
            exportar_relatorio(lancamentos)
        elif opcao != "" and opcao.upper() in "SALVAR":
            print(f"Opção SALVAR selecionada.")
            salva_em_arquivo()
        else:
            print("Até a próxima!")
            break

roda_programa()