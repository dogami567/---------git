import httpx
import asyncio

async def main():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://127.0.0.1:8000/api/v1/competitions/")
            print(f"Status Code: {response.status_code}")
            print("Response JSON:")
            print(response.json())
    except httpx.ConnectError as e:
        print(f"Connection Failed: {e}")
        print("Error: The backend server is not running or not accessible.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 