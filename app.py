from datetime import date
from flask import Flask, jsonify, request, redirect, session, render_template
import uuid
import hashlib
from urllib.parse import parse_qsl
import json
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.environ["BOT_TOKEN"]
BOT_USERNAME = os.environ.get("BOT_USERNAME", "YourBotName")  # добавь в .env
print("APP BOT_TOKEN prefix:", BOT_TOKEN[:10])

app = Flask(__name__)
app.secret_key = "SOME_SECRET_FOR_SESSION"  # замени на случайную длинную строку

DATA_FILE = "data.json"

# users = {
#   user_id: {
#       "name": ...,
#       "tg_user_id": ...,
#       "people": {
#           person_id: {
#               "name": ...,
#               "level": int,
#               "xp": int,
#               "last_action_date": str|None,
#               "actions_today": int,
#               "dev_mode": bool,
#               "streak_days": int,
#               "last_streak_date": str|None,
#               "linked_user_id": str|None,
#           },
#           ...
#       }
#   }
# }
users = {}

def validate_init_data(init_data: str, bot_token: str) -> dict:
    """
    Упрощённый вариант: разбираем initData в dict без проверки подписи.
    Для продакшена нужно вернуть HMAC-проверку по документации Telegram.
    """
    data = dict(parse_qsl(init_data, keep_blank_values=True))

    user_raw = data.get("user")
    if isinstance(user_raw, str):
        try:
            data["user"] = json.loads(user_raw)
        except Exception:
            pass

    print("AUTH_TG: WARNING: hash validation DISABLED")
    return data

def load_data():
    global users
    if not os.path.exists(DATA_FILE):
        return
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            users = data
    except Exception:
        pass

def save_data():
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

load_data()

XP_PER_CARD = 15
MAX_LEVEL = 5
MAX_ACTIONS_PER_DAY = 1

def get_gem_style(level: int, progress: int):
    t = max(0.0, min(1.0, progress / 100.0))

    if level == 1:
        gradient = "linear-gradient(135deg, #245f46, #184232, #53b383)"
    elif level == 2:
        gradient = "linear-gradient(135deg, #2c8b63, #1f6245, #7bd3a4)"
    elif level == 3:
        gradient = "linear-gradient(135deg, #35a86f, #24754c, #a6e79b)"
    elif level == 4:
        gradient = "linear-gradient(135deg, #40c67b, #298b53, #cff4a5)"
    else:
        gradient = "linear-gradient(135deg, #4be987, #2fa35e, #f2ffbc)"

    outer_glow_alpha = 0.30 + 0.45 * t
    far_glow_alpha = 0.10 + 0.35 * t
    halo_alpha = 0.16 + 0.26 * t
    halo_inner = 40 + int(30 * t)

    box_shadow = (
        f"0 0 34px rgba(76, 237, 165, {outer_glow_alpha}), "
        f"0 0 95px rgba(76, 237, 165, {far_glow_alpha})"
    )

    halo_background = (
        f"radial-gradient(circle, rgba(159,230,184,{halo_alpha}) {halo_inner}%, transparent 82%)"
    )

    return gradient, box_shadow, halo_background

def generate_id():
    return uuid.uuid4().hex[:8]

def get_current_user():
    user_id = session.get("user_id")
    if not user_id or user_id not in users:
        return None, None
    return user_id, users[user_id]

def today_str():
    return date.today().isoformat()

def get_or_create_user_for_tg(tg_user_id: str, tg_first_name: str | None = None) -> str:
    for uid, udata in users.items():
        if udata.get("tg_user_id") == tg_user_id:
            return uid

    name = tg_first_name or f"Пользователь {tg_user_id}"
    new_user_id = generate_id()
    users[new_user_id] = {
        "name": name,
        "tg_user_id": tg_user_id,
        "people": {}
    }
    save_data()
    return new_user_id

def process_referral(new_user_id: str, start_param: str | None):
    """
    Создаём пару камней между пригласившим (owner) и приглашённым (new_user),
    если пришёл валидный start_param вида "ref_<owner_user_id>".
    """
    if not start_param:
        return

    if not isinstance(start_param, str):
        return

    if not start_param.startswith("ref_"):
        return

    owner_user_id = start_param[4:]
    if owner_user_id == new_user_id:
        return
    if owner_user_id not in users or new_user_id not in users:
        return

    owner = users[owner_user_id]
    invited = users[new_user_id]

    # Проверим, что у них ещё нет связи
    for p in owner.get("people", {}).values():
        if p.get("linked_user_id") == new_user_id:
            return

    owner_person_id = generate_id()
    invited_person_id = generate_id()

    owner["people"][owner_person_id] = {
        "name": invited.get("name", "Друг"),
        "level": 1,
        "xp": 0,
        "last_action_date": None,
        "actions_today": 0,
        "dev_mode": False,
        "streak_days": 0,
        "last_streak_date": None,
        "linked_user_id": new_user_id,
    }

    invited["people"][invited_person_id] = {
        "name": owner.get("name", "Друг"),
        "level": 1,
        "xp": 0,
        "last_action_date": None,
        "actions_today": 0,
        "dev_mode": False,
        "streak_days": 0,
        "last_streak_date": None,
        "linked_user_id": owner_user_id,
    }

    save_data()
    print(f"REFERRAL: created link {owner_user_id} <-> {new_user_id} with start_param={start_param}")

@app.route("/auth_telegram", methods=["POST"])
def auth_telegram():
    print("AUTH_TG: вызывается")

    try:
        data = request.get_json(silent=True) or {}
        raw_init_data = data.get("initData", "") or ""
        start_param = data.get("start_param") or data.get("startParam")

        print(f"AUTH_TG: длина init_data {len(raw_init_data)}, start_param={start_param}")

        user_data = validate_init_data(raw_init_data, BOT_TOKEN)

        user_json = user_data.get("user")
        if isinstance(user_json, str):
            user_obj = json.loads(user_json)
        else:
            user_obj = user_json or {}

        tg_user_id = str(user_obj.get("id"))
        tg_first_name = user_obj.get("first_name") or user_obj.get("username") or None
        local_user_id = get_or_create_user_for_tg(tg_user_id, tg_first_name)

        session["tg_user_id"] = tg_user_id
        session["user_id"] = local_user_id

        # Обработка реферального параметра
        process_referral(local_user_id, start_param)

        return jsonify({"ok": True, "user_id": tg_user_id})
    except ValueError as e:
        print("AUTH_TG: ошибка проверки:", e)
        return jsonify({"ok": False, "error": str(e)}), 400
    except Exception as e:
        print("AUTH_TG: неожиданная ошибка:", e)
        return jsonify({"ok": False, "error": "Internal server error"}), 500

@app.route("/")
def index():
    user_id, user = get_current_user()
    people = user.get("people", {}) if user else {}
    today = today_str()

    return render_template(
        "index.html",
        user=user,
        people=people,
        today=today,
    )

@app.route("/person/<person_id>")
def person_page(person_id):
    user_id, user = get_current_user()
    if not user:
        return "no user in session", 400

    people = user["people"]
    if person_id not in people:
        return "Такого человека нет", 404

    p = people[person_id]
    level = p["level"]
    xp = p["xp"]
    progress = max(0, min(100, xp))
    dev_mode = p.get("dev_mode", False)
    streak = p.get("streak_days", 0)

    gradient, box_shadow, halo_bg = get_gem_style(level, progress)

    today = today_str()
    limit_reached = (
        (not dev_mode)
        and p.get("last_action_date") == today
        and p.get("actions_today", 0) >= MAX_ACTIONS_PER_DAY
    )

    active_today = (p.get("last_action_date") == today)

    return render_template(
        "person.html",
        person=p,
        level=level,
        progress=progress,
        streak=streak,
        gradient=gradient,
        box_shadow=box_shadow,
        halo_bg=halo_bg,
        max_actions=MAX_ACTIONS_PER_DAY,
        xp_per_card=XP_PER_CARD,
        dev_mode=dev_mode,
        person_id=person_id,
        limit_reached=limit_reached,
        active_today=active_today,
    )

@app.route("/send_card/<person_id>", methods=["POST"])
def send_card(person_id):
    user_id, user = get_current_user()
    if not user:
        return jsonify({"error": "no user"}), 400

    people = user["people"]
    if person_id not in people:
        return jsonify({"error": "unknown person"}), 404

    p = people[person_id]
    today = today_str()

    if p.get("last_action_date") != today:
        p["last_action_date"] = today
        p["actions_today"] = 0

    last_streak = p.get("last_streak_date")
    if last_streak is None:
        p["streak_days"] = 1
        p["last_streak_date"] = today
    else:
        if last_streak == today:
            pass
        else:
            last_date = date.fromisoformat(last_streak)
            diff = (date.today() - last_date).days
            if diff == 1:
                p["streak_days"] = p.get("streak_days", 0) + 1
                p["last_streak_date"] = today
            elif diff > 1:
                p["streak_days"] = 0
                p["last_streak_date"] = today
                p["level"] = 1
                p["xp"] = 0

    if not p.get("dev_mode", False) and p.get("actions_today", 0) >= MAX_ACTIONS_PER_DAY:
        progress = max(0, min(100, p["xp"]))
        gradient, box_shadow, halo_bg = get_gem_style(p["level"], progress)
        return jsonify({
            "level": p["level"],
            "progress": progress,
            "limit_reached": True,
            "actions_today": p["actions_today"],
            "max_actions": MAX_ACTIONS_PER_DAY,
            "dev_mode": p.get("dev_mode", False),
            "gradient": gradient,
            "box_shadow": box_shadow,
            "halo_bg": halo_bg,
            "streak_days": p.get("streak_days", 0),
        })

    if not p.get("dev_mode", False):
        p["actions_today"] = p.get("actions_today", 0) + 1

    p["xp"] += XP_PER_CARD

    while p["xp"] >= 100 and p["level"] < MAX_LEVEL:
        p["xp"] -= 100
        p["level"] += 1

    if p["level"] >= MAX_LEVEL and p["xp"] > 100:
        p["xp"] = 100

    progress = max(0, min(100, p["xp"]))
    gradient, box_shadow, halo_bg = get_gem_style(p["level"], progress)

    save_data()

    return jsonify({
        "level": p["level"],
        "progress": progress,
        "limit_reached": (not p.get("dev_mode", False) and p["actions_today"] >= MAX_ACTIONS_PER_DAY),
        "actions_today": p["actions_today"],
        "max_actions": MAX_ACTIONS_PER_DAY,
        "dev_mode": p.get("dev_mode", False),
        "gradient": gradient,
        "box_shadow": box_shadow,
        "halo_bg": halo_bg,
        "streak_days": p.get("streak_days", 0),
    })

@app.route("/dev_toggle/<person_id>", methods=["POST"])
def dev_toggle(person_id):
    user_id, user = get_current_user()
    if not user:
        return jsonify({"error": "no user"}), 400

    people = user["people"]
    if person_id not in people:
        return jsonify({"error": "unknown person"}), 404

    p = people[person_id]
    p["dev_mode"] = not p["dev_mode"]

    if p["dev_mode"]:
        today = today_str()
        p["last_action_date"] = today
        p["actions_today"] = 0

    progress = max(0, min(100, p["xp"]))
    gradient, box_shadow, halo_bg = get_gem_style(p["level"], progress)

    save_data()

    return jsonify({
        "level": p["level"],
        "progress": progress,
        "dev_mode": p["dev_mode"],
        "actions_today": p["actions_today"],
        "max_actions": MAX_ACTIONS_PER_DAY,
        "gradient": gradient,
        "box_shadow": box_shadow,
        "halo_bg": halo_bg,
        "streak_days": p.get("streak_days", 0),
    })

@app.route("/delete_person/<person_id>", methods=["POST"])
def delete_person(person_id):
    user_id, user = get_current_user()
    if not user:
        return jsonify({"error": "no user"}), 400

    people = user["people"]
    if person_id in people:
        del people[person_id]
        save_data()
        return jsonify({"status": "ok"})
    else:
        return jsonify({"error": "unknown person"}), 404

@app.route("/dev/info")
def dev_info():
    user_id, user = get_current_user()
    if not user:
        return "no user", 400

    return f"""
    <html>
      <head>
        <meta charset="utf-8">
        <title>Dev info</title>
        <style>
          body {{
            font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            background: #050811;
            color: #f5f5f5;
            padding: 16px;
          }}
          pre {{
            background: rgba(255,255,255,0.04);
            padding: 12px;
            border-radius: 8px;
            white-space: pre-wrap;
          }}
        </style>
      </head>
      <body>
        <h2>Current user_id: {user_id}</h2>
        <pre>{json.dumps(user, ensure_ascii=False, indent=2)}</pre>
      </body>
    </html>
    """

@app.route("/get_ref_link")
def get_ref_link():
    """
    Возвращает реферальную ссылку для текущего пользователя.
    """
    user_id, user = get_current_user()
    if not user:
        return jsonify({"error": "no user"}), 400

    ref_code = f"ref_{user_id}"
    link = f"https://t.me/{BOT_USERNAME}?startapp={ref_code}"
    return jsonify({"link": link})

if __name__ == "__main__":
    app.run(debug=True)
