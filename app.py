import streamlit as st
import google.generativeai as genai

# ==========================================
# 🔑 請在下方引號內替換成您的 Gemini API Key 🔑
# ==========================================
GOOGLE_API_KEY = "AIzaSyCeMv9WbDJuLGvwfIJ9LiZ7UgjgHMEkIAk"

# 設定 API 金鑰
genai.configure(api_key=GOOGLE_API_KEY)

# 網頁基本設定
st.set_page_config(page_title="OPENBOOK 書評小程式", page_icon="📖")
st.title("📖 OPENBOOK 書評自動生成器")
st.markdown("輸入書籍與參考資料網址，AI 將為您自動整合分析並產出百字書評。")

# 1. 必填：主書籍網址
st.subheader("📚 主書籍")
book_url = st.text_input("主書籍網址 (必填)：", placeholder="請貼上書籍的網頁連結")

# 2. 選填：補充參考網址 (分成 5 格)
st.subheader("🔗 補充參考資料 (最多 5 個)")
st.markdown("請在下方格子分別貼上參考文章或書評的網址（若無可留白）：")

url_1 = st.text_input("補充網址 1：", placeholder="https://...")
url_2 = st.text_input("補充網址 2：", placeholder="https://...")
url_3 = st.text_input("補充網址 3：", placeholder="https://...")
url_4 = st.text_input("補充網址 4：", placeholder="https://...")
url_5 = st.text_input("補充網址 5：", placeholder="https://...")

# 執行按鈕
if st.button("🚀 開始分析與生成", type="primary"):
    if not book_url:
        st.error("請務必輸入「主書籍網址」！")
    else:
        with st.spinner("AI 正在讀取網址並進行深度分析，請稍候..."):
            try:
                # 收集所有填寫的補充網址
                all_extra_urls = [url_1, url_2, url_3, url_4, url_5]
                # 過濾掉空白的格子
                valid_extra_urls = [url.strip() for url in all_extra_urls if url.strip()]
                extra_urls_str = "\n".join(valid_extra_urls) if valid_extra_urls else "無"

                # 建立 AI Prompt
                prompt = f"""
                你是一位專業的書籍評論家，特別擅長為台灣的 OPENBOOK 閱讀誌撰寫書評。
                請閱讀以下網址的內容，並執行分析與書評撰寫。所有輸出必須為「繁體中文」。

                【資料來源】
                主書籍網址: {book_url}
                補充參考網址 (需整合這些網址的觀點):
                {extra_urls_str}

                【任務要求】
                請提供以下兩個部分的輸出：

                ### 【輸出 1：整合深度分析】
                請綜合主書籍與補充網址的洞察，分析以下五個面向：
                * **主題 (Theme)**:
                * **結構 (Structure)**:
                * **文學技巧 (Literary Techniques)**:
                * **亮點 (Highlights)**:
                * **閱讀樂趣 (Reading Pleasure)**:

                ### 【輸出 2：OPENBOOK 百字書評】
                根據上方的深度分析，撰寫一篇字數約在 100 字左右的精煉書評。要求文筆流暢、觀點精闢，能迅速勾起讀者的閱讀興趣。
                """

                # 呼叫模型
                model = genai.GenerativeModel('gemini-1.5-pro')
                response = model.generate_content(prompt)

                # 顯示結果
                st.success("✅ 生成完成！")
                st.markdown("---")
                st.markdown(response.text)

            except Exception as e:
                st.error(f"發生錯誤：{e}")
