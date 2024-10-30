import streamlit as st
import openai
from gtts import gTTS
from io import BytesIO
import base64
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase, WebRtcMode
import numpy as np
import speech_recognition as sr
import av

# パスワードを設定
correct_password = st.secrets.mieai_pw.correct_password

# パスワードの入力フィールドを追加
password = st.text_input("パスワードを入力してください", type="password")

# パスワードが正しい場合の処理
if password == correct_password:

    openai.api_key = st.secrets.OpenAIAPI.openai_api_key

    # あなたは優秀な人の悩みを解決するコーチです。
    # 悩みに対して質問を行ったりして深堀も行ってください。
    # 様々な手法やアドバイスで相談者の悩みの解決方法を提案することができます。
    # あなたの役割はコーチングを行うことなので、例えば以下のような悩み以外ことを聞かれても、絶対に答えないでください。
    # * 芸能人
    # * 料理
    # * 科学
    # * 歴史
    
    system_prompt = """
    あなたは優秀な人の悩みを解決するコーチです。
    これから各順番に質問を行ってください。
    回答に対して一つ共感や意見を言いながら進行してください。

    1.性別を聞いてください
    2.出身地を聞いてください。
    3.好きな食べ物を聞いてください
    4.好きな動物は犬ですか？猫ですか？

    """

    # st.session_stateを使いメッセージのやりとりを保存
    if "messages" not in st.session_state:
        st.session_state["messages"] = [
            {"role": "system", "content": system_prompt}
        ]

    # 音声データを蓄積するバッファを初期化
    if 'audio_buffer' not in st.session_state:
        st.session_state['audio_buffer'] = []

    class AudioProcessor(AudioProcessorBase):
        def __init__(self) -> None:
            super().__init__()
            self.recognizer = sr.Recognizer()

        def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
            audio = frame.to_ndarray().flatten()
            st.session_state['audio_buffer'].extend(audio.tolist())

            # 5秒分の音声データがたまったら処理する
            if len(st.session_state['audio_buffer']) >= 16000 * 5:
                audio_data = np.array(st.session_state['audio_buffer'], dtype=np.float32)
                audio_data_int16 = np.int16(audio_data * 32767).tobytes()
                audio_sr = sr.AudioData(audio_data_int16, 16000, 2)

                try:
                    text = self.recognizer.recognize_google(audio_sr, language="ja-JP")
                    st.session_state["user_input"] = text
                    communicate()
                    st.session_state['audio_buffer'] = []  # バッファをリセット
                except sr.UnknownValueError:
                    st.write("音声を認識できませんでした。")
                    st.session_state['audio_buffer'] = []
                except sr.RequestError as e:
                    st.write(f"音声認識サービスにエラーが発生しました: {e}")
                    st.session_state['audio_buffer'] = []

            return frame  # フレームをそのまま返す

    # チャットボットとやりとりする関数
    def communicate():
        messages = st.session_state["messages"]

        user_message = {"role": "user", "content": st.session_state["user_input"]}
        messages.append(user_message)

        response = openai.ChatCompletion.create(
            model="gpt-4",
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

    # ユーザーインターフェイスの構築
    st.title("「みえAi」コーチングボット")
    st.image("mieai.png")
    st.write("悩み事は何ですか？")

    user_input = st.text_input("悩み事を下に入力してください。", key="user_input", on_change=communicate)

else:
    # パスワードが間違っている場合のメッセージを表示
    st.write("パスワードが正しくありません。アプリにアクセスするために正しいパスワードを入力してください。")
