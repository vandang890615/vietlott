from datetime import datetime
from typing import List, Dict

from bs4 import BeautifulSoup

from vietlott.crawler.products.base import BaseProduct
from vietlott.crawler.schema.requests import RequestMax3D, ORenderInfoCls

# Re-use 655 base for threading/fetch logic if possible, or just inherit BaseProduct and copy crawl logic if needed
# Actually inheriting Power655 is easier if logic is similar, but Max3D request body is different (RequestMax3D)
# So I should inherit BaseProduct and implement crawl, o reuse Power655 crawl but with my own logic.
# Power655 crawl method uses self.org_body. It uses cattrs to structure it. 
# It's better to inherit ProductPower655 to reuse the crawl method, just override org_body and process_result.

from vietlott.crawler.products.power655 import ProductPower655

class ProductMax3D(ProductPower655):
    name = "max3d"
    url = "https://vietlott.vn/ajaxpro/Vietlott.PlugIn.WebParts.GameMax3DCompareWebPart,Vietlott.PlugIn.WebParts.ashx"

    org_body = RequestMax3D(
        ORenderInfo=ProductPower655.orender_info_default,
        GameId="5", # numeric GameId for Max 3D
        GameDrawId="",
        PageIndex=1,
    )

    def process_result(self, params, body, res_json, task_data) -> List[Dict]:
        html_content = res_json.get("value", {}).get("HtmlContent", "")
        if not html_content:
             return []
        
        soup = BeautifulSoup(html_content, "lxml")
        data = []
        
        import re
        # Max 3D structure: each draw is in a <tr> with a single <td>
        for tr in soup.select("table tr"):
            td = tr.find("td")
            if not td: continue
            
            text = td.text
            # Extract ID: "Kỳ quay: 01037"
            id_match = re.search(r'Kỳ quay:\s*(\d+)', text)
            # Extract Date: "Ngày: 02/02/2026"
            date_match = re.search(r'Ngày:\s*(\d{2}/\d{2}/\d{4})', text)
            
            if not id_match or not date_match:
                continue
                
            row = {}
            row["id"] = id_match.group(1)
            row["date"] = datetime.strptime(date_match.group(1), "%d/%m/%Y").strftime("%Y-%m-%d")
            
            # Extract numbers from spans
            spans = td.select("span.bong_tron")
            nums = []
            current_num = ""
            for span in spans:
                val = span.text.strip()
                if val.isdigit():
                    current_num += val
                    if len(current_num) == 3:
                        nums.append(int(current_num))
                        current_num = ""
            
            row["result"] = nums
            row["page"] = body.get("PageIndex", -1)
            row["process_time"] = datetime.now().isoformat()
            data.append(row)
                
        return data


class ProductMax3DPro(ProductMax3D):
    name = "max3d_pro"
    url = "https://vietlott.vn/ajaxpro/Vietlott.PlugIn.WebParts.GameMax3DProCompareWebPart,Vietlott.PlugIn.WebParts.ashx"

    org_body = RequestMax3D(
        ORenderInfo=ProductPower655.orender_info_default,
        GameId="7", # numeric GameId for Max 3D Pro
        GameDrawId="",
        PageIndex=1,
    )
    # Reuse process_result as structure is likely similar
