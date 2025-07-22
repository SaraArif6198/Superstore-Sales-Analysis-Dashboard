# Customer Segmentation & Sales reporting Dashboard (Task 05)

##  Project Objective
This project focuses on clustering customers into meaningful groups using **K-Means Clustering** based on behavioral and demographic data. The goal? Help businesses target the right customers, personalize strategies, and boost marketing ROI.

Rather than treating all customers the same, we unlock insights from patterns in **Annual Income**, **Spending Score**, and more — and present the findings in an **interactive Streamlit dashboard**.


## 📁 Dataset
**Name:** Mall Customer Segmentation Data  
**Source:** [Kaggle – Mall Customer Segmentation Dataset](https://www.kaggle.com/vjchoudhary7/customer-segmentation-tutorial)

| Feature          | Description                                                  |
|------------------|--------------------------------------------------------------|
| `CustomerID`     | Unique ID for each customer                                  |
| `Gender`         | Male / Female                                                |
| `Age`            | Age of the customer                                          |
| `Annual Income`  | Income in thousands of dollars                               |
| `Spending Score` | Score assigned by the mall based on spending behavior (1–100)|

---

## 🛠 Tools & Libraries Used
- **Pandas** – Data cleaning and EDA  
- **Matplotlib & Seaborn** – Static visualizations  
- **Scikit-learn** – K-Means clustering  
- **Plotly** – Interactive charts  
- **Streamlit** – Web-based interactive dashboard  


##  Project Workflow

1. **Data Preprocessing**  
   - Checked for nulls and correct data types  
   - Transformed categorical features (e.g., `Gender` → numerical)  
   - Scaled numerical features for clustering stability  

2. **Exploratory Data Analysis (EDA)**  
   - Distribution of Age, Annual Income, and Spending Score  
   - Relationship between Income and Spending  
   - Spending behavior segmented by Gender  

3. **Clustering with K-Means**  
   - Elbow Method to find optimal `k`  
   - Silhouette Score analysis  
   - **Final Model:** `k = 5` clusters selected based on combined metrics  

4. **Visualization**  
   - 2D & 3D clustering scatter plots  
   - Color-coded cluster groups  
   - Customer profiles labeled with business-friendly tags:  
     - **Target Customers** (High spenders, moderate income)  
     - **Careful Spenders** (Low spenders, high income)  
     - **Potential Customers** (Mid-income, mid-score)  

## Streamlit Dashboard Features

| Feature                       | Description                                                        |
|------------------------------|--------------------------------------------------------------------|
| **Cluster Summary**          | Pie chart + bar chart of cluster distribution                      |
| **2D & 3D Scatter Plots**    | Visualizes clusters across income and spending dimensions          |
| **Customer Profile Insights**| Displays customer segments using business-friendly labels          |
| **Interactive Filters**      | Slice data based on gender, age range, and cluster assignments     |
| **Tooltips & Color Legends** | Easy interpretation of data points                                 |
| **Download Buttons**         | Export filtered data as CSV                                        |
| **Animated KPIs**            | Highlight cluster counts with animated counters (via `streamlit_extras`) |


## ✅ Results & Insights
- **5 distinct clusters** were identified, each with unique spending behaviors.  
- Businesses can now easily target:  
  -  **High-value Customers** to prioritize for promotions  
  -  **Cost-sensitive Customers** to retain with value-based offers  
  -  **Low-engagement Customers** to exclude from expensive ad spend  


##  Lessons Learned
- **Imbalanced cluster sizes** were mitigated by adjusting feature scaling.  
- **3D Plotly** rendering in Streamlit required converting `.ipynb` to `.py`.  
- **Layout issues** in Streamlit fixed by using `st.columns()` instead of excessive sidebar elements.  
- **Semantic cluster labels** improved stakeholder understanding and buy-in.  


## Conclusion
This project demonstrates the power of **unsupervised learning** to guide marketing decisions through:  
- ✅ **Visual storytelling**  
- ✅ **Segmentation based on real patterns**  
- ✅ **Interactive dashboards** for decision-makers  

## 🔗 Useful Resources
- [Scikit-learn KMeans Documentation](https://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html)  
- [Streamlit Documentation](https://docs.streamlit.io/)  
- [Plotly for Python](https://plotly.com/python/)  
- [Mall Customer Segmentation Dataset (Kaggle)](https://www.kaggle.com/vjchoudhary7/customer-segmentation-tutorial)  

---

> 🔖 *Part of a business-focused ML portfolio showcasing real-world applications in customer analytics and segmentation at DevelopersHub Corporation.*  
