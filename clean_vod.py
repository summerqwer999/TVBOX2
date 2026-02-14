import requests
import json
import concurrent.futures

# 配置区
SOURCE_URL = "https://raw.githubusercontent.com/gaotianliuyun/gao/master/js.json"
EXCLUDE_KEYWORDS = ["网盘", "阿里", "夸克", "UC", "PikPak", "搜索", "云盘", "盘", "115"]

def check_url(site):
    """测试接口连通性"""
    name = site.get("name", "未知")
    api = site.get("api", "")
    
    # 如果不是 http 开头的，通常是加密接口或内部协议，暂时保留
    if not api.startswith("http"):
        return site

    try:
        # 尝试请求接口，超时设为 3 秒
        resp = requests.head(api, timeout=3, allow_redirects=True)
        if resp.status_code < 400:
            return site
    except:
        pass
    
    print(f"[-] 剔除失效源: {name}")
    return None

def main():
    try:
        print("🚀 正在下载原始源...")
        resp = requests.get(SOURCE_URL, timeout=15)
        data = resp.json()

        # 1. 彻底清空直播
        data["lives"] = []

        # 2. 预过滤：根据关键词剔除网盘/搜索类
        original_sites = data.get("sites", [])
        filtered_sites = [
            s for s in original_sites 
            if not any(k in s.get("name", "") for k in EXCLUDE_KEYWORDS)
        ]
        print(f"关键词过滤完成，剩余 {len(filtered_sites)} 个，准备测试连通性...")

        # 3. 并发测试连通性 (开启 10 个线程)
        final_sites = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(check_url, filtered_sites))
            final_sites = [r for r in results if r is not None]

        data["sites"] = final_sites
        
        # 4. 保存结果
        with open("my_vod.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        print(f"✅ 处理完成！最终保留点播源: {len(final_sites)} 个")

    except Exception as e:
        print(f"❌ 运行出错: {e}")

if __name__ == "__main__":
    main()
