import os
from supabase import create_client, Client

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

record_data = []


def get_data():
    response = supabase.table("syai_news").select("*").execute()
    return response.data


# def handle_record_updated():
#     pass


#     response = (
#         supabase.channel("room1")
#         .on_postgres_changes(
#             "*", schema="public", table="syai_news", callback=handle_record_updated
#         )
#         .subscribe()
#     )
