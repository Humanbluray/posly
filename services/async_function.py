import httpx
import asyncio
from typing import Dict, Any, Optional
from services.supabase_client import url, key

import httpx
from typing import Optional, Dict, Any


async def supabase_request_async(
        access_token: str,
        tenant_id: str,
        table_name: str,
        method: str = "GET",
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        supabase_url: str = url,  # Assure-toi que 'url' est défini globalement
        supabase_key: str = key,  # Assure-toi que 'key' est défini globalement
) -> Any:
    # Liste des fonctions RPC connues
    rpc_functions = ["valider_panier_rpc", "get_total_sales_by_date", "cloturer_journee_rpc"]
    is_rpc = table_name in rpc_functions

    # 1. Construction de l'URL
    if is_rpc:
        base_url = f"{supabase_url}/rest/v1/rpc/{table_name}"
        if data is None: data = {}
        # Injection automatique du tenant_id pour la sécurité
        data['p_tenant_id'] = tenant_id
    else:
        base_url = f"{supabase_url}/rest/v1/{table_name}"

    # 2. En-têtes
    final_headers = {
        "apikey": supabase_key,
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "Prefer": "return=representation" if method.upper() in ["POST", "PATCH"] else None,
    }
    # Nettoyage des headers None
    final_headers = {k: v for k, v in final_headers.items() if v is not None}
    if headers: final_headers.update(headers)

    # 3. Préparation des arguments
    # Pour les RPC : les arguments vont dans 'json=data'
    # Pour les Tables : les filtres vont dans 'params=final_params'
    final_params = params.copy() if params else {}
    if not is_rpc:
        final_params['tenant_id'] = f"eq.{tenant_id}"

    # 4. Exécution
    try:
        async with httpx.AsyncClient() as client:
            if is_rpc:
                # RPC : On force POST et on envoie les données en JSON
                response = await client.request(
                    method="POST",
                    url=base_url,
                    headers=final_headers,
                    json=data  # Paramètres envoyés dans le corps
                )
            else:
                # Tables : On utilise les paramètres d'URL (GET/POST/PATCH)
                response = await client.request(
                    method=method.upper(),
                    url=base_url,
                    headers=final_headers,
                    params=final_params,
                    json=data if method.upper() in ["POST", "PATCH"] else None
                )

            response.raise_for_status()
            return response.json() if response.text else None

    except httpx.HTTPStatusError as e:
        print(f"Erreur HTTP Supabase ({e.response.status_code}): {e.response.text}")
        return {"error": e.response.text}
    except Exception as e:
        print(f"Erreur générale: {e}")
        return {"error": str(e)}



    
    