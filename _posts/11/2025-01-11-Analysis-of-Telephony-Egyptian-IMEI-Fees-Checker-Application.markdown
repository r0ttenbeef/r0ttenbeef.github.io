---
layout: post
title: Analysis of Telephony Egyptian IMEI Fees Checker Application
date: 2025-01-11
image: 11/00-main.jpg
tags: android ReverseEngineering
---

من بعد ما نزل تطبيق Telephony اللي بيتيح لمصلحة الجمارك المصرية للتحقق من حالة الهواتف المستوردة إلى البلاد بدأ تظهر تخوفات تجاه التطبيق ده و انه ليه مساحته كبيرة جدا مقارنة ب اللي المفروض بيعمله و هو انه مجرد بيعمل تحقق لموديل الهاتف من خلال كود ال IMEI فقط ؟
طيب اول حاجة خلينا نشوف ازاي التطبيق ده بيشتغل و نحاول نعمله هندسه عكسية سريعه و ناخد فكره عنه.

اول حاجة خلينا نعمل decompile لل APK ب apktool .. انا حملت التطبيق من Apkpure : https://apkpure.com/telephony/com.ntra.citizen
![1.png](/img/11/1.png)

التطبيق لما بينزل من apkpure بينزل بصيغة **.xapk** و بيكون عبارة عن zip file عادي .. انا هنا عملتله extract ب **7z** و طلع معايا 4 apk
- **com.ntra.citizen.apk** : **118M**
- config.arm64_v8a.apk : 59M
- config.en.apk : 95k
- config.mdpi.apk : 204k
![2.png](/img/11/2.png)

طبعا التركيز هيكون علي com.ntra.citizen.apk .. لو بصينا علي ال files بعد ال decompilation هنلاقي فيه directories مساحتها مبالغ فيها شوية
- assets: **86M**
خلينا من ال smali classes دلوقتي هنرجعلها بعدين و خلينا نروح علي ال assets
![3.png](/img/11/3.png)

لما عملت find علي ال files الموجودة جوا ال directory بتاع assets علي الفايلات اللي اكبر من 10MB هتلاقي فايل **db.dat** مساحته 76MB
![4.png](/img/11/4.png)

طبعا الفايل مش واضح هو ايه حتي لو فتحناه ف hex viewer مش هنلاقي حاجة ف ال magic bytes بتاعت الفايل تحدد ايه ال file type ده لكن واضح من ال extension بتاعته انه database
![5.png](/img/11/5.png)

لما عملت binwalk علي db.dat لقيت فيه ZIP Archives كتير ف عملتلهم extract
![6.png](/img/11/6.png)

ال files اللي اتعملها extract ال extensions بتاعتها عبارة عن:
- .dat
- .dnn
- .onnx
![7.png](/img/11/7.png)

لو بصينا علي ال strings في file عشوائي من onnx files دول هنلاقي strings مشتركة ليها علاقة ب onnx modules و onnx runtime
![8.png](/img/11/8.png)

ف نلاقي ان دي files تابعة ل framework اسمه Onnx 
> ***ONNX** is an open format built to represent machine learning models*
![9.png](/img/11/9.png)

لو عملنا سيرش بقي علي Regula اللي موجود ف ال path هنلاقي انه ليه علاقة ب Regula Forensics و اللي بيستخدم ال AI ف انه يعمل تحقق للبطاقات و الباسبورات و التعرف علي الوجه و خلافه https://regulaforensics.com/solutions/industries/banking/
> ***Regula Forensics** Helps organizations make document authentication and identity verification seem easy*
![10.png](/img/11/10.png)

و اللي ليهم اصلا تطبيق منفصل 
![11.png](/img/11/11.png)

نقدر نتأكد لو حملنا التطبيق ده و نعمله decompile بنفس الطريقة و نشوف محتواه هنلاقي نفس ال db.dat بنفس ال architectures 
![12.png](/img/11/12.png)

خلينا نطلع من ال rabbit hole ده بقي و نشوف التطبيق ده بيشتغل ازاي و بيعمل تحقق لل IMEI منين.
المرة دي هنعمل decompile ب jadx عشان نقدر نشوف الكود بطريقة نفهمها .. توقعت ان الكود ممكن يكون معموله obfuscation بس في واقع الامر لا.

خلينا نشوف اول حاجة خالص ال permissions 
![13.png](/img/11/13.png)

ال Google API key
![14.png](/img/11/14.png)

لما قلبت شوية ف الكود بتاع التطبيق لقيت فيه حاجات تبع efinance sdk و mastercard و intuit و [JakeWharton ThreeTenABP](https://github.com/JakeWharton/ThreeTenABP) كلها ليها علاقة بال online payment 
المهم ان ركزت علي **com/ntra** .. فيه file اسمه Constants.java و ده فيه URLs متخزنة ف constant variables نقدر نقول عليها APIs 
- https://login.di.gov.eg/realms/digitalegypt/protocol/openid-connect/logout?client_id=ceir-portal&post_logout_redirect_uri=https://api-citizens-prod-imei.gs-ef.com : بوابة تسجيل الدخول مصر الرقمية
- https://login.di.gov.eg/realms/digitalegypt/protocol/openid-connect/auth?response_type=code&redirect_uri=https://api-citizens-prod-imei.gs-ef.com&client_id=ceir-portal
- https://minio-prod-imei.gs-ef.com:9000/logo
- https://api-citizens-prod-imei.gs-ef.com
![15.png](/img/11/15.png)

و في ال **app/common/core/util** برضو فيه فايل **Constant.java** فيه API URLs تانيه
- https://sandbox.di.gov.eg/realms/sandbox/protocol/openid-connect/auth?state=7F9CC7E9-0D3C-4867-A2C4-702B3435C7B4&response_type=code&scope=openid&client_id=ceir_portal&redirect_uri=https://imei.tra.gov.eg/userportal
- https://sandbox.di.gov.eg/realms/sandbox/protocol/openid-connect/auth?state=7F9CC7E9-0D3C-4867-A2C4-702B3435C7B4&response_type=code&scope=openid&client_id=ceir_portal&redirect_uri=https://imei.tra.gov.eg/userportal
- https://sandbox.di.gov.eg/realms/sandbox/protocol/openid-connect/logout?client_id=ceir_portal&post_logout_redirect_uri=https://imei.tra.gov.eg/userportal
![16.png](/img/11/16.png)

هنلاقي فايل اسمه RefreshApi.java و ده بيعمل Post Request علي واحد من ال APIs اللي فوق عشان يعمل refresh لل API tokens
![17.png](/img/11/17.png)

و في نفس ال path هنلاقي فايل Api.java و ده فيه كل ال POST Requests اللي بتتعمل علي ال APIs 
![18.png](/img/11/18.png)

هنا هنلاقي انه بيبعت Post request لل data بتاعت ال user لل API .. و اللي ملاحظه هنا ف الكود انه بيبعت IMEI مع اسم المستخدم و صورته و رقم الباسبور و ميعاد الوصول
![19.png](/img/11/19.png)

![20.png](/img/11/20.png)

و هنا هنلاقي results برضو بس اقل و ده معناه انه فيه registered check و unregistered check
![21.png](/img/11/21.png)

لو جمعنا كل جزء مع بعض نقدر نفهم ان التطبيق بيبعت Post Request لل Base API و ال data بيكون فيها ال **imeiNumber** 
![22.png](/img/11/22.png)

هنا هيبدأ يعمل Authenticated Request و بيضيف ال headers
- `"Content-Type", "application/json"` كده الداتا بتتبعت json
- `HttpHeaders.ACCEPT, "*/*"`
- `"clientType", "Android"`
![23.png](/img/11/23.png)

بعد شوية كتير فضلت اجرب curl و ابعت post request زي ما ال application بيبعت لحد ما عملت سكريبت بايثون بسيط اقدر اعمل منه check علي IMEI
مفيش اي validations ولا tokens لكن فيه rate limitation و عدد 10 trials 

```python
#!/usr/bin/python3
import requests
import sys
from optparse import OptionParser

def api_request(host, url, imei_num):
    headers = {
        "Host": host,
        "User-Agent": "NTRA",
        "Content-Type": "application/json",
        "Connection": "keep-alive",
        "Accept-Language": "en",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept": "*/*"
    }

    data = {"imeiNumber": [imei_num]}

    response = requests.post(f"https://{host}/{url}", json=data, headers=headers)

    return response
    
def main(imei):
    api_host = "api-citizens-prod-imei.gs-ef.com"
    api_url_path = "ceirimeicheck/api/v1/imei/check"
    resp_info = api_request(api_host, api_url_path, imei)
     

    match resp_info.status_code:
        case 403:
            if "supportID" in resp_info.text:
                print("[x] Your IP might have been blocked because you have exceeded submission trials.")
                print(resp_info.json())
        case 400:
            if resp_info.json()["status"]["error"] == "Invalid IMEI Exception" or resp_info.json()["status"]["error"] == "An error occurred in the data sent!":
                print("[x] Invalid IMEI number")
        case 404:
            if resp_info.json()["status"]["error"] == "Device Model Does Not Exit Exception":
                print("[x] Device model is not exist")
        case 200:
            if "model" in resp_info.text:
                print("[*] IMEI number is valid")
                print("[+] Manufacturer: " + resp_info.json()["result"]["manufacturerName"])
                print("[+] Model: " + resp_info.json()["result"]["model"])
                print("[+] Registeration Status: " + resp_info.json()["result"]["status"])
                print("[+] Activity Status: " + resp_info.json()["result"]["active"])
                print("[*] Number of trials left: " + str(resp_info.json()["result"]["numberOfTrialsLeft"]))
        case default:
            print(resp_info.json())
                

if __name__ == '__main__':
    print("NTRA IMEI fees checker - r0ttenbeef")
    parser = OptionParser(usage="%prog [options]")
    parser.add_option("-i", "--imei", dest="imei", default=None, help="Provide IMEI number of device model")
    (options, args) = parser.parse_args()
    if options.imei != None:
        main(options.imei)
    else:
        parser.error("[-] Please provide IMEI number of device model, Use -h, --help for help menu.")
        sys.exit(1)

```
![24.png](/img/11/24.png)

### Useful Indicators

- Filenames:
```c
exported_model_Korea1042.onnx
exported_model_China2052.onnx
exported_model_Korea1042.onnxPK
exported_model_China2052.onnxPK
handwritten_model.onnx
epoch_00068-test_0.98437-train_0.97540-validation_0.99218_recipient_model_Quant_freeze.onnx
handwritten_model.onnxPK
epoch_00068-test_0.98437-train_0.97540-validation_0.99218_recipient_model_Quant_freeze.onnxPK
epoch_00043-test_0.99999-train_0.99629-validation_0.99813_model_Global.onnx
epoch_00043-test_0.99999-train_0.99629-validation_0.99813_model_Global.onnx
are_1102875519_20220923.onnx
are_1102875519_20220923.onnx
checkpoint_0300_with_nms.onnx
checkpoint_0300_with_nms.onnx
are_-1381771989_20220922.onnx
are_-1381771989_20220922.onnx
epoch_00295-test_1.0-train_0.96093-validation_1.0_model_Global.pth.onnx
epoch_00295-test_1.0-train_0.96093-validation_1.0_model_Global.pth.onnx
mex_448926514_20220718.onnx
mex_448926514_20220718.onnx
deu_454858311_20220727.onnx
deu_454858311_20220727.onnx
model.onnx
model.onnx
DocumentHologramModel_128x128_Paraguay_fixed_labels5_14.08.2023.onnx
DocumentHologramModel_128x128_Paraguay_fixed_labels5_14.08.2023.onnx
border_detector.onnx
russian_stamp_segmentator.onnx
border_detector.onnxPK
russian_stamp_segmentator.onnxPK
```


