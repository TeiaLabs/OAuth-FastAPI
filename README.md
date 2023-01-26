# OAuth-FastAPI

This repository contains a middleware compatible with FastAPI that provides OAuth functionalities.

## Example app

`uvicorn example_api.app:app --reload`

## URLs and params

### AD

```bash
https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/authorize?
client_id={value}
&response_type=token
&redirect_uri=https://teialabs.com.br/
&response_mode=fragment
&scope=email+openid+profile
```
