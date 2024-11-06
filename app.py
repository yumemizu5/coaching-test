import streamlit as st
import openai
from gtts import gTTS
from io import BytesIO
import base64
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase, WebRtcMode
import numpy as np
import av
import tempfile
from scipy.io.wavfile import write
from audio_recorder_streamlit import audio_recorder
from tempfile import NamedTemporaryFile

# パスワードを設定
correct_password = st.secrets.mieai_pw.correct_password

# パスワードの入力フィールドを追加
password = st.text_input("パスワードを入力してください", type="password")

# パスワードが正しい場合の処理
if password == correct_password:

    openai.api_key = st.secrets.OpenAIAPI.openai_api_key

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
        # 初回のボットメッセージを追加
        st.session_state["messages"].append(
            {"role": "assistant", "content": "こんにちは、コーチのAIです。お話を始めましょう。"}
        )

    # 音声データを蓄積するバッファを初期化
    if 'audio_buffer' not in st.session_state:
        st.session_state['audio_buffer'] = []

    class AudioProcessor(AudioProcessorBase):
        def __init__(self) -> None:
            super().__init__()
            st.write("AudioProcessor initialized")
    
        def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
            st.write("Received audio frame")
            audio = frame.to_ndarray().flatten()
            st.write(f"Audio frame length: {len(audio)}")
        # def __init__(self) -> None:
        #     super().__init__()
        #     st.write("AudioProcessor initialized")

        # def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
        #     st.write("Received audio frame")
        #     audio = frame.to_ndarray().flatten()
        #     st.session_state['audio_buffer'].extend(audio.tolist())
        #     st.write(f"Audio buffer length: {len(st.session_state['audio_buffer'])}")

            # 3秒分の音声データがたまったら処理する
            if len(st.session_state['audio_buffer']) >= 16000 * 3:
                audio_data = np.array(st.session_state['audio_buffer'], dtype=np.float32)
                st.session_state['audio_buffer'] = []  # バッファをリセット

                # 一時ファイルに音声データを保存
                with tempfile.NamedTemporaryFile(suffix=".wav") as tmp_file:
                    write(tmp_file.name, 16000, audio_data)
                    tmp_file.flush()

                    # Whisper API を使用して音声認識
                    audio_file = open(tmp_file.name, "rb")
                    try:
                        transcript = openai.Audio.transcribe("whisper-1", audio_file, language="ja")
                        text = transcript["text"]
                        st.session_state["user_input"] = text
                        st.write(f"認識されたテキスト: {text}")
                        communicate()
                    except Exception as e:
                        st.write(f"音声認識中にエラーが発生しました: {e}")

            return frame  # フレームをそのまま返す



    
    def transcribe_audio_to_text(audio_bytes):
        #openai.api_key = st.secrets.OpenAIAPI.openai_api_key
        with NamedTemporaryFile(delete=True, suffix=".wav") as temp_file:
            temp_file.write(audio_bytes)
            temp_file.flush()
            with open(temp_file.name, "rb") as audio_file:
                response = openai.Audio.transcribe("whisper-1", audio_file, language="ja", temperature=0, top_p=0.1)
        return response["text"]



    

    # チャットボットとやりとりする関数
    def communicate():
        messages = st.session_state["messages"]

        user_input = st.session_state.get("user_input", "")
        if user_input:
            user_message = {"role": "user", "content": user_input}
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
        st.write("### チャット履歴")
        for message in reversed(messages[1:]):  # 直近のメッセージを上に
            speaker = "🙂"
            if message["role"] == "assistant":
                speaker = "🤖"

            st.write(speaker + ": " + message["content"])

    # ユーザーインターフェイスの構築
    st.title("「みえAi」コーチングボット")
    st.image("mieai.png")
    st.write("マイクでお話しください。")

    # Record audio using Streamlit widget
    audio_bytes = audio_recorder(pause_threshold=30)
    
    # Convert audio to text using OpenAI Whisper API
    if audio_bytes:
        transcript = transcribe_audio_to_text(audio_bytes)
        st.write("Transcribed Text:", transcript)

        # 変換されたテキストをセッションステートに保存
        st.session_state["user_input"] = transcript
        
        # チャットボットとやりとり
        communicate()

    
    # 初回のボットメッセージを表示
    if "init" not in st.session_state:
        communicate()
        st.session_state["init"] = True

else:
    # パスワードが間違っている場合のメッセージを表示
    st.write("パスワードが正しくありません。アプリにアクセスするために正しいパスワードを入力してください。")
