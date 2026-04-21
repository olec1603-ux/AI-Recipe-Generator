import streamlit as st
import pandas as pd
import os
import plotly.express as px
from agent_engine import generate_recipe_and_nutrition, generate_health_reflection, init_storage

st.set_page_config(page_title="Pro AI Diet Agent", layout="wide", page_icon="🧪")
init_storage()

# 侧边栏
with st.sidebar:
    st.title("🛡️ Health Control")
    goal = st.selectbox("Goal", ["Muscle Gain", "Weight Loss", "Balanced Diet", "Recovery"])
    restriction = st.selectbox("Restriction", ["None", "Keto", "Vegan", "Gluten-Free"])
    
st.title("🧪 Next-Gen AI Recipe & Health Agent")

tab1, tab2, tab3 = st.tabs(["👨‍🍳 Kitchen", "📊 Nutrition", "🧠 AI Reflection"])

with tab1:
    col1, col2 = st.columns([1, 1.2])
    with col1:
        ingredients = st.text_area("Input Ingredients:", placeholder="e.g. Eggs, Salmon...", height=150)
        if st.button("Generate Pro Recipe", use_container_width=True):
            with st.spinner("Processing..."):
                st.session_state.data, st.session_state.audio = generate_recipe_and_nutrition(ingredients, restriction, goal)

    with col2:
        if 'data' in st.session_state and "error" not in st.session_state.data:
            res = st.session_state.data
            st.success(f"### **{res['recipe_name']}**")
            # 增加 Markdown 渲染确保排版规整
            with st.expander("📖 Cooking Instructions", expanded=True):
                st.markdown(res['steps'])
            with st.expander("🔄 Smart Substitutions"):
                st.markdown(res.get('substitutions', "N/A"))
            with st.expander("🛒 Grocery Checklist"):
                for item in res.get('grocery_list', []):
                    st.checkbox(item, key=f"item_{item}")
            if st.session_state.audio: st.audio(st.session_state.audio)

with tab2:
    if 'data' in st.session_state and "error" not in st.session_state.data:
        m = st.session_state.data['macros']
        st.plotly_chart(px.pie(names=["Protein", "Carbs", "Fat"], values=[m['protein'], m['carbs'], m['fat']], title="Macro Ratio"), use_container_width=True)

with tab3:
    st.subheader("🤖 AI Health Audit (Agent Reflection)")
    # 纯英文描述
    st.write("This feature leverages AI to reflect on your long-term dietary history and provides professional health insights.")
    
    if st.button("Run AI Health Audit", use_container_width=True):
        with st.spinner("Analyzing..."):
            st.markdown(f"--- \n {generate_health_reflection()}")
            
    if os.path.exists("recipe_history.csv"):
        hist_df = pd.read_csv("recipe_history.csv")
        if not hist_df.empty:
            st.write("### **Calorie Intake Trend**")
            # 核心修复点：将 Date 转为字符串，强制 Plotly 视其为分类标签而非连续时间
            hist_df['Date_Str'] = hist_df['Date'].astype(str)
            
            line_fig = px.line(hist_df, x="Date_Str", y="Calories", markers=True)
            
            # 优化 X 轴：强制水平显示，且不进行时间轴合并
            line_fig.update_xaxes(
                type='category',   # 关键：设置为分类轴，这样每一个日期都会显示
                tickangle=0,       # 水平显示
                title_text="Entry Time (MM/DD HH:MM)"
            )
            line_fig.update_layout(hovermode="x unified", template="plotly_white")
            st.plotly_chart(line_fig, use_container_width=True)