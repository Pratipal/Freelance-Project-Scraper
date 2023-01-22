import pandas as pd
import requests
from time import sleep
import datetime
import os
from kaggle.api.kaggle_api_extended import KaggleApi

def create_session():
    session = requests.session()
    session.headers.update({
    'authority': 'www.peopleperhour.com',
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9',
    'if-none-match': '61a1ac1bbd0a707d169a331d42481925d8c835c9',
    'referer': 'https://www.peopleperhour.com/freelance-jobs?page=2',
    'sec-ch-ua': '"Not_A Brand";v="99", "Brave";v="109", "Chromium";v="109"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'sec-gpc': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'x-device-user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'x-forwarded-for': '43.224.8.191',
    })
    
    return session

def get_projects(api):
    api.dataset_download_files("prtpljdj/freeelance-platform-projects", path = "./data", unzip=True)
    df = pd.read_csv("./data/Freelance Platform Projects.csv")
    return df, df["Title"].values[0], df['Date Posted'].values[0]


def main():

    experience_dict = { 
                    1 : 'Entry ($)',
                    2 : 'Intermediate ($$)',
                    3 : 'Expert ($$$)'
            }

    session = create_session()
    
    try:
        SOME_SECRET = os.environ["SOME_SECRET"]
    except KeyError:
        SOME_SECRET = "Token not available"

    params = {
        'app_id': '23h2j27d',
        'app_key': SOME_SECRET,
        'include': 'remoteCountry,watchlists,onsiteLocation',
        'page[number]': '1',
        'page[size]': '40',
        'withSeoMeta': '1',
    }

    response = session.get('https://www.peopleperhour.com/v2/projects/listAll', params=params)

    jdata = response.json()['data']

    data = []
    for jd in jdata:
        title             = jd['attributes']['title']
        category_name     = jd['attributes']['category']['cate_name']
        experience        = experience_dict[jd['attributes']['budget_bracket']]
        sub_category_name = jd['attributes']['sub_category']['subcate_name']
        project_currency  = jd['attributes']['currency']
        budget            = jd['attributes']['budget']
        project_location  = jd['attributes']['location_type']
        cnd_pref_from     = jd['attributes']['where_can_bid']
        project_type      = jd['attributes']['project_type']
        project_date      = jd['attributes']['posted_dt']
        project_desc      = jd['attributes']['proj_desc']
        project_duration  = jd['attributes']['duration']
        client_reg_date   = jd['attributes']['client']['reg_dt']
        client_city       = jd['attributes']['client']['city']
        client_country    = jd['attributes']['client']['country']
        client_currency   = jd['attributes']['client']['currency']
        client_job_title  = jd['attributes']['client']['job_title']
        data.append([title, category_name, experience, sub_category_name, project_currency, budget, project_location, cnd_pref_from,
                     project_type, project_date, project_desc, project_duration, client_reg_date,
                     client_city, client_country, client_currency, client_job_title])

    columns = [ 
                'Title', 'Category Name', 'Experience', 'Sub Category Name', 'Currency', 'Budget', 'Location', 'Freelancer Preferred From',
                'Type', 'Date Posted', 'Description', 'Duration', 'Client Registration Date',
                'Client City', 'Client Country', 'Client Currency', 'Client Job Title']

    df = pd.DataFrame(data, columns = columns)
    
    api = KaggleApi()
    api.authenticate()

    current_dataset, last_project_title, last_project_date = get_projects(api)

    try:
        idx = df[(df['Title']==last_project_title) & (df['Date Posted'] == last_project_date)].index[0]
        latest = df[:idx]
    except:
        latest = df.copy()

    new_version = pd.concat([latest, current_dataset.fillna('')])

    api.dataset_metadata("prtpljdj/freeelance-platform-projects", path = "./data")

    new_version.to_csv("./data/Freelance Platform Projects.csv", index=False)
    api.dataset_create_version(
        "./data/",
        version_notes=f"Updated on {datetime.datetime.now().strftime('%Y-%m-%d')}",
    )
if __name__ == '__main__':
    main()
