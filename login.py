from bilibili import bilibili
import base64
import requests

class login():

    def normal_login(self, username, password):
        # url = 'https://passport.bilibili.com/api/oauth2/login'   //旧接口
        url = "https://passport.bilibili.com/api/v2/oauth2/login"
        temp_params = 'appkey=' + bilibili().dic_bilibili['appkey'] + '&password=' + password + '&username=' + username
        sign = bilibili().calc_sign(temp_params)
        headers = {"Content-type": "application/x-www-form-urlencoded"}
        payload = "appkey=" + bilibili().dic_bilibili[
            'appkey'] + "&password=" + password + "&username=" + username + "&sign=" + sign
        response = requests.post(url, data=payload, headers=headers)
        return response

    def login_with_captcha(self, username, password):
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36',
            'Host': 'passport.bilibili.com',
            'cookie': "sid=hxt5szbb"
        }
        s = requests.session()
        url = "https://passport.bilibili.com/captcha"
        res = s.get(url, headers=headers)
        tmp1 = base64.b64encode(res.content)
        captcha = bilibili().cnn_captcha(tmp1)
        temp_params = 'actionKey=' + bilibili().dic_bilibili[
            'actionKey'] + '&appkey=' + bilibili().dic_bilibili['appkey'] + '&build=' + bilibili().dic_bilibili[
                          'build'] + '&captcha=' + captcha + '&device=' + bilibili().dic_bilibili['device'] + '&mobi_app=' + \
                      bilibili().dic_bilibili['mobi_app'] + '&password=' + password + '&platform=' + bilibili().dic_bilibili[
                          'platform'] + '&username=' + username
        sign = bilibili().calc_sign(temp_params)
        payload = temp_params + '&sign=' + sign
        headers['Content-type'] = "application/x-www-form-urlencoded"
        headers['cookie'] = "sid=hxt5szbb"
        url = "https://passport.bilibili.com/api/v2/oauth2/login"
        response = s.post(url, data=payload, headers=headers)
        return response

    async def login(self):
        username = str(bilibili().dic_bilibili['account']['username'])
        password = str(bilibili().dic_bilibili['account']['password'])
        if username != "":
            response = bilibili().request_getkey()
            value = response.json()['data']
            key = value['key']
            Hash = str(value['hash'])
            username, password = bilibili().calc_name_passw(key, Hash, username, password)
            response = self.normal_login(username, password)
            while response.json()['code'] == -105:
                response = self.login_with_captcha(username, password)
            try:
                access_key = response.json()['data']['token_info']['access_token']
                cookie = (response.json()['data']['cookie_info']['cookies'])
                cookie_format = ""
                for i in range(0, len(cookie)):
                    cookie_format = cookie_format + cookie[i]['name'] + "=" + cookie[i]['value'] + ";"
                bilibili().dic_bilibili['csrf'] = cookie[0]['value']
                bilibili().dic_bilibili['access_key'] = access_key
                bilibili().dic_bilibili['cookie'] = cookie_format
                bilibili().dic_bilibili['uid'] = cookie[1]['value']
                bilibili().dic_bilibili['pcheaders']['cookie'] = cookie_format
                bilibili().dic_bilibili['appheaders']['cookie'] = cookie_format
                response = await bilibili().check_activity_exist()
                json_res = await response.json()
                if json_res['code'] == 0:
                    activity_name = (list((json_res['data']['eventList'][0]['lottery']['config']).keys()))[0]
                    bilibili().dic_bilibili['activity_name'] = activity_name
                else:
                    print("# 自动查询没有查询到新活动")
                print("# 登录成功")
            except:
                print("# 登录失败,错误信息为:",response.json()['message'])
