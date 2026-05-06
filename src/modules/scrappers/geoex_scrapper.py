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
                                safe_get(result, ['response_body', 'PostePriPrev']) + safe_get(result, ['response_body', 'PosteSecPrev']),
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
            "cookies": "access_token=CfDJ8EerL3cRo_FKsXfpNBDca0V-hB7HWWzcaI0tAYeiG8lYHo5LTZPynCWZILukKJvLNSns9FFRI0lf04v8kRlB_wY_zkP2YSvQYZATSUCf7AnOM-9BUuo66xsD-AJBGc3UP1NYOJypmFFZ0xpzrifqdEi14eq6xwBDtcj7mRj4tpqcrurNC0CTOQDrCq4b9NMDwvYqRQSbdTds9kaMxPqYpuo2B1WaS9CVQtqdzysMrN9dVngYxb_GObCiIISgha3sS0kFCUodn6xfOj_ijmIs46obTVvLf322A4Ogb5yqHNty9OF-RBv1Qae5VloFLDFOwauInPNTodK8T77Ev-QkIVqQm4qrTKEXaYB9KFuk65V04Ye5zyRVLcFOm0vcVDesi0EQ3nlFYPCkLxiqgQd2eNTCEqPl1wDaaQLAH6UAzIKxYvAauoFTsWcNLQvWMq8IK1Iqp-7UNVBmbUqKDlGlg1Y; .AspNetCore.Session=CfDJ8EerL3cRo%2FFKsXfpNBDca0WgJlMVgkpjvhYFkss7GqLQFoXmZE7Bq7f7J0%2Bws8%2BJxSuBhS7YkCAs4euXZLB9zuxsdEhHMF09KkFljWmOQ8dlorcd3iwygxx0IF8vAz6BrijQEo8l%2FJ5trGz5T9SZnxdB55aTBS6AtXHrKFBMkVPR",
            "gxsessao": "XW5gSzdpdDciSzdgJyIoJmBLIktvKHQiV3xLXSg3V1d8fEt8HzdpN283bm9LIi18N0siRG9EbiJpN29LIm5uS29XJl00KDQmJw==",
            "gxbot": "XW5gSzdpdDciSzdgJyIoJmBLIktvKHQiV3xLXSg3V1d8fEt8Hy10RUo0"
        },
        projects_to_consult=projects['PROJETOS PESQUISAR'].array,
        google_sheet_id="1AMjoJGQmEhpAz5_-XqilCUe4P3-SArAMHtC8nCPR094",
        google_sheet_range="DADOS!A:ZZ",
        progress_callback=print,
    ) # executar comando python.exe -m src.modules.scrappers.geoex_scrapper
    # projects = SheetsPython().get_data_from_sheets(
    #     id_sheets="1Hx4nyAgSNSjl8QRvAnW5pCNBS3cC-5Id3e96XX4e_Bs",
    #     range_sheets="Página25!A1:A",
    #     with_headers=True
    # )
    # print(projects['PROJETOS PESQUISAR'].array)
    # GeoexScraper().scrape_projects_budgets(
    #     geoex_credentials={
    #         "cookies": "access_token=CfDJ8DYAIeEKlntJtLGnblY3-fOZ-sBGz2uDV9CW1GEBaYlqWen9TjBzGh3EGh2i0OX5aBKceWgqy4U2uvRVC0d7L2zxzkP-eMF0WB_muAKtnxVA6LHQ2yoDammIcK51PcjWL4F1VoFGICEdjqbMvAopTGc9fUlleixt6vqAen2aI902OVJBeWH04hGgFfw8ZWJZpUKiKVtH8MpE0ay0Lx-y3o5OEFNkeHtpyiM1XhN1F0uZrdxFmdGmRqw4YtBfJiTkwp5T5AOMWSDLmJDSkNh5kqtRwx4T4uA-DL4ZnneFeyNHt0e4PRh6E5IHfjUd_8fygKl9bNckx7jXPq2CYC3tVbRGso72ar76wER22aEDNSnbipFBhJNrzv_k14y4SCChJSb37mjOdfy2ySP4LauvjRl61muEyg77-12Lo-Sl1PMCXusOxN7JD9gw4goQAhCvCaSzKwYZ_JMqmp_Ak6auRro; .AspNetCore.Session=CfDJ8DYAIeEKlntJtLGnblY3%2BfPoySfSorajyO%2B31knKER%2B6nEOrjYxZGbHLh091UOufCqEtJoF%2F5%2FwF6DIHorXcxmXCVj9OGyTZzQjR27WFnR%2FYTx14hmLBwVzuhe61KCVGjMOn72Voi84dNt9Lt4ZqC249zlP7F7miUM8PazqaHNWJ; TemaEscuro=true; FirmaId=1; Home.Buscar.Texto=; ConsultarProjeto.Numero=B-1208863; cf_clearance=X0tcKwrowPKwSC5voowMn.MlI10l0nOGsYrT6pYh7Tk-1752843981-1.2.1.1-0NCSx8mTudiQxJPRvf.w.UCtvz_DdebcINxl1yi7kkyIAcSe0XqWcAaMHXpNoxE3i1uQKrUb_NTwpFwJ52z4O4tLtPweRNtDSIbebqxBuxRrR7qgiuF2vp5vw2FOvU2QjDAb0zt7q2mNTGZGvMxdHgL7zMEpcY2kneqWgL68721GPMyeM.LBamq2hfrLK23STSjSuQgIaE3xm9knxsP3wvI.O6TyfoynlqNFNnISw7c",
    #         "gxsessao": "NG8oJ2koREsiXSgmNCJEXW8nImBXJ0siLXwmS25uJyddJ11gHzdpN283bm9LIi18N0siRG9EbiJpN29LIm5uS29XJl00KDQmJw==",
    #         "gxbot": "NG8oJ2koREsiXSgmNCJEXW8nImBXJ0siLXwmS25uJyddJ11gHy10RUo0"
    #     },
    #     projects_to_consult=projects['PROJETOS PESQUISAR'].array,
    #     google_sheet_id="1AMjoJGQmEhpAz5_-XqilCUe4P3-SArAMHtC8nCPR094",
    #     google_sheet_range="ORC_GEOEX!A:ZZ",
    #     progress_callback=print,
    # )
