import streamlit as st
import openai
from gtts import gTTS
from io import BytesIO
import base64
import speech_recognition as sr

# パスワードを設定
correct_password = st.secrets.mieai_pw.correct_password

# パスワードの入力フィールドを追加
password = st.text_input("パスワードを入力してください", type="password")

# パスワードが正しい場合の処理
if password == correct_password:

    openai.api_key = st.secrets.OpenAIAPI.openai_api_key

    system_prompt = """
    あなたは優秀な人の悩みを解決するコーチです。
    悩みに対して質問を行ったりして深堀も行ってください。
    様々な手法やアドバイスで相談者の悩みの解決方法を提案することができます。
    あなたの役割はコーチングを行うことなので、例えば以下のような悩み以外ことを聞かれても、絶対に答えないでください。

    * 芸能人
    * 料理
    * 科学
    * 歴史
    """

    # st.session_stateを使いメッセージのやりとりを保存
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
        tts.write_to_fp(tts_file)
        tts_file.seek(0)

        # 音声データをbase64にエンコード
        audio_bytes = tts_file.read()
        audio_base64 = base64.b64encode(audio_bytes).decode()

        # カスタムHTMLを使用して自動再生
        audio_html = f"""
            <audio autoplay>
                <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
            </audio>
        """
        st.components.v1.html(audio_html, height=0)

        # チャット履歴を表示
        for message in reversed(messages[1:]):  # 直近のメッセージを上に
            speaker = "🙂"
            if message["role"] == "assistant":
                speaker = "🤖"

            st.write(speaker + ": " + message["content"])
        
    # 音声入力を処理する関数
    def recognize_speech():
        recognizer = sr.Recognizer()
        mic = sr.Microphone()
    
        with mic as source:
            st.write("音声入力中... 何か話してください。")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)
    
        try:
            st.session_state["user_input"] = recognizer.recognize_google(audio, language="ja-JP")
            st.write(f"音声入力: {st.session_state['user_input']}")
            communicate()  # 音声入力後にチャットを実行
        except sr.UnknownValueError:
            st.write("音声を認識できませんでした。もう一度お試しください。")
        except sr.RequestError:
            st.write("音声認識サービスにアクセスできませんでした。")

    # ユーザーインターフェイスの構築
    st.title("「みえAi」コーチングボット")
    st.image("mieai.png")
    st.write("悩み事は何ですか？")

    st.button("音声入力開始", on_click=recognize_speech)

    user_input = st.text_input("悩み事を下に入力してください。", key="user_input", on_change=communicate)

else:
    # パスワードが間違っている場合のメッセージを表示
    st.write("パスワードが正しくありません。アプリにアクセスするために正しいパスワードを入力してください。")
