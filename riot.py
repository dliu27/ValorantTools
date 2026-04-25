import requests
import os
from requests.utils import quote
from requests.auth import HTTPBasicAuth
import base64

import dotenv
import webbrowser
import time

requests.packages.urllib3.disable_warnings()

# dotenv_file = dotenv.find_dotenv()
# dotenv.load_dotenv(dotenv_file)

# gets match id
# ENV_REGION = os.getenv('REGION')
# ENV_USER = os.getenv('USER')
# ENV_TAG = os.getenv('TAG')
# ENV_RIOT_API_KEY = os.getenv('RIOT_API_KEY')
# ENV_X_RIOT_ENTITLEMENTS_JWT = os.getenv('X_RIOT_ENTITLEMENTS_JWT')
# ENV_X_RIOT_CLIENTPLATFORM = os.getenv('X_RIOT_CLIENTPLATFORM')
# ENV_X_RIOT_CLIENTVERSION = os.getenv('X_RIOT_CLIENTVERSION')

# Local auth flow, MUST HAVE VALORANT RUNNING! Format: name:pid:port:password:protocol
lockfile = os.path.join(os.getenv("LOCALAPPDATA"),
                        R"Riot Games\Riot Client\Config\lockfile")

with open(lockfile) as f:
    lockfile = f.read().split(":")
    # print(lockfile)

    lockfile_name, lockfile_pid, lockfile_port, lockfile_pass, lockfile_protocol = lockfile

get_riot_token = requests.get(
    f'https://127.0.0.1:{lockfile_port}/entitlements/v1/token', auth=HTTPBasicAuth('riot', lockfile_pass), verify=False).json()
# print(get_riot_token)

token = get_riot_token['accessToken']
puuid = get_riot_token['subject']

get_entitlement = requests.post(
    f'https://entitlements.auth.riotgames.com/api/token/v1', headers={'Authorization': f'Bearer {token}',
                                                                      'Content-Type': 'application/json'}).json()
# print(get_entitlement)

entitlements = get_entitlement['entitlements_token']

# standard value that works
# https://valapidocs.techchrism.me/endpoint/name-service#client-platform
client_platform = 'ew0KCSJwbGF0Zm9ybVR5cGUiOiAiUEMiLA0KCSJwbGF0Zm9ybU9TIjogIldpbmRvd3MiLA0KCSJwbGF0Zm9ybU9TVmVyc2lvbiI6ICIxMC4wLjE5MDQyLjEuMjU2LjY0Yml0IiwNCgkicGxhdGZvcm1DaGlwc2V0IjogIlVua25vd24iDQp9'

get_sessions = get_entitlement = requests.get(
    f'https://127.0.0.1:{lockfile_port}/product-session/v1/external-sessions', auth=HTTPBasicAuth('riot', lockfile_pass), verify=False).json()

client_version = None
for session in get_sessions.values():
    if session.get("productId") == "valorant":
        client_version = session.get("version")
        break

get_player_region = requests.get(
    f'https://127.0.0.1:{lockfile_port}/riotclient/region-locale', auth=HTTPBasicAuth('riot', lockfile_pass), verify=False).json()

region = get_player_region['region']

# gets chat messages and returns
# now_time = time.time() * 1000

# get_all_chat_ids = requests.get(
#     f'https://127.0.0.1:{lockfile_port}/chat/v6/conversations/ares-pregame', auth=HTTPBasicAuth('riot', lockfile_pass), verify=False).json()

# cids = []
# # print(get_all_chat_ids)
# for i in range(len(get_all_chat_ids["conversations"])):
#     cids.append(
#         get_all_chat_ids["conversations"][i]['body'])


# get all player ids from match
get_pregame_match_id = requests.get(
    f'https://glz-{region}-1.{region}.a.pvp.net/pregame/v1/players/{puuid}', 
    headers={
        'X-Riot-ClientPlatform': client_platform,
        'X-Riot-ClientVersion': client_version,
        'X-Riot-Entitlements-JWT': entitlements,
        'Authorization': f'Bearer {token}'}).json()
# print(get_pregame_match_id)
pregame_match_id = get_pregame_match_id['MatchID']

get_pregame_match = requests.get(
    f'https://glz-{region}-1.{region}.a.pvp.net/pregame/v1/matches/{pregame_match_id}', 
    headers={
        'X-Riot-ClientPlatform': client_platform,
        'X-Riot-ClientVersion': client_version,
        'X-Riot-Entitlements-JWT': entitlements,
        'Authorization': f'Bearer {token}'}).json()



# print(get_pregame_match)
# print(get_pregame_match_loadouts)
team_puuids = []

for i in range(len(get_pregame_match["AllyTeam"]["Players"])):
    team_puuids.append(get_pregame_match["AllyTeam"]["Players"][i]['Subject'])

# print(team_puuids)

# not sure when this will be false, just in case
if puuid in team_puuids:
    team_puuids.remove(puuid)

# gets username#tag of all PUUIDs supplied in json param
# headers are not needed, uncomment if needed
get_username_from_puuids = requests.put('https://pd.NA.a.pvp.net/name-service/v2/players',
    json=team_puuids,
    headers={
        'X-Riot-ClientPlatform': client_platform,
        'X-Riot-ClientVersion': client_version,
        'X-Riot-Entitlements-JWT': entitlements,
        'Authorization': f'Bearer {token}'}).json()


# opens tracker.gg profile of the players
print('opening tracker.gg profiles in browser...')
for i in range(len(team_puuids)):
    name = get_username_from_puuids[i]['GameName']
    tag = '#' + get_username_from_puuids[i]['TagLine']
    print(name, tag)
    webbrowser.open("https://tracker.gg/valorant/profile/riot/" +
                    quote(name) + quote(tag) + '/overview')