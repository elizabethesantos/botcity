from time import sleep
from selenium import webdriver
from botcity.web.parsers import table_to_dict
from webdriver_manager.firefox import GeckoDriverManager
from botcity.maestro import *

# Desabilitando os erros caso não estivermos conectados ao Maestro
BotMaestroSDK.RAISE_NOT_CONNECTED = False

cep = "28633-530"

def main():
    try:
        # Instanciando o BotMaestroSDK através dos argumentos passados pelo Runner
        maestro = BotMaestroSDK.from_sys_args()
        # Obtendo as informações da execução atual
        execution = maestro.get_execution()

        # Instanciando WebDriver
        driver = webdriver.Firefox(executable_path=GeckoDriverManager().install())
        driver.set_window_size(1600, 900)

        # Acessando página de consulta do CEP
        driver.get("https://buscacepinter.correios.com.br/app/endereco/index.php")
        sleep(1)

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

        print(tabela_resultados)
        driver.save_screenshot("resultado.png")

        # Finalizando tarefa no Maestro
        maestro.finish_task(
            task_id=execution.task_id,
            status=AutomationTaskFinishStatus.SUCCESS,
            message="Task finalizada!"
        )

    except Exception as erro:
        print(f"Erro inesperado: {erro}")
        driver.save_screenshot("erro.png")

    finally:
        # Finalizando o navegador
        sleep(3)
        driver.quit()


if __name__ == '__main__':
    main()
