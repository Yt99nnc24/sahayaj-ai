from test_workflow import request, signup, login

def test_public_policy_pages_and_aliases(app):
    client=app.test_client()
    for path,title in [('/privacy',b'Privacy Policy'),('/cookies',b'Cookie Policy'),('/terms',b'Terms &amp; Conditions')]:
        response=client.get(path)
        assert response.status_code==200
        assert title in response.data
        assert b'16 October 2026' in response.data
        assert b'aria-current="page"' in response.data
        assert b'/privacy' in response.data and b'/cookies' in response.data and b'/terms' in response.data
    for alias,path in [('/privacy-policy','/privacy'),('/cookie-policy','/cookies'),('/terms-and-conditions','/terms')]:
        assert client.get(alias).headers['Location']==path

def test_policy_notices_match_local_features(app):
    c=app.test_client()
    privacy=c.get('/privacy').data
    assert b'hashed password' in privacy
    assert b'not encrypted at rest' in privacy
    assert b'page memory' in privacy
    assert b'browser or operating-system speech service' in privacy
    cookies=c.get('/cookies').data
    assert b'sahayaj_*' in cookies
    assert b'sahayaj-language' in cookies
    assert b'Reset display preferences' in cookies
    assert b'not cookies' in cookies

def test_policies_are_reachable_before_login_and_in_both_portals(app):
    c=app.test_client()
    for path in ['/','/patient/login','/doctor/login']:
        html=c.get(path).data
        for link in [b'href="/privacy"',b'href="/cookies"',b'href="/terms"']: assert link in html
    for role in ['patient','doctor']:
        c=app.test_client();signup(c,role+'-policy@example.test',role);login(c,role+'-policy@example.test')
        html=c.get('/'+role).data
        assert b'/static/chatbot.js' in html and b'/static/chatbot.css' in html
        assert b'href="/cookies"' in html
    assert c.get('/static/legal.js').status_code==200
