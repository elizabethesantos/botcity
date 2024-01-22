from time import sleep
from selenium import webdriver
from botcity.web.parsers import table_to_dict
from webdriver_manager.firefox import GeckoDriverManager
from botcity.maestro import *

# Desabilitando os erros caso não estivermos conectados ao Maestro
BotMaestroSDK.RAISE_NOT_CONNECTED = False

def main():
    try:
        # Instanciando o BotMaestroSDK através dos argumentos passados pelo Runner
        maestro = BotMaestroSDK.from_sys_args()
        # Obtendo as informações da execução atual
        execution = maestro.get_execution()

        # Obtendo credenciais do Maestro
        usuario = maestro.get_credential("dados-login", "usuario")
        senha = maestro.get_credential("dados-login", "senha")

        # Obtendo parâmetro da tarefa
        cep = execution.parameters.get("cep")

        # Enviando alerta para o Maestro
        maestro.alert(
            task_id=execution.task_id,
            title="Iniciando processo",
            message=f"O processo de consulta foi iniciado - CEP: {cep}",
            alert_type=AlertType.INFO
        )

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

        print(tabela_resultados)
        driver.save_screenshot("resultado.png")

        # Subindo arquivo de resultados
        maestro.post_artifact(
            task_id=execution.task_id,
            artifact_name=f"Resultados-CEP-{cep}.png",
            filepath="resultado.png"
        )

        # Finalizando tarefa no Maestro
        maestro.finish_task(
            task_id=execution.task_id,
            status=AutomationTaskFinishStatus.SUCCESS,
            message="Task finalizada!"
        )


    except Exception as erro:
        print(f"Erro inesperado: {erro}")
        driver.save_screenshot("erro.png")

    # Reportando erro ao Maestro
        maestro.error(
            task_id=execution.task_id,
            exception=erro,
            screenshot="erro.png"
        )
       
        # Finalizando tarefa no Maestro como falha
        maestro.finish_task(
            task_id=execution.task_id,
            status=AutomationTaskFinishStatus.FAILED,
            message="Task falhou!"
        )

    finally:
        # Finalizando o navegador
        sleep(3)
        driver.quit()


if __name__ == '__main__':
    main()
