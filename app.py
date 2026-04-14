from flask import Flask, jsonify

app = Flask(__name__)

state = {
    "level": 1,
    "xp": 30
}

XP_PER_CARD = 10
MAX_LEVEL = 5


@app.route("/")
def index():
    level = state["level"]
    xp = state["xp"]
    progress = max(0, min(100, xp))

    html = f"""
    <html>
        <head>
            <meta charset="utf-8">
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
                .gem-shape {{
                    width: 100%;
                    height: 100%;
                    background: linear-gradient(135deg, #3ceaaa, #2b9f73, #9fe6b8);
                    clip-path: polygon(50% 0%, 95% 35%, 80% 100%, 20% 100%, 5% 35%);
                    box-shadow:
                        0 0 20px rgba(76, 237, 165, 0.7),
                        0 0 60px rgba(76, 237, 165, 0.3);
                }}
                .gem-glow {{
                    position: absolute;
                    inset: -15px;
                    border-radius: 40%;
                    background: radial-gradient(circle, rgba(159,230,184,0.15), transparent 60%);
                    filter: blur(4px);
                    pointer-events: none;
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
                .hint {{
                    margin-top: 8px;
                    font-size: 11px;
                    opacity: 0.6;
                }}
            </style>
        </head>
        <body>
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

            <button class="btn" id="card-btn">Отправить открытку</button>
            <div class="hint">В тестовом режиме каждая открытка даёт +{XP_PER_CARD}% заряда.</div>

            <script>
                const btn = document.getElementById("card-btn");
                const bar = document.getElementById("bar");
                const label = document.getElementById("label");

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
                        const p = Math.max(0, Math.min(100, data.progress));
                        bar.style.width = p + "%";
                        label.textContent = "Заряд камня: " + p + "% (уровень " + data.level + ")";
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
    state["xp"] += XP_PER_CARD

    while state["xp"] >= 100 and state["level"] < MAX_LEVEL:
        state["xp"] -= 100
        state["level"] += 1

    if state["level"] >= MAX_LEVEL and state["xp"] > 100:
        state["xp"] = 100

    progress = max(0, min(100, state["xp"]))

    return jsonify({
        "level": state["level"],
        "progress": progress
    })


if __name__ == "__main__":
    app.run(debug=True)
