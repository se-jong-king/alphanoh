import streamlit as st
from streamlit.runtime.caching.hashing import HashFuncsDict

import parsing as pars
import chunking as chunk
import embedding as embed
from parsing import File


def file_hash_func(file: File) -> str:
    """Get a unique hash for a file"""
    return file.id


@st.cache_data(show_spinner=False)
def bootstrap_caching():
    """Patch module functions with caching"""

    # Get all substypes of File from module
    file_subtypes = [
        cls
        for cls in vars(pars).values()
        if isinstance(cls, type) and issubclass(cls, File) and cls != File
    ]
    file_hash_funcs: HashFuncsDict = {cls: file_hash_func for cls in file_subtypes}

    pars.read_file = st.cache_data(show_spinner=False)(pars.read_file)
    chunk.chunk_file = st.cache_data(show_spinner=False, hash_funcs=file_hash_funcs)(
        chunk.chunk_file
    )
    embed.embed_files = st.cache_data(
        show_spinner=False, hash_funcs=file_hash_funcs
    )(embed.embed_files)