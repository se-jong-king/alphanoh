import streamlit as st

from alphanoh.components.sidebar import sidebar

from alphanoh.ui import (
    wrap_doc_in_html,
    is_query_valid,
    is_file_valid,
    is_open_ai_key_valid,
    display_file_read_error,
)

from alphanoh.core.caching import bootstrap_caching

from alphanoh.core.parsing import read_file
from alphanoh.core.chunking import chunk_file
from alphanoh.core.embedding import embed_files
from alphanoh.core.qa import query_folder
from alphanoh.core.utils import get_llm


EMBEDDING = "openai"
VECTOR_STORE = "faiss"
MODEL_LIST = ["gpt-3.5-turbo", "gpt-4"]

# Uncomment to enable debug mode
# MODEL_LIST.insert(0, "debug")

st.set_page_config(page_title="AlphaNoh", page_icon="?", layout="wide")
st.header("AlphaNoh")

# Enable caching for expensive functions
bootstrap_caching()

sidebar()

openai_api_key = st.session_state.get("OPENAI_API_KEY")


if not openai_api_key:
    st.warning(
        "OpenAI API key를 좌측 사이드바에 입력하세요. API key를 다음 링크를 통해 얻을 수 있습니다."
        " https://platform.openai.com/account/api-keys."
    )


uploaded_file = st.file_uploader(
    "pdf, docx, or txt file을 업로드하세요.",
    type=["pdf", "docx", "txt"],
    help="지원이 되지 않는 파일 형식입니다.!",
)

model: str = st.selectbox("Model", options=MODEL_LIST)  # type: ignore

with st.expander("고급 옵션"):
    return_all_chunks = st.checkbox("벡터 검색에서 검색된 모든 청크 표시")
    show_full_doc = st.checkbox("구문 분석된 문서 내용 표시")


if not uploaded_file:
    st.stop()

try:
    file = read_file(uploaded_file)
except Exception as e:
    display_file_read_error(e, file_name=uploaded_file.name)

chunked_file = chunk_file(file, chunk_size=300, chunk_overlap=0)

if not is_file_valid(file):
    st.stop()


if not is_open_ai_key_valid(openai_api_key, model):
    st.stop()


with st.spinner("문서를 인덱싱중입니다. 잠시만 기다려주세요.?"):
    folder_index = embed_files(
        files=[chunked_file],
        embedding=EMBEDDING if model != "debug" else "debug",
        vector_store=VECTOR_STORE if model != "debug" else "debug",
        openai_api_key=openai_api_key,
    )

with st.form(key="qa_form"):
    query = st.text_area("문서에 관한 질문을 해주세요.")
    submit = st.form_submit_button("입력")


if show_full_doc:
    with st.expander("Document"):
        # Hack to get around st.markdown rendering LaTeX
        st.markdown(f"<p>{wrap_doc_in_html(file.docs)}</p>", unsafe_allow_html=True)


if submit:
    if not is_query_valid(query):
        st.stop()

    # Output Columns
    answer_col, sources_col = st.columns(2)

    llm = get_llm(model=model, openai_api_key=openai_api_key, temperature=0)
    result = query_folder(
        folder_index=folder_index,
        query=query,
        return_all=return_all_chunks,
        llm=llm,
    )

    with answer_col:
        st.markdown("#### Answer")
        st.markdown(result.answer)

    with sources_col:
        st.markdown("#### Sources")
        for source in result.sources:
            st.markdown(source.page_content)
            st.markdown(source.metadata["source"])
            st.markdown("---")