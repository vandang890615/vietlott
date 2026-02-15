from vietlott.crawler.products.power655 import ProductPower655
from vietlott.crawler.schema.requests import RequestPower655, ORenderInfoCls

class ProductLotto(ProductPower655):
    name = "lotto"
    # Actually Lotto 5/35?
    # Based on browser finding: Game535ResultDetailWebPart
    # But usually CompareWebPart is used for history crawling.
    # Let's guess Game535CompareWebPart exists.
    url = "https://vietlott.vn/ajaxpro/Vietlott.PlugIn.WebParts.Game535CompareWebPart,Vietlott.PlugIn.WebParts.ashx"

    # Lotto 5/35 probably similar to 6/45 but 5/35.
    # ArrayNumbers structure needs checking. Assuming 5 numbers.
    org_body = RequestPower655(
        ORenderInfo=ProductPower655.orender_info_default,
        Key="8e794f99", # Updated from 5c24ced4
        GameDrawId="",
        ArrayNumbers=[["" for _ in range(35)] for _ in range(5)], # 35 elements instead of 18
        CheckMulti=False,
        PageIndex=0,
    )
