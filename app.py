# from typing import Dict
#
# import uvicorn
# from fastapi import FastAPI
# from starlette.middleware.sessions import SessionMiddleware
#
# from src import init_app
#
# app = FastAPI()
#
# init_app(app, {"authorizer": {"type": "Azure", "config": {}}, "generator_routes": ["/"], "verifier_routes": ["/"]})
#
#
# app.add_middleware(
#     SessionMiddleware,
#     secret_key="notsafe",
#     session_cookie="session",
#     max_age=60 * 60,
#     same_site="lax"
# )
#
#
# @app.get('/', response_model=Dict[str, str])
# def test():
#     return {'status': 'ok'}
#
#
# if __name__ == '__main__':
#     # PYTHON-JOSE
#     # https://github.com/awslabs/aws-support-tools/blob/master/Cognito/decode-verify-jwt/decode-verify-jwt.py
#
#     # AWS
#     # https://docs.aws.amazon.com/cognito/latest/developerguide/amazon-cognito-user-pools-authentication-flow.html
#     # https://stackoverflow.com/questions/37941780/what-is-the-rest-or-cli-api-for-logging-in-to-amazon-cognito-user-pools
#
#     # Azure
#     # https://docs.microsoft.com/pt-br/azure/active-directory/develop/v2-oauth-ropc
#
#     uvicorn.run(app)


if __name__ == '__main__':
    from jose import jws

    token = jws.sign({"test": "tested"}, "batata", algorithm="HS256", headers={"kid": "nOo3ZDrODXEK1jKWhXslHR_KXEg"})

    from src.authorizers import ADAuthorizer

    a = ADAuthorizer("", "common")
    a.validate_access_token(token)
