from onest_captcha import OneStCaptchaClient

def bypassCaptcha(APIKEY):
    for i in range(5):
        client = OneStCaptchaClient(apikey=APIKEY)
        result = client.recaptcha_v2_task_proxyless(site_url="https://traodoisub.com/view/chtiktok/", site_key="6LeGw7IZAAAAAECJDwOUXcriH8HNN7_rkJRZYF8a", invisible=False)
        return result["token"]
    return False