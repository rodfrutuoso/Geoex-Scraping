"""
    Module to consult project rejection detailed information in Geoex
    using the provided rejection id and session information.
"""
import cloudscraper

def consult_project_rejection_details_in_geoex(
    rejection_id : str,
    cookies : str,
    gxsessao : str,
    gxbot : str
    ) -> dict:
    """
    Consult a project rejection details in Geoex using the
    provided rejection id and session information.
    This function uses the cloudscraper library to
    bypass Cloudflare's anti-bot protection.

    Args:
        rejection_id (str): Rejection id to be consulted.
        cookies (str): Cookies for the request.
        gxsessao (str): GXSession ID for the request.
        gxbot (str): GXBot ID for the request.

    Returns:
        dict: A object containing the response status and body.
    """
    scraper = cloudscraper.create_scraper()

    response = scraper.post(
        'https://neoex.net.br/api/ConsultarProjeto/EnvioPasta/Item',
        json={"ProjetoEnvioPastaId": rejection_id},
        headers={
            "cookie": cookies,
            "gxsessao": gxsessao,
            "gxbot": gxbot,
            # "Content-Type": "application/json;charset=UTF-8",
            # "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
        }
    )

    response_data = response.json()

    return {
        "response_status": response.status_code,
        "response_body": response_data.get("Content")
    }
