# notes_project/supabase_client.py
from supabase import create_client, Client

url: str = "https://mqkygzptkzpmrsyjjeyf.supabase.co"
key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1xa3lnenB0a3pwbXJzeWpqZXlmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTkzNjE2OTEsImV4cCI6MjAzNDkzNzY5MX0.yeKHh36VNcQw-i4GEwm2Ta8oGo6iXsb3lIoJO3rjugc"

supabase: Client = create_client(url, key)
