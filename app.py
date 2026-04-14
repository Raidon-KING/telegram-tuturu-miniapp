from flask import Flask

app = Flask(__name__)


@app.route("/")
def index():
    return """
    <html>
        <head>
            <meta charset="utf-8">
            <title>Наш камень</title>
            <style>
                body {
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
                }
                .gem-wrapper {
                    position: relative;
                    width: 140px;
                    height: 140px;
                    margin-bottom: 12px;
                }
                .gem-shape {
                    width: 100%;
                    height: 100%;
                    background: linear-gradient(135deg, #3ceaaa, #2b9f73, #9fe6b8);
                    clip-path: polygon(50% 0%, 95% 35%, 80% 100%, 20% 100%, 5% 35%);
                    box-shadow:
                        0 0 20px rgba(76, 237, 165, 0.7),
                        0 0 60px rgba(76, 237, 165, 0.3);
                }
                .gem-glow {
                    position: absolute;
                    inset: -15px;
                    border-radius: 40%;
                    background: radial-gradient(circle, rgba(159,230,184,0.15), transparent 60%);
                    filter: blur(4px);
                    pointer-events: none;
                }
                .name {
                    font-size: 20px;
                    margin-bottom: 8px;
                    color: #9fe6b8;
                    letter-spacing: 0.04em;
                    text-transform: uppercase;
                }
                .subtitle {
                    font-size: 14px;
                    max-width: 280px;
                    opacity: 0.85;
                    margin-bottom: 18px;
                }
                .bar-wrapper {
                    width: 240px;
                    height: 8px;
                    border-radius: 999px;
                    background: rgba(255,255,255,0.08);
                    overflow: hidden;
                    margin-bottom: 6px;
                }
                .bar-fill {
                    width: 30%; /* здесь будет "заряд" камня */
                    height: 100%;
                    background: linear-gradient(90deg, #3ceaaa, #9fe6b8);
                    box-shadow: 0 0 10px rgba(76, 237, 165, 0.8);
                }
                .bar-label {
                    font-size: 12px;
                    opacity: 0.8;
                }
            </style>
        </head>
        <body>
            <div class="gem-wrapper">
                <div class="gem-glow"></div>
                <div class="gem-shape"></div>
            </div>
            <div class="name">Хризолит</div>
            <div class="subtitle">
                Это ваш общий камень. Чем больше вы общаетесь, тем выше его качество и сила.
                В будущем здесь можно будет выбирать и другие камни.
            </div>

            <div class="bar-wrapper">
                <div class="bar-fill"></div>
            </div>
            <div class="bar-label">Заряд камня: 30%</div>
        </body>
    </html>
    """
