import streamlit as st
import pandas as pd
import altair as alt

# APP SETUP
st.set_page_config(page_title="Nomora AI", layout="wide", page_icon="🍽️")

# HEADER
try:
    st.image("nomoraimg.jpeg", width=100)
except:
    st.warning("Logo not found. Skipping image display.")

st.title("Nomora AI")
st.markdown("#### 🍄 Smart Menu Insights to Reduce Food Waste & Boost Efficiency")
st.markdown("---")

# LOAD DATA
@st.cache_data
def load_data():
    dishes = pd.read_csv("data/dish_sales.csv")
    waste = pd.read_csv("data/ingredient_waste.csv")
    return dishes, waste

dishes_df, waste_df = load_data()

# --- SIMPLE CHATBOT INTERFACE ---
st.markdown("## 🤖 Ask Nomora AI")
user_query = st.chat_input("Ask a question about your menu or waste...")

if user_query:
    user_query = user_query.lower()

    with st.chat_message("user"):
        st.write(user_query)

    with st.chat_message("assistant"):
        response = ""

        if "most wasted" in user_query or "high waste" in user_query:
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
            for _, row in dishes_df.iterrows():
                if any(ing.lower() in user_query for ing in row['Ingredients'].split(', ')):
                    ingredient = [ing for ing in row['Ingredients'].split(', ') if ing.lower() in user_query][0]
                    if ingredient.lower() in row['Ingredient Shelf Life'].lower():
                        shelf_info = row['Ingredient Shelf Life']
                        response = f"🧊 Shelf life info: {shelf_info}"
                        break
            else:
                response = "I couldn't find shelf life info for that ingredient."

        else:
            response = "🤔 I'm not sure how to answer that yet, but you can ask things like:\n- 'Which dish should we remove?'\n- 'Shelf life of Avocado'\n- 'Profit of Veg Burger'"

        st.write(response)

# SECTION 1: Dish Performance
st.subheader("📉 Low-Performing Dishes")
low_performers = dishes_df[dishes_df['Weekly Orders'] < 30].sort_values(by='Weekly Orders')

st.write("These dishes had low orders. Consider removing or reworking them:")
st.dataframe(low_performers[['Dish Name', 'Weekly Orders', 'Profit Margin', 'Ingredient Cost']])

# SECTION 2: Ingredient Waste
st.subheader("🗑️ High-Waste Ingredients")
high_waste = waste_df.sort_values(by='waste_kg', ascending=False).head(5)

chart = alt.Chart(high_waste).mark_bar().encode(
    x=alt.X('ingredient', sort='-y'),
    y='waste_kg',
    color=alt.value('orange')
).properties(width=600, height=300)

st.altair_chart(chart)
st.write("Top wasted ingredients to focus on repurposing or reducing.")

# SECTION 3: Suggested Recipes
st.subheader("🍽️ Suggested New Dishes Using Wasted Ingredients")
suggested_dishes = {
    "Creamy Mushroom Soup": ["Mushrooms", "Cream", "Onion"],
    "Stuffed Bell Peppers": ["Bell Peppers", "Rice", "Cheese"],
    "Veggie Frittata": ["Spinach", "Eggs", "Cheese"]
}

for dish, ingredients in suggested_dishes.items():
    st.markdown(f"**{dish}** – Uses: _{', '.join(ingredients)}_")

# SECTION 4: Ingredient Overlap & Margins
st.subheader("🔁 High-Margin Dishes with Ingredient Overlap")
common_ingredients = dishes_df.copy()
common_ingredients['Ingredient List'] = common_ingredients['Ingredients'].str.split(', ')
exploded = common_ingredients.explode('Ingredient List')
overlap = exploded.groupby(['Ingredient List'])['Dish Name'].nunique().reset_index()
overlap.columns = ['Ingredient', 'Dish Count']
overlap = overlap.sort_values(by='Dish Count', ascending=False)

st.dataframe(overlap.head(10))
st.write("These ingredients are used across multiple dishes. Optimize usage to minimize waste.")

# FOOTER
st.markdown("---")
st.markdown("💡 **Nomora AI** empowers restaurants to cut costs, reduce waste, and reimagine menus with data.")
