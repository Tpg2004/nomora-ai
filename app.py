import streamlit as st
import pandas as pd
import altair as alt

# SETUP
st.set_page_config(page_title="Nomora AI", layout="wide", page_icon="🍽️")

# LOGO (Optional)
try:
    st.image("assets/logo.png", width=100)
except:
    st.warning("Logo not found. Skipping image display.")

# HEADER
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

# ✅ DEBUG (optional during development)
# st.write("DISHES COLUMNS:", dishes_df.columns)
# st.write("WASTE COLUMNS:", waste_df.columns)

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
st.markdown("---")
st.markdown("💡 **Nomora AI** empowers restaurants to cut costs, reduce waste, and reimagine menus with data.")
