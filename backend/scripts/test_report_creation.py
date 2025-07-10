import httpx
import json
import time
from pathlib import Path

# --- 配置 ---
BASE_URL = "http://127.0.0.1:8000"
ACCESS_TOKEN = "fake-jwt-token-for-user-3"

# --- 请求数据 ---
report_payload = {
    "title": "Automated PDF Test Report",
    "competition_ids": [1],
    "template_id": 1,
    "format": "pdf", # <--- 我们现在测试PDF格式
    "included_sections": ["basic_info", "summary", "schedule"]
}

headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

def run_full_test():
    """
    运行一个完整的端到端报告创建和下载测试。
    """
    try:
        with httpx.Client(timeout=60) as client:
            # --- 步骤 1: 创建报告记录 ---
            create_endpoint = f"{BASE_URL}/api/v1/reports/"
            print("--- 步骤 1: 创建报告 ---")
            print(f"向 {create_endpoint} 发送 POST 请求...")
            
            create_response = client.post(create_endpoint, json=report_payload, headers=headers)
            
            if create_response.status_code != 201:
                print(f"❌ 报告创建失败! 状态码: {create_response.status_code}")
                print("响应内容:", create_response.text)
                return

            print(f"✅ 报告创建成功! 状态码: {create_response.status_code}")
            report_data = create_response.json()
            report_id = report_data.get("id")
            print(f"新报告 ID: {report_id}")

            # --- 步骤 2: 下载生成的报告 ---
            # 等待片刻，以防文件生成需要时间
            print("\n--- 步骤 2: 下载报告 ---")
            print("等待2秒...")
            time.sleep(2)
            
            download_endpoint = f"{BASE_URL}/api/v1/reports/download/{report_id}"
            print(f"向 {download_endpoint} 发送 GET 请求...")

            download_response = client.get(download_endpoint, headers={"Authorization": f"Bearer {ACCESS_TOKEN}"})

            if download_response.status_code != 200:
                print(f"❌ 文件下载失败! 状态码: {download_response.status_code}")
                print("响应内容:", download_response.text)
                return

            print(f"✅ 文件下载成功! 状态码: {download_response.status_code}")

            # --- 步骤 3: 保存并验证文件 ---
            output_path = Path(__file__).parent / "test_output.pdf"
            output_path.write_bytes(download_response.content)
            
            print("\n--- 步骤 3: 验证文件 ---")
            if output_path.exists() and output_path.stat().st_size > 0:
                print(f"✅ 文件已成功保存到: {output_path}")
                print(f"文件大小: {output_path.stat().st_size} bytes")
                print("\n🎉 端到端测试成功!")
            else:
                print("❌ 文件保存失败或文件为空!")

    except httpx.ConnectError as e:
        print(f"\n❌ 连接错误: 无法连接到后端服务。请确保服务正在 {BASE_URL} 运行。")
    except Exception as e:
        print(f"\n❌ 发生未知错误: {e}")

if __name__ == "__main__":
    run_full_test() 