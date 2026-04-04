import os
from dotenv import load_dotenv

# Load the environment variables from .env
load_dotenv()

def test_supabase_connection():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

    if not url or not key:
        print("❌ ERROR: Missing SUPABASE_URL or SUPABASE_KEY in your .env file!")
        return

    print(f"✅ Found SUPABASE_URL: {url}")
    print(f"✅ Found SUPABASE_KEY: {key[:10]}...[hidden]")

    try:
        from supabase import create_client, Client
        supabase: Client = create_client(url, key)

        print("\nAttempting to connect to the 'sessions' table...")
        
        # Test fetching data from the 'sessions' table
        response = supabase.table("sessions").select("*").limit(5).execute()
        
        print(f"✅ SUCCESS! Connected to Supabase.")
        print(f"📊 Found {len(response.data)} session(s). Here is the data:")
        for row in response.data:
            print(f"  - {row}")

    except Exception as e:
        print(f"\n❌ ERROR connecting to Supabase: {e}")

if __name__ == "__main__":
    test_supabase_connection()
