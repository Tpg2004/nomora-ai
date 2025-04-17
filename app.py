import streamlit as st
import pandas as pd
import altair as alt

# SETUP
st.set_page_config(page_title="Nomora AI", layout="wide", page_icon="🍽️")

# LOGO (Optional)
try:
    st.markdown(
        """
        <div style="text-align: center;">
            <img src="https://raw.githubusercontent.com/nomora-ai/nomoraimg.jpeg" width="120">
        </div>
        """,
        unsafe_allow_html=True
    )
except Exception as e:
    st.warning("Logo not found. Skipping image display.")


# HEADER
st.markdown("""
    <div style='text-align:center;'>
        <h1 style='color:#2c3e50;'>Nomora AI</h1>
        <h4 style='color:#16a085;'>🍄 Smart Menu Insights to Reduce Food Waste & Boost Efficiency</h4>
    </div>
    <hr style='border:1px solid #ccc;'>
    """, unsafe_allow_html=True)

# LOAD DATA
@st.cache_data
def load_data():
    dishes = pd.read_csv("dish_sales.csv")
    waste = pd.read_csv("ingredient_waste.csv")
    return dishes, waste

dishes_df, waste_df = load_data()

st.markdown("## 🤖 Ask Nomora AI")
user_query = st.chat_input("Ask a question about our food menu or wastage optimization statistics!")

if user_query:
    user_query = user_query.lower()

    with st.chat_message("user"):
        st.write(user_query)

    with st.chat_message("assistant"):
        response = ""

        if user_query in ["hi", "hello", "hey"]:
            response = "👋 Hey there! Am so delighted to meet you! How can I help you today?"

        elif "stock less" in user_query or "reduce stock" in user_query:
           top_waste = waste_df.sort_values(by='waste_kg', ascending=False).head(1).iloc[0]
           response = f"📦 You should consider stocking less of **{top_waste['ingredient']}**, as it had the highest waste last week: **{top_waste['waste_kg']} kg**."
        elif "low-selling" in user_query and "high-waste" in user_query:
           combined = pd.merge(dishes_df, waste_df, left_on='Dish Name', right_on='dish_name', how='inner')
           combined['waste_pct'] = combined['waste_kg'] / (combined['waste_kg'] + 0.001)  # avoid zero div
           filtered = combined[(combined['Weekly Orders'] < 10) & (combined['waste_kg'] > 1)]
           if not filtered.empty:
              dish = filtered.iloc[0]
              response = f"❌ Consider removing **{dish['Dish Name']}** – low sales (**{dish['Weekly Orders']}** orders) and high waste (**{dish['ingredient']}**: **{dish['waste_kg']} kg**)."
           else:
              response = "All dishes with low orders currently have acceptable waste levels."

        elif "most wasted" in user_query or "high waste" in user_query:
            top_waste = waste_df.sort_values(by='waste_kg', ascending=False).iloc[0]
            response = f"🔝 The most wasted ingredient is **{top_waste['ingredient']}**, with **{top_waste['waste_kg']} kg** wasted."

        elif "remove" in user_query or "low orders" in user_query:
            low_dish = dishes_df.sort_values(by='Weekly Orders').iloc[0]
            response = f"⚠️ Consider removing **{low_dish['Dish Name']}** – it had just **{low_dish['Weekly Orders']}** orders last week."

        elif "suggest" in user_query or "new dish" in user_query:
            response = "👩‍🍳 Try creating new dishes using high-waste ingredients like Avocado or Lemon. For example:\n\n- **Avocado Hummus Wrap**\n- **Lemon Herb Pasta**"

        elif "overlap" in user_query or "common ingredient" in user_query:
            common = dishes_df['Ingredients'].str.split(', ').explode().value_counts().head(1)
            ingredient = common.index[0]
            response = f"🔁 The most common ingredient across dishes is **{ingredient}**. Use it wisely to reduce waste."

        elif "profit" in user_query:
            for _, row in dishes_df.iterrows():
                if row['Dish Name'].lower() in user_query:
                    response = f"💰 The profit margin of **{row['Dish Name']}** is **{row['Profit Margin']}**."
                    break
            else:
                response = "I couldn't find that dish. Please check the name and try again."

        elif "shelf life" in user_query:
            for _, row in waste_df.iterrows():
                if row['ingredient'].lower() in user_query:
                    response = f"🧂 The shelf life of **{row['ingredient']}** is **{row['shelf_life']}**."
                    break
            else:
                response = "I couldn't find shelf life info for that ingredient."

        else:
            response = "🤔 I'm not sure how to answer that yet, but you can ask things like:\n- 'Which dish should we remove?'\n- 'Shelf life of Avocado'\n- 'Profit of Veg Burger'"

        st.write(response)

# SECTION 1: Low-Performing Dishes
st.subheader("📉 Low-Performing Dishes")
low_performers = dishes_df[dishes_df['Weekly Orders'] < 15].sort_values(by='Weekly Orders')
st.write("These dishes had low orders. Consider removing or reworking them:")
st.dataframe(low_performers[['Dish Name', 'Weekly Orders', 'Profit Margin', 'Ingredient Cost']])

# SECTION 2: High-Waste Ingredients
st.subheader("🗑️ High-Waste Ingredients")
if 'Avg Waste %' in waste_df.columns:
    high_waste = waste_df.sort_values(by='Avg Waste %', ascending=False).head(5)

    chart = alt.Chart(high_waste).mark_bar().encode(
        x=alt.X('Ingredient', sort='-y'),
        y=alt.Y('Avg Waste %'),
        color=alt.value('orange')
    ).properties(width=600, height=300)

    st.altair_chart(chart)
    st.write("Top wasted ingredients to focus on repurposing or reducing.")
else:
    st.warning("Missing 'Avg Waste %' column in ingredient_waste.csv")

# SECTION 3: Suggested Recipes
st.subheader("🍽️ Suggested New Dishes Using Wasted Ingredients")
suggested_dishes = {
    "Creamy Mushroom Soup": ["Mushrooms", "Cream", "Onion"],
    "Stuffed Bell Peppers": ["Bell Peppers", "Rice", "Cheese"],
    "Veggie Frittata": ["Spinach", "Eggs", "Cheese"]
}

for dish, ingredients in suggested_dishes.items():
    st.markdown(f"**{dish}** – Uses: _{', '.join(ingredients)}_")

# SECTION 4: Overlapping Ingredients in High-Margin Dishes
st.subheader("🔁 High-Margin Dishes with Ingredient Overlap")

# Convert ingredients string to a list
dishes_df['Ingredients List'] = dishes_df['Ingredients'].apply(lambda x: [i.strip() for i in x.split(',')])

# Explode for overlap analysis
exploded_df = dishes_df[['Dish Name', 'Profit Margin', 'Ingredients List']].explode('Ingredients List')

# Count overlaps
overlap = exploded_df.groupby('Ingredients List')['Dish Name'].nunique().reset_index()
overlap.columns = ['Ingredient', 'Dish Count']
overlap = overlap.sort_values(by='Dish Count', ascending=False)

st.dataframe(overlap.head(10))
st.write("These ingredients are used across multiple dishes. Optimize usage to minimize waste.")

# FOOTER
st.markdown("""
    <hr>
    <p style='text-align:center; color: #7f8c8d;'>
        💡 <b>Nomora AI</b> empowers restaurants to cut costs, reduce waste, and reimagine menus with data.
    </p>
    """, unsafe_allow_html=True)
