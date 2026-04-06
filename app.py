import streamlit as st
import google.generativeai as genai

# ==========================================
# 🔑 請在下方引號內替換成您的 Gemini API Key 🔑
# ==========================================
GOOGLE_API_KEY = "AIzaSyCeMv9WbDJuLGvwfIJ9LiZ7UgjgHMEkIAk"

# 設定 API 金鑰
genai.configure(api_key=GOOGLE_API_KEY)

# 網頁基本設定
st.set_page_config(page_title="OPENBOOK 書評小程式", page_icon="📖", layout="wide")
st.title("📖 OPENBOOK 書評自動生成器")
st.markdown("請填寫書籍資訊並貼上參考內容，AI 將為您自動整合分析並產出百字書評。")

# === 自動抓取支援的模型清單 ===
try:
    available_models = []
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            clean_name = m.name.replace("models/", "")
            available_models.append(clean_name)
    if not available_models:
        st.error("您的 API Key 似乎沒有可用模型權限。")
except Exception as e:
    available_models = ["gemini-1.5-pro", "gemini-1.5-flash"]

# 0. 選擇 AI 模型
st.subheader("⚙️ AI 模型設定")
st.markdown("💡 **推薦選擇帶有 `pro` 字眼的模型**，能獲得更深度的思考與分析喔！")
selected_model = st.selectbox("請選擇模型：", available_models)
st.markdown("---")

# 1. 必填：主書籍資訊
st.subheader("📚 主書籍資訊")

# 使用 columns 讓欄位並排，版面更簡潔
col_info1, col_info2, col_info3 = st.columns(3)
with col_info1:
    book_title = st.text_input("書名 (必填)：", placeholder="例如：爧")
with col_info2:
    book_author = st.text_input("作者 (必填)：", placeholder="例如：張芳慈")
with col_info3:
    book_publisher = st.text_input("出版社：", placeholder="例如：鏡萬象")

book_content = st.text_area("書籍簡介 / 內容 (必填)：", height=150, placeholder="請貼上書籍的內容簡介或核心摘要...")

# 2. 選填：補充參考文章內容
st.subheader("📝 補充參考資料 (最多 3 篇)")
st.markdown("請將其他書評文章的**「內文重點」**直接複製貼上（若無可留白）：")

col_ref1, col_ref2, col_ref3 = st.columns(3)
with col_ref1:
    extra_1 = st.text_area("補充文章 1：", height=150, placeholder="貼上文章內容...")
with col_ref2:
    extra_2 = st.text_area("補充文章 2：", height=150, placeholder="貼上文章內容...")
with col_ref3:
    extra_3 = st.text_area("補充文章 3：", height=150, placeholder="貼上文章內容...")

# 執行按鈕
if st.button("🚀 開始分析與生成", type="primary", use_container_width=True):
    # 檢查必填欄位
    if not book_title.strip() or not book_author.strip() or not book_content.strip():
        st.error("請務必填寫「書名」、「作者」與「書籍簡介」！")
    else:
        with st.spinner(f"AI 正在使用 {selected_model} 進行深度分析，請稍候..."):
            try:
                # 收集所有填寫的補充內容
                all_extras = [extra_1, extra_2, extra_3]
                valid_extras = [text.strip() for text in all_extras if text.strip()]
                extra_text_str = "\n\n---\n\n".join(valid_extras) if valid_extras else "無"

                # 建立 AI Prompt (結構化資料)
                prompt = f"""
                你是一位專業的書籍評論家，特別擅長為台灣的 OPENBOOK 閱讀誌撰寫書評。
                請閱讀以下我提供的書籍資訊與文章內容，並執行分析與書評撰寫。所有輸出必須為「繁體中文」。

                【資料來源】
                [主書籍]
                書名: {book_title}
                作者: {book_author}
                出版社: {book_publisher if book_publisher.strip() else "未提供"}
                書籍簡介/內容:
                {book_content}

                [補充參考文章內容] (需整合這些內容的觀點):
                {extra_text_str}

                【任務要求】
                請提供以下兩個部分的輸出：

                ### 【輸出 1：整合深度分析】
                請綜合上述所有內容的洞察，分析以下五個面向：
                * **主題 (Theme)**:
                * **結構 (Structure)**:
                * **文學技巧 (Literary Techniques)**:
                * **亮點 (Highlights)**:
                * **閱讀樂趣 (Reading Pleasure)**:

                ### 【輸出 2：OPENBOOK 百字書評】
                根據上方的深度分析，撰寫一篇字數約在 100 字左右的精煉書評。請在書評的開頭自然地帶入書名與作者，要求文筆流暢、觀點精闢，能迅速勾起讀者的閱讀興趣。
                """

                model = genai.GenerativeModel(selected_model)
                response = model.generate_content(prompt)

                st.success("✅ 生成完成！")
                st.markdown("---")
                st.markdown(response.text)

            except Exception as e:
                st.error(f"發生錯誤：{e}")
