# DisasterShield: Disaster Relief System

DisasterShield is an disaster relief system designed to optimize disaster response efforts. It leverages predictive analytics, and resource tracking to provide actionable insights for disaster management.

## Features

- **Resource Tracking**  
   - Integrates with IBM Cloud to provide real-time data on resource availability and deployment.
   - Ensures efficient tracking and distribution of critical resources.

- **Disaster Prediction Models**  
   - Flood prediction using Snap Logistic Regression trained with IBM Watsonx AutoAI.
   - Earthquake magnitude prediction using Snap Random Forest trained with IBM Watsonx AutoAI.

- **Interactive Web Interface**  
   - Built with Streamlit to enable users to interact with data and models effortlessly.
   - Provides dynamic visualizations and prediction outputs for informed decision-making.

- **Custom Dataset Handling**  
   - Merges and preprocesses multiple datasets for training and evaluation.
   - Focuses on disaster-specific parameters, such as rainfall, water levels, seismic activity, and river discharge.

## Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Smruti0109/disaster-relief-optimization.git
   cd disaster-relief-optimization


2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt

3. **Run the application:**
   ```bash
   streamlit run app.py

## Contribution

- **Team Members**  
   - Pratiksha Ashok Mohite
   - Smruti Shripad Deshpande
     
- **Mentors**  
   - Dr. Puja Padiya
   - Mr. Yogesh Raje
     
## Technical Stack

- **Backend Framework**: Watsonx AutoAI – For automated machine learning model generation and training.
- **Frontend Framework**: Streamlit – Provides an interactive and user-friendly web interface.
- **Cloud Platform**: IBM Cloud – For real-time resource tracking and data integration.
- **ML Model**: Snap Logistic Regression for flood prediction based on parameters like rainfall, river discharge, and water levels. Snap Random Forest for earthquake magnitude prediction using parameters such as latitude, longitude, and depth.

## Acknowledgements

- Watsonx AutoAI for simplifying model development with automated training and deployment.
- IBM Cloud for enabling real-time resource tracking.
- Streamlit for building the interactive interface.
