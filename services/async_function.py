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
        supabase_url: str = url,
        supabase_key: str = key,
) -> Any:
    rpc_functions = ["valider_panier_rpc", "get_total_sales_by_date", "cloturer_journee_rpc"]
    is_rpc = table_name in rpc_functions
    method_upper = method.upper()

    # 1. Construction de l'URL
    if is_rpc:
        base_url = f"{supabase_url}/rest/v1/rpc/{table_name}"
        if data is None: data = {}
        data['p_tenant_id'] = tenant_id
    else:
        base_url = f"{supabase_url}/rest/v1/{table_name}"

    # 2. En-têtes
    final_headers = {
        "apikey": supabase_key,
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "Prefer": "return=representation" if method_upper in ["POST", "PATCH"] else None,
    }
    final_headers = {k: v for k, v in final_headers.items() if v is not None}
    if headers: final_headers.update(headers)

    # 3. Préparation des filtres (params)
    final_params = params.copy() if params else {}
    if not is_rpc:
        # SÉCURITÉ : On n'ajoute le filtre d'URL eq.tenant_id QUE si on lit, modifie ou supprime.
        # Lors d'un POST (Insertion), les filtres d'URL sont ignorés ou génèrent des conflits.
        if method_upper in ["GET", "PATCH", "DELETE"]:
            final_params['tenant_id'] = f"eq.{tenant_id}"

    # 4. Exécution
    try:
        async with httpx.AsyncClient() as client:
            if is_rpc:
                response = await client.request(
                    method="POST",
                    url=base_url,
                    headers=final_headers,
                    json=data
                )
            else:
                response = await client.request(
                    method=method_upper,
                    url=base_url,
                    headers=final_headers,
                    params=final_params if final_params else None, # Passer uniquement s'il y a des filtres
                    json=data if method_upper in ["POST", "PATCH"] else None
                )

            response.raise_for_status()
            return response.json() if response.text else None

    except httpx.HTTPStatusError as e:
        print(f"Erreur HTTP Supabase ({e.response.status_code}): {e.response.text}")
        return {"error": e.response.text}
    except Exception as e:
        print(f"Erreur générale: {e}")
        return {"error": str(e)}


    
    