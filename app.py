import streamlit as st
import google.generativeai as genai

# ==========================================
# 🔐 安全升級：從 Streamlit Secrets 讀取金鑰 🔐
# ==========================================
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=GOOGLE_API_KEY)
except Exception as e:
    st.error("❌ 找不到 API 金鑰設定，請確認 Streamlit Secrets 已正確配置。")
    st.stop()

# 網頁基本設定
st.set_page_config(page_title="OPENBOOK 書評小程式", page_icon="📖", layout="wide")
st.title("📖 OPENBOOK 書評自動生成器 (專業分享版)")
st.markdown("請填寫書籍資訊並勾選需要的分析項目，AI 將為您自動整合分析並產出百字書評。")

# 0. 選擇 AI 模型
st.subheader("⚙️ AI 模型設定")
st.markdown("💡 **推薦選擇 `gemini-1.5-pro-latest`**。如果再次遇到 404 錯誤，請選擇最下方的安全牌 `gemini-pro`！")

# 放棄自動抓取，改用最穩定的手動清單 (加上了 latest 後綴)
stable_models = [
    "gemini-1.5-pro-latest",
    "gemini-1.5-flash-latest",
    "gemini-pro" # 這是 1.0 版，最老但也最不容易報錯的終極備案
]
selected_model = st.selectbox("請選擇模型：", stable_models)
st.markdown("---")

# 1. 必填：主書籍資訊
st.subheader("📚 1. 主書籍資訊")
col_info1, col_info2, col_info3 = st.columns(3)
with col_info1:
    book_title = st.text_input("書名 (必填)：", placeholder="例如：爧")
with col_info2:
    book_author = st.text_input("作者 (必填)：", placeholder="例如：張芳慈")
with col_info3:
    book_publisher = st.text_input("出版社：", placeholder="例如：鏡萬象")

book_content = st.text_area("書籍簡介 / 內容 (必填)：", height=150, placeholder="請貼上書籍的內容簡介或核心摘要...")

# 2. 選填：補充參考文章內容
st.subheader("📝 2. 補充參考資料 (最多 3 篇)")
st.markdown("請將其他書評文章的**「內文重點」**直接複製貼上（若無可留白）：")
col_ref1, col_ref2, col_ref3 = st.columns(3)
with col_ref1:
    extra_1 = st.text_area("補充文章 1：", height=150, placeholder="貼上文章內容...")
with col_ref2:
    extra_2 = st.text_area("補充文章 2：", height=150, placeholder="貼上文章內容...")
with col_ref3:
    extra_3 = st.text_area("補充文章 3：", height=150, placeholder="貼上文章內容...")

# 3. 分析項目設定 (動態勾選)
st.subheader("🔍 3. 勾選額外分析項目")
st.markdown("基本必備項目：**主題、結構、優點、閱讀樂趣** (將自動包含)。")

col_chk1, col_chk2, col_chk3, col_chk4, col_chk5 = st.columns(5)
with col_chk1:
    check_content = st.checkbox("內容 (Content)")
with col_chk2:
    check_literary = st.checkbox("文學手法 (Literary)")
with col_chk3:
    check_arguments = st.checkbox("論點 (Arguments)")
with col_chk4:
    check_social = st.checkbox("社會意義 (Social)")
with col_chk5:
    check_visual = st.checkbox("圖像技巧 (Visual)")

# 執行按鈕
if st.button("🚀 開始分析與生成", type="primary", use_container_width=True):
    if not book_title.strip() or not book_author.strip() or not book_content.strip():
        st.error("請務必填寫「書名」、「作者」與「書籍簡介」！")
    else:
        with st.spinner(f"AI 正在使用 {selected_model} 進行深度分析，請稍候..."):
            try:
                all_extras = [extra_1, extra_2, extra_3]
                valid_extras = [text.strip() for text in all_extras if text.strip()]
                extra_text_str = "\n\n---\n\n".join(valid_extras) if valid_extras else "無"

                analysis_items = [
                    "* **主題 (Theme)**: 探討的核心議題與深層思想。",
                    "* **結構 (Structure)**: 敘事編排、章節安排與節奏。",
                    "* **優點與亮點 (Strengths & Highlights)**: 最引人入勝的情節或獨特見解。",
                    "* **閱讀樂趣 (Reading Pleasure)**: 帶給讀者的情感共鳴或智性啟發。"
                ]
                
                if check_content: analysis_items.insert(0, "* **內容 (Content)**: 簡述本書的核心情節或重點涵蓋範圍。")
                if check_literary: analysis_items.append("* **文學手法 (Literary Techniques)**: 筆法、修辭、象徵或獨特文風。")
                if check_arguments: analysis_items.append("* **論點 (Arguments)**: 作者提出的主要觀點或主張。")
                if check_social: analysis_items.append("* **社會意義 (Social Significance)**: 本書對當代社會、文化或讀者價值觀的啟發與影響。")
                if check_visual: analysis_items.append("* **圖像技巧 (Visual Techniques)**: 插畫風格、媒材運用、圖文搭配與視覺敘事表現。")

                analysis_items_str = "\n                ".join(analysis_items)
                
                prompt = f"""
                你是一位專業的書籍評論家，特別擅長為台灣的 OPENBOOK 閱讀誌撰寫書評。所有輸出必須為「繁體中文」。
                [主書籍] 書名: {book_title} / 作者: {book_author} / 出版社: {book_publisher}
                內容: {book_content}
                [補充參考] {extra_text_str}
                [任務要求]
                1. 輸出 1：針對以下面向進行深度整合分析：
                {analysis_items_str}
                2. 輸出 2：撰寫約 100 字精煉書評，開頭自然帶入書名作者。
                """

                model = genai.GenerativeModel(selected_model)
                response = model.generate_content(prompt)
                st.success("✅ 生成完成！")
                st.markdown("---")
                st.markdown(response.text)
            except Exception as e:
                st.error(f"發生錯誤：{e}")
