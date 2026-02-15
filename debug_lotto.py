import requests
import json

headers = {
    'Accept': 'text/plain, */*; q=0.01',
    'Accept-Language': 'en-US,en;q=0.9',
    'X-AjaxPro-Method': 'GetDrawResult',
    'Content-Type': 'text/plain; charset=UTF-8',
    'Origin': 'https://vietlott.vn',
    'Referer': 'https://vietlott.vn/vi/trung-thuong/ket-qua-trung-thuong/max-4d',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36',
}

methods = [
    ('GameMax4DResultWebPart', 'GetDrawResult'),
    ('GameMax4DResultWebPart', 'ServerSideDrawResult'),
    ('GameMax4DCompareWebPart', 'ServerSideDrawResult'),
]

for webpart, method in methods:
    url = f'https://vietlott.vn/ajaxpro/Vietlott.PlugIn.WebParts.{webpart},Vietlott.PlugIn.WebParts.ashx'
    headers['X-AjaxPro-Method'] = method
    
    # Try different bodies
    bodies = [
        {"GameDrawId": 0},
        {"PageIndex": 1, "GameDrawId": 0},
        {"PageIndex": 1},
    ]
    
    print(f"Testing {webpart} / {method}...")
    
    for b in bodies:
        try:
            resp = requests.post(url, headers=headers, json=b, timeout=5)
            print(f"  Body: {b}")
            print(f"  Status: {resp.status_code}, Len: {len(resp.text)}")
            if "error" not in resp.text.lower() and len(resp.text) > 200:
                print(f"  SUCCESS? Content: {resp.text[:200]}...")
        except Exception as e:
            print(f"  Error: {e}")
            
    print("-" * 40)
