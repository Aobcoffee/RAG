"""
Streamlit web interface for the RAG SQL Agent.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sys
from pathlib import Path

# Add src to Python path
sys.path.append(str(Path(__file__).parent / 'src'))

from src.agents.rag_agent import RAGSQLAgent


# Configure Streamlit page
st.set_page_config(
    page_title="RAG SQL Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        margin: 1rem 0;
    }
    .error-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        margin: 1rem 0;
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def initialize_agent():
    """Initialize the RAG SQL Agent with caching."""
    agent = RAGSQLAgent()
    
    if agent.initialize():
        return agent
    else:
        return None


def main():
    """Main Streamlit application."""
    
    # Header
    st.markdown('<h1 class="main-header">🤖 RAG SQL Agent</h1>', unsafe_allow_html=True)
    st.markdown("Ask questions about your database in natural language!")
    
    # Initialize agent
    if 'agent' not in st.session_state:
        with st.spinner("Initializing RAG SQL Agent..."):
            agent = initialize_agent()
            if agent:
                st.session_state.agent = agent
                st.session_state.initialized = True
            else:
                st.error("❌ Failed to initialize agent. Please check your configuration.")
                st.stop()
    
    agent = st.session_state.agent
    
    # Sidebar
    with st.sidebar:
        st.header("🔧 Agent Controls")
        
        # Schema information
        if st.button("📊 Refresh Schema"):
            with st.spinner("Refreshing schema..."):
                success = agent.refresh_schema()
                if success:
                    st.success("Schema refreshed successfully!")
                else:
                    st.error("Failed to refresh schema")
        
        # Available tables
        st.subheader("📋 Available Tables")
        tables = agent.get_available_tables()
        if tables:
            for table in tables:
                st.write(f"• {table}")
        else:
            st.write("No tables found")
        
        # Agent statistics
        st.subheader("📈 Statistics")
        stats = agent.get_stats()
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Queries", stats['total_queries'])
            st.metric("Success Rate", f"{stats['success_rate']}%")
        with col2:
            st.metric("Successful", stats['successful_queries'])
            st.metric("Avg Time", f"{stats['average_processing_time']}s")
        
        # Clear history
        if st.button("🗑️ Clear History"):
            agent.clear_history()
            if 'query_results' in st.session_state:
                st.session_state.query_results = []
            st.success("History cleared!")
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("💬 Ask Your Question")
        
        # Example questions
        with st.expander("💡 Example Questions"):
            examples = [
                "What are the sales last month?",
                "Show me the top 10 customers by revenue",
                "What's the average order value this quarter?",
                "Which products have the highest profit margins?",
                "How many orders were placed yesterday?",
                "What's the trend in monthly sales this year?",
                "Which customer segment generates the most revenue?"
            ]
            for example in examples:
                if st.button(example, key=f"example_{example}"):
                    st.session_state.current_question = example
        
        # Question input
        question = st.text_area(
            "Enter your question:",
            value=st.session_state.get('current_question', ''),
            height=100,
            placeholder="e.g., What are the total sales for last month?"
        )
        
        col_btn1, col_btn2 = st.columns([1, 4])
        with col_btn1:
            ask_button = st.button("🚀 Ask", type="primary")
        
        # Process question
        if ask_button and question.strip():
            with st.spinner("🤔 Processing your question..."):
                result = agent.ask(question)
                
                # Store result in session state
                if 'query_results' not in st.session_state:
                    st.session_state.query_results = []
                st.session_state.query_results.insert(0, result)
                
                # Keep only last 10 results
                if len(st.session_state.query_results) > 10:
                    st.session_state.query_results = st.session_state.query_results[:10]
    
    with col2:
        st.subheader("🔍 Quick Schema Info")
        schema_info = agent.get_schema_info()
        
        if 'error' not in schema_info:
            st.json(schema_info)
        else:
            st.error(schema_info['error'])
    
    # Display results
    if 'query_results' in st.session_state and st.session_state.query_results:
        st.markdown("---")
        st.subheader("📊 Query Results")
        
        # Tabs for different results
        if len(st.session_state.query_results) > 1:
            tabs = st.tabs([f"Query {i+1}" for i in range(min(5, len(st.session_state.query_results)))])
        else:
            tabs = [st.container()]
        
        for i, (tab, result) in enumerate(zip(tabs, st.session_state.query_results[:5])):
            with tab:
                display_result(result)


def display_result(result):
    """Display a single query result."""
    if result['success']:
        # Success header
        st.markdown(f'<div class="success-box">✅ <strong>Success!</strong> Query processed in {result["processing_time"]}s</div>', unsafe_allow_html=True)
        
        # Question and SQL
        st.write(f"**Question:** {result['question']}")
        st.code(result['sql_query'], language='sql')
        
        # Results
        if result.get('results'):
            st.write(f"**Results:** {result['result_count']} rows returned")
            
            # Convert to DataFrame for better display
            df = pd.DataFrame(result['results'])
            
            # Display data
            st.dataframe(df, use_container_width=True)
            
            # Try to create visualizations if data is suitable
            create_visualizations(df, result['question'])
        
        # Analysis
        if result.get('analysis'):
            st.subheader("📈 Analysis")
            st.write(result['analysis'])
        
        # Metadata
        with st.expander("🔍 Query Details"):
            st.write(f"**Timestamp:** {result['timestamp']}")
            st.write(f"**Tables Used:** {', '.join(result.get('schema_used', []))}")
            st.write(f"**Processing Time:** {result['processing_time']}s")
    
    else:
        # Error display
        st.markdown(f'<div class="error-box">❌ <strong>Error:</strong> {result["error"]}</div>', unsafe_allow_html=True)
        st.write(f"**Question:** {result['question']}")
        
        if result.get('sql_query'):
            st.write("**Generated SQL:**")
            st.code(result['sql_query'], language='sql')


def create_visualizations(df, question):
    """Create visualizations based on the data."""
    if df.empty:
        return
    
    st.subheader("📊 Visualizations")
    
    try:
        # Determine chart type based on data
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        
        if len(numeric_cols) >= 1 and len(categorical_cols) >= 1:
            # Bar chart
            if len(df) <= 20:  # Only for reasonable number of categories
                fig = px.bar(df, x=categorical_cols[0], y=numeric_cols[0], 
                           title=f"{numeric_cols[0]} by {categorical_cols[0]}")
                st.plotly_chart(fig, use_container_width=True)
        
        elif len(numeric_cols) >= 2:
            # Scatter plot
            fig = px.scatter(df, x=numeric_cols[0], y=numeric_cols[1],
                           title=f"{numeric_cols[1]} vs {numeric_cols[0]}")
            st.plotly_chart(fig, use_container_width=True)
        
        elif len(numeric_cols) == 1:
            # Histogram
            fig = px.histogram(df, x=numeric_cols[0], 
                             title=f"Distribution of {numeric_cols[0]}")
            st.plotly_chart(fig, use_container_width=True)
        
        # Time series if date column exists
        date_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
        if date_cols and numeric_cols:
            fig = px.line(df, x=date_cols[0], y=numeric_cols[0],
                         title=f"{numeric_cols[0]} over time")
            st.plotly_chart(fig, use_container_width=True)
    
    except Exception as e:
        st.write(f"Could not create visualization: {e}")


if __name__ == "__main__":
    main()
