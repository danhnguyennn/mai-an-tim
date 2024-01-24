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
    def POST(self, url, data):
        for _ in range(5):
            try:
                return requests.post(url, data=data)
            except: pass
        return False
    def GPM_StartProfile(self, profile_id, x, dpi, toa_x):
        arg = f'{self.host_gpm}/v2/start?profile_id={profile_id}&addination_args=--window-size=700,600 --force-device-scale-factor={dpi} --window-position=%s,%s'%\
                (str((int(x) % int(toa_x))*600), str((int(x) // int(toa_x))*550))
        call_open = self.GET(arg).json()
        return call_open
    
    def GPM_CreateProfile(self, proxie='null', group='All'):
        name = str(random.randint(100000, 999999))
        arg = f'{self.host_gpm}/v2/create?name={name}&group={group}&proxy={proxie}'
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

    # API v3
    def GPM_ListGroupv3(self):
        list_gr = self.GET(f'{self.host_gpm}/api/v3/groups').json()
        return list_gr
    
    def GPM_ListProfilev3(self, id_gr=1):
        list_group = self.GET(f'{self.host_gpm}/api/v3/profiles?group_id={id_gr}&per_page=1000000&sort=1').json()
        return list_group
    
    def GPM_StartProfilev3(self, profile_id, x, dpi, toa_x):
        arg = f'{self.host_gpm}/api/v3/profiles/start/{profile_id}?win_size=700,600&win_scale={dpi}&win_pos=%s,%s'%\
                (str((int(x) % int(toa_x))*600), str((int(x) // int(toa_x))*550))
        call_open = self.GET(arg).json()
        return call_open
    
    def GPM_CreateProfilev3(self, proxie='', group='All'):
        name = str(random.randint(100000, 999999))
        arg = f'{self.host_gpm}/api/v3/profiles/create'
        json_data = {
            "profile_name" : name,
            "group_name" : group,
            "raw_proxy" : proxie
        }
        data = json.dumps(json_data)
        try:
            return self.POST(arg, data).json()['data']
        except: return False

    def GPM_UpdateProfilev3(self, profile_id, proxie):
        json_data = {
            "raw_proxy" : proxie,
        }
        data = json.dumps(json_data)
        update = self.POST(f'{self.host_gpm}/api/v3/profiles/update/{profile_id}', data).json()
        return update
    
    def GPM_CloseProfilev3(self, profile_id):
        self.GET(f'{self.host_gpm}/api/v3/profiles/close/{profile_id}')

    def GPM_DeleteProfilev3(self, profile_id):
        self.GET(f"{self.host_gpm}/api/v3/profiles/delete/{profile_id}")


# gpm = API_GPM('http://127.0.0.1:19995')
# a = gpm.GPM_DeleteProfile('999dcfc6-d8ed-43b5-8b97-c4d3bc8033a4')
# print(a)

