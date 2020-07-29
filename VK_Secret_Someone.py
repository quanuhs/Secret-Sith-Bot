import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import time
import os
import psycopg2
import random
import sqlite3 as sql
import threading

# START
import json


def get_button(label, color, payload):
    return {
        "action": {
            "type": "text",
            "payload": json.dumps(payload),
            "label": label
        },
        "color": color
    }


def list_keyboard(array, page_forward, index, req):
    buttons_array = []
    mass = []

    if len(array) > 10:
        offset = 8
    else:
        offset = 10

    for i in range(page_forward, len(array)):
        buttons_array.append(get_button(str(array[i][index]), "secondary", str(req) + " " + str(i + 1)))

        if (i) % 2 == 1 and len(buttons_array) > 0:
            mass.append(buttons_array)
            buttons_array = []

        if i == page_forward + offset:
            break

    b_reg = []
    if page_forward > 0:
        b_reg.append(get_button("<--", "negative", str(req) + "-goto_" + str(page_forward - offset)))

    if len(array) > (page_forward + offset):
        b_reg.append(get_button("-->", "positive", str(req) + "-goto_" + str(page_forward + offset)))
    else:
        if len(array) % 2 == 1:
            mass.append([get_button(str(array[len(array) - 1][index]), "secondary", str(req) + " " + str(len(array)))])

    if len(b_reg) != 0:
        mass.append(b_reg)

    keyboard = {
        "inline": True,
        "buttons": mass
    }

    keyboard = json.dumps(keyboard, ensure_ascii=False).encode('utf-8')
    keyboard = str(keyboard.decode('utf-8'))
    return keyboard


def three_keyboard(text1, color1, payload1, text2, color2, payload2, text3, color3, payload3):
    keyboard = {
        "one_time": False,
        "buttons": [
            [get_button(text1, color1, payload1)],
            [get_button(text2, color2, payload2)],
            [get_button(text3, color3, payload3)]
        ]

    }

    keyboard = json.dumps(keyboard, ensure_ascii=False).encode('utf-8')
    keyboard = str(keyboard.decode('utf-8'))
    return keyboard


def create_keyboard(buttons):
    keyboard = {
        "one_time": False,
        "buttons": buttons

    }

    keyboard = json.dumps(keyboard, ensure_ascii=False).encode('utf-8')
    keyboard = str(keyboard.decode('utf-8'))
    return keyboard


def create_inlinekeyboard(buttons):
    keyboard = {
        "inline": True,
        "buttons": buttons

    }

    keyboard = json.dumps(keyboard, ensure_ascii=False).encode('utf-8')
    keyboard = str(keyboard.decode('utf-8'))
    return keyboard


def one_keyboard(text1, color1, payload1):
    keyboard = {
        "one_time": False,
        "buttons": [
            [get_button(text1, color1, payload1)]
        ]

    }

    keyboard = json.dumps(keyboard, ensure_ascii=False).encode('utf-8')
    keyboard = str(keyboard.decode('utf-8'))
    return keyboard


def two_keyboard(text1, color1, payload1, text2, color2, payload2):
    keyboard = {
        "one_time": False,
        "buttons": [
            [get_button(text1, color1, payload1)],
            [get_button(text2, color2, payload2)]
        ]

    }

    keyboard = json.dumps(keyboard, ensure_ascii=False).encode('utf-8')
    keyboard = str(keyboard.decode('utf-8'))
    return keyboard


def inline_one(text1, color1, payload1):
    keyboard = {
        "inline": True,
        "buttons": [
            [get_button(text1, color1, payload1)]
        ]
    }

    keyboard = json.dumps(keyboard, ensure_ascii=False).encode('utf-8')
    keyboard = str(keyboard.decode('utf-8'))
    return keyboard


def inline_two(text1, color1, payload1, text2, color2, payload2):
    keyboard = {
        "inline": True,
        "buttons": [
            [get_button(text1, color1, payload1)],
            [get_button(text2, color2, payload2)]
        ]
    }

    keyboard = json.dumps(keyboard, ensure_ascii=False).encode('utf-8')
    keyboard = str(keyboard.decode('utf-8'))
    return keyboard


def inline_three(text1, color1, payload1, text2, color2, payload2, text3, color3, payload3):
    keyboard = {
        "inline": True,
        "buttons": [
            [get_button(text1, color1, payload1)],
            [get_button(text2, color2, payload2)],
            [get_button(text3, color3, payload3)]
        ]
    }

    keyboard = json.dumps(keyboard, ensure_ascii=False).encode('utf-8')
    keyboard = str(keyboard.decode('utf-8'))
    return keyboard


# DELETE

# Ключи авторизации.
token = os.environ.get('key')
group_id = os.environ.get('group_id')
DATABASE_URL = os.environ.get('DATABASE_URL')

vk = vk_api.VkApi(token=token)
vk._auth_token()
vk.get_api()
longpoll = VkBotLongPoll(vk, group_id)

all_roles = ["lib", "imper"]
cards = [1, 0]

liberal = 5
lib_choice = 3
imperial = 6

lib_cards = 6
imp_cards = 11

# Для 5-6: [x, x, посмотреть 3 верхнии карты, убить игрок, убить игрока + право веты, gg] 1 имперец, 1 ситх. (знают)
# 7-8: [x, проверить карту, выбрать следующего, убить игрок, убить игрока + право веты, gg] 2 имперца 1 ситх (не знают)
# 9-10: [проверкить, проверить карту, выбрать следующего, убить игрок, убить игрока + право веты, gg] 3 имперца 1 ситх


# lobby_id, можно ли зайти, пароль, количество участников, список участников, текущий президент, текущий канслер,
# бывший президент, бывший канслер, колода, сброс, на доске империи, на доске либиралов, раскрытие закона, стадия, ход

try:
    connection = psycopg2.connect(DATABASE_URL, sslmode='require')
    #connection = sql.connect("some.sqlite", check_same_thread=False)
    q = connection.cursor()
    q.execute('''CREATE TABLE user_info
               (
               User_ID INTEGER,
               Lobby_ID INTEGER,
               Role TEXT,
               Cards TEXT,
               Status TEXT,
               Game_Status TEXT,
               Language TEXT,
               Nickname TEXT
               )
               ''')
    q.close()
    connection.commit()
    connection.close()

except Exception:
    print("user_data already created")

try:
    #connection = sql.connect("some.sqlite", check_same_thread=False)
    connection = psycopg2.connect(DATABASE_URL, sslmode='require')
    q = connection.cursor()
    q.execute('''CREATE TABLE lobby_info
               (
               Lobby_ID INTEGER,
               Can_Enter INTEGER,
               Lobby_Password TEXT,
               Players_Amount INTEGER,
               Players_List TEXT,
               Current_President INTEGER,
               Current_Chancellor INTEGER,
               Ex_President INTEGER,
               Ex_Chancellor INTEGER,
               Deck TEXT,
               Discard TEXT,
               In_Place_Imp INTEGER,
               In_Place_Lib INTEGER,
               Lib_State INTEGER,
               In_Game_Cards TEXT,
               Status TEXT,
               Turn INTEGER,
               Lobby_Host INTEGER
               )
               ''')
    q.close()
    connection.commit()
    connection.close()

except Exception:
    print("lobby_data already created")


def update_lobby(lobby_id, param, value):
    q.execute(
        "UPDATE lobby_info SET %s = '%s' WHERE Lobby_ID = '%s'" % (param, value, lobby_id))
    connection.commit()


def make_list_string(arr):
    # Will make list [1,2,3,4..] -> 1_2_3_4..

    output = ""
    if arr != "" or arr is not None:
        for i in range(len(arr)):
            output += "_" + str(arr[i])

        return output[1:]
    else:
        return ""


def set_lobby_deck():
    random.seed()
    deck = [cards[0]] * lib_cards + [cards[1]] * imp_cards
    random.shuffle(deck)
    return make_list_string(deck)


class Lobby:
    def __init__(self, lobby_data):
        lobby_data = lobby_data[0]
        self.id = lobby_data[0]
        self.can_enter = lobby_data[1]
        self.password = lobby_data[2]
        self.votes = lobby_data[3]
        self.players = lobby_data[4].split("_")
        if len(self.players) == 1:
            if self.players[0] == '':
                self.players = []
        self.current_president = lobby_data[5]
        self.current_chancellor = lobby_data[6]
        self.ex_president = lobby_data[7]
        self.ex_chancellor = lobby_data[8]
        self.deck = lobby_data[9].split("_")
        if len(self.deck) == 1:
            if self.deck[0] == '':
                self.deck = []

        self.discard = lobby_data[10].split("_")
        if len(self.discard) == 1:
            if self.discard[0] == '':
                self.discard = []

        self.imperial_table = lobby_data[11]
        self.republican_table = lobby_data[12]
        self.republican_state = lobby_data[13]

        self.cards_in_use = lobby_data[14].split("_")
        if len(self.cards_in_use) == 1:
            if self.cards_in_use[0] == '':
                self.cards_in_use = []

        self.status = lobby_data[15]
        self.turn = lobby_data[16]
        self.host = lobby_data[17]

    def add_republican_state(self, value):
        if value == 0:
            self.republican_state = 0
        else:
            self.republican_state += 1

            if self.republican_state == lib_choice:
                self.republican_state = 0
                card = take_actions(self, 1)
                self.discard = self.discard + [card[0]]
                self.update_discard(self.discard)
                add_to_table(self, card[0])

        q.execute(
            "UPDATE lobby_info SET Lib_State = '%s', Ex_President = '%s', Ex_Chancellor = '%s' WHERE Lobby_ID = '%s'" % (
                self.republican_state, -1, -1, self.id))
        connection.commit()

    def change_rulers(self):
        self.ex_president = self.current_president
        self.ex_chancellor = self.current_chancellor
        self.current_president = -1
        self.current_chancellor = -1

        q.execute(
            "UPDATE lobby_info SET Current_President = '%s', Current_Chancellor = '%s', Ex_President = '%s', Ex_Chancellor = '%s' WHERE Lobby_ID = '%s'" % (
                self.current_president, self.current_chancellor, self.ex_president, self.ex_chancellor, self.id))

        connection.commit()

    def next_turn(self):
        if self.turn < len(self.players) - 1:
            self.turn += 1
        else:
            self.turn = 0

        q.execute("UPDATE lobby_info SET Turn = '%s' WHERE Lobby_ID = '%s'" % (self.turn, self.id))
        connection.commit()

    def update_deck(self, deck):
        self.deck = deck
        deck = make_list_string(deck)
        q.execute("UPDATE lobby_info SET Deck = '%s' WHERE Lobby_ID = '%s'" % (deck, self.id))
        connection.commit()

    def update_discard(self, discard):
        self.discard = discard
        discard = make_list_string(discard)
        q.execute("UPDATE lobby_info SET Discard = '%s' WHERE Lobby_ID = '%s'" % (discard, self.id))
        connection.commit()

    def update_cards_in_use(self, cards_in_use):
        self.cards_in_use = cards_in_use
        cards_in_use = make_list_string(cards_in_use)
        q.execute("UPDATE lobby_info SET In_Game_Cards = '%s' WHERE Lobby_ID = '%s'" % (cards_in_use, self.id))
        connection.commit()

    def update_players(self, players_list):
        self.players = players_list
        if len(players_list) == 0:
            q.execute("DELETE FROM lobby_info WHERE Lobby_ID = '%s'" % self.id)
        else:
            players_list = make_list_string(players_list)
            q.execute("UPDATE lobby_info SET Players_List = '%s' WHERE Lobby_ID = '%s'" % (players_list, self.id))

        connection.commit()

    def update_votes(self, votes):
        self.votes = votes
        q.execute("UPDATE lobby_info SET Players_Amount = '%s' WHERE Lobby_ID = '%s'" % (votes, self.id))
        connection.commit()

    def update_rulers(self):
        q.execute("UPDATE lobby_info SET Current_President = '%s', Current_Chancellor = '%s' WHERE Lobby_ID = '%s'" % (
            self.current_president, self.current_chancellor, self.id))
        connection.commit()

    def update_status(self, status):
        self.status = status
        q.execute("UPDATE lobby_info SET Status = '%s' WHERE Lobby_ID = '%s'" % (status, self.id))
        connection.commit()


def get_line(language, line):
    conn = sql.connect("language.db", check_same_thread=False)
    info = conn.cursor()
    info.execute("SELECT * FROM language WHERE KEY_TEXT = '%s' AND %s != ''" % (line, language))
    res = info.fetchall()

    if len(res) > 0:
        ret = random.randint(0, len(res) - 1)
        if language == "RU":
            return res[ret][1]
        elif language == "ENG":
            return res[ret][2]

    else:
        if language == "RU":
            return line + " | RU"
        elif language == "ENG":
            return line + " | ENG"


class Player:
    def __init__(self, user_data):
        if len(user_data) != 0:
            user_data = user_data[0]
            self.user_id = user_data[0]
            self.lobby_id = user_data[1]
            self.role = user_data[2]
            self.cards_in_hand = user_data[3]
            self.status = user_data[4]
            self.game_status = user_data[5]
            self.lang = user_data[6]
            self.nickname = user_data[7]

    def update_game_status(self, game_status):
        self.game_status = game_status
        q.execute("UPDATE user_info SET Game_Status = '%s' WHERE User_ID = '%s'" % (self.game_status, self.user_id))
        connection.commit()

    def game_update(self):
        q.execute(
            "UPDATE user_info SET Role = '%s', Cards = '%s', Status = '%s', Game_Status = '%s', Nickname = '%s' WHERE User_ID = '%s'" %
            (self.role, self.cards_in_hand, self.status, self.game_status, self.nickname, self.user_id))
        connection.commit()

    def update_status(self, status):
        self.status = status
        q.execute("UPDATE user_info SET Status = '%s' WHERE User_ID = '%s'" % (self.status, self.user_id))
        connection.commit()

    def language(self, line):
        return get_line(self.lang, line)


def msg_k(user_id, keyboard, text):
    vk.method("messages.send",
              {"user_id": user_id,
               "message": text,
               "keyboard": keyboard,
               "random_id": 0})


def msg(user_id, text):
    vk.method("messages.send",
              {"user_id": user_id,
               "message": text,
               "random_id": 0})


def connect_to_lobby(player, lobby_id, password):
    lobby_info = get_lobby(lobby_id)
    if len(lobby_info) == 0:
        msg(player.user_id, player.language("connect_error_no_lobby_found"))
        return False

    else:
        lobby = Lobby(lobby_info)
        if lobby.password == "" or lobby.password == password:
            if lobby.can_enter:
                players_list = lobby.players

                players_list.append(user_id)
                players_list = make_list_string(players_list)

                q.execute(
                    "UPDATE lobby_info SET Players_List = '%s' WHERE Lobby_ID = '%s'"
                    % (players_list, lobby_id))

                q.execute("UPDATE user_info SET Lobby_ID = '%s' WHERE User_ID = '%s'" % (lobby_id, user_id))
                player.lobby_id = lobby_id
                connection.commit()

                players_in = lobby.players
                player.update_status("in_lobby")

                for i in range(len(players_in)):
                    user = Player(get_player(players_in[i]))
                    if user.user_id != player.user_id:
                        msg(user.user_id,
                            "@id%s %s %s" % (player.user_id, user.language("someone_connected"), str(len(players_in))))
                    else:
                        msg_k(user.user_id, lobby_keyboard(user), user.language("in_lobby") + str(lobby_id))

                return True

        else:
            if password == "":
                return "password"

            msg(player.user_id, player.language("connect_error_wrong_password"))


def create_lobby(player, password):
    q = connection.cursor()

    while True:
        lobby_id = random.randint(0, 99999999)
        q.execute("SELECT * FROM lobby_info WHERE Lobby_ID = '%s'" % (lobby_id))
        lobby_info = q.fetchall()
        if len(lobby_info) == 0:
            break

    q.execute(
        "INSERT INTO lobby_info"
        "(Lobby_ID, Can_Enter, Lobby_Password, Players_Amount, Players_List, Current_President, "
        "Current_Chancellor, Ex_President, Ex_Chancellor,"
        "Deck, Discard, In_Place_Imp, In_Place_Lib, Lib_State, In_Game_Cards, Status, Turn, Lobby_Host) "

        "VALUES ('%s', '%s','%s', '%s', '%s', '%s', '%s', '%s', '%s','%s','%s','%s','%s','%s','%s','%s','%s', '%s')" %
        (lobby_id, 1, password, 0, "", -1, -1, -1, -1, set_lobby_deck(), "", 0, 0, 0, "", "waiting_for_players", -1,
         player.user_id))
    connection.commit()

    connect_to_lobby(player, lobby_id, password)


def leave(player):
    lobby = Lobby(get_lobby(player.lobby_id))
    players_list = lobby.players
    index = 0
    # Go trow all users, check and notify. Delete the user at last.
    for i in range(len(lobby.players)):
        if int(players_list[i]) == player.user_id:
            index = i
        else:
            user = Player(get_player(int(players_list[i])))
            msg(user.user_id, "@id" + str(player.user_id) + user.language("someone_left") +
                user.language("someone_left_amount") + str(len(lobby.players) - 1))

    players_list.pop(index)
    lobby.update_players(players_list)


def get_player(user_id):
    q.execute("SELECT * FROM user_info WHERE User_ID = '%s'" % (user_id))
    return q.fetchall()


def lobby_keyboard(player):
    lobby = Lobby(get_lobby(player.lobby_id))

    if lobby.host == player.user_id:
        buttons = [
            [get_button(player.language("start"), "positive", "!start"),
             get_button(player.language("list_players"), "primary", "!players")],
            [get_button(player.language("cancel"), "negative", "!leave")],
            [get_button(player.language("rules"), "primary", "!rules"),
             get_button(player.lang, "secondary", "!language")]
        ]
    else:
        buttons = [
            [get_button(player.language("list_players"), "primary", "!players")],
            [get_button(player.language("cancel"), "negative", "!leave")],
            [get_button(player.language("rules"), "primary", "!rules"),
             get_button(player.lang, "secondary", "!language")]
        ]

    return create_keyboard(buttons)


def game_keyboard(player):
    buttons = [
        [get_button(player.language("table"), "primary", "!table")],
        [get_button(player.language("list_players"), "primary", "!players")],
        [get_button(player.language("rules"), "primary", "!rules"),
         get_button(player.language("cancel"), "negative", "!leave"), get_button(player.lang, "secondary", "!language")]
    ]

    return create_keyboard(buttons)


def vote_for_president(lobby, who_president, who_chancellor):
    players = lobby.players

    lobby.current_president = who_president.user_id
    lobby.current_chancellor = who_chancellor.user_id

    lobby.update_rulers()

    for user in players:
        player = Player(get_player(int(user)))

        text = "@id%s (%s) " % (who_president.user_id, who_president.nickname) + player.language(
            "runs_for_president") + "\n " \
                                    "@id%s (%s) " % (who_chancellor.user_id, who_chancellor.nickname) + player.language(
            "runs_for_chancellor")
        player.update_game_status("vote")
        msg_k(player.user_id,
              inline_two(player.language("yes"), "positive", "!yes", player.language("no"), "negative", "!no"), text)


def actions_keyboard(user_id, cards_list):
    player = Player(get_player(user_id))
    lobby = Lobby(get_lobby(player.lobby_id))

    buttons = []

    same_amount = 0
    for i in range(len(cards_list)):
        if int(cards_list[i]):
            color = "primary"
            name = player.language("rep")
            same_amount -= 1
        else:
            color = "negative"
            name = player.language("imp")
            same_amount += 1

        buttons.append([get_button(name, color, "!choose " + str(i + 1))])

        if lobby.imperial_table == 5 and user_id == lobby.current_chancellor and abs(same_amount) == 2:
            lobby.update_status("can_veto")
            buttons.append([get_button(player.language("veto"), "positive", "!veto")])

    return create_inlinekeyboard(buttons)


def vote_for_rulers(lobby, who, choice):
    q.execute("SELECT * FROM user_info WHERE Lobby_ID = '%s' and Game_Status = '%s'" % (lobby.id, "vote"))
    result = q.fetchall()

    if choice:
        lobby.update_votes(lobby.votes + 1)
    else:
        lobby.update_votes(lobby.votes - 1)

    players = lobby.players
    who.update_game_status("")

    for user in players:
        player = Player(get_player(user))
        if choice:
            msg(player.user_id,
                "@id%s (%s) " % (str(who.user_id), who.nickname) + player.language("voted_for"))
        else:
            msg(player.user_id,
                "@id%s (%s) " % (str(who.user_id), who.nickname) + player.language("voted_against"))

    if len(result) == 1 or len(result) == 0:
        if lobby.votes >= 0:
            lobby.add_republican_state(0)
            lobby.update_status("take_actions")
            lobby.update_votes(0)

            if lobby.imperial_table >= 4:
                chancellor = Player(get_player(lobby.current_chancellor))
                if chancellor.role == "sith":
                    finish_game(lobby, "imperial")
                    return
                else:
                    msg_all(0, lobby, "not_sith", "@id%s (%s)" % (chancellor.user_id, chancellor.nickname))

            president = Player(get_player(lobby.current_president))
            cards_arr = take_actions(lobby, 3)
            lobby.update_cards_in_use(cards_arr)
            msg_k(president.user_id, actions_keyboard(president.user_id, cards_arr),
                  president.language("take_actions_p") + "\n\n" + visual_acts(president, cards_arr))
            president.update_game_status("take_actions")
            msg_all(president.user_id, lobby, "president_choice", "")

        else:
            lobby.add_republican_state(1)
            lobby.update_votes(0)
            lobby.current_president = -1
            lobby.current_chancellor = -1
            lobby.update_rulers()
            msg_all(0, lobby, "election_failed", "")
            game_turn(lobby)


def take_actions(lobby, amount):
    cards_arr = []
    deck = lobby.deck

    if len(deck) < amount:
        cards = lobby.discard
        random.shuffle(cards)
        if len(deck) > 0:
            cards = deck + cards

        lobby.update_deck(cards)
        lobby.update_discard([])
        deck = lobby.deck

    for i in range(amount):
        cards_arr.append(int(deck[0]))
        deck.pop(0)

    lobby.update_deck(deck)
    return cards_arr


def setup_game(lobby):
    lobby = Lobby(get_lobby(lobby.id))
    players = lobby.players
    random.shuffle(players)
    roles = [all_roles[0]] * len(players)
    # Stupid method to set roles
    if 5 <= len(players) <= 6:
        roles[0] = all_roles[1]
        roles[3] = "sith"

    elif 7 <= len(players) <= 8:
        roles[0] = all_roles[1]
        roles[1] = all_roles[1]
        roles[3] = "sith"
    else:
        roles[0] = all_roles[1]
        roles[1] = all_roles[1]
        roles[2] = all_roles[1]
        roles[3] = "sith"

    random.shuffle(roles)

    male_names = ["Steven", "Cody", "Gabriel", "Juniper", "Jack", "Augustus", "Michael", "Stephan", "Benjamin", "Claus",
                  "Garry", "Christopher", "George", "Roland", "Oliver", "Robert", "Thomas", "Brian", "Jakob", "Mark"]

    female_names = ["Jessica", "Betty", "Rosa", "Katherine", "Anastasia", "Sandra", "Emma", "Isabella", "Maria",
                    "Angel",
                    "Clara", "Barbara", "Samantha", "Anne", "Tiffany", "Agnes", "Linda", "Pearl", "Helen", "Grace"]

    random.shuffle(male_names)
    random.shuffle(female_names)

    sent_to = []
    imp_names = ""
    sith_name = ""

    for user in players:
        player = Player(get_player(user))
        player.status = "in_game"
        player.role = roles[0]

        gen = vk.method("users.get", {"user_ids": player.user_id, "fields": "sex"})
        sex = gen[0].get('sex')

        if sex != 1 or sex != 2:
            sex = random.randint(1, 2)

        if sex == 1:
            player.nickname = female_names[0]
            female_names.pop(0)
        elif sex == 2:
            player.nickname = male_names[0]
            male_names.pop(0)


        if roles[0] == "imp" or roles[0] == "sith":
            sent_to.append([player.user_id, roles[0]])
            if roles[0] == "imp":
                imp_names += "@id%s (%s) \n" % (player.user_id, player.nickname)
            elif roles[0] == "sith":
                sith_name = "@id%s (%s) " % (player.user_id, player.nickname)

        player.game_update()
        roles.pop(0)

        text = player.language("game_start") + "\n" + player.language("role") + player.language(player.role)
        msg_k(player.user_id, game_keyboard(player), text)

    for i in range(len(sent_to)):
        if len(sent_to) > 2:
            if sent_to[i][1] != "sith":
                msg(sent_to[i][0], imp_names + "\n>> " + sith_name)
        else:
            msg(sent_to[i][0], imp_names + "\n>> " + sith_name)

    lobby.update_status("choose_president")
    lobby.update_players(players)
    game_turn(lobby)


def game_turn(lobby):
    lobby = Lobby(get_lobby(lobby.id))
    q.execute("SELECT * FROM lobby_info WHERE Lobby_ID = '%s'" % lobby.id)
    res = q.fetchall()
    if len(res) == 0:
        return

    turn = lobby.turn
    players = lobby.players

    if turn < len(players) - 1:
        turn += 1
    else:
        turn = 0

    update_lobby(lobby.id, "Turn", turn)

    # Если что, исправить:
    lobby.update_status("choose_president")

    if lobby.current_president != -1 and lobby.current_chancellor != -1:
        lobby.change_rulers()

    choose_chancellor(players[turn], lobby, 0)


def choose_chancellor(user_id, lobby, page):
    player = Player(get_player(user_id))
    if player.game_status != "choose_chancellor":
        player.update_game_status("choose_chancellor")

    info = all_players_in_lobby(lobby, page)
    msg_k(user_id, info.get('keyboard'), player.language("choose_chancellor") + info.get('text'))
    msg_all(player.user_id, lobby, "president_choose_chancellor", "@id%s (%s)"%(player.user_id, player.nickname))


def all_players_in_lobby(lobby, page):
    lobby = Lobby(get_lobby(lobby.id))
    players = lobby.players

    all_players = []
    text = "\n"
    for i in range(len(players)):
        player = get_player(players[i])
        vote = ""

        if player[0][4] == "vote":
            vote = "| ❌"

        us = vk.method("users.get", {"user_ids": player[0][0], "fields": "sex"})
        text += str(i + 1) + ". @id%s (%s) - %s\n" % (player[0][0], player[0][7], ("%s %s %s" % (us[0].get('first_name'), us[0].get('last_name'), vote)))
        all_players += player

    return {'keyboard': list_keyboard(all_players, page, 7, "!choose"), 'text': text}


def users_in_same_lobby(first_user_id, second_user_id):
    try:
        user1 = Player(get_player(first_user_id))
        user2 = Player(get_player(second_user_id))

        if user1.lobby_id == user2.lobby_id:
            return True
        else:
            return False

    except Exception:
        return False


def player_actions(player, request):
    original_requset = request
    request = request.lower()

    if player.status != "in_game":
        if request == "!menu":
            player.update_status("")
            player.lobby_id = -1
            q.execute("UPDATE user_info SET Lobby_ID = '-1' WHERE User_ID = '%s'" % (player.user_id))
            connection.commit()
            msg_k(player.user_id, main_keyboard(player), player.language("return"))

        elif player.status == "":
            # All the commands down, if the player in the main menu:
            if request == "!create":
                msg_k(player.user_id, two_keyboard(player.language('accept'), 'positive', '!no',
                                                   player.language('cancel'), 'negative', '!menu'),
                      player.language('set_pass'))
                player.update_status("setting_password")

            elif request == "!connect":
                msg_k(user_id, one_keyboard(player.language('cancel'), 'negative', '!menu'),
                      player.language("enter_lobby_id"))
                player.update_status("connecting_to_lobby")

        elif player.status == "setting_password":
            if request == "!no":
                create_lobby(player, "")
            else:
                create_lobby(player, original_requset)

        elif player.status == "connecting_to_lobby":
            if request == "!menu":
                player.update_status("")
                msg_k(player, main_keyboard(player), player.language("return"))
                return
            else:
                if not request.isnumeric():
                    msg(player.user_id, player.language("wrong_lobby_id"))
                    return

            conn = connect_to_lobby(player, request, "")
            if conn:
                if conn == "password":
                    player.update_status("connecting_to_lobby-%s" % request)
                    msg(player.user_id, player.language("password_req"))
                    return

        elif player.status.startswith("connecting_to_lobby-"):
            lobby_id = player.status.split("-", 1)[1]
            password = original_requset
            conn = connect_to_lobby(player, lobby_id, password)
            if conn:
                if conn == "password":
                    msg(player.user_id, player.language("wrong_pass"))
                    return

        elif player.status == "in_lobby":
            lobby = Lobby(get_lobby(player.lobby_id))

            if request == "!leave" and lobby.can_enter:
                leave(player)
                player_actions(player, "!menu")
                lobby = Lobby(get_lobby(lobby.id))

            elif request == "!start":
                if lobby.host == player.user_id:
                    if 5 <= len(lobby.players) <= 10:
                        update_lobby(lobby.id, "Can_Enter", 0)
                        lobby.can_enter = 0
                        setup_game(lobby)
                    else:
                        msg(player.user_id, player.language("not_enough_players") + "%s" % (len(lobby.players)))
                        return
                else:
                    msg(player.user_id, player.language("not_host"))
                    return

            elif request == "!players":
                info = all_players_in_lobby(lobby, 0)
                msg(player.user_id, player.language("list_players") + "\n" + info.get("text"))
                return
    else:
        # If player is in game:

        lobby = Lobby(get_lobby(player.lobby_id))
        # In case of bug, will return to the menu
        if request == "!bug" and lobby.host == player.user_id:
            finish_game(lobby, "republic")
            return

        if request == "!players":
            info = all_players_in_lobby(lobby, 0)
            msg(player.user_id, player.language("list_players") + "\n" + info.get("text"))
            return

        elif request == "!table":
            table = get_table(lobby)

            msg(player.user_id, "%s"
                                "\n%s"
                                "\n\n"
                                "%s"
                                "\n%s"
                                "\n%s" % (
                    player.language("imperial_table"), table[0], player.language("republican_table"), table[1],
                    table[2]))
            return

        # Taking acts
        if lobby.status == "act" and player.user_id == lobby.current_president:
            if request.startswith("!choose "):
                request = request.replace("!choose ", "")
                if not request.isnumeric():
                    msg(player.user_id, player.language("must_be_numeric"))
                    return
                request = int(request) - 1
                all_players = lobby.players
                if request < len(all_players):
                    request = all_players[request]

                    if users_in_same_lobby(player.user_id, request):

                        victim = Player(get_player(request))
                        if player.game_status == "kill":
                            msg_k(victim.user_id, one_keyboard(victim.language("start"), "positive", "!"), victim.language("death"))
                            if victim.role == "sith":
                                finish_game(lobby, "republic")
                            else:
                                clear_user(victim)

                            lobby = Lobby(get_lobby(lobby.id))
                            game_turn(lobby)

                        elif player.game_status == "check":
                            if victim.role == "sith":
                                victim.role = "imper"

                            msg(player.user_id, player.language("checked") + "\n@id%s (%s) " % (
                                victim.user_id, victim.nickname) + player.language(victim.role))
                            game_turn(lobby)

                        elif player.game_status == "elect":
                            lobby.update_status("choose_chancellor")
                            lobby.change_rulers()
                            choose_chancellor(victim.user_id, lobby, 0)

                else:
                    msg(player.user_id, player.language("incorrect_number"))
                    return

        if player.game_status == "vote":
            if request == "!yes":
                vote_for_rulers(lobby, player, True)
            elif request == "!no":
                vote_for_rulers(lobby, player, False)

        elif player.game_status == "choose_chancellor":
            if request.startswith("!choose "):
                request = request.replace("!choose ", "")
                if not request.isnumeric():
                    msg(player.user_id, player.language("must_be_numeric"))
                    return

                request = int(request) - 1
                all_players = lobby.players
                if request < len(all_players):
                    request = all_players[request]
                else:
                    msg(player.user_id, player.language("incorrect_number"))
                    return

                if users_in_same_lobby(player.user_id, int(request)):

                    if not can_chancellor(get_player(int(request)), lobby) or int(request) == int(player.user_id):
                        msg(player.user_id, player.language("wrong_user"))
                    else:
                        player.update_game_status("")
                        vote_for_president(lobby, player, Player(get_player(int(request))))
                else:
                    msg(player.user_id, player.language("no_user_in_lobby"))
            elif request.startswith("!choose-goto_"):
                page = request.replace("!choose-goto_", "")
                if page.isnumeric():
                    choose_chancellor(player.user_id, lobby, int(page))

        elif player.game_status == "take_actions":



            if request == "!veto":
                if lobby.imperial_table == 5:
                    if lobby.status == "veto":
                        if player.user_id == lobby.current_president:
                            lobby.current_president = -1
                            lobby.current_chancellor = -1
                            lobby.update_rulers()
                            lobby.add_republican_state(1)
                            game_turn(lobby)

                    if player.user_id == lobby.current_chancellor and lobby.status == "veto_can":
                        lobby.update_status("veto")
                        player.update_game_status("")
                        president = Player(get_player(lobby.current_president))
                        msg_k(lobby.current_president, inline_two(president.language("veto"), "positive", "!veto", president.language("no"), "negative", "!no"),
                              president.language("veto_ask"))
                return

            elif request == "!no":
                if lobby.status == "veto":
                    cards_in_use = lobby.cards_in_use
                    disc = lobby.discard
                    disc = disc + [cards_in_use[0]]
                    lobby.update_discard(disc)
                    cards_in_use.pop(0)
                    lobby.update_cards_in_use(cards_in_use)
                    add_to_table(lobby, cards_in_use[0])
                    game_turn(lobby)
                    return

            if request.startswith("!choose "):
                request = request.replace("!choose ", "")
                if request.isnumeric():
                    request = int(request) - 1
                    cards_in_use = lobby.cards_in_use
                    if 0 <= request < len(cards_in_use):
                        disc = lobby.discard

                        player.update_game_status("")
                        chancellor = Player(get_player(lobby.current_chancellor))

                        if lobby.current_president == player.user_id and len(cards_in_use) > 2:
                            disc = disc + [cards_in_use[request]]
                            lobby.update_discard(disc)
                            cards_in_use.pop(request)
                            lobby.update_cards_in_use(cards_in_use)

                            msg_all(chancellor.user_id, lobby, "chancellor_choice", "")
                            msg_k(chancellor.user_id, actions_keyboard(chancellor.user_id, cards_in_use),
                                  chancellor.language("take_actions_c") + "\n\n" + visual_acts(chancellor, cards_in_use))
                            chancellor.update_game_status("take_actions")

                        elif lobby.current_chancellor == player.user_id:
                            disc = disc + [cards_in_use[len(cards_in_use) - request - 1]]
                            lobby.update_discard(disc)
                            cards_in_use.pop(len(cards_in_use) - request - 1)
                            lobby.update_cards_in_use(cards_in_use)

                            chancellor.update_game_status("")
                            add_to_table(lobby, cards_in_use[0])

                            if lobby.status == "act":
                                president = Player(get_player(lobby.current_president))
                                gs = president.game_status
                                info = all_players_in_lobby(lobby, 0)

                                if gs == "kill":
                                    msg_k(president.user_id, info.get('keyboard'),
                                          president.language("kill") + info.get('text'))

                                elif gs == "look":
                                    look_cards = take_actions(lobby, 3)
                                    lobby.update_deck(look_cards + lobby.deck)
                                    lobby.update_cards_in_use([])

                                    msg(president.user_id,
                                        president.language("look") + "\n\n" + visual_acts(president, look_cards))
                                    game_turn(lobby)

                                elif gs == "check":
                                    msg_k(president.user_id, info.get('keyboard'),
                                          president.language("check") + info.get('text'))

                                elif gs == "elect":
                                    msg_k(president.user_id, info.get('keyboard'),
                                          president.language("elect") + info.get('text'))

                            else:
                                game_turn(lobby)
                    else:
                        msg(player.user_id, player.language("incorrect_number"))
                else:
                    msg(player.user_id, player.language("must_be_numeric"))


def msg_all(but_user, lobby, text, addition):
    players = lobby.players
    for i in range(len(players)):
        player = Player(get_player(players[i]))
        if player.user_id != but_user:
            msg(player.user_id, player.language(text) + " " + addition)


def visual_acts(player, acts_arr):
    text = ""
    for i in range(len(acts_arr)):
        if int(acts_arr[i]):
            text += str(i + 1) + ". 📘 " + player.language("rep") + "\n"
        else:
            text += str(i + 1) + ". 📕 " + player.language("imp") + "\n"

    return text


def add_to_table(lobby, choice):
    if int(choice):
        lobby.republican_table += 1
        q.execute(
            "UPDATE lobby_info SET In_Place_Lib = '%s' WHERE Lobby_ID = '%s'" % (lobby.republican_table, lobby.id))
        act = "republican"
        connection.commit()
    else:
        lobby.imperial_table += 1
        q.execute("UPDATE lobby_info SET In_Place_Imp = '%s' WHERE Lobby_ID = '%s'" % (lobby.imperial_table, lobby.id))
        act = "imperial"
        # проверяем, если есть дополнительные правила
        connection.commit()
        take_additions(lobby)

    users = lobby.players

    table = get_table(lobby)
    for user in users:
        player = Player(get_player(user))
        msg(player.user_id, player.language("added_" + act) +
            "\n______________\n\n%s"
            "\n%s"
            "\n\n"
            "%s"
            "\n%s"
            "\n%s" % (
                player.language("imperial_table"), table[0], player.language("republican_table"), table[1], table[2]))

    if lobby.republican_table == liberal:
        finish_game(lobby, "republic")
        return

    if lobby.imperial_table == imperial:
        finish_game(lobby, "imperial")
        return


def take_additions(lobby):
    players = lobby.players
    players_amount = len(players)
    imperial_time = lobby.imperial_table

    # x: 0 || check: 2 || elect: 3 || kill: 4 || kill+veto: 5 || look: 6

    five_six = [0, 0, 6, 4, 5]
    seven_eight = [0, 2, 3, 4, 5]
    nine_ten = [0, 2, 3, 4, 5]

    action = 0
    if imperial_time != 5:
        if 5 <= players_amount <= 6:
            action = five_six[imperial_time - 1]
        else:
            if 7 <= players_amount <= 8:
                action = seven_eight[imperial_time - 1]
            elif 9 <= players_amount <= 10:
                action = nine_ten[imperial_time - 1]
    else:
        action = 5

    if action:
        player = Player(get_player(lobby.current_president))
        lobby.update_status("act")
        if action == 2:
            player.update_game_status("check")
            msg_all(player.user_id, lobby, "check_p", "")
            return False
        elif action == 3:
            player.update_game_status("elect")
            msg_all(player.user_id, lobby, "elect_p", "")
            return False
        elif action == 4:
            player.update_game_status("kill")
            msg_all(player.user_id, lobby, "kill_p", "")
            return False
        elif action == 5:
            player.update_game_status("kill")
            msg_all(player.user_id, lobby, "kill+v_p", "")
            return False
        elif action == 6:
            player.update_game_status("look")
            msg_all(player.user_id, lobby, "look_p", "")
            return False
    return True


def get_table(lobby):
    gun = '💣'
    check = '🔎'
    look = '👁‍🗨'
    next_president = '👥'
    veto = '⚖'

    # Для 5-6: [x, x, посмотреть 3 верхнии карты, убить игрок, убить игрока + право веты, gg] 1 имперец, 1 ситх. (знают)
    # 7-8: [x, проверить карту, выбрать следующего, убить игрок, убить игрока + право веты, gg] 2 имперца 1 ситх (не знают)
    # 9-10: [проверкить, проверить карту, выбрать следующего, убить игрок, убить игрока + право веты, gg] 3 имперца 1 ситх

    imper = ['▫'] * imperial

    players = len(lobby.players)

    if 5 <= players <= 6:
        imper[2] = look
    else:
        if 7 <= players <= 8:
            imper[1] = check
        if 9 <= players <= 10:
            imper[0] = check
        imper[2] = next_president

    imper[3] = gun
    imper[4] = gun
    imper[5] = '👺'

    chosen_imp = lobby.imperial_table
    imper_table = ""

    for i in range(imperial):
        if chosen_imp > i:
            imper[i] = '📕'
        imper_table += imper[i] + " "

    repub_table = '📘 ' * lobby.republican_table + '▫ ' * (liberal - lobby.republican_table - 1)

    if lobby.republican_table != liberal:
        repub_table += '🕊'

    rep_state = '🔸 ' * (lobby.republican_state + 1) + '🔹 ' * (lib_choice - lobby.republican_state)

    return [imper_table, repub_table, rep_state]


def finish_game(lobby, winners):
    players = lobby.players

    for user in players:
        player = Player(get_player(user))
        clear_user(player)
        msg_k(player.user_id, one_keyboard(player.language("start"), "positive", "!"), player.language("finished_" + winners))

    lobby.update_players([])


def clear_user(player):
    leave(player)
    q.execute("DELETE FROM user_info WHERE User_ID = '%s'" % player.user_id)
    connection.commit()


def can_chancellor(user_info, lobby):
    if len(user_info) > 0:
        player = Player(user_info)
    else:
        return False

    if player.lobby_id == lobby.id:
        if lobby.ex_chancellor != player.user_id:
            if lobby.ex_president != player.user_id or len(lobby.players) <= 5:
                return True

    return False


def get_lobby(lobby_id):
    q.execute("SELECT * FROM lobby_info WHERE Lobby_ID = '%s'" % (lobby_id))
    return q.fetchall()


def main_keyboard(player):
    lang = player.lang
    buttons = [
        [get_button(get_line(lang, "create_lobby"), "primary", "!create")],
        [get_button(get_line(lang, "connect_to_lobby"), "positive", "!connect")],
        [get_button(get_line(lang, "rules"), "primary", "!rules"), get_button(lang, "secondary", "!language")]
    ]

    return create_keyboard(buttons)


while True:
    try:
        for event in longpoll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:

                user_id = event.object.from_id
                request = str(event.object.text)  # Обробатываем сообщение от пользователя.
                payload = event.object.get("payload")  # Получаем payload (в случае, если используется клавиатура)

                if payload is not None:
                    request = payload.replace("\"", "")


                connection = psycopg2.connect(DATABASE_URL, sslmode='require')
                #connection = sql.connect("some.sqlite", check_same_thread=False)
                q = connection.cursor()
                q.execute("SELECT * FROM user_info WHERE User_ID = '%s'" % (user_id))
                user_data = q.fetchall()

                if len(user_data) == 0:
                    q.execute("INSERT INTO user_info "
                              "(User_ID, Lobby_ID, Role, Cards, Status, Game_Status, Language, Nickname) VALUES ('%s', '%s','%s', '%s', '%s', '%s', '%s', '%s')" %
                              (user_id, -1, "", "", "", "", "RU", ""))
                    connection.commit()

                    q.execute("SELECT * FROM user_info WHERE User_ID = '%s'" % (user_id))
                    user_data = q.fetchall()
                    msg_k(user_id, main_keyboard(Player(user_data)), "Добро пожаловать!")

                else:
                    print(user_data, ":> ", request)

                    #action = threading.Thread(target=player_actions, args=(Player(user_data), request))
                    #action.start()
                    player_actions(Player(user_data), request)


    except Exception as e:
        print(str(e))
        time.sleep(5)
