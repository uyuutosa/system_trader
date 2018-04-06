import hashlib
import hmac
import requests
import datetime 
import json 

class CcApi:
    API_KEY=""
    API_SECRET=""
    API_URL="https://coincheck.com"
    nonce=int((datetime.datetime.today() - datetime.datetime(2017,1,1)).total_seconds())*10
    #コンストラクタ
    def __init__(self,key,secret):
        self.API_KEY = key
        self.API_SECRET = secret
        return
    # CoinCheckのプライベートAPIリクエストを送信する
    def _private_api(self,i_path,i_nonce,i_params=None,i_method="get"):
        headers={'ACCESS-KEY':self.API_KEY,
                 'ACCESS-NONCE':str(i_nonce),
                 'Content-Type': 'application/json'}
        s = hmac.new(bytearray(self.API_SECRET.encode('utf-8')), digestmod=hashlib.sha256)
        c=None
        if i_params is None:
            w=str(i_nonce)+API_URL+i_path
            s.update(w.encode('utf-8'))
            headers['ACCESS-SIGNATURE']=s.hexdigest()
            if i_method=="delete":
                c=requests.delete(API_URL+i_path, headers=headers)
            else:
                c=requests.get(API_URL+i_path, headers=headers)
        else:        
            body=json.dumps(i_params);
            w=str(i_nonce)+API_URL+i_path+body
            s.update(w.encode('utf-8'))
            headers['ACCESS-SIGNATURE']=s.hexdigest()
            c=requests.post(API_URL+i_path, data=body, headers=headers)
        #戻り値のチェック
        if c.status_code!=200:
            raise Exception("HTTP ERROR status={0},{1}".format(c.status_code,c.text))
        j=c.json()
        if j["success"]!=True:
            raise Exception("API ERROR json={0}".format(j))
        return j
    # TradeAPIの共通部分
    def _trade_api(self,price,amount,order_type):
        self.nonce=self.nonce+1
        j=self._private_api("/api/exchange/orders",self.nonce,
            {
            "rate": price,
            "amount": amount,
            "order_type": order_type,
            "pair": "btc_jpy"    
        })
        return j
    #注文板情報を得る
    def orderbook(self):
        c=requests.get('https://coincheck.com/api/order_books')
        if c.status_code!=200:
            raise Exception("HTTP ERROR status={0}".format(c.status_code))
        j=c.json()
        return {"asks":[(float(i[0]),float(i[1])) for i in j["asks"]],"bids":[(float(i[0]),float(i[1])) for i in j["bids"]]}
    def balance(self):
        self.nonce=self.nonce+1
        c=self._private_api("/api/accounts/balance",self.nonce)
        return {"btc":float(c["btc"]),"jpy":float(c["jpy"])}
    # 売り注文を出す
    def sell(self,price,amount):
        j=self._trade_api(price,amount,"sell")
        return j["id"]
    #買い注文を出す
    def buy(self,price,amount):
        j=self._trade_api(price,amount,"buy")
        return j["id"]
    #注文をキャンセルする
    def cancel(self,oid):
        self.nonce=self.nonce+1
        return self._private_api(
            "/api/exchange/orders/"+str(oid),
            self.nonce,i_method="delete")
    #注文が有効かを返す
    def is_active_order(self,oid):
        self.nonce=self.nonce+1
        j=self._private_api("/api/exchange/orders/opens",self.nonce)
        w=[i["id"] for i in j["orders"]]
        return oid in w 


