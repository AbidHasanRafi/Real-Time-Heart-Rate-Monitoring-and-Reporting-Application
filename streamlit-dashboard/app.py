import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import time
import json
import numpy as np
import random

# Page configuration
st.set_page_config(
    page_title="Heart Rate Monitor",
    page_icon="❤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #ff4b4b;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin: 10px;
    }
    .status-indicator {
        width: 20px;
        height: 20px;
        border-radius: 50%;
        display: inline-block;
        margin-right: 10px;
    }
    .status-online {
        background-color: #00cc00;
    }
    .status-offline {
        background-color: #ff4b4b;
    }
    .heart-animation {
        animation: heartbeat 1.5s ease-in-out infinite;
    }
    @keyframes heartbeat {
        0% { transform: scale(1); }
        50% { transform: scale(1.1); }
        100% { transform: scale(1); }
    }
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        font-size: 1rem;
        cursor: pointer;
    }
    .stTextInput>div>div>input {
        border: 2px solid #667eea;
        border-radius: 0.5rem;
        padding: 0.5rem;
    }
    .report-section {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .telegram-button {
        background: linear-gradient(135deg, #0088cc 0%, #005580 100%) !important;
    }
</style>
""", unsafe_allow_html=True)

class HeartRateMonitor:
    def __init__(self):
        self.data_history = []
        self.max_history = 100
        self.api_url = ""
        self.use_mock_data = False
        
    def set_api_url(self, url):
        self.api_url = url
        
    def set_use_mock_data(self, use_mock):
        self.use_mock_data = use_mock
        
    def generate_mock_data(self):
        """Generate realistic mock heart rate data for testing"""
        current_bpm = random.randint(60, 100)
        if random.random() < 0.2:  # 20% chance of abnormal reading
            current_bpm = random.choice([random.randint(40, 59), random.randint(101, 140)])
            
        return {
            "heart_rate": {
                "current_bpm": current_bpm,
                "average_bpm": random.randint(65, 85),
                "timestamp": int(time.time() * 1000)
            },
            "sensor": {
                "ir_value": random.randint(800, 1000),
                "finger_detected": random.random() > 0.3  # 70% chance finger is detected
            }
        }
        
    def fetch_data(self):
        if self.use_mock_data:
            # Generate mock data for testing
            mock_data = self.generate_mock_data()
            mock_data['timestamp'] = datetime.now()
            self.data_history.append(mock_data)
            if len(self.data_history) > self.max_history:
                self.data_history.pop(0)
            return mock_data
            
        if not self.api_url:
            return None
            
        try:
            response = requests.get(self.api_url, timeout=3)
            if response.status_code == 200:
                data = response.json()
                data['timestamp'] = datetime.now()
                self.data_history.append(data)
                if len(self.data_history) > self.max_history:
                    self.data_history.pop(0)
                return data
            else:
                st.warning(f"API returned status code: {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            st.warning(f"Connection issue: {str(e)}")
            return None
        except json.JSONDecodeError:
            st.warning("Invalid JSON response from API")
            return None
    
    def get_current_status(self):
        if not self.data_history:
            return "No data"
        
        current_data = self.data_history[-1]
        heart_rate = current_data['heart_rate']['current_bpm']
        finger_detected = current_data['sensor']['finger_detected']
        
        if not finger_detected:
            return "No finger detected"
        elif heart_rate == 0:
            return "Measuring..."
        elif heart_rate < 60:
            return "Low heart rate"
        elif heart_rate > 100:
            return "High heart rate"
        else:
            return "Normal"
    
    def get_heart_rate_trend(self):
        if len(self.data_history) < 2:
            return "No trend data"
        
        recent_rates = [d['heart_rate']['current_bpm'] for d in self.data_history[-5:] if d['heart_rate']['current_bpm'] > 0]
        if len(recent_rates) < 2:
            return "Insufficient data"
        
        if recent_rates[-1] > recent_rates[0] + 5:
            return "Rising"
        elif recent_rates[-1] < recent_rates[0] - 5:
            return "Falling"
        else:
            return "Stable"
    
    def generate_health_insights(self, heart_rates):
        """Generate health insights based on heart rate data"""
        if not heart_rates or len(heart_rates) < 5:
            return ["Insufficient data for health analysis"]
            
        insights = []
        avg_hr = np.mean(heart_rates)
        max_hr = max(heart_rates)
        min_hr = min(heart_rates)
        hr_std = np.std(heart_rates)
        
        # Overall health assessment
        if avg_hr < 60:
            insights.append("Low average heart rate - may indicate good cardiovascular fitness")
        elif avg_hr > 100:
            insights.append("High average heart rate - consider consulting a healthcare provider")
        else:
            insights.append("Normal average heart rate - within healthy range")
        
        # Variability assessment
        if hr_std > 15:
            insights.append("High heart rate variability - may indicate stress or changing activity levels")
        else:
            insights.append("Stable heart rate pattern - consistent activity or rest state")
        
        # Extreme values alert
        if max_hr > 120:
            insights.append("⚠️ Warning: Detected very high heart rate values")
        if min_hr < 50:
            insights.append("⚠️ Warning: Detected very low heart rate values")
            
        return insights

def create_heart_rate_chart(data_history):
    if len(data_history) < 2:
        return None
    
    timestamps = [d['timestamp'] for d in data_history]
    heart_rates = [d['heart_rate']['current_bpm'] for d in data_history]
    ir_values = [d['sensor']['ir_value'] for d in data_history]
    
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Heart Rate (BPM)', 'IR Sensor Values'),
        vertical_spacing=0.15
    )
    
    # Heart rate line
    fig.add_trace(
        go.Scatter(
            x=timestamps, y=heart_rates,
            mode='lines+markers',
            name='Heart Rate',
            line=dict(color='#ff4b4b', width=3),
            marker=dict(size=6)
        ),
        row=1, col=1
    )
    
    # IR values line
    fig.add_trace(
        go.Scatter(
            x=timestamps, y=ir_values,
            mode='lines',
            name='IR Values',
            line=dict(color='#667eea', width=2)
        ),
        row=2, col=1
    )
    
    fig.update_layout(
        height=500,
        showlegend=False,
        plot_bgcolor='rgba(240,240,240,0.1)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#2c3e50')
    )
    
    fig.update_xaxes(title_text="Time", row=1, col=1)
    fig.update_xaxes(title_text="Time", row=2, col=1)
    fig.update_yaxes(title_text="BPM", row=1, col=1)
    fig.update_yaxes(title_text="IR Value", row=2, col=1)
    
    return fig

def send_telegram_message(token, chat_id, message):
    """Send message via Telegram bot"""
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={message}"
        response = requests.get(url)
        return response.status_code == 200
    except Exception as e:
        st.error(f"Failed to send Telegram message: {str(e)}")
        return False

def format_telegram_report(monitor, latest_data, patient_name):
    """Format the current state as a Telegram report"""
    if not latest_data:
        return "No data available for report"
    
    # Get current metrics
    heart_rate = latest_data['heart_rate']['current_bpm']
    avg_heart_rate = latest_data['heart_rate']['average_bpm']
    finger_detected = latest_data['sensor']['finger_detected']
    ir_value = latest_data['sensor']['ir_value']
    status = monitor.get_current_status()
    trend = monitor.get_heart_rate_trend()
    
    # Get health insights
    valid_rates = [d['heart_rate']['current_bpm'] for d in monitor.data_history if d['heart_rate']['current_bpm'] > 0]
    insights = monitor.generate_health_insights(valid_rates)
    
    # Format message
    message = "❤️ HEART RATE STATUS REPORT ❤️\n\n"
    message += f"👤 Patient: {patient_name}\n" if patient_name else "👤 Patient: Not specified\n"
    message += f"📊 Current Status: {status}\n"
    message += f"📈 Trend: {trend}\n\n"
    
    message += "🔢 CURRENT METRICS:\n"
    message += f"• Heart Rate: {heart_rate if heart_rate > 0 else 'N/A'} BPM\n"
    message += f"• Average HR: {avg_heart_rate if avg_heart_rate > 0 else 'N/A'} BPM\n"
    message += f"• Finger Detected: {'Yes' if finger_detected else 'No'}\n"
    message += f"• IR Sensor Value: {ir_value}\n\n"
    
    if len(valid_rates) > 0:
        message += "📈 STATISTICS:\n"
        message += f"• Max HR: {max(valid_rates)} BPM\n"
        message += f"• Min HR: {min(valid_rates)} BPM\n"
        message += f"• Data Points: {len(valid_rates)}\n"
        hr_std = np.std(valid_rates) if len(valid_rates) > 1 else 0
        message += f"• Variability: {hr_std:.2f}\n\n"
    
    message += "💡 HEALTH INSIGHTS:\n"
    for i, insight in enumerate(insights, 1):
        message += f"{i}. {insight}\n"
    
    message += f"\n⏰ Report generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    return message

def main():
    # Initialize session state variables
    if 'monitor' not in st.session_state:
        st.session_state.monitor = HeartRateMonitor()
        st.session_state.api_configured = False
        st.session_state.api_url = "http://192.168.0.102/api"
    
    if 'use_mock_data' not in st.session_state:
        st.session_state.use_mock_data = False
    
    # Header
    st.markdown('<h1 class="main-header">❤️ Real-time Heart Rate Monitor</h1>', unsafe_allow_html=True)
    
    # API Configuration Section
    with st.expander("API Configuration", expanded=not st.session_state.api_configured):
        st.subheader("Enter API URL")
        api_url = st.text_input("API Endpoint", value=st.session_state.api_url, 
                               placeholder="http://your-api-url-here/api")
        
        # Mock data option
        use_mock = st.checkbox("Use mock data for testing", value=st.session_state.use_mock_data)
        if use_mock != st.session_state.use_mock_data:
            st.session_state.use_mock_data = use_mock
            st.session_state.monitor.set_use_mock_data(use_mock)
            if use_mock:
                st.info("Using mock data for testing. Uncheck to use real API.")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Connect to API"):
                if api_url:
                    st.session_state.monitor.set_api_url(api_url)
                    st.session_state.api_url = api_url
                    
                    # Test the connection (only if not using mock data)
                    if not st.session_state.use_mock_data:
                        try:
                            response = requests.get(api_url, timeout=3)
                            if response.status_code == 200:
                                st.session_state.api_configured = True
                                st.success("✅ Successfully connected to API!")
                                st.rerun()
                            else:
                                st.error(f"❌ API returned status code: {response.status_code}")
                        except Exception as e:
                            st.error(f"❌ Connection failed: {str(e)}")
                    else:
                        st.session_state.api_configured = True
                        st.success("✅ Using mock data for testing!")
                        st.rerun()
                else:
                    st.error("Please enter a valid API URL")
        
        with col2:
            if st.button("Reset Connection"):
                st.session_state.api_configured = False
                st.session_state.monitor.data_history = []
                st.rerun()
    
    # If API is not configured, show instructions and stop execution
    if not st.session_state.api_configured:
        st.info("""
        ## Instructions:
        1. Enter your heart rate API URL in the field above
        2. Click 'Connect to API' to establish connection
        3. The dashboard will appear once connected
        
        Example API URL: `http://192.168.0.102/api`
        
        **Troubleshooting:**
        - Check if your sensor device is powered on
        - Verify the IP address is correct
        - Ensure your computer is on the same network
        - Try using mock data for testing while troubleshooting
        """)
    
    else:
        # Telegram configuration in sidebar
        with st.sidebar:
            st.header("Telegram Settings")
            patient_name = st.text_input("Patient Name", 
                                       placeholder="Enter patient name",
                                       help="This will be included in the report")
            telegram_token = st.text_input("Bot Token", type="password", 
                                          help="Get this from @BotFather on Telegram")
            telegram_chat_id = st.text_input("Chat ID", 
                                            help="Your Telegram user ID or group ID")
            
            st.header("Settings")
            refresh_rate = st.slider("Refresh rate (seconds)", 1, 10, 2)
            st.session_state.max_history = st.slider("Data points to keep", 50, 500, 100)
            st.session_state.monitor.max_history = st.session_state.max_history
            
            st.header("Current Connection")
            if st.session_state.use_mock_data:
                st.warning("Using Mock Data")
            else:
                st.success(f"Connected to: `{st.session_state.api_url}`")
            
            if st.button("Change API URL"):
                st.session_state.api_configured = False
                st.rerun()
            
            st.header("About")
            st.info("""
            This app monitors heart rate data from a sensor API.
            - Green status: Normal operation
            - Red status: No finger detected or connection issue
            - Data updates every few seconds
            """)
        
        # Main content
        col1, col2, col3, col4 = st.columns(4)
        
        # Fetch latest data
        latest_data = st.session_state.monitor.fetch_data()
        
        if latest_data:
            # Connection status
            with col1:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                if st.session_state.use_mock_data:
                    st.markdown('<span class="status-indicator" style="background-color: orange;"></span> MOCK DATA', unsafe_allow_html=True)
                    st.metric("API Status", "Mock Data", delta=None)
                else:
                    st.markdown('<span class="status-indicator status-online"></span> CONNECTED', unsafe_allow_html=True)
                    st.metric("API Status", "Online", delta=None)
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Current heart rate with animation
            with col2:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                heart_rate = latest_data['heart_rate']['current_bpm']
                status = st.session_state.monitor.get_current_status()
                
                if heart_rate > 0 and latest_data['sensor']['finger_detected']:
                    st.markdown(f'<div class="heart-animation">❤️</div>', unsafe_allow_html=True)
                    st.metric("Current BPM", f"{heart_rate}", delta=None)
                else:
                    st.markdown('❤️', unsafe_allow_html=True)
                    st.metric("Current BPM", "---", delta=None)
                
                st.caption(f"Status: {status}")
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Average heart rate
            with col3:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                avg_heart_rate = latest_data['heart_rate']['average_bpm']
                trend = st.session_state.monitor.get_heart_rate_trend()
                
                st.metric("Average BPM", f"{avg_heart_rate}" if avg_heart_rate > 0 else "---", 
                         delta=trend if trend != "No trend data" else None)
                st.caption(f"Trend: {trend}")
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Sensor status
            with col4:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                finger_detected = latest_data['sensor']['finger_detected']
                ir_value = latest_data['sensor']['ir_value']
                
                status_color = "🟢" if finger_detected else "🔴"
                st.metric("Finger Detection", f"{status_color} {'Detected' if finger_detected else 'Not Detected'}")
                st.metric("IR Value", f"{ir_value}")
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Telegram report button
            st.markdown("---")
            report_col1, report_col2 = st.columns([3, 1])
            
            with report_col2:
                st.markdown("### Send Report")
                if st.button("📤 Send Telegram Report", key="telegram_report", use_container_width=True):
                    if telegram_token and telegram_chat_id:
                        report_message = format_telegram_report(st.session_state.monitor, latest_data, patient_name)
                        if send_telegram_message(telegram_token, telegram_chat_id, report_message):
                            st.success("Report sent successfully via Telegram!")
                        else:
                            st.error("Failed to send report. Please check your token and chat ID.")
                    else:
                        st.error("Please provide both Telegram Bot Token and Chat ID in the sidebar")
            
            # Charts
            with report_col1:
                st.subheader("Real-time Monitoring")
                fig = create_heart_rate_chart(st.session_state.monitor.data_history)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Collecting data... Please wait.")
            
            # Statistics
            st.subheader("Statistics")
            stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
            
            if len(st.session_state.monitor.data_history) > 1:
                valid_rates = [d['heart_rate']['current_bpm'] for d in st.session_state.monitor.data_history 
                              if d['heart_rate']['current_bpm'] > 0]
                if valid_rates:
                    with stat_col1:
                        st.metric("Max BPM", f"{max(valid_rates)}")
                    with stat_col2:
                        st.metric("Min BPM", f"{min(valid_rates)}")
                    with stat_col3:
                        st.metric("Data Points", f"{len(valid_rates)}")
                    with stat_col4:
                        hr_std = np.std(valid_rates) if len(valid_rates) > 1 else 0
                        st.metric("Variability", f"{hr_std:.2f}")
                else:
                    st.info("No valid heart rate data yet")
            else:
                st.info("Collecting data...")
        
        else:
            # Connection failed
            with col1:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.markdown('<span class="status-indicator status-offline"></span> OFFLINE', unsafe_allow_html=True)
                st.metric("API Status", "Offline", delta=None)
                st.markdown('</div>', unsafe_allow_html=True)
            
            st.error("Unable to connect to the heart rate sensor API. Please check:")
            st.write("1. The device is powered on and connected to the network")
            st.write(f"2. The IP address is correct: {st.session_state.api_url}")
            st.write("3. The device is on the same network as this computer")
            st.write("4. Try using mock data for testing while troubleshooting")
            
            if st.button("Try to reconnect"):
                st.rerun()
        
        # Auto-refresh
        time.sleep(refresh_rate)
        st.rerun()

if __name__ == "__main__":
    main()