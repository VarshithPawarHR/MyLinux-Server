import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from crewai import Agent, Task, Crew, Process
from langchain_google_genai import ChatGoogleGenerativeAI
import smtplib
from email.message import EmailMessage
from fpdf import FPDF
import os
import logging
import time
from dotenv import load_dotenv

# Load env vars
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Prometheus config
PROMETHEUS = "http://prometheus:9090"
CPU_QUERY = '100 - (avg by (instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)'
BATTERY_QUERY = 'node_battery_charge_percent'
STORAGE_QUERY = '100 - ((node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"}) * 100)'

# Env vars
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECIPIENT = os.getenv("EMAIL_RECIPIENT")

required_vars = {
    "GEMINI_API_KEY": GEMINI_API_KEY,
    "EMAIL_ADDRESS": EMAIL_ADDRESS,
    "EMAIL_PASSWORD": EMAIL_PASSWORD,
    "EMAIL_RECIPIENT": EMAIL_RECIPIENT
}

missing_vars = [k for k, v in required_vars.items() if not v]
if missing_vars:
    logger.error(f"Missing environment variables: {', '.join(missing_vars)}")
    exit(1)

# -----------------------------------
# Fetch Prometheus data
def fetch_prometheus_data(query, days=7, retries=3):
    end = int(datetime.now().timestamp())
    start = int((datetime.now() - timedelta(days=days)).timestamp())

    for attempt in range(retries):
        try:
            logger.info(f"Fetching data for: {query[:50]}... (try {attempt + 1}/{retries})")
            res = requests.get(
                f"{PROMETHEUS}/api/v1/query_range",
                params={"query": query, "start": start, "end": end, "step": "300"},
                timeout=30
            )
            res.raise_for_status()
            data = res.json()

            if 'data' not in data or 'result' not in data['data']:
                logger.warning(f"Invalid response for: {query}")
                return None

            result = data['data']['result']
            if not result:
                logger.warning(f"No data for: {query}")
                return None

            values = result[0]['values']
            if not values:
                logger.warning(f"Empty values for: {query}")
                return None

            df = pd.DataFrame(values, columns=["timestamp", "value"])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
            df['value'] = pd.to_numeric(df['value'], errors='coerce').dropna()

            if df.empty:
                logger.warning(f"All NaN for: {query}")
                return None

            logger.info(f"Fetched {len(df)} points for query")
            return df

        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
            time.sleep(5 * (attempt + 1))
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            time.sleep(5 * (attempt + 1))

    logger.error(f"Failed to fetch after {retries} attempts: {query}")
    return None

def get_all_metrics_data():
    cpu_df = fetch_prometheus_data(CPU_QUERY)
    battery_df = fetch_prometheus_data(BATTERY_QUERY)
    storage_df = fetch_prometheus_data(STORAGE_QUERY)
    return {'cpu': cpu_df, 'battery': battery_df, 'storage': storage_df}

# -----------------------------------
# Analysis
def analyze_metrics_data(data_dict):
    analysis = {}
    for metric_name, df in data_dict.items():
        if df is not None and not df.empty:
            stats = {
                'mean': df['value'].mean(),
                'median': df['value'].median(),
                'max': df['value'].max(),
                'min': df['value'].min(),
                'std': df['value'].std(),
                'percentile_95': df['value'].quantile(0.95),
                'percentile_5': df['value'].quantile(0.05),
                'total_samples': len(df),
                'peak_times': df[df['value'] > df['value'].quantile(0.95)]['timestamp'].dt.strftime('%Y-%m-%d %H:%M').tolist()[:5],
                'low_times': df[df['value'] < df['value'].quantile(0.05)]['timestamp'].dt.strftime('%Y-%m-%d %H:%M').tolist()[:5],
            }
            analysis[metric_name] = stats
        else:
            analysis[metric_name] = None
            logger.warning(f"No data for: {metric_name}")
    return analysis

# -----------------------------------
# Plot graphs
def plot_graphs(data_dict, analysis):
    available = [k for k, v in data_dict.items() if v is not None and not v.empty]
    n = len(available)

    if n == 0:
        logger.warning("No metrics to plot")
        plt.figure(figsize=(10, 6))
        plt.text(0.5, 0.5, 'No Data Available', ha='center', va='center', fontsize=20)
        plt.axis('off')
        plt.savefig('system_metrics_report.png')
        plt.close()
        return

    fig, axes = plt.subplots(n, 2, figsize=(15, 6 * n))
    if n == 1:
        axes = axes.reshape(1, -1)

    colors = {'cpu': '#2E8B57', 'battery': '#FFD700', 'storage': '#4682B4'}

    for i, metric in enumerate(available):
        df = data_dict[metric]
        stats = analysis[metric]
        color = colors.get(metric, '#333')

        ax1 = axes[i, 0]
        ax1.plot(df['timestamp'], df['value'], color=color)
        ax1.axhline(y=stats['mean'], color='red', linestyle='--', label=f"Mean {stats['mean']:.1f}%")
        ax1.fill_between(df['timestamp'], df['value'], alpha=0.3, color=color)
        ax1.set_title(f"{metric.upper()} Usage")
        ax1.legend()
        ax1.tick_params(axis='x', rotation=45)

        ax2 = axes[i, 1]
        ax2.hist(df['value'], bins=30, color=color, alpha=0.7)
        ax2.axvline(stats['mean'], color='red', linestyle='--')
        ax2.set_title(f"{metric.upper()} Distribution")

    plt.tight_layout()
    plt.savefig('system_metrics_report.png')
    plt.close()

# -----------------------------------
# PDF Report
class SystemReportPDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'Weekly System Metrics Report', ln=True, align='C')
        self.set_font('Arial', '', 10)
        self.cell(0, 5, f'Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', ln=True, align='C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', align='C')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, title, ln=True)
        self.ln(4)

    def chapter_body(self, body):
        self.set_font('Arial', '', 10)
        self.multi_cell(0, 6, body)
        self.ln()

    def add_summary(self, summary):
        self.chapter_title("Executive Summary")
        self.chapter_body(summary)

    def add_metric_analysis(self, metric_name, stats):
        self.chapter_title(f"{metric_name.upper()} Analysis")
        if stats is None:
            self.chapter_body("No data available.")
        else:
            body = f"""
Mean: {stats['mean']:.2f}%
Median: {stats['median']:.2f}%
Max: {stats['max']:.2f}%
Min: {stats['min']:.2f}%
Std: {stats['std']:.2f}%
95th Percentile: {stats['percentile_95']:.2f}%
5th Percentile: {stats['percentile_5']:.2f}%
Total Samples: {stats['total_samples']}

Peak Times: {', '.join(stats['peak_times'])}
Low Times: {', '.join(stats['low_times'])}
"""
            self.chapter_body(body)

    def add_insights(self, insights):
        self.chapter_title("AI Insights & Recommendations")
        self.chapter_body(insights)

    def add_graphs(self, img):
        if os.path.exists(img):
            self.add_page()
            self.chapter_title("Visual Analysis")
            self.image(img, x=10, y=40, w=190)

# -----------------------------------
# Email
def send_email(summary, pdf_file):
    msg = EmailMessage()
    msg['Subject'] = "Weekly System Metrics Report"
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = EMAIL_RECIPIENT

    msg.set_content(f"Hi,\n\nFind attached your weekly system report.\n\nSummary:\n{summary}\n\nRegards,\nYour Homelab System")

    with open(pdf_file, 'rb') as f:
        msg.add_attachment(f.read(), maintype='application', subtype='pdf', filename=os.path.basename(pdf_file))

    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.starttls()
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)

    logger.info("Email sent successfully!")

# -----------------------------------
# MAIN
def main():
    logger.info("Generating system report...")
    llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=GEMINI_API_KEY)

    # Agents
    analyst = Agent(role="System Analyst", goal="Analyze metrics", backstory="Expert analyst.", llm=llm)
    insight_agent = Agent(role="Optimization Specialist", goal="Generate insights", backstory="Optimization pro.", llm=llm)
    writer = Agent(role="Report Writer", goal="Write executive summary", backstory="Professional tech writer.", llm=llm)

    # Tasks
    data_task = Task(description="Analyze metrics data.", expected_output="Detailed analysis.", agent=analyst)
    insight_task = Task(description="Find trends & insights.", expected_output="Recommendations.", agent=insight_agent)
    write_task = Task(description="Write executive summary.", expected_output="Summary.", agent=writer)

    crew = Crew(agents=[analyst, insight_agent, writer], tasks=[data_task, insight_task, write_task], process=Process.sequential)

    data = get_all_metrics_data()
    analysis = analyze_metrics_data(data)

    if any(df is not None and not df.empty for df in data.values()):
        plot_graphs(data, analysis)

        context = "\n".join([f"{k}: Mean {v['mean']:.2f}%" for k, v in analysis.items() if v])
        result = crew.kickoff(inputs={"system_metrics": context})
        summary = getattr(result, 'output', str(result))
        insights = "CrewAI found potential optimizations."

        pdf = SystemReportPDF()
        pdf.add_page()
        pdf.add_summary(summary)
        for metric, stats in analysis.items():
            pdf.add_metric_analysis(metric, stats)
        pdf.add_insights(insights)
        pdf.add_graphs('system_metrics_report.png')

        pdf_name = f"weekly_report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
        pdf.output(pdf_name)

        send_email(summary, pdf_name)

        logger.info(f"Done! Report: {pdf_name}")
    else:
        logger.warning("No data fetched. Check Prometheus config.")

if __name__ == "__main__":
    main()
