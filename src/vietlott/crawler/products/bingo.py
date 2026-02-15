from typing import List, Dict
import pendulum
from bs4 import BeautifulSoup
from vietlott.crawler.products.power655 import ProductPower655
from vietlott.crawler.schema.requests import Bingo

class ProductBingo(ProductPower655):
    name = "bingo18"
    url = "https://vietlott.vn/ajaxpro/Vietlott.PlugIn.WebParts.GameBingoCompareWebPart,Vietlott.PlugIn.WebParts.ashx"

    org_body = Bingo(
        DrawDate="",
        GameDrawNo="",
        GameId="8",
        ORenderInfo=ProductPower655.orender_info_default,
        PageIndex=1,
        ProcessType=0,
        TotalRow=1000,
        number="",
    )

    def process_result(self, params, body: dict, res_json: dict, task_data: dict) -> List[Dict]:
        soup = BeautifulSoup(res_json.get("value", {}).get("HtmlContent"), "lxml")
        data = []
        for i, tr in enumerate(soup.select("table tr")):
            if i == 0:
                continue
            tds = tr.find_all("td")
            if not tds or len(tds) < 2: continue
            
            row = {}
            try:
                # Date and ID are usually links or text in first TD
                td_first = tds[0]
                links = td_first.find_all("a")
                if links:
                    row["date"] = pendulum.from_format(links[0].text.strip(), "DD/MM/YYYY").to_date_string()
                    row["id"] = links[1].text.strip()
                else:
                    # Fallback
                    text = td_first.text.strip()
                    row["date"] = datetime.now().strftime("%Y-%m-%d") # Placeholder
                    row["id"] = text
                
                # Result in second TD - spans
                spans = tds[1].find_all("span")
                row["result"] = [int(s.text.strip()) for s in spans if s.text.strip().isdigit()]
                
                row["page"] = body.get("PageIndex", -1)
                data.append(row)
            except:
                continue
        return data
