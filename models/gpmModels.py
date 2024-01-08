import json
import requests
import random
import pandas as pd

class API_GPM:
    def __init__(self, API_URL) -> None:
        self.host_gpm = API_URL
    def GET(self, url):
        for _ in range(5):
            try:
                return requests.get(url)
            except: pass
        return False
    def GPM_StartProfile(self, profile_id, x, dpi, toa_x):
        arg = f'{self.host_gpm}/v2/start?profile_id={profile_id}&addination_args=--window-size=700,600 --force-device-scale-factor={dpi} --window-position=%s,%s'%\
                (str((int(x) % int(toa_x))*550), str((int(x) // int(toa_x))*550))
        call_open = self.GET(arg).json()
        return call_open
    
    def GPM_CreateProfile(self, proxie='null', group='All'):
        name = str(random.randint(100000, 999999))
        arg = f'{self.host_gpm}/v2/create?name={name}&group={group}&proxy={proxie}&'
        try:
            return self.GET(arg).json()['profile_id']
        except: return False

    def GPM_CloseProfile(self, profile_id):
        return self.GET(f'{self.host_gpm}/v2/stop?profile_id={profile_id}')

    def GPM_GetProfileList(self):
        call_list_profile = self.GET(f'{self.host_gpm}/v2/profiles?per_page=1000000').json()
        return call_list_profile
    
    def GPM_UpdateProfile(self, profile_id, proxy):
        call_update = self.GET(f'{self.host_gpm}/v2/update?id={profile_id}&proxy={proxy}').text
     
    def GPM_DeleteProfile(self, profile_id):
        call_dele = self.GET(f"{self.host_gpm}/v2/delete?profile_id={profile_id}")

    def scanProfile(self, name_profile='', list_profile=[]):
        df = pd.DataFrame(list_profile)
        filtered_data = df[lambda x: x["name"] == name_profile]
        print(filtered_data)
        return {
            'id': filtered_data['id'].iloc[0]
        }

# API_GPM('http://127.0.0.1:19995').GPM_CloseProfile('ee619b28-cfce-4e8d-a28c-a24d27ea2368')

