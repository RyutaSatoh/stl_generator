import streamlit as st
import os
from generator import generate_scad
from renderer import render_scad

st.set_page_config(page_title="Text-to-STL Generator", layout="wide")

st.title("🛠️ Text-to-STL Generator")
st.markdown("Enter a description of the 3D object you want to create.")

# 出力ディレクトリの作成
OUTPUT_DIR = "output"
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

SCAD_PATH = os.path.join(OUTPUT_DIR, "model.scad")
PNG_PATH = os.path.join(OUTPUT_DIR, "preview.png")
STL_PATH = os.path.join(OUTPUT_DIR, "output.stl")

# サイドバーまたはメインエリアにプロンプト入力
prompt = st.text_area("What would you like to build?", placeholder="A simple coffee mug with a handle", height=150)

if st.button("Generate 🚀"):
    if prompt:
        with st.spinner("Asking Gemini to design..."):
            code, err = generate_scad(prompt)
            
            if err:
                st.error(err)
            else:
                # SCADコードを保存
                with open(SCAD_PATH, "w") as f:
                    f.write(code)
                
                st.success("Code generated!")
                
                # Check if Agent produced the files
                agent_success = os.path.exists(PNG_PATH) and os.path.exists(STL_PATH)
                
                if agent_success:
                     st.info("Using Agent-generated models.")
                else:
                    with st.spinner("Rendering 3D model (fallback)..."):
                        success, render_err = render_scad(SCAD_PATH, PNG_PATH, STL_PATH)
                        if not success:
                            st.error(render_err)
                            agent_success = False
                        else:
                            agent_success = True
                
                if agent_success:
                        st.balloons()
                        
                        col1, col2 = st.columns([1, 1])
                        
                        with col1:
                            st.subheader("Preview")
                            if os.path.exists(PNG_PATH):
                                st.image(PNG_PATH, width="stretch")
                        
                        with col2:
                            st.subheader("Generated Code")
                            st.code(code, language="cpp")
                            
                            st.subheader("Downloads")
                            if os.path.exists(STL_PATH):
                                with open(STL_PATH, "rb") as f:
                                    st.download_button(
                                        label="Download STL",
                                        data=f,
                                        file_name="output.stl",
                                        mime="application/sla"
                                    )
                            
                            with open(SCAD_PATH, "rb") as f:
                                st.download_button(
                                    label="Download SCAD",
                                    data=f,
                                    file_name="model.scad",
                                    mime="text/plain"
                                )
                else:
                    st.error("Failed to generate or render model.")
    else:
        st.warning("Please enter a prompt.")

st.markdown("---")
st.caption("Powered by Gemini CLI and OpenSCAD")
