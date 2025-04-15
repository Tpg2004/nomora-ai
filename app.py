import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from PIL import Image

# APP SETUP
st.set_page_config(page_title="Nomora AI", layout="wide", page_icon="🍽️")

# HEADER
st.title("Nomora AI")
st.markdown("#### 🍄 Smart Menu Insights to Reduce Food Waste & Boost Efficiency")

st.markdown("---")

# LOAD DATA
@st.cache_data
def load_data():
    dishes = pd.read_csv("dish_sales.csv")
    waste = pd.read_csv("ingredient_waste.csv")
    return dishes, waste

dishes_df, waste_df = load_data()

# SECTION 1: Dish Performance
st.subheader("📉 Low-Performing Dishes")
low_performers = dishes_df[dishes_df['orders'] < 30].sort_values(by='orders')

st.write("These dishes had low orders. Consider removing or reworking them:")
st.dataframe(low_performers[['dish_name', 'orders', 'profit_margin', 'ingredient_cost']])

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
common_ingredients = dishes_df.explode('ingredients')
overlap = common_ingredients.groupby(['ingredients'])['dish_name'].nunique().reset_index()
overlap.columns = ['Ingredient', 'Dish Count']
overlap = overlap.sort_values(by='Dish Count', ascending=False)

st.dataframe(overlap.head(10))
st.write("These ingredients are used across multiple dishes. Optimize usage to minimize waste.")

# FOOTER
st.markdown("---")
st.markdown("💡 **Nomora AI** empowers restaurants to cut costs, reduce waste, and reimagine menus with data.")

