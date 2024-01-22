from time import sleep
from selenium import webdriver
from botcity.web.parsers import table_to_dict
from webdriver_manager.firefox import GeckoDriverManager
from botcity.maestro import *

# Desabilitando os erros caso não estivermos conectados ao Maestro
BotMaestroSDK.RAISE_NOT_CONNECTED = False

def main():
    # Instanciando o BotMaestroSDK através dos argumentos passados pelo Runner
    maestro = BotMaestroSDK.from_sys_args()
    # Obtendo as informações da execução atual
    execution = maestro.get_execution()

    # Instanciando WebDriver
    driver = webdriver.Firefox(executable_path=GeckoDriverManager().install())

    # Acessando página de consulta do CEP
    driver.get("https://buscacepinter.correios.com.br/app/endereco/index.php")
    sleep(1)

    # Obtendo a referência do Datapool para consumir os itens
    dp = maestro.get_datapool(label="Dados_Consulta_CEP")

    while dp.has_next():
        item = dp.next(task_id=execution.task_id)
        try:
            # Processando item
            consulta_cep(item, driver, maestro)
            sleep(2)
            # Finalizando como 'CONCLUÍDO' após o processamento
            item.report_done()

        except Exception as ex:
            # Finalizando o processamento do item como 'ERRO'
            item.report_error()
            print(f"\nExcecao inesperada ao processar item: {ex}\n")

    # Finalizando o navegador
    sleep(3)
    driver.quit()

    # Finalizando tarefa no Maestro
    maestro.finish_task(
        task_id=execution.task_id,
        status=AutomationTaskFinishStatus.SUCCESS,
        message="Task finalizada!"
    )


def consulta_cep(item: DataPoolEntry, driver: webdriver.Firefox, maestro: BotMaestroSDK):
    cep = item["cep"]

    # Inserindo CEP
    input_cep = driver.find_element_by_id("endereco")
    input_cep.send_keys(cep)

    # Buscando resultados
    btn_pesquisa = driver.find_element_by_id("btn_pesquisar")
    btn_pesquisa.click()

    # Coletando resultados da página
    tabela_resultados = driver.find_element_by_id("resultado-DNEC")
    # Convertendo dados da tabela para um dicionário
    tabela_resultados = table_to_dict(table=tabela_resultados)[0]
    sleep(1)

    # Criando uma nova entrada de log
    maestro.new_log_entry(
        activity_label="consulta-cep",
        values={
            "cep": cep,
            "logradouro": tabela_resultados['logradouronome'],
            "bairro": tabela_resultados['bairrodistrito'],
            "localidade": tabela_resultados['localidadeuf']
        }
    )

    # Voltando para a página inicial
    btn_nova_busca = driver.find_element_by_id("btn_nbusca")
    btn_nova_busca.click()


if __name__ == '__main__':
    main()
