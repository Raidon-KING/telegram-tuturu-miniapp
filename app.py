from datetime import date
from flask import Flask, jsonify

app = Flask(__name__)

state = {
    "level": 1,
    "xp": 30,
    "last_action_date": None,
    "actions_today": 0,
    "dev_mode": False
}

XP_PER_CARD = 10
MAX_LEVEL = 5
MAX_ACTIONS_PER_DAY = 3


def get_gem_style(level: int, progress: int):
    """
    Базовый, мягкий вариант:
    - оттенок камня слегка меняется по уровням,
    - свечение плавно усиливается по мере роста прогресса.
    """
    t = max(0.0, min(1.0, progress / 100.0))

    if level == 1:
        gradient = "linear-gradient(135deg, #2c8c67, #24654a, #6bc79a)"
        glow_color = "rgba(107,199,154,{alpha})"
    elif level == 2:
        gradient = "linear-gradient(135deg, #31a875, #24895c, #86e0b2)"
        glow_color = "rgba(134,224,178,{alpha})"
    elif level == 3:
        gradient = "linear-gradient(135deg, #3bbf79, #2e9961, #bde98a)"
        glow_color = "rgba(189,233,138,{alpha})"
    elif level == 4:
        gradient = "linear-gradient(135deg, #47d187, #35a66a, #d6f19c)"
        glow_color = "rgba(214,241,156,{alpha})"
    else:
        gradient = "linear-gradient(135deg, #55e494, #3bb774, #f0ffb8)"
        glow_color = "rgba(240,255,184,{alpha})"

    # базовая мягкая яркость + немного от прогресса
    base_brightness = 0.7
    progress_factor = 0.3 * t
    glow_strength = min(1.0, base_brightness + progress_factor)

    outer_glow_alpha = 0.5 * glow_strength
    far_glow_alpha = 0.2 * glow_strength
    halo_alpha = 0.2 * glow_strength

    box_shadow = (
        f"0 0 20px rgba(76, 237, 165, {outer_glow_alpha}), "
        f"0 0 60px rgba(76, 237, 165, {far_glow_alpha})"
    )
    halo_background = (
        f"radial-gradient(circle, {glow_color.format(alpha=halo_alpha)}, transparent 60%)"
    )

    return gradient, box_shadow, halo_background


@app.route("/")
def index():
    level = state["level"]
    xp = state["xp"]
    progress = max(0, min(100, xp))
    dev_mode = state["dev_mode"]

    gradient, box_shadow, halo_bg = get_gem_style(level, progress)
    dev_label = "DEV ON" if dev_mode else "DEV OFF"

    html = f"""
    <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>Наш камень</title>
            <style>
                body {{
                    font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
                    background: radial-gradient(circle at top, #16243a 0, #050811 60%, #020308 100%);
                    color: #f5f5f5;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    height: 100vh;
                    margin: 0;
                    text-align: center;
                }}
                .gem-wrapper {{
                    position: relative;
                    width: 140px;
                    height: 140px;
                    margin-bottom: 12px;
                }}
                .gem-glow {{
                    position: absolute;
                    inset: -15px;
                    border-radius: 40%;
                    background: {halo_bg};
                    filter: blur(4px);
                    pointer-events: none;
                    transition: background 0.4s ease-out;
                }}
                .gem-shape {{
                    width: 100%;
                    height: 100%;
                    background: {gradient};
                    clip-path: polygon(50% 0%, 95% 35%, 80% 100%, 20% 100%, 5% 35%);
                    box-shadow: {box_shadow};
                    transition: background 0.4s ease-out, box-shadow 0.4s ease-out;
                }}
                .name {{
                    font-size: 20px;
                    margin-bottom: 4px;
                    color: #9fe6b8;
                    letter-spacing: 0.04em;
                    text-transform: uppercase;
                }}
                .level {{
                    font-size: 13px;
                    opacity: 0.85;
                    margin-bottom: 8px;
                }}
                .subtitle {{
                    font-size: 14px;
                    max-width: 280px;
                    opacity: 0.85;
                    margin-bottom: 18px;
                }}
                .bar-wrapper {{
                    width: 240px;
                    height: 8px;
                    border-radius: 999px;
                    background: rgba(255,255,255,0.08);
                    overflow: hidden;
                    margin-bottom: 6px;
                }}
                .bar-fill {{
                    width: {progress}%;
                    height: 100%;
                    background: linear-gradient(90deg, #3ceaaa, #9fe6b8);
                    box-shadow: 0 0 10px rgba(76, 237, 165, 0.8);
                    transition: width 0.3s ease-out;
                }}
                .bar-label {{
                    font-size: 12px;
                    opacity: 0.8;
                    margin-bottom: 14px;
                }}
                .btn {{
                    border: none;
                    outline: none;
                    padding: 10px 18px;
                    border-radius: 999px;
                    background: linear-gradient(135deg, #3ceaaa, #2b9f73);
                    color: #050811;
                    font-size: 14px;
                    cursor: pointer;
                    box-shadow: 0 0 12px rgba(76, 237, 165, 0.6);
                }}
                .btn:active {{
                    transform: scale(0.97);
                    box-shadow: 0 0 6px rgba(76, 237, 165, 0.6);
                }}
                .btn:disabled {{
                    opacity: 0.5;
                    cursor: default;
                    box-shadow: none;
                }}
                .hint {{
                    margin-top: 8px;
                    font-size: 11px;
                    opacity: 0.6;
                }}
                .dev-btn {{
                    position: fixed;
                    top: 8px;
                    right: 8px;
                    font-size: 10px;
                    padding: 4px 8px;
                    border-radius: 999px;
                    border: none;
                    cursor: pointer;
                    transition: opacity 0.2s ease, box-shadow 0.2s ease;
                }}
                .dev-off {{
                    background: rgba(255,255,255,0.08);
                    color: #9fe6b8;
                    opacity: 0.4;
                }}
                .dev-on {{
                    background: rgba(76,237,165,0.85);
                    color: #050811;
                    opacity: 0.95;
                    box-shadow: 0 0 10px rgba(76,237,165,0.8);
                }}

                @media (max-width: 480px) {{
                    .gem-wrapper {{
                        width: 120px;
                        height: 120px;
                    }}
                    .bar-wrapper {{
                        width: 90vw;
                        max-width: 260px;
                    }}
                }}
            </style>
        </head>
        <body>
            <button class="dev-btn {'dev-on' if dev_mode else 'dev-off'}" id="dev-btn">{dev_label}</button>

            <div class="gem-wrapper">
                <div class="gem-glow"></div>
                <div class="gem-shape"></div>
            </div>
            <div class="name">Хризолит</div>
            <div class="level">Уровень {level}</div>
            <div class="subtitle">
                Это ваш общий камень. Каждое действие внутри усиливает его и поднимает уровень.
            </div>

            <div class="bar-wrapper">
                <div class="bar-fill" id="bar"></div>
            </div>
            <div class="bar-label" id="label">Заряд камня: {progress}% (уровень {level})</div>

            <button class="btn" id="card-btn">Отправить знак внимания</button>
            <div class="hint">Не более {MAX_ACTIONS_PER_DAY} знаков внимания в день. Каждый даёт +{XP_PER_CARD}% заряда.</div>

            <script>
                const btn = document.getElementById("card-btn");
                const bar = document.getElementById("bar");
                const label = document.getElementById("label");
                const devBtn = document.getElementById("dev-btn");

                function applyCommon(data) {{
                    const p = Math.max(0, Math.min(100, data.progress));
                    bar.style.width = p + "%";
                    label.textContent = "Заряд камня: " + p + "% (уровень " + data.level + ")";
                }}

                btn.addEventListener("click", async () => {{
                    try {{
                        const response = await fetch("/send_card", {{
                            method: "POST",
                            headers: {{
                                "Content-Type": "application/json"
                            }},
                            body: JSON.stringify({{}})
                        }});
                        const data = await response.json();
                        applyCommon(data);

                        if (!data.dev_mode && data.limit_reached) {{
                            btn.disabled = true;
                            btn.textContent = "Лимит на сегодня исчерпан";
                        }} else {{
                            btn.disabled = false;
                            btn.textContent = "Отправить знак внимания";
                        }}

                        if (data.dev_mode) {{
                            devBtn.classList.remove("dev-off");
                            devBtn.classList.add("dev-on");
                            devBtn.textContent = "DEV ON";
                        }} else {{
                            devBtn.classList.remove("dev-on");
                            devBtn.classList.add("dev-off");
                            devBtn.textContent = "DEV OFF";
                        }}
                    }} catch (e) {{
                        console.error(e);
                    }}
                }});

                devBtn.addEventListener("click", async () => {{
                    try {{
                        const response = await fetch("/dev_toggle", {{
                            method: "POST"
                        }});
                        const data = await response.json();
                        applyCommon(data);

                        if (data.dev_mode) {{
                            devBtn.classList.remove("dev-off");
                            devBtn.classList.add("dev-on");
                            devBtn.textContent = "DEV ON";
                            btn.disabled = false;
                            btn.textContent = "Отправить знак внимания";
                        }} else {{
                            devBtn.classList.remove("dev-on");
                            devBtn.classList.add("dev-off");
                            devBtn.textContent = "DEV OFF";
                        }}
                    }} catch (e) {{
                        console.error(e);
                    }}
                }});
            </script>
        </body>
    </html>
    """
    return html


@app.route("/send_card", methods=["POST"])
def send_card():
    today = date.today().isoformat()

    if state["last_action_date"] != today:
        state["last_action_date"] = today
        state["actions_today"] = 0

    if not state["dev_mode"] and state["actions_today"] >= MAX_ACTIONS_PER_DAY:
        progress = max(0, min(100, state["xp"]))
        return jsonify({
            "level": state["level"],
            "progress": progress,
            "limit_reached": True,
            "actions_today": state["actions_today"],
            "max_actions": MAX_ACTIONS_PER_DAY,
            "dev_mode": state["dev_mode"]
        })

    if not state["dev_mode"]:
        state["actions_today"] += 1

    state["xp"] += XP_PER_CARD

    while state["xp"] >= 100 and state["level"] < MAX_LEVEL:
        state["xp"] -= 100
        state["level"] += 1

    if state["level"] >= MAX_LEVEL and state["xp"] > 100:
        state["xp"] = 100

    progress = max(0, min(100, state["xp"]))

    return jsonify({
        "level": state["level"],
        "progress": progress,
        "limit_reached": False,
        "actions_today": state["actions_today"],
        "max_actions": MAX_ACTIONS_PER_DAY,
        "dev_mode": state["dev_mode"]
    })


@app.route("/dev_toggle", methods=["POST"])
def dev_toggle():
    state["dev_mode"] = not state["dev_mode"]

    if state["dev_mode"]:
        today = date.today().isoformat()
        state["last_action_date"] = today
        state["actions_today"] = 0

    progress = max(0, min(100, state["xp"]))

    return jsonify({
        "level": state["level"],
        "progress": progress,
        "dev_mode": state["dev_mode"],
        "actions_today": state["actions_today"],
        "max_actions": MAX_ACTIONS_PER_DAY
    })


if __name__ == "__main__":
    app.run(debug=True)
