# User Manual for MOSDAC Data Download API | Meteorological & Oceanographic Satellite Data Archival Centre

**URL:** https://mosdac.gov.in/downloadapi-manual#mdda-hfydi
**Extracted:** 2025-09-15T15:50:39.997786
**Quality Score:** 0.850

[Skip to main Content](https://mosdac.gov.in/downloadapi-manual#main-content "Skip to main Content")
[-A](javascript:;) [A](javascript:;) [+A](javascript:;)
[A](javascript:drupalHighContrast.enableStyles\(\))[A](javascript:drupalHighContrast.disableStyles\(\))
हिन्दी English
## Secondary menu
  * [SignUp](https://mosdac.gov.in/internal/registration)
  * [Login](https://mosdac.gov.in/internal/uops)
  * [Logout](https://mosdac.gov.in/internal/logout)

[ ![Home](https://mosdac.gov.in/sites/default/files/mosdac_small.png) ](https://mosdac.gov.in/ "Home")
**[ Meteorological & Oceanographic Satellite Data Archival Centre](https://mosdac.gov.in/ "Home") **
Space Applications Centre, ISRO 
  * [Home](https://mosdac.gov.in/)
  * [Missions »](https://mosdac.gov.in/downloadapi-manual)
    * [INSAT-3DR](https://mosdac.gov.in/insat-3dr)
    * [INSAT-3D](https://mosdac.gov.in/insat-3d)
    * [KALPANA-1](https://mosdac.gov.in/kalpana-1)
    * [INSAT-3A](https://mosdac.gov.in/insat-3a)
    * [MeghaTropiques](https://mosdac.gov.in/megha-tropiques)
    * [SARAL-AltiKa](https://mosdac.gov.in/saral-altika)
    * [OCEANSAT-2](https://mosdac.gov.in/oceansat-2)
    * [OCEANSAT-3](https://mosdac.gov.in/oceansat-3)
    * [INSAT-3DS](https://mosdac.gov.in/insat-3ds)
    * [SCATSAT-1](https://mosdac.gov.in/scatsat-1)
  * [Catalog »](https://mosdac.gov.in/downloadapi-manual)
    * [Satellite](https://mosdac.gov.in/internal/catalog-satellite)
    * [Insitu (AWS)](https://mosdac.gov.in/internal/catalog-insitu)
    * [RADAR](https://mosdac.gov.in/internal/catalog-radar)
  * [Galleries »](https://mosdac.gov.in/downloadapi-manual)
    * [Satellite Products](https://mosdac.gov.in/internal/gallery)
    * [Weather Forecast](https://mosdac.gov.in/internal/gallery/weather)
    * [Ocean Forecast](https://mosdac.gov.in/internal/gallery/ocean)
    * [RADAR (DWR)](https://mosdac.gov.in/internal/gallery/dwr)
    * [Global Ocean Current](https://mosdac.gov.in/internal/gallery/current)
  * [Data Access »](https://mosdac.gov.in/downloadapi-manual)
    * [Order Data](https://mosdac.gov.in/internal/uops)
    * [API based Access](https://mosdac.gov.in/downloadapi-manual)
    * [Open Data »](https://mosdac.gov.in/downloadapi-manual)
      * [Atmosphere »](https://mosdac.gov.in/downloadapi-manual)
        * [Bayesian based MT-SAPHIR rainfall](https://mosdac.gov.in/bayesian-based-mt-saphir-rainfall)
        * [GPS derived Integrated water vapour](https://mosdac.gov.in/gps-derived-integrated-water-vapour)
        * [GSMap ISRO Rain](https://mosdac.gov.in/gsmap-isro-rain)
        * [METEOSAT8 Cloud Properties](https://mosdac.gov.in/meteosat8-cloud-properties)
      * [Land »](https://mosdac.gov.in/downloadapi-manual)
        * [3D Volumetric TERLS DWRproduct](https://mosdac.gov.in/3d-volumetric-terls-dwrproduct)
        * [Inland Water Height](https://mosdac.gov.in/inland-water-height)
        * [River Discharge](https://mosdac.gov.in/river-discharge)
        * [Soil Moisture](https://mosdac.gov.in/soil-moisture-0)
      * [Ocean »](https://mosdac.gov.in/downloadapi-manual)
        * [Global Ocean Surface Current](https://mosdac.gov.in/global-ocean-surface-current)
        * [High Resolution Sea Surface Salinity](https://mosdac.gov.in/high-resolution-sea-surface-salinity)
        * [Indian Mainland Coastal Product](https://mosdac.gov.in/indian-mainland-coastal-product)
        * [Ocean Subsurface](https://mosdac.gov.in/ocean-subsurface)
        * [Oceanic Eddies Detection](https://mosdac.gov.in/oceanic-eddies-detection)
        * [Sea Ice Occurrence Probability](https://mosdac.gov.in/sea-ice-occurrence-probability)
        * [Wave based Renewable Energy](https://mosdac.gov.in/wave-based-renewable-energy)
    * [Cal-Val](https://mosdac.gov.in/internal/calval-data)
    * [Forecast](https://mosdac.gov.in/internal/forecast-menu)
    * [RSS Feeds](https://mosdac.gov.in/rss-feed "ISROCast")
  * [Reports »](https://mosdac.gov.in/downloadapi-manual)
    * [Calibration »](https://mosdac.gov.in/downloadapi-manual)
      * [Insitu](https://mosdac.gov.in/insitu)
      * [Relative](https://mosdac.gov.in/calibration-reports)
    * [Validation](https://mosdac.gov.in/validation-reports)
    * [Data Quality](https://mosdac.gov.in/data-quality)
    * [Weather](https://mosdac.gov.in/weather-reports)
  * [Atlases](https://mosdac.gov.in/atlases)
  * [Tools](https://mosdac.gov.in/tools)
  * [Sitemap](https://mosdac.gov.in/sitemap)
  * [Help](https://mosdac.gov.in/help)


## You are here
[Home](https://mosdac.gov.in/) » [Data Access](https://mosdac.gov.in/downloadapi-manual) » API based Access
# User Manual for MOSDAC Data Download API
## **Overview:**
Welcome to the User Manual for **MOSDAC Data Download API**!
This tool allows you to download satellite data seamlessly using a simple configuration fileâ€”config.json. Once you have filled out this file correctly according to your download requirements, simply run the script mdapi.py. No need to modify any code!
This manual will provide you step-by-step guide to download data though "**MOSDAC Data Download API** ".
## **1. Prerequisites:**
**For running this application, you will need following things:**
**i**. Python (Version 3+)
**ii.** Python Library: 'requests'
**iii.** MOSDAC Account credentials (Refer section 5 for '[Authentication](https://mosdac.gov.in/node/2035#mdda-aar)')
**iv.** 'datasetId' (Refer section 5 for '[How to find your DatasetId (datasetId)](https://mosdac.gov.in/downloadapi-manual#mdda-hfydi)?')
**Optional Requirement:**
**i.** Python Library: 'tqdm'
**Steps to Install Python Libraries:**
**Requests:**
**i.** Check if you have the 'requests' module already installed in your system, by running this on your terminal:
**pip show requests**
If it is already installed in your system, it will display various details such as version, location, etc.
**ii.** If you don't see any response, then it means that 'requests' is not yet installed in your system. In order to download it, open your terminal and run this:
**pip install requests**
This will successfully install the 'requests' module in your system. You can follow the first step again to confirm whether the module has been successfully installed or not.
**Tqdm (Optional):**
**iii.** Check if you have the 'tqdm' module already installed in your system, by running this on your terminal:
**pip show tqdm**
If it is already installed in your system, it will display various details such as version, location, etc.
**iv.** If you don't see any response, then it means that 'requests' is not yet installed in your system. In order to download it, open your terminal and run this:
**pip install tqdm**
This will successfully install the 'requests'module in your system. You can follow the previous step again to confirm whether the module has been successfully installed or not.
[**Hint** : Although not a requirement, installing the Python library - 'tqdm', will provide an enhanced download experience by providing a well-structured 'Progress Bar' while downloading data, providing a clean and visually appealing download process.]
## **2. How to Download, Install & Run:**
**i. Download 'mdapi' from:**[**https://mosdac.gov.in/software/mdapi.zip**](https://mosdac.gov.in/software/mdapi.zip)
**ii. Unzip the folder in your desired directory. One will find the following files:**
**a. mdapi.py**
**b. config.json**
Following is the structure of **config.json:**
**{**
**"user_credentials": {**
**"username": "",**
**"password": ""**
**},**
**"search_parameters": {**
**"datasetId": "",**
**"startTime": "",**
**"endTime": "",**
**"count": "",**
**"boundingBox": "",**
**"gId": ""**
**},**
**"download_settings": {**
**"download_path": "",**
**"organize_by_date":false,**
**"skip_user_prompt":false,**
**"generate_error_log":false,**
**"error_log_path": ""**
**}**
**}**
##  [ Important Tip: Make sure you don't change the name of your Configuration File, i.e. - 'config.json'. Doing so will prevent successful execution of your 'mdapi.py' code, as the name of the Configuration file is already pre-configured inside it.]
**iii. Edit****config.json****correctly as per your data requirement, along with your user credentials. (** Refer section: '[**Parameter Reference of config.json**](https://mosdac.gov.in/downloadapi-manual#mdda-aprc)'**)**
**iv. In your terminal, run:**
**python mdapi.py**
**v. After fetching the search results, you will see the following message: (If****skip_user_prompt****is set****false****)**
**Do you want to start downloading? (Y/N):**
**vi. Type Y (or Yes) and hit Enter to start the download process.**
**vii. After the Download is complete, you will see a logout message, containing:**
**Download Complete!**
**Logout Successful. Goodbye****(your_username)****!**
[ **Background Download** : For background downloading set 'skip_user_input' as - true in your 'config.json' file. This will start data download without user interaction.]  
[ **Daily Download Limit** : We allow users to download a maximum of 5000 data files per day, per user. If your download exceeds that limit, you will see the message: 'You have reached your Daily Download Quota (5000 per day)' and will be automatically logged out. You will have to wait until the next day if you want to download more data.]
## **3. Data Download Workflow:**
Data download workflow includes the following steps to download data through MOSDAC:
**i.****Data Search** : Based on the input provided by the user in 'search_parameter' of 'client.json', our application will first fetch the total available files count and their total size. For this, one should know the required 'datasetId'. (Refer [section 4 ](https://mosdac.gov.in/downloadapi-manual#mdda-sd)for details)
**ii.****Authentication process** : Once the search results are retrieved, if the user provides the input to proceed for download, user authentication takes place. (Refer [section 5](https://mosdac.gov.in/downloadapi-manual#mdda-aar) for details)
**iii.****Data download** : After successful authentication, the data download begins as per user defined configuration.
**iv****.****Logout****:** After completion of the entire process, the user is logged out automatically.
## **4. Searching data:**
You don't need to log in to search; an account is only required to **download data**.
If your goal is just to **search or preview** available datasets using filters like datasetId, startTime, or boundingBox, etc., you can leave the 'user_credentials' blank. **No authentication** is needed in that case. However, DatasetId is required for search. Following section will guide you how to find your DatasetId:
##  **How to Find Your Dataset ID (****datasetId****)?**
In the config.json file, under the search_parameters section, there is a required field called datasetId. This field specifies **which dataset you want to download from** , and it is **mandatory** for the application to fetch any data.
### **Where to Find Available Dataset IDs**
You can explore the available dataset IDs here:
**Browse datasets** : [https://mosdac.gov.in/catalog/satellite.php](https://mosdac.gov.in/catalog/satellite.php)
On this page, you can:
  *     *       * Browse or filter datasets based on:


o**Satellite**
o**Sensor**
o**Search**
  *     *       * Find your desired **Product Name (Eg:****3SIMG_L1B_STD, E06OCM_L2C_AD****)** , which corresponds to the datasetId you should enter in your config file.


### **Example Workflow**
i. Visit the dataset browser: [https://mosdac.gov.in/catalog/satellite.php](https://mosdac.gov.in/catalog/satellite.php)
ii. Use filters to narrow down your options by satellite, sensor, etc.
iii. Identify the product you're interested in.
iv. Copy the **Product Name** exactly as shown - this is your datasetId.
#### **Example:**
If the product name is 3SIMG_L1B_STD, then your config should include:
"datasetId": "3SIMG_L1B_STD"
**Tip:** Make sure there are no typos or extra spaces in the datasetId. It must match the platform's listing **exactly**.
## **5. Authentication and Account Requirements**
To download any data using this application, you must first **authenticate** yourself using valid credentials.
### **Authentication Process**
The application uses your **MOSDAC Account credentials** (username and password) to authenticate your session before downloading begins. These credentials must be provided in the config.json file under the user_credentials section:
"user_credentials": {
"username": "your_username",
"password": "your_password"
}
**Important:** Without valid credentials, you will **not** be able to download any data.
#### **Don't Have an Account?**
If you donâ€™t already have an account, you must create one first:
**Create your account here** : [https://mosdac.gov.in/signup/](https://mosdac.gov.in/signup/)
Once your registration is complete and your account is **approved** , you will be eligible to use the application for downloading datasets.
* * *
#### **Forgot Your Password?**
You can reset your password here:
**Reset your password** : [https://mosdac.gov.in/auth/realms/Mosdac/login-actions/reset-credentials](https://mosdac.gov.in/auth/realms/Mosdac/login-actions/reset-credentials)  

* * *
#### **Failed Login Attempts**
  *     *       * If you enter incorrect credentials **three times consecutively** , your account will be **temporarily locked for 1 hour**.
      * Please double-check your username and password before running the script to avoid triggering this lockout.


* * *
## **Appendix: Parameter Reference of Config.json**
### **A. user_credentials:**
**Field**  
|  **Description** |  **Required**  
---|---|---  
username |  Your username for MOSDAC login (*) |  _**Yes**_  
password |  Your password for MOSDAC login (*) |  _**Yes**_  
**Correct****Example:**
"user_credentials": {
"username": "your_username",
"password": "your_password"
}
###  **Incorrect****Example** :
"user_credentials": {
"username": "",
"password": ""
}
_(Both fields must be filled in correctly for authentication to succeed.)_
_**B. search_parameters:**_
_**Field**_ | _**Description**_ | _**Required**_ | _**Notes**_  
---|---|---|---  
_datasetId_ | _The dataset that you want to download_ | _**Yes**_ | _Example: "**3SIMG_L1B_STD** "_  
_startTime_ | _he start date from which data should be downloaded._ | _**No**_ |  _Format: "YYYY-MM-DD"_ _Example: "2024-09-25"_  
_endTime_ | _The end date up to which data should be downloaded._ | _**No**_ |  _Format: "YYYY-MM-DD"_ _Example: "2024-10-25"_  
_count_ | _Maximum number of records you want to download._ | _**No**_ | _Max value: 100_  
_boundingBox_ | _Area-wise filter your selected â€˜datasetIdâ€™._ | _**No**_ |  _Format: "minLon,minLat,maxLon,maxLat"_ _Example: "70.0,8.0,90.0,28.0"_  
_gId_ | _Granule ID (specific ID if only one file is to be downloaded.)_ | _**No**_ | _Must be exact. Example: "15039367"_  
[ **Tip:** Although not required, we recommend setting the 'startTime' and 'endTime' according to your requirement, otherwise the search API will fetch results of the entire lifespan of the provided dataset.]
**Correct****Example:**
**"search_parameters": {**
**"datasetId": "3SIMG_L1B_STD",**
**"startTime": "2024-10-25",**
**"endTime": "2025-03-27",**
**"count": "50",**
**"boundingBox": "70.0,8.0,90.0,28.0",**
**"gId": ""**
**}**  

**Incorrect****Example** : 
**"search_parameters": {**
**"datasetId": "3SIMG_L1",****// Incorrect/Incomplete datasetId value**
**"startTime": "25-10-2024",****//Incorrect Date Format**
**"endTime": "2023-10-25â€™,****// endTime****>****startTime**
**"count": "500",****// Count****>****Max Count**
**"boundingBox": "70.0, 8.0",****// Incorrect boundingBox Format**
**"gId": "1437ZBL1"****// Incorrect gId value**
**}**
**C. download_settings (Optional)**
Customize how downloads and logging behave. Not mandatory to be set.
**Field** |  **Description** |  **Example**  
---|---|---  
download_path |  Directory path to store downloaded files |  **"/home/user/downloads"**  
organize_by_date |  Automatically organize downloaded data into subfolders (by year & date) |  **true****or****false**  
skip_user_prompt |  Whether to skip the "yes/no" prompt before download |  **true****(skip) or****false****(ask)**  
generate_error_log |  Enables detailed error logs |  **true****or****false**  
error_log_path |  Custom directory for log storage (optional) |  **"/home/user/logs"**  
[ Tip: Organize download data by Date Structure (if enabled through option 'organize_by_date']:
**[download_path]/**
**____ datasetId/**
**____YYYY/**
**___ DDMMM/**
**___ [downloaded files...]**]
###  **Correct****Example:**
**"download_settings": {**
**"download_path": "/home/user/data",**
**"organize_by_date": true,**
**"skip_user_prompt": false,**
**"generate_error_log": true,**
**"error_log_path": "/home/user/logs"**
**}**
###  **Incorrect****Example** :
**"download_settings": {**
**"download_path": "",**
**"organize_by_date": "yes",****// Should be boolean - true/false**
**"skip_user_prompt": yes,****// Should be boolean - true/false**
**"generate_error_log": â€œnoâ€,****// Should be boolean - true/false**
**"error_log_path": ""**
**}**
[Tip: If error_log_path is not set, logs will be created under following default path:
[ source folder]/error_logs/DD-MM-YY_error.log ]
**Need Help?**
If you encounter errors that persist even after following the steps defined in this user guide, you can reach out to our team on admin[at]mosdsac[dot]gov[dot]in. Please make sure you attach your Error log along with any further details you want to specify, enabling our team to understand and provide an appropriate solution for your encountered issues quickly.]
## Search
Search 
## Follow Us
  * [![Facebook icon](https://mosdac.gov.in/sites/all/modules/social_media_links/libraries/elegantthemes/PNG/facebook.png)](https://www.facebook.com/mosdac.sac.isro "Facebook")
  * [![Youtube \(Channel\) icon](https://mosdac.gov.in/sites/all/modules/social_media_links/libraries/elegantthemes/PNG/youtube.png)](http://www.youtube.com/channel/UCDVkai9WIgY2ZgrlF_08Yeg "Youtube \(Channel\)")
  * [![RSS icon](https://mosdac.gov.in/sites/all/modules/social_media_links/libraries/elegantthemes/PNG/rss.png)](https://mosdac.gov.in/rss.xml "RSS")


Website owned and maintained by MOSDAC, Space Applications Centre, Indian Space Research Organisation, Govt. of INDIA.
  * [![CQW LOGO](https://mosdac.gov.in/docs/cqw_logo.gif)](https://mosdac.gov.in/docs/STQC.pdf "Quality Certificate")


  * [Feedback](https://mosdac.gov.in/mosdac-feedback)
  * [About Us](https://mosdac.gov.in/about-us)
  * [Contact Us](https://mosdac.gov.in/contact-us)
  * [Copyright Policy](https://mosdac.gov.in/copyright-policy)
  * [Data Access Policy](https://mosdac.gov.in/data-access-policy)
  * [Hyperlink Policy](https://mosdac.gov.in/hyperlink-policy)
  * [Privacy Policy](https://mosdac.gov.in/privacy-policy)
  * [Website Policies](https://mosdac.gov.in/website-policies)
  * [Terms & Conditions](https://mosdac.gov.in/terms-conditions)
  * [FAQs](https://mosdac.gov.in/faq-page)


  * [![ISRO](https://mosdac.gov.in/sites/default/files/styles/thumbnail/public/logo-transparent.png?itok=IUS20l-w)](http://www.isro.gov.in)
  * [![Space Applications Center](https://mosdac.gov.in/sites/default/files/styles/thumbnail/public/saclogo.png?itok=_Jv4AuIn)](http://www.sac.gov.in)
  * [![NationalPortal](https://mosdac.gov.in/sites/default/files/styles/thumbnail/public/india-gov_0.png?itok=yssAPH3m)](http://www.india.gov.in)
  * [![MyGov](https://mosdac.gov.in/sites/default/files/styles/thumbnail/public/mygov_0.png?itok=Po-dzdT3)](http://mygov.in/)
  * [![DigitalIndia](https://mosdac.gov.in/sites/default/files/styles/thumbnail/public/digital-india_0.png?itok=ntlP7atE)](http://www.digitalindia.gov.in/)
  * [![DataPortal](https://mosdac.gov.in/sites/default/files/styles/thumbnail/public/data-gov.png?itok=qYA78FgB)](http://data.gov.in)


"Ver 3.0; Last reviewed and updated on 15 Sep, 2025& Served By: Web-Srv-Pri
[](https://mosdac.gov.in/downloadapi-manual "Previous")[](https://mosdac.gov.in/downloadapi-manual "Next")
[](https://mosdac.gov.in/downloadapi-manual)
[](https://mosdac.gov.in/downloadapi-manual "Previous")[](https://mosdac.gov.in/downloadapi-manual "Next")
[](https://mosdac.gov.in/downloadapi-manual "Close")[](https://mosdac.gov.in/downloadapi-manual)[](https://mosdac.gov.in/downloadapi-manual)[](https://mosdac.gov.in/downloadapi-manual "Pause Slideshow")[](https://mosdac.gov.in/downloadapi-manual "Play Slideshow")
[Back to top](https://mosdac.gov.in/downloadapi-manual#top)
