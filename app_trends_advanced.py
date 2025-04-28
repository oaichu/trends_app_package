import streamlit as st
import pandas as pd
from pytrends.request import TrendReq
import plotly.express as px

pytrends = TrendReq(hl='vi', tz=420)

st.title("📈 App Thống Kê So Sánh Từ Khóa - Google Trends")

mode = st.sidebar.radio(
    "Chọn chế độ:",
    ("Tìm kiếm từ khóa tự chọn", "Xem từ khóa hot hôm nay theo quốc gia")
)

countries = {
    'Việt Nam': 'VN',
    'Hoa Kỳ': 'US',
    'Nhật Bản': 'JP',
    'Hàn Quốc': 'KR',
    'Anh Quốc': 'GB',
    'Pháp': 'FR',
    'Đức': 'DE',
    'Toàn Cầu': ''
}

if mode == "Tìm kiếm từ khóa tự chọn":
    st.subheader("🔍 Tìm kiếm và so sánh nhiều từ khóa")
    country = st.selectbox("Chọn quốc gia:", list(countries.keys()))
    geo = countries[country]
    keywords_input = st.text_area("Nhập danh sách từ khóa (phân cách bằng dấu phẩy):", "sữa cho bé, bỉm trẻ em, ăn dặm")
    keywords = [kw.strip() for kw in keywords_input.split(",") if kw.strip()]

    if st.button("Tìm kiếm"):
        if not keywords:
            st.warning("Vui lòng nhập ít nhất 1 từ khóa.")
        else:
            try:
                pytrends.build_payload(kw_list=keywords, timeframe='today 1-m', geo=geo)
                df_interest = pytrends.interest_over_time()

                if df_interest.empty:
                    st.warning("Không có dữ liệu phù hợp cho các từ khóa.")
                else:
                    df_interest = df_interest.drop(columns=['isPartial'])
                    st.success("📊 Dữ liệu so sánh chi tiết theo thời gian:")
                    st.dataframe(df_interest)

                    fig = px.line(df_interest, x=df_interest.index, y=df_interest.columns,
                                  title=f"Biểu đồ xu hướng tìm kiếm (1 tháng) tại {country}")
                    st.plotly_chart(fig)

                    avg_searches = df_interest.mean().sort_values(ascending=False).reset_index()
                    avg_searches.columns = ['Từ khóa', 'Mức độ tìm kiếm trung bình']

                    st.subheader("📈 So sánh tổng thể trung bình các từ khóa")
                    st.dataframe(avg_searches)

                    fig2 = px.bar(avg_searches,
                                  x='Từ khóa',
                                  y='Mức độ tìm kiếm trung bình',
                                  title="So sánh mức độ tìm kiếm trung bình")
                    st.plotly_chart(fig2)

            except Exception as e:
                st.error("⚠️ Gặp lỗi khi truy cập Google Trends. Có thể do giới hạn số lần yêu cầu. Vui lòng thử lại sau vài phút.")

elif mode == "Xem từ khóa hot hôm nay theo quốc gia":
    st.subheader("🔥 Từ khóa hot trong ngày")
    country = st.selectbox("Chọn quốc gia (cho Trending Searches):", ['Việt Nam', 'Hoa Kỳ', 'Nhật Bản', 'Hàn Quốc', 'Anh Quốc'])
    country_map = {
        'Việt Nam': 'vietnam',
        'Hoa Kỳ': 'united_states',
        'Nhật Bản': 'japan',
        'Hàn Quốc': 'south_korea',
        'Anh Quốc': 'united_kingdom'
    }

    try:
        trending_df = pytrends.trending_searches(pn=country_map[country])
        trending_df.columns = ['Từ khóa']
        st.dataframe(trending_df)

        top10 = trending_df.head(10)
        fig = px.bar(top10,
                     x='Từ khóa',
                     y=top10.index,
                     orientation='h',
                     title=f"Top 10 từ khóa hot nhất hôm nay tại {country}")
        st.plotly_chart(fig)
    except Exception as e:
        st.error(f"Lỗi khi tải dữ liệu trending: {str(e)}")