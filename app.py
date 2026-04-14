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
                    font-family: sans-serif;
                    background: #050811;
                    color: #f5f5f5;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    height: 100vh;
                    margin: 0;
                    text-align: center;
                }
                .gem {
                    font-size: 64px;
                    margin-bottom: 12px;
                }
                .name {
                    font-size: 20px;
                    margin-bottom: 8px;
                    color: #9fe6b8;
                }
                .subtitle {
                    font-size: 14px;
                    max-width: 280px;
                    opacity: 0.85;
                }
            </style>
        </head>
        <body>
            <div class="gem">💎</div>
            <div class="name">Хризолит</div>
            <div class="subtitle">
                Это ваш общий камень. Чем больше вы общаетесь, тем сильнее он становится.
                В будущем здесь можно будет выбрать и другие камни.
            </div>
        </body>
    </html>
    """
