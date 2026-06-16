import asyncio
from services.supabase_client import supabase_client


def fetch_all_products_sync():
    """
    Récupère les produits du tenant de l'utilisateur connecté.
    Grâce au RLS que nous avons configuré, Supabase filtre AUTOMATIQUEMENT
    les produits par tenant_id selon l'utilisateur connecté.
    """
    try:
        # Supabase utilise les politiques RLS pour appliquer le filtre invisible
        # lié à l'id de l'utilisateur connecté (auth.uid())
        response = supabase_client.table("products").select("*").execute()

        # Formatage des données pour correspondre aux clés attendues par ton CardItem
        products_list = []
        for row in response.data:
            products_list.append({
                "id": row["id"],
                "name": row["designation"],
                "catégorie": row["product_type"],
                "prix": int(row["price"]) if row["price"] else 0,
                "stock": row["stock"] if row["stock"] else 0,
                "image": row["image"]
            })
        return products_list
    except Exception as e:
        print(f"Erreur lors de la récupération des produits : {e}")
        return []

