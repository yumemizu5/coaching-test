import streamlit as st
import openai
from gtts import gTTS
from io import BytesIO

# Assuming you have an mp3 file named "sample.mp3" in the same directory
audio_file_path = "sample.mp3"

# Open and play a static audio file to test
st.title("Test Static MP3 Playback")
st.write("Testing with a pre-existing MP3 file.")

try:
    # Reading the file as binary
    with open(audio_file_path, "rb") as audio_file:
        audio_bytes = audio_file.read()

    # Play the audio using Streamlit's audio player
    st.audio(audio_bytes, format="audio/mp3")

except FileNotFoundError:
    st.error("MP3 file not found. Please upload or provide the correct path.")


# # パスワードを設定
# correct_password = st.secrets.mieai_pw.correct_password

# # パスワードの入力フィールドを追加
# password = st.text_input("パスワードを入力してください", type="password")

# # パスワードが正しい場合の処理
# if password == correct_password:
#     openai.api_key = st.secrets.OpenAIAPI.openai_api_key

#     system_prompt = """
#     あなたは優秀な人の悩みを解決するコーチです。
#     悩みに対して質問を行ったりして深堀も行ってください。
#     様々な手法やアドバイスで相談者の悩みの解決方法を提案することができます。
#     あなたの役割はコーチングを行うことなので、例えば以下のような悩み以外ことを聞かれても、絶対に答えないでください。

#     * 芸能人
#     * 料理
#     * 科学
#     * 歴史
#     """

#     # st.session_stateを使いメッセージのやりとりを保存
#     if "messages" not in st.session_state:
#         st.session_state["messages"] = [
#             {"role": "system", "content": system_prompt}
#         ]

#     # チャットボットとやりとりする関数
#     def communicate():
#         messages = st.session_state["messages"]

#         user_message = {"role": "user", "content": st.session_state["user_input"]}
#         messages.append(user_message)

#         response = openai.ChatCompletion.create(
#             model="gpt-3.5-turbo",
#             messages=messages
#         )

#         bot_message = response["choices"][0]["message"]
#         messages.append(bot_message)

#         st.session_state["user_input"] = ""  # 入力欄を消去

#         # ボットの応答メッセージを音声に変換
#         tts = gTTS(bot_message["content"], lang='ja')  # 日本語対応
#         tts_file = BytesIO()
#         tts.save(tts_file)
#         tts_file.seek(0)

#         # 音声再生（フォーマットを指定）
#         st.audio(tts_file, format='audio/mp3')

#     # ユーザーインターフェイスの構築
#     st.title("「みえAi」コーチングボット")
#     st.image("mieai.png")
#     st.write("悩み事は何ですか？")

#     user_input = st.text_input("悩み事を下に入力してください。", key="user_input", on_change=communicate)

#     if st.session_state["messages"]:
#         messages = st.session_state["messages"]

#         for message in reversed(messages[1:]):  # 直近のメッセージを上に
#             speaker = "🙂"
#             if message["role"] == "assistant":
#                 speaker = "🤖"

#             st.write(speaker + ": " + message["content"])

# else:
#     # パスワードが間違っている場合のメッセージを表示
#     st.write("パスワードが正しくありません。アプリにアクセスするために正しいパスワードを入力してください。")
