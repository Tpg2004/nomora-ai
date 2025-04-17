# ... (previous imports remain same)

# Add this function for image handling
def handle_sidebar_image():
    try:
        # Attempt to load logo from current directory
        st.sidebar.image("nomora.jpeg", use_column_width=True, 
                        caption="MenuMind AI - Food Waste Reduction System")
    except FileNotFoundError:
        st.sidebar.warning("Logo image not found - using text header")
        st.sidebar.title("MenuMind AI")
    except Exception as e:
        st.sidebar.error(f"Error loading image: {str(e)}")

# Modified UI Setup section
st.set_page_config(page_title="MenuMind AI", page_icon="🍽️", layout="wide")

with st.sidebar:
    handle_sidebar_image()  # Image handling with error protection
    st.divider()
    st.header("Settings")
    start_date = st.date_input("Analysis Period Start", datetime.today())
    end_date = st.date_input("Analysis Period End", datetime.today())
    st.divider()
    st.caption("Powered by MenuMind AI • v1.2")

# ... rest of the previous code remains same ...

# Add this in dashboard section for potential food waste visualization
with tab1:
    try:
        st.subheader("Waste Pattern Visualization")
        fig = px.sunburst(ingredients_df, path=['Ingredient', 'Frequently Wasted In'],
                         values='Avg Waste %', color='Avg Waste %')
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Couldn't generate waste pattern visualization: {str(e)}")
        st.info("Showing basic bar chart instead")
        fig = px.bar(ingredients_df, x='Ingredient', y='Avg Waste %')
        st.plotly_chart(fig, use_container_width=True)

# ... rest of the code ...
