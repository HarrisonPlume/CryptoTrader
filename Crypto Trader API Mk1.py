import xlsxwriter
import os
import pyswyft as sw
import markets
import accounts
import Auth
from ibroker_api import (
    ITradeAPI,
    Asset,
    Account)

os.chdir("G:\Crypto Trader")

MARKET_BUY = 1
MARKET_SELL = 2
LIMIT_BUY = 3
LIMIT_SELL = 4
STOP_LIMIT_BUY = 5
STOP_LIMIT_SELL = 6
DUST_SELL = 8

ORDER_MAP = {
    "MARKET_BUY": MARKET_BUY,
    "MARKET_SELL": MARKET_SELL,
    "LIMIT_BUY": LIMIT_BUY,
    "LIMIT_SELL": LIMIT_SELL,
    "STOP_LIMIT_BUY": STOP_LIMIT_BUY,
    "STOP_LIMIT_SELL": STOP_LIMIT_SELL,
    "DUST_SELL": DUST_SELL,
}

# Create an new Excel file and add a worksheet.
workbook = xlsxwriter.Workbook('Finance.xlsx')
worksheet = workbook.add_worksheet()

# Increase the cell size of the merged cells to highlight the formatting.
worksheet.set_column('A:C', 15)


# Create a format to use in the merged range.
merge_format = workbook.add_format({
    'bold': 1,
    'border': 1,
    'align': 'center',
    'valign': 'vcenter',
    'fg_color': '#acacac'})


# Merge 3 cells.
worksheet.merge_range('A1:C1', 'Crypto Trader MK1', merge_format)

workbook.close()



class SwiftxAPI(ITradeAPI):
    def __init__(
        self,
        access_token:str,
        demo_mode: bool = True,
    ):
        self.access_token = access_token
        self.api = sw.API(access_token,environment="demo")

        self.default_curency = "AUD"

        #Build up data structures
        self._build_assets_list()

    def _build_assets_list(self) -> bool:
        tempAPI = sw.API(access_token=self.access_token, environment='live')
        raw_assets = tempAPI.request(markets.MarketsAssets())
        valid_assets = []
        self._invalid_assets = {}
        #convert request to asset objects
        for this_asset in raw_assets:
            yf_symbol = self._sw_to_yf(this_asset["code"])
            minimum_order = float(this_asset["minimum_order"])
            minimum_order_increment = float(this_asset["minimum_order_increment"])
            asset_obj = Asset(
                symbol=yf_symbol,
                min_quantity=minimum_order,
                min_quantity_increment=minimum_order_increment,
                min_price_increment=0.00001,
            )
            asset_obj.id = this_asset["id"]
            if self._is_invalid_asset(this_asset):
                self._invalid_assets[yf_symbol] = asset_obj
            else:
                valid_assets.append(asset_obj)
            counter += 1

        # #set up the asset lists
        self._asset_list_by_yf_symbol = self._structure_asset_dict_by_yf_symbol(valid_assets)
        self._asset_list_by_id = self._structure_asset_dict_by_id(valid_assets)

        return True

    
    def get_asset(self, symbol: str) -> Asset:
        return self._asset_list_by_yf_symbol[symbol]

    def get_asset_by_id(self, id) -> Asset:
        return self._asset_list_by_id[id]
    
    def _sw_to_yf(self, sw_symbol: str) -> str:
        skip_symbols = ["AUD", "USD"]
        if sw_symbol in skip_symbols:
            return sw_symbol
        return sw_symbol + "-USD"

    def _is_invalid_asset(self, asset_dict:dict) -> dict:
        if (
            asset_dict["tradable"] == 0
            or asset_dict["buyDisabled"] == 1
            or asset_dict["delisting"] == 1
        ):
            return True
        return False

        

    def _structure_asset_dict_by_id(self, asset_dict: dict) -> dict:
        return_dict = {}
        for asset in asset_dict:
            return_dict[asset.id] = asset
        return return_dict

    def _structure_asset_dict_by_yf_symbol(self, asset_dict: dict) -> dict:
        return_dict = {}
        for asset in asset_dict:
            return_dict[asset.symbol] = asset
        return return_dict
    
    def get_asset_list_by_yf_symbol(self):
        return self._asset_list_by_yf_symbol
    
    def get_asset_list_by_id(self):
        return self._asset_list_by_id
    
    def order_id_to_text(self, id) -> str:
        return ORDER_MAP[id]
    
    def get_account(self) -> Account:
        """Retrieves data about the trading account
        Returns:
            Account: User's trading account information
        """
        # AccountBalance
        assets = {}
        request = self.api.request(accounts.AccountBalance())

        for asset in request:
            symbol = self._asset_list_by_id[asset["assetId"]].symbol
            if symbol == self.default_currency:
                balance = float(asset["availableBalance"])
                if balance < 10:
                    assets[symbol] = 0
                else:
                    assets[symbol] = float(asset["availableBalance"]) - 10
            else:
                assets[symbol] = float(asset["availableBalance"])

        return Account(assets=assets)
    
    def get_NEW_API_ACESS_TOKEN(self):
        request = self.api.request(Auth.APIKEY())
        return request


#Get pyswift API to work
API_Key = "xTlsq__GGNCW5Ps7O7M4luaRlsmgNvLkiZ2GOMrsp0lYB"

Access_Token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IlJrVTRRelF6TlRaQk5rTkNORGsyTnpnME9EYzNOVEZGTWpaRE9USTRNalV6UXpVNE1UUkROUSJ9.eyJodHRwczovL3N3eWZ0eC5jb20uYXUvLWp0aSI6IjFlN2IyMzhhLWY3ZTMtNDNjYy1hNjUyLWMyM2Q4Nzc2ZjA2MCIsImh0dHBzOi8vc3d5ZnR4LmNvbS5hdS8tbWZhX2VuYWJsZWQiOmZhbHNlLCJodHRwczovL3N3eWZ0eC5jb20uYXUvLXVzZXJVdWlkIjoidXNyX01QRTFGVnRrUDc4MW5jYjQzajJyTkwiLCJodHRwczovL3N3eWZ0eC5jb20uYXUvLWNvdW50cnlfbmFtZSI6IkF1c3RyYWxpYSIsImh0dHBzOi8vc3d5ZnR4LmNvbS5hdS8tY2l0eV9uYW1lIjoiU3lkbmV5IiwiaXNzIjoiaHR0cHM6Ly9zd3lmdHguYXUuYXV0aDAuY29tLyIsInN1YiI6ImF1dGgwfDY0MWZhNmQ2NmFjNTg0YmUzMWJmYzQ0NCIsImF1ZCI6Imh0dHBzOi8vYXBpLnN3eWZ0eC5jb20uYXUvIiwiaWF0IjoxNjc5ODA0MTE4LCJleHAiOjE2ODA0MDg5MTgsImF6cCI6IkVRdzNmYUF4T1RoUllUWnl5MXVsWkRpOERIUkFZZEVPIiwic2NvcGUiOiJhcHAgYXBwLmFjY291bnQgYXBwLmFjY291bnQuYWZmaWxpYXRpb24gYXBwLmFjY291bnQubW9kaWZ5IGFwcC5hY2NvdW50LnRheC1yZXBvcnQgYXBwLmFjY291bnQudmVyaWZpY2F0aW9uIGFwcC5hY2NvdW50LmJhbGFuY2UgYXBwLmFjY291bnQuc3RhdHMgYXBwLmFjY291bnQucmVhZCBhcHAucmVjdXJyaW5nLW9yZGVycyBhcHAucmVjdXJyaW5nLW9yZGVycy5yZWFkIGFwcC5yZWN1cnJpbmctb3JkZXJzLmNyZWF0ZSBhcHAucmVjdXJyaW5nLW9yZGVycy5kZWxldGUgYXBwLmFkZHJlc3MgYXBwLmFkZHJlc3MuYWRkIGFwcC5hZGRyZXNzLnJlbW92ZSBhcHAuYWRkcmVzcy5jaGVjay1kZXBvc2l0IGFwcC5hZGRyZXNzLnJlYWQgYXBwLmZ1bmRzIGFwcC5mdW5kcy53aXRoZHJhdyBhcHAuZnVuZHMud2l0aGRyYXdhbC1saW1pdCBhcHAuZnVuZHMucmVhZCBhcHAub3JkZXJzIGFwcC5vcmRlcnMuY3JlYXRlIGFwcC5vcmRlcnMuZGVsZXRlIGFwcC5vcmRlcnMucmVhZCBhcHAub3JkZXJzLmR1c3QgYXBwLmFwaSBhcHAuYXBpLnJldm9rZSBhcHAuYXBpLnJlYWQgb2ZmbGluZV9hY2Nlc3MiLCJndHkiOiJwYXNzd29yZCJ9.RHYRm5w2OF3eh1kld7nZUoij1Csjx5DM7x3EQ4hGN2xcaEIyDTdlu8ly2uPl_6dCbAOlFIdkYN4nU3i_MuRncpnMy5D1S0Ew1NnrA40Zj1cMO7XvkTQwJxJLHii7N0CtNGlYAmMTjXeWKWEVa4dAopbDImpHS5dLaOr6ItvtEr4NyUmVNaZeJVYkkR5davbth3TUGl1pDHoF6ZGYwswzWIGdPcKxN5c1CsHPNpdR9OvbAMAbmnWwZTE_k89ZgDB4oMXWAvwG9g158yRElJsLE3K_Hx_iOnwqhDnjBcXCZ2yrPwTCBVi6hr3TfC3u0eSvvSF1huCWF8GfaTU8lQ2HSQ"


#Create the API Object
TestAPI = SwiftxAPI(access_token=Access_Token)
print(TestAPI.get_NEW_API_ACESS_TOKEN())
#Print account info
# a = TestAPI.get_account()
# print(a)
