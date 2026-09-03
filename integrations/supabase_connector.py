import os
import json
import urllib.request
import urllib.error

class SupabaseConnector:
    def __init__(self, supabase_url=None, supabase_key=None):
        self.supabase_url = supabase_url or os.environ.get("SUPABASE_URL", "")
        self.supabase_key = supabase_key or os.environ.get("SUPABASE_ANON_KEY", "")

    def is_configured(self):
        return bool(self.supabase_url and self.supabase_key)

    def fetch_public_projects(self):
        if not self.is_configured():
            return {"status": "erro", "mensagem": "SUPABASE_ANON_KEY não configurado."}

        endpoint = f"{self.supabase_url.rstrip('/')}/rest/v1/core_studentproject?publico=eq.true&select=*"
        req = urllib.request.Request(endpoint, headers={
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}",
            "Content-Type": "application/json"
        })

        try:
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
                return {"status": "sucesso", "dados": data}
        except urllib.error.URLError as e:
            return {"status": "erro", "mensagem": str(e)}

    def insert_safe_report_comment(self, report_id, comentario):
        if not self.is_configured():
            return {"status": "offline_fallback", "mensagem": "Banco SQLite local em uso."}

        endpoint = f"{self.supabase_url.rstrip('/')}/rest/v1/safe_report_comments"
        payload = json.dumps({"report_id": report_id, "comentario": comentario}).encode("utf-8")
        
        req = urllib.request.Request(endpoint, data=payload, headers={
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }, method="POST")

        try:
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
                return {"status": "sucesso", "dados": data}
        except Exception as e:
            return {"status": "erro", "mensagem": str(e)}
