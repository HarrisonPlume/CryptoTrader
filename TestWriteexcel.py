import pandas as pd
import openpyxl
import xlsxwriter
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

#Test Control loop
buy= 10.26
Funds = 100
newassetcode = "MASK"
new_assetid = "45"
sell = 10.22
Asset_Amount = Funds/(buy*1.006)
Funds_at_purchase = Asset_Amount*buy
currentAsset = pd.DataFrame(columns=["id","code","Buy","Sell","Amount","FP"])
currentAsset.loc[0] = [str(new_assetid)]+[str(newassetcode)]+[float(buy)]+[float(sell)]+[float(Asset_Amount)]+[float(Funds_at_purchase)]
Funds_at_purchase = Asset_Amount*buy

oldProfit = 0

while True:
        print(".")
        #get higest apreciating asset at the moment
        
        if new_assetid != str(currentAsset["id"]):
            #sell current asset
            sell = float(input("Sell Price: "))
            if_sold_Funds = Asset_Amount*(sell-sell*0.006)
            Profit = if_sold_Funds - Funds
            
            if Profit < 0:
                print("\n")
                print("Asset Name:",newassetcode)
                print("Buy Price:",buy)
                print("Sell Price:",sell)
                print("Profit:",Profit)
                if Profit < -5.5:
                    #Sell condition
                    print("SOLD!", Funds)
                    Funds = if_sold_Funds
                    currentAsset["FS"] = Funds
                    with pd.ExcelWriter('Finance.xlsx',engine="openpyxl", mode='a',if_sheet_exists="overlay") as writer:
                        currentAsset.to_excel(writer, sheet_name='Sheet1', index=False, header = False, startrow=writer.sheets['Sheet1'].max_row )
                    break
            else:
                if Profit > oldProfit:   
                    #Check to see if the item is going negative
                    print("\n")
                    print("Asset Name:",newassetcode)
                    print("Buy Price:",buy)
                    print("Sell Price:",sell)
                    print("Profit:",Profit)
                    print("oldProffit", oldProfit)
                    oldProfit = Profit
                else:
                    #Sell condition
                    print("SOLD!", Funds)
                    print("Positive Profit!")
                    Funds = if_sold_Funds
                    currentAsset["FS"] = Funds
                    # Set up the SMTP server details for Outlook
                    smtp_server = "smtp.office365.com"
                    smtp_port = 587
                    smtp_username = "plume521@outlook.com"
                    smtp_password = "Tq49XUQ7"

                    # Set up the email details
                    sender = "plume521@outlook.com"
                    recipient = "plume521@outlook.com"
                    subject = "Crypto trader recorded a positive Profit"
                    message = "Hi Haz, a possitive proffit was recorded on your crypto trader bot. {} sold for: {}".format(newassetcode,if_sold_Funds)

                    # Create a MIME message
                    msg = MIMEMultipart()
                    msg['From'] = sender
                    msg['To'] = recipient
                    msg['Subject'] = subject
                    msg.attach(MIMEText(message))

                    # Connect to the SMTP server and send the email
                    with smtplib.SMTP(smtp_server, smtp_port) as server:
                        server.starttls()
                        server.login(smtp_username, smtp_password)
                        server.sendmail(sender, recipient, msg.as_string())
                    with pd.ExcelWriter('Finance.xlsx',engine="openpyxl", mode='a',if_sheet_exists="overlay") as writer:
                        currentAsset.to_excel(writer, sheet_name='Sheet1', index=False, header = False, startrow=writer.sheets['Sheet1'].max_row )
                    break