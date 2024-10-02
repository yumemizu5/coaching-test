import streamlit as st
import openai
from gtts import gTTS
from io import BytesIO

# OpenAI APIキーを設定
openai.api_key = 'YOUR_OPENAI_API_KEY'  # ご自身のAPIキーに置き換えてください

# システムプロンプトの定義
system_prompt = "あなたは優秀なコーチングボットです。"

# メッセージのやりとりを保存
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "system", "content": system_prompt}
    ]

# チャットボットとやりとりする関数
def communicate():
    messages = st.session_state["messages"]
    
    user_message = {"role": "user", "content": st.session_state["user_input"]}
    messages.append(user_message)
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )

    bot_message = response["choices"][0]["message"]
    messages.append(bot_message)
    
    st.session_state["user_input"] = ""  # 入力欄を消去

    # ボットの応答メッセージを音声に変換
    tts = gTTS(bot_message["content"], lang='ja')  # 日本語対応
    tts_file = BytesIO()
    tts.write_to_fp(tts_file)  # 修正箇所: save()からwrite_to_fp()に変更
    tts_file.seek(0)
    
    # 音声再生（フォーマットを指定）
    st.audio(tts_file, format='audio/mp3')

# ユーザーインターフェイスの構築
st.title("「みえAi」コーチングボット")
st.image("mieai.png")
st.write("悩み事は何ですか？")

user_input = st.text_input("悩み事を下に入力してください。", key="user_input", on_change=communicate)

if st.session_state["messages"]:
    messages = st.session_state["messages"]

    for message in reversed(messages[1:]):  # 直近のメッセージを上に
        speaker = "🙂"
        if message["role"] == "assistant":
            speaker = "🤖"
        
        st.write(speaker + ": " + message["content"])

# パスワードチェックがないため、以下の部分はコメントアウトまたは削除
# else:
#     # パスワードが間違っている場合のメッセージを表示
#     st.write("パスワードが正しくありません。アプリにアクセスするために正しいパスワードを入力してください。")
