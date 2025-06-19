import streamlit as st
import pandas as pd
import os
from datetime import date
from streamlit.runtime.scriptrunner import RerunException


LOG_FILE = "data/logs.csv"
st.set_page_config(layout="wide",
                   page_title="myLog",
                   page_icon="🌓")

st.markdown("<h1 style='text-align:center;'>🌓 myLog</h1>",
            unsafe_allow_html=True)
st.write("---")

# これを app.py の冒頭部分（たとえば st.set_page_config(...) の直後）に追加：
save_from_sidebar = False

# -------------- ① サイドバー：入力／編集パネル -----------------
with st.sidebar:
    mode = st.radio("モードを選択", ["新規入力", "過去ログ編集"])

    # CSV があればロード
    if os.path.exists(LOG_FILE):
        df = pd.read_csv(LOG_FILE)
    else:
        df = pd.DataFrame()

    # === 新規入力 ===
    if mode == "新規入力":
        selected_date = st.date_input("📅 日付", value=date.today())
        mood_score = st.slider("😄 気分スコア（0〜5）", 0, 5, 3)

    # === 過去ログ編集 ===
    else:
        if df.empty:
            st.warning("まだログがありません。")
            st.stop()

        date_options = df["日付"].unique()[::-1]  # 新しい順
        selected_date = st.selectbox("✏️ 編集する日付を選択", date_options)
        row = df[df["日付"] == selected_date].iloc[0]

        # 既存値で初期化
        mood_score = st.slider("😄 気分スコア（0〜5）",
                               0, 5, int(row["気分スコア"]))
        
        save_from_sidebar = st.button("💾 保存", key="save_sidebar")


        
# -------------- ② メインエリア：本文記入 -----------------
st.markdown("#### ✅ 今日やったこと")
summary = st.text_area("・やったこと（例：読書、筋トレなど）",
                       height=300,
                       value=row["やったこと"] if mode == "過去ログ編集" else "")

details = st.text_area("・詳細（例：学習内容、運動メニューなど）",
                       height=300,
                       value=row["詳細"] if mode == "過去ログ編集" else "")

tomorrow = st.text_area("・明日やること",
                        height=100,
                        value=row["明日やること"] if mode == "過去ログ編集" else "")

journal = st.text_area("・気付き・感想・内省など",
                       height=100,
                       value=row["日記"] if mode == "過去ログ編集" else "")

st.markdown("#### 🤖 AIフィードバック（任意）")
feedback = st.text_area("AIからのコメント",
                        height=100,
                        value=row["AIフィードバック"] if mode == "過去ログ編集" else "")



# -------------- ③ 保存処理 -----------------
if st.button("💾 保存する", use_container_width=True)or save_from_sidebar:
    new_row = pd.DataFrame([{
        "日付": str(selected_date),
        "気分スコア": mood_score,
        "やったこと": summary,
        "詳細": details,
        "明日やること": tomorrow,
        "日記": journal,
        "AIフィードバック": feedback
    }])

    if df.empty:
        df = new_row
    else:
        # 同日があれば削除（＝上書き）、なければそのまま追記
        df = df[df["日付"] != str(selected_date)]
        df = pd.concat([df, new_row], ignore_index=True)

    df.to_csv(LOG_FILE, index=False)
    st.success("✅ 保存しました！")

# -------------- ④ ログ表示（折りたたみ） -----------------
# ========== ④ ログ表示（操作ボタン付き） ==========
st.write("---")
if not df.empty:
    with st.expander("📘 ログ一覧（編集・削除）", expanded=False):
        df_sorted = df.sort_values("日付", ascending=False).reset_index(drop=True)

        for i, row in df_sorted.iterrows():
            st.markdown("---")
            cols = st.columns([2, 6, 2])

            # 日付と気分
            with cols[0]:
                st.write(f"📅 **{row['日付']}**")
                st.write(f"気分スコア: {row['気分スコア']}")

            # 概要
            with cols[1]:
                st.markdown(f"""
                <div style='padding:10px; border:1px solid #444; border-radius:10px; background-color:#1f1f1f'>
                <b>やったこと:</b><br>{str(row['やったこと']).replace(chr(10), '<br>')}<br><br>
                <b>詳細:</b><br>{str(row['詳細']).replace(chr(10), '<br>')}<br><br>
                <b>内省:</b><br>{str(row['日記']).replace(chr(10), '<br>')}
                </div>
                """, unsafe_allow_html=True)

            # 削除ボタン
            with cols[2]:
                edit_key = f"edit_{i}"
                delete_key = f"delete_{i}"

                if st.button("🗑 削除", key=delete_key):
                    df = df[df["日付"] != row["日付"]]
                    df.to_csv(LOG_FILE, index=False)
                    st.success(f"🗑 {row['日付']} のログを削除しました")
                    # st.rerun() => 

