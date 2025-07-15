"""
    Main entry point for the application.
"""
import pandas as pd
import time
import datetime
import random

from src.modules.consult_builders.budget_consult import consult_budget_in_geoex
from src.modules.consult_builders.folders_status_consult import consult_folder_status_in_geoex
from src.modules.consult_builders.project_consult import consult_project_in_geoex
from src.modules.consult_builders.project_rejection_details_consult import consult_project_rejection_details_in_geoex
from src.modules.utils.fix_geoex_returned_dates import fix_geoex_returned_date
from src.modules.utils.safe_get_for_body import safe_get
from src.modules.google_sheets.sheets_python import SheetsPython



class GeoexScraper:
    """
    Initialize the GeoexScraper class.
    This class is responsible for scraping data from Geoex.
    """
    def __init__(self):
        # self.geoex_credentials = load_env_configs()
        self.folder_status_reversed_enum = {
            118: "PASTA ACEITA E FINALIZADA",
            30: "ACEITO",
            22: "PENDENTE",
            32: "REJEITADO",
            35: "VALIDADO",
            31: "ACEITO COM RESTRIÇÕES",
            99: "ERRO DE SUBGRUPO",
            1: "CRIADO",
            6: "CANCELADO",
            }
    def scrape_projects_infos(
        self,
        geoex_credentials: dict,
        projects_to_consult: list,
        google_sheet_id: str,
        google_sheet_range: str,
        progress_callback: callable
        ):
        """
        Scrape project information from Geoex.
        This method iterates through the list of projects to consult
        and retrieves their information using the Geoex API.
        """
        scraped_data = []
        date_today = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        for i,project in enumerate(projects_to_consult):
            print(f"Project: {project}")
            result = consult_project_in_geoex(
                project_numbers=project,
                cookies=geoex_credentials["cookies"],
                gxsessao=geoex_credentials["gxsessao"],
                gxbot=geoex_credentials["gxbot"]
            )

            if result['response_status'] == 200:
                folder_status_result = consult_folder_status_in_geoex(
                    safe_get(result, ['response_body', 'ProjetoId']),
                    cookies=geoex_credentials["cookies"],
                    gxsessao=geoex_credentials["gxsessao"],
                    gxbot=geoex_credentials["gxbot"]
                )

                correct_send = next(
                    (element for element in folder_status_result['response_body']["Envios"] if element["Empresa"] == "FUTURO"),
                    None)
                folder_status1 = self.folder_status_reversed_enum.get(safe_get(folder_status_result, ['response_body','HistoricoStatusId']))
                folder_status2 = self.folder_status_reversed_enum.get(safe_get(correct_send, ['HistoricoStatus'],99))
                folder_date = safe_get(correct_send, ['Ultimo', 'DataValidacao'])
                folder_down_date = safe_get(correct_send, ['Ultimo', 'DataBaixa'])
                folder_n_attempts = len(safe_get(correct_send, ['EnvioPastas'],[]))

                scraped_data.append([
                                safe_get(result, ['response_body', 'ProjetoText']),
                                safe_get(result, ['response_body', 'Titulo']),
                                safe_get(result, ['response_body', 'Nota', 'Numero']),
                                safe_get(result, ['response_body', 'Empresa']),
                                safe_get(result, ['response_body', 'Municipio']),
                                safe_get(result, ['response_body', 'Localidade']),
                                safe_get(result, ['response_body', 'StatusProjeto', 'Descricao']),
                                fix_geoex_returned_date(safe_get(result, ['response_body', 'StatusProjetoData'])),
                                fix_geoex_returned_date(safe_get(result, ['response_body', 'DtZps09'])),
                                safe_get(result, ['response_body', 'Termo', 'Serial']),
                                safe_get(result, ['response_body', 'Termo', 'Status']),
                                fix_geoex_returned_date(safe_get(result, ['response_body', 'Termo', 'StatusData'])),
                                safe_get(result, ['response_body', 'GseProjeto', 'Status', 'Nome']),
                                fix_geoex_returned_date(safe_get(result, ['response_body', 'GseProjeto', 'StatusData'])),
                                safe_get(result, ['response_body', 'VlProjeto']),
                                safe_get(result, ['response_body', 'PosicaoInvestimento']),
                                f'{folder_status1} - {folder_status2}',
                                safe_get(result, ['response_body', 'CarteirasObras', 0, 'Criterio']),
                                safe_get(result, ['response_body', 'ArquivoTipologia', 'Nome']),
                                safe_get(result, ['response_body', 'ResponsavelCarteiraProgramacaoUsuario', 'Nome']),
                                safe_get(result, ['response_body', 'ProjetoMedidor']),
                                safe_get(result, ['response_body', 'ProjetoKit']),
                                fix_geoex_returned_date(folder_date),
                                safe_get(result, ['response_body', 'Etiquetas', 0, 'Nome']),
                                fix_geoex_returned_date(folder_down_date),
                                folder_n_attempts,
                                safe_get(result, ['response_body', 'CarteirasObras', 0, 'Carteira'],"")[:7],
                                safe_get(result, ['response_body', 'CarteirasObras', 0, 'Previsao']),
                                safe_get(result, ['response_body', 'ResponsavelCarteiraProgramacaoUsuario','Nome']),
                                date_today,
                            ])
            wait_time = 3 + random.uniform(-2, 2)
            time.sleep(wait_time)  # To avoid overwhelming the server with requests
            progress_callback(i+1)
        SheetsPython().update_sheets_data(
            data_frame=pd.DataFrame(scraped_data),
            id_sheets=google_sheet_id,
            range_sheets=google_sheet_range,
            append=True,
            append_col_ref="A",
        )
        return (True,"Scraping completed successfully.")

    def scrape_projects_budgets(
        self,
        geoex_credentials: dict,
        projects_to_consult: list,
        google_sheet_id: str,
        google_sheet_range: str,
        progress_callback: callable
        ):
        """
        Scrape project budget information from Geoex.
        This method iterates through the list of projects to consult
        and retrieves their budget information using the Geoex API.
        """
        scraped_data = []
        for i,project in enumerate(projects_to_consult):
            print(f"Project: {project}")
            result = consult_project_in_geoex(
                project_numbers=project,
                cookies=geoex_credentials["cookies"],
                gxsessao=geoex_credentials["gxsessao"],
                gxbot=geoex_credentials["gxbot"]
            )
            if result['response_status'] == 200:
                project_budget = consult_budget_in_geoex(
                    safe_get(result, ['response_body', 'ProjetoId']),
                    cookies=geoex_credentials["cookies"],
                    gxsessao=geoex_credentials["gxsessao"],
                    gxbot=geoex_credentials["gxbot"]
                    )
                no_null_budget_rows = [row for row in safe_get(project_budget,['response_body','Item','Itens']) if row['Quantidade'] >0]

                if len(no_null_budget_rows) == 0:
                    continue

                for row in no_null_budget_rows:
                    scraped_data.append([
                        safe_get(result, ['response_body', 'ProjetoText']).split("-")[1],
                        safe_get(row, ['Grupo']),
                        safe_get(row, ['Codigo']),
                        safe_get(row, ['UnidadeMedida']),
                        safe_get(row, ['Nome']),
                        safe_get(row, ['JustificativaAnalise']),
                        safe_get(row, ['Quantidade']),
                        safe_get(row, ['QuantidadeAnalise']),
                        safe_get(row, ['QuantidadeAjuste']),
                        safe_get(row, ['Validado']),
                    ])
            progress_callback(i+1)
        SheetsPython().update_sheets_data(
            data_frame=pd.DataFrame(scraped_data),
            id_sheets=google_sheet_id,
            range_sheets=google_sheet_range,
            append=True,
            append_col_ref="A",
        )
        return (True,"Scraping completed successfully.")


    def scrape_projects_rejection_details(self,
        geoex_credentials: dict,
        projects_to_consult: list,
        google_sheet_id: str,
        google_sheet_range: str,
        progress_callback: callable
        ):
        """
        Scrape project rejections details from Geoex.

        Args:
            google_sheet_id (str): Id of the Google Sheet to update.
            google_sheet_range (str): Range of the Google Sheet to update.
        """
        scraped_data = []
        print(len(projects_to_consult))

        for i,project in enumerate(projects_to_consult):
            print(f"Project: {project}")
            result = consult_project_in_geoex(
                project_numbers=project,
                cookies=geoex_credentials["cookies"],
                gxsessao=geoex_credentials["gxsessao"],
                gxbot=geoex_credentials["gxbot"]
            )
            if result['response_status'] == 200:
                folder_status_result = consult_folder_status_in_geoex(
                    safe_get(result, ['response_body', 'ProjetoId']),
                    cookies=geoex_credentials["cookies"],
                    gxsessao=geoex_credentials["gxsessao"],
                    gxbot=geoex_credentials["gxbot"]
                )
                correct_send = next(
                    (element for element in folder_status_result['response_body']["Envios"] if element["Empresa"] == "FUTURO"),
                    None)

                if correct_send is None:
                    continue

                sended_folders = safe_get(correct_send, ['EnvioPastas'],[])

                for folder in sended_folders:
                    eco_analist = safe_get(folder, ['Usuario', 'Nome'])
                    eco_request_date = fix_geoex_returned_date(safe_get(folder, ['Data']))
                    response_date = fix_geoex_returned_date(safe_get(folder, ['DataResponsavelValidacao']))
                    acceptance_date = fix_geoex_returned_date(safe_get(folder, ['DataResponsavel']))
                    status = safe_get(folder, ['HistoricoStatusId'],99)

                    folder_rejection_details = consult_project_rejection_details_in_geoex(
                        safe_get(folder, ['ProjetoEnvioPastaId']),
                        cookies=geoex_credentials["cookies"],
                        gxsessao=geoex_credentials["gxsessao"],
                        gxbot=geoex_credentials["gxbot"]
                    )
                    rejects_at_response = []
                    rejects_at_response_observations = []
                    rejects_at_acceptance = []
                    rejects_at_acceptance_observations = []
                    rejects_general_observations = safe_get(folder_rejection_details, ['response_body', 'ObservacaoValidacao'], '')
                    for item in safe_get(folder_rejection_details, ['response_body', 'Itens'], []):
                        if item['HistoricoStatusIdValidacao'] == 32:
                            rejects_at_response.append(item['EnvioPastaItem'])
                            rejects_at_response_observations.append(safe_get(item,['ObservacaoValidacao'],''))
                        if item['HistoricoStatusId'] == 32:
                            rejects_at_acceptance.append(item['EnvioPastaItem'])
                            rejects_at_acceptance_observations.append(safe_get(item,['Observacao'],''))
                    scraped_data.append([
                        project,
                        eco_analist,
                        eco_request_date,
                        self.folder_status_reversed_enum[status],
                        response_date,
                        "\n".join(rejects_at_response),
                        "\n".join(rejects_at_response_observations),
                        acceptance_date,
                        "\n".join(rejects_at_acceptance),
                        "\n".join(rejects_at_acceptance_observations),
                        rejects_general_observations,
                    ])
            progress_callback(i+1)
        SheetsPython().update_sheets_data(
            data_frame=pd.DataFrame(scraped_data),
            id_sheets=google_sheet_id,
            range_sheets=google_sheet_range,
            append=True,
            append_col_ref="A",
        )
        return (True,"Scraping completed successfully.")

if __name__ == "__main__":
    
    projects = SheetsPython().get_data_from_sheets(
        id_sheets="1AMjoJGQmEhpAz5_-XqilCUe4P3-SArAMHtC8nCPR094",
        range_sheets="PROJETOS!A1:A",
        with_headers=True
    )
    print(projects['PROJETOS PESQUISAR'].array)
    GeoexScraper().scrape_projects_infos(
        geoex_credentials={
            "cookies": "access_token=CfDJ8DYAIeEKlntJtLGnblY3-fPyrBldz3XVrHgqNGfzwBM9bi6gFkT7gURYXoAPgUalVrsnEFloSfhjd69id_1YQhJr_8vRaeDBL2fdMeca_XUbTs10VX7vlgcWHPGejM7iheAb7YIdggQ8a869RbTa7LBMM6u7XBDiD80h6a1M8QSnyOglhhOuKMnPu-Y8Ntg-_l1YWUMUFGt_j8NmRHZE-mRLeCBO7aa4Dg2PXw_uCWp_5EF09-euXXaDomU2UKAgv0656eOvzsdqQiFWbobsvaLex3iuhIkRFV47dWq-TjY8Dv56a3hkIU0vGeMD5MPS43sH0RNdbmHftP5V4YjhXoMi4JIMURumD2Xpo3LWhGYZBSKtjAOJl2U69JyKFu91m2GZ_XYfH_ycfD8qRyXMdo27g1oz5VoHgP4Gh5TRP0OBVw0k9V4dAEigBtYsqq3AS1PxFf4idsw15-g5DkoTOMs; .AspNetCore.Session=CfDJ8DYAIeEKlntJtLGnblY3%2BfPoySfSorajyO%2B31knKER%2B6nEOrjYxZGbHLh091UOufCqEtJoF%2F5%2FwF6DIHorXcxmXCVj9OGyTZzQjR27WFnR%2FYTx14hmLBwVzuhe61KCVGjMOn72Voi84dNt9Lt4ZqC249zlP7F7miUM8PazqaHNWJ; TemaEscuro=true; FirmaId=1; Home.Buscar.Texto=; ConsultarProjeto.Numero=B-0957422; cf_clearance=EQO4CJjb4OQNG_V6pXeyJXO7YP_Km4nDCEBzxJq7wm0-1752576903-1.2.1.1-Kj7w95NTJPIu4NncRF_54LBMEBZsGuMVTdNnTO0kCHOg52Q00zJrXS1qCleflr6M6RfqhRI7nNdIN4qGzXcjMWKk9nq6EFl4RfsWB8ZkVEvEW.oXc4F0J.yH2m3K3aZ7SDW4Hpr8voKgYGuZzJ617XO1xis1hBdkDfEzcQyCmAQq4DHSTbpboTJ5uvc247l6ZiI.xsjUYLSDNxh8PqmM0wyTZMLkcNB.Bkq8FiNcXio",
            "gxsessao": "NG8oJ2koREsiXSgmNCJEXW8nImBXJ0siLXwmS25uJyddJ11gH3xgaWkmfDR8IihLRFciLW5ERCJpJktXIktgJi00b3woJjR0NA==",
            "gxbot": "NG8oJ2koREsiXSgmNCJEXW8nImBXJ0siLXwmS25uJyddJ11gHy10RUo0"
        },
        projects_to_consult=projects['PROJETOS PESQUISAR'].array,
        google_sheet_id="1AMjoJGQmEhpAz5_-XqilCUe4P3-SArAMHtC8nCPR094",
        google_sheet_range="DADOS!A:ZZ",
        progress_callback=print,
    )
