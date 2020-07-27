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
    offset = 8

    for i in range(page_forward, len(array)):
        buttons_array.append(get_button(str(array[i][index]), "secondary", str(req)+" "+str(i+1)))

        if (i)%2 == 1 and len(buttons_array) > 0:
            mass.append(buttons_array)
            buttons_array = []

        if i == page_forward+offset:
            break

    b_reg = []
    if page_forward > 0:
        b_reg.append(get_button("<--", "negative", str(req)+"-goto_"+str(page_forward - offset)))

    if len(array) > (page_forward+offset):
        b_reg.append(get_button("-->", "positive", str(req)+"-goto_"+str(page_forward + offset)))
    else:
        if len(array)%2 == 1:
            mass.append([get_button(str(array[len(array)-1][index]), "secondary", str(req) + " " + str(len(array)))])

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
