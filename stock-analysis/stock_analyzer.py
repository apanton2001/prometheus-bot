#!/usr/bin/env python3
"""
Stock Analysis Tool - Analyzes stocks based on user preferences and fundamentals
"""
import argparse
import os
import json
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import requests
from concurrent.futures import ThreadPoolExecutor
import time

# Configuration
DEFAULT_CACHE_DIR = "cache"
API_KEY = os.environ.get("ALPHA_VANTAGE_API_KEY", "")
NEWS_API_KEY = os.environ.get("NEWS_API_KEY", "")

# Industry mappings - example mapping for healthcare/plastic surgery sector
INDUSTRY_KEYWORDS = {
    "plastic_surgery": [
        "plastic surgery", "cosmetic", "aesthetic", "medical devices", 
        "reconstructive", "dermatology", "beauty", "elective procedures"
    ],
    "technology": [
        "software", "hardware", "cloud", "semiconductor", "artificial intelligence",
        "machine learning", "saas", "internet", "technology"
    ],
    "electric_vehicles": [
        "electric vehicle", "ev", "battery", "autonomous", "charging",
        "lithium", "mobility", "transportation"
    ],
    # Add more industry mappings as needed
}

class StockAnalyzer:
    def __init__(self, cache_dir=DEFAULT_CACHE_DIR):
        """Initialize the stock analyzer with cache directory"""
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        
        # Track API call counts to avoid rate limiting
        self.api_call_count = 0
        self.api_call_reset_time = datetime.now()
        
    def find_companies_by_industry(self, industry_name, max_results=10):
        """
        Find companies that match the given industry keywords
        """
        if industry_name not in INDUSTRY_KEYWORDS:
            print(f"Industry '{industry_name}' not found in database")
            return []
            
        # In a real implementation, we would:
        # 1. Query a stock screening API or database
        # 2. Use INDUSTRY_KEYWORDS to filter companies
        # 3. Return a list of matching companies
        
        # For now, we'll use a hard-coded example for plastic surgery
        if industry_name == "plastic_surgery":
            return [
                {"symbol": "INMD", "name": "InMode Ltd.", "sector": "Healthcare", "industry": "Medical Devices"},
                {"symbol": "SIEN", "name": "Sientra, Inc.", "sector": "Healthcare", "industry": "Medical Devices"},
                {"symbol": "ABBV", "name": "AbbVie Inc.", "sector": "Healthcare", "industry": "Pharmaceuticals"},
                {"symbol": "EW", "name": "Edwards Lifesciences", "sector": "Healthcare", "industry": "Medical Devices"},
                {"symbol": "ALGN", "name": "Align Technology", "sector": "Healthcare", "industry": "Medical Devices"},
                {"symbol": "EBS", "name": "Emergent BioSolutions", "sector": "Healthcare", "industry": "Biotechnology"},
                {"symbol": "CMLS", "name": "Cumulus Media", "sector": "Healthcare", "industry": "Medical Devices"}
            ]
        
        # Default fallback - empty list
        return []
    
    def get_stock_data(self, symbol, period="2y"):
        """
        Get historical stock data and cache it
        """
        cache_file = f"{self.cache_dir}/{symbol}_{period}.json"
        
        # Check cache first
        if os.path.exists(cache_file):
            with open(cache_file, 'r') as f:
                cache_data = json.load(f)
                # Check if cache is recent (less than 1 day old)
                if datetime.now().timestamp() - cache_data['timestamp'] < 86400:
                    print(f"Using cached data for {symbol}")
                    return pd.DataFrame(cache_data['data'])
        
        # Fetch new data
        print(f"Fetching data for {symbol}...")
        stock = yf.Ticker(symbol)
        hist = stock.history(period=period)
        
        # Cache the data
        cache_data = {
            'timestamp': datetime.now().timestamp(),
            'data': hist.reset_index().to_dict('records')
        }
        with open(cache_file, 'w') as f:
            json.dump(cache_data, f)
        
        return hist
    
    def get_company_fundamentals(self, symbol):
        """
        Get fundamental data for a company
        """
        try:
            self._check_api_rate_limit()
            stock = yf.Ticker(symbol)
            
            # Basic company info
            info = stock.info
            
            # Financial data
            try:
                balance_sheet = stock.balance_sheet
                income_stmt = stock.income_stmt
                cash_flow = stock.cashflow
                
                # Calculate key financial metrics
                metrics = {
                    "Market Cap": info.get('marketCap', 'N/A'),
                    "P/E Ratio": info.get('trailingPE', 'N/A'),
                    "EPS": info.get('trailingEps', 'N/A'),
                    "Dividend Yield": info.get('dividendYield', 'N/A'),
                    "52 Week High": info.get('fiftyTwoWeekHigh', 'N/A'),
                    "52 Week Low": info.get('fiftyTwoWeekLow', 'N/A'),
                    "50-Day MA": info.get('fiftyDayAverage', 'N/A'),
                    "200-Day MA": info.get('twoHundredDayAverage', 'N/A'),
                    "Profit Margin": info.get('profitMargins', 'N/A'),
                    "Return on Equity": info.get('returnOnEquity', 'N/A'),
                    "Revenue Growth": info.get('revenueGrowth', 'N/A'),
                    "Debt to Equity": info.get('debtToEquity', 'N/A'),
                }
                
                return {
                    "symbol": symbol,
                    "name": info.get('shortName', symbol),
                    "sector": info.get('sector', 'Unknown'),
                    "industry": info.get('industry', 'Unknown'),
                    "description": info.get('longBusinessSummary', 'No description available'),
                    "metrics": metrics,
                    "recommendation": info.get('recommendationKey', 'Unknown')
                }
                
            except Exception as e:
                print(f"Error getting financial data for {symbol}: {e}")
                return {
                    "symbol": symbol,
                    "name": info.get('shortName', symbol),
                    "sector": info.get('sector', 'Unknown'),
                    "industry": info.get('industry', 'Unknown'),
                    "description": info.get('longBusinessSummary', 'No description available'),
                    "metrics": {},
                    "recommendation": 'Unknown'
                }
                
        except Exception as e:
            print(f"Error analyzing {symbol}: {e}")
            return {"symbol": symbol, "error": str(e)}
    
    def calculate_technical_indicators(self, df):
        """
        Calculate technical indicators for a stock
        """
        # Make a copy to avoid SettingWithCopyWarning
        df = df.copy()
        
        # Moving Averages
        df['MA50'] = df['Close'].rolling(window=50).mean()
        df['MA200'] = df['Close'].rolling(window=200).mean()
        
        # Relative Strength Index (RSI)
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # Bollinger Bands
        df['BB_middle'] = df['Close'].rolling(window=20).mean()
        df['BB_upper'] = df['BB_middle'] + 2 * df['Close'].rolling(window=20).std()
        df['BB_lower'] = df['BB_middle'] - 2 * df['Close'].rolling(window=20).std()
        
        # MACD
        df['EMA12'] = df['Close'].ewm(span=12, adjust=False).mean()
        df['EMA26'] = df['Close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = df['EMA12'] - df['EMA26']
        df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        
        return df
    
    def analyze_stock(self, symbol, period="2y"):
        """
        Comprehensive analysis of a single stock
        """
        # Get stock data and calculate indicators
        data = self.get_stock_data(symbol, period)
        data_with_indicators = self.calculate_technical_indicators(data)
        
        # Get fundamentals
        fundamentals = self.get_company_fundamentals(symbol)
        
        # Calculate trend strength
        last_price = data_with_indicators['Close'].iloc[-1]
        ma50 = data_with_indicators['MA50'].iloc[-1]
        ma200 = data_with_indicators['MA200'].iloc[-1]
        rsi = data_with_indicators['RSI'].iloc[-1]
        
        # Determine trend
        trend = "Neutral"
        if last_price > ma50 and ma50 > ma200:
            trend = "Strong Bullish"
        elif last_price > ma50:
            trend = "Bullish"
        elif last_price < ma50 and ma50 < ma200:
            trend = "Strong Bearish"
        elif last_price < ma50:
            trend = "Bearish"
        
        # RSI interpretation
        rsi_signal = "Neutral"
        if rsi > 70:
            rsi_signal = "Overbought"
        elif rsi < 30:
            rsi_signal = "Oversold"
        
        # Calculate volatility
        volatility = data['Close'].pct_change().std() * np.sqrt(252) * 100  # Annualized volatility in %
        
        # Calculate returns
        returns = {
            "1-month": self._calculate_return(data, 30),
            "3-month": self._calculate_return(data, 90),
            "6-month": self._calculate_return(data, 180),
            "1-year": self._calculate_return(data, 365),
        }
        
        # Calculate risk metrics
        max_drawdown = self._calculate_max_drawdown(data) * 100  # In %
        
        # Return analysis
        analysis = {
            "symbol": symbol,
            "company_info": fundamentals,
            "technical": {
                "trend": trend,
                "rsi": rsi,
                "rsi_signal": rsi_signal,
                "last_price": last_price,
                "ma50": ma50,
                "ma200": ma200,
                "volatility": volatility,
            },
            "returns": returns,
            "risk": {
                "max_drawdown": max_drawdown,
                "volatility": volatility,
            },
            "data": data_with_indicators
        }
        
        return analysis
    
    def generate_report(self, analysis, output_format="text"):
        """
        Generate a report from stock analysis
        """
        if output_format == "text":
            report = []
            report.append(f"=== Analysis Report for {analysis['symbol']} ===")
            report.append(f"Company: {analysis['company_info']['name']}")
            report.append(f"Sector: {analysis['company_info']['sector']}")
            report.append(f"Industry: {analysis['company_info']['industry']}")
            report.append("\nDescription:")
            report.append(analysis['company_info']['description'])
            
            report.append("\nFundamental Metrics:")
            for k, v in analysis['company_info']['metrics'].items():
                if isinstance(v, float):
                    report.append(f"  {k}: {v:.2f}")
                else:
                    report.append(f"  {k}: {v}")
            
            report.append("\nTechnical Analysis:")
            report.append(f"  Trend: {analysis['technical']['trend']}")
            report.append(f"  Current Price: ${analysis['technical']['last_price']:.2f}")
            report.append(f"  50-Day MA: ${analysis['technical']['ma50']:.2f}")
            report.append(f"  200-Day MA: ${analysis['technical']['ma200']:.2f}")
            report.append(f"  RSI: {analysis['technical']['rsi']:.2f} ({analysis['technical']['rsi_signal']})")
            report.append(f"  Volatility (Annualized): {analysis['technical']['volatility']:.2f}%")
            
            report.append("\nPerformance:")
            for period, ret in analysis['returns'].items():
                report.append(f"  {period}: {ret:.2f}%")
            
            report.append("\nRisk Assessment:")
            report.append(f"  Maximum Drawdown: {analysis['risk']['max_drawdown']:.2f}%")
            report.append(f"  Volatility: {analysis['risk']['volatility']:.2f}%")
            
            report.append("\nAnalyst Recommendation:")
            report.append(f"  {analysis['company_info']['recommendation']}")
            
            return "\n".join(report)
        
        elif output_format == "json":
            return json.dumps(analysis, default=str, indent=2)
        
        elif output_format == "html":
            # Simple HTML report
            html = f"""
            <html>
            <head>
                <title>Analysis for {analysis['symbol']}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; }}
                    h1, h2, h3 {{ color: #333; }}
                    .metrics {{ display: flex; flex-wrap: wrap; }}
                    .metric {{ margin: 10px; padding: 15px; background: #f5f5f5; border-radius: 5px; min-width: 150px; }}
                    .positive {{ color: green; }}
                    .negative {{ color: red; }}
                    .neutral {{ color: gray; }}
                </style>
            </head>
            <body>
                <h1>{analysis['company_info']['name']} ({analysis['symbol']})</h1>
                <p><strong>Sector:</strong> {analysis['company_info']['sector']} | <strong>Industry:</strong> {analysis['company_info']['industry']}</p>
                
                <h2>Company Description</h2>
                <p>{analysis['company_info']['description']}</p>
                
                <h2>Fundamental Metrics</h2>
                <div class="metrics">
            """
            
            for k, v in analysis['company_info']['metrics'].items():
                if isinstance(v, float):
                    html += f'<div class="metric"><strong>{k}:</strong> {v:.2f}</div>'
                else:
                    html += f'<div class="metric"><strong>{k}:</strong> {v}</div>'
            
            html += f"""
                </div>
                
                <h2>Technical Analysis</h2>
                <div class="metrics">
                    <div class="metric"><strong>Trend:</strong> <span class="{'positive' if 'Bullish' in analysis['technical']['trend'] else 'negative' if 'Bearish' in analysis['technical']['trend'] else 'neutral'}">{analysis['technical']['trend']}</span></div>
                    <div class="metric"><strong>Current Price:</strong> ${analysis['technical']['last_price']:.2f}</div>
                    <div class="metric"><strong>50-Day MA:</strong> ${analysis['technical']['ma50']:.2f}</div>
                    <div class="metric"><strong>200-Day MA:</strong> ${analysis['technical']['ma200']:.2f}</div>
                    <div class="metric"><strong>RSI:</strong> {analysis['technical']['rsi']:.2f} ({analysis['technical']['rsi_signal']})</div>
                    <div class="metric"><strong>Volatility:</strong> {analysis['technical']['volatility']:.2f}%</div>
                </div>
                
                <h2>Performance</h2>
                <div class="metrics">
            """
            
            for period, ret in analysis['returns'].items():
                html += f'<div class="metric"><strong>{period}:</strong> <span class="{"positive" if ret > 0 else "negative"}">{ret:.2f}%</span></div>'
            
            html += f"""
                </div>
                
                <h2>Risk Assessment</h2>
                <div class="metrics">
                    <div class="metric"><strong>Maximum Drawdown:</strong> {analysis['risk']['max_drawdown']:.2f}%</div>
                    <div class="metric"><strong>Volatility:</strong> {analysis['risk']['volatility']:.2f}%</div>
                </div>
                
                <h2>Analyst Recommendation</h2>
                <p>{analysis['company_info']['recommendation']}</p>
            </body>
            </html>
            """
            return html
    
    def plot_stock_charts(self, analysis, output_file=None):
        """
        Generate charts for the stock analysis
        """
        data = analysis['data']
        symbol = analysis['symbol']
        
        # Create subplots
        fig, axs = plt.subplots(3, 1, figsize=(12, 15), gridspec_kw={'height_ratios': [3, 1, 1]})
        
        # Price and Moving Averages
        axs[0].plot(data.index, data['Close'], label='Close Price')
        axs[0].plot(data.index, data['MA50'], label='50-day MA', alpha=0.7)
        axs[0].plot(data.index, data['MA200'], label='200-day MA', alpha=0.7)
        axs[0].fill_between(data.index, data['BB_lower'], data['BB_upper'], alpha=0.1, color='blue')
        axs[0].set_title(f'{symbol} Price History')
        axs[0].set_ylabel('Price ($)')
        axs[0].legend()
        axs[0].grid(True, alpha=0.3)
        
        # Volume
        axs[1].bar(data.index, data['Volume'], width=1, alpha=0.5, color='blue')
        axs[1].set_title('Volume')
        axs[1].set_ylabel('Volume')
        axs[1].grid(True, alpha=0.3)
        
        # RSI
        axs[2].plot(data.index, data['RSI'], label='RSI', color='purple')
        axs[2].axhline(y=70, color='r', linestyle='-', alpha=0.3)
        axs[2].axhline(y=30, color='g', linestyle='-', alpha=0.3)
        axs[2].set_title('Relative Strength Index (RSI)')
        axs[2].set_ylabel('RSI')
        axs[2].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if output_file:
            plt.savefig(output_file)
            plt.close()
            return output_file
        else:
            plt.show()
            return None
    
    def batch_analyze_stocks(self, symbols, parallel=True):
        """
        Analyze multiple stocks in parallel
        """
        if parallel:
            with ThreadPoolExecutor(max_workers=5) as executor:
                results = list(executor.map(self.analyze_stock, symbols))
        else:
            results = [self.analyze_stock(symbol) for symbol in symbols]
        
        return {result['symbol']: result for result in results}
    
    def find_investment_opportunities(self, industry, market_cap_min=None, market_cap_max=None):
        """
        Find investment opportunities based on filters
        """
        # Get companies in the industry
        companies = self.find_companies_by_industry(industry)
        
        if not companies:
            return []
        
        # Filter by market cap if specified
        if market_cap_min or market_cap_max:
            filtered_companies = []
            for company in companies:
                # Get fundamentals to check market cap
                fundamentals = self.get_company_fundamentals(company['symbol'])
                market_cap = fundamentals.get('metrics', {}).get('Market Cap', 0)
                
                # Apply filters
                if isinstance(market_cap, (int, float)):
                    if market_cap_min and market_cap < market_cap_min:
                        continue
                    if market_cap_max and market_cap > market_cap_max:
                        continue
                
                filtered_companies.append(company)
            
            companies = filtered_companies
        
        # Analyze all companies
        symbols = [company['symbol'] for company in companies]
        analyses = self.batch_analyze_stocks(symbols)
        
        # Score companies based on fundamentals and technicals
        scored_companies = []
        for symbol, analysis in analyses.items():
            score = self._calculate_investment_score(analysis)
            
            scored_companies.append({
                'symbol': symbol,
                'name': analysis['company_info']['name'],
                'sector': analysis['company_info']['sector'],
                'industry': analysis['company_info']['industry'],
                'score': score,
                'analysis': analysis
            })
        
        # Sort by score (descending)
        scored_companies.sort(key=lambda x: x['score'], reverse=True)
        
        return scored_companies
    
    def _calculate_investment_score(self, analysis):
        """
        Calculate an investment score based on analysis
        """
        score = 50  # Start with neutral score
        
        # Technical factors (up to 25 points)
        if analysis['technical']['trend'] == 'Strong Bullish':
            score += 15
        elif analysis['technical']['trend'] == 'Bullish':
            score += 10
        elif analysis['technical']['trend'] == 'Bearish':
            score -= 10
        elif analysis['technical']['trend'] == 'Strong Bearish':
            score -= 15
        
        # RSI (up to 10 points)
        rsi = analysis['technical']['rsi']
        if 40 <= rsi <= 60:  # Neutral is good for long-term
            score += 10
        elif 30 <= rsi < 40 or 60 < rsi <= 70:
            score += 5
        elif rsi < 30:  # Oversold might be good entry
            score += 7
        
        # Performance (up to 25 points)
        year_return = analysis['returns']['1-year']
        if year_return > 30:
            score += 20
        elif year_return > 15:
            score += 15
        elif year_return > 0:
            score += 10
        elif year_return > -15:
            score += 5
        
        # Fundamentals (up to 25 points)
        try:
            metrics = analysis['company_info']['metrics']
            
            # P/E ratio
            pe = metrics.get('P/E Ratio')
            if isinstance(pe, (int, float)) and pe > 0:
                if 5 < pe < 25:
                    score += 10
                elif 25 <= pe < 40:
                    score += 5
            
            # Profit Margin
            profit_margin = metrics.get('Profit Margin')
            if isinstance(profit_margin, (int, float)) and profit_margin > 0:
                if profit_margin > 0.2:
                    score += 10
                elif profit_margin > 0.1:
                    score += 5
            
            # Debt to Equity
            debt_equity = metrics.get('Debt to Equity')
            if isinstance(debt_equity, (int, float)):
                if debt_equity < 0.5:
                    score += 5
                elif debt_equity < 1:
                    score += 3
                elif debt_equity > 2:
                    score -= 5
        except:
            # If metrics calculation fails, don't add/subtract points
            pass
        
        # Risk adjustment
        max_drawdown = analysis['risk']['max_drawdown']
        if max_drawdown > 40:
            score -= 15
        elif max_drawdown > 25:
            score -= 10
        elif max_drawdown > 15:
            score -= 5
        
        # Cap score between 0 and 100
        return max(0, min(100, score))
    
    def _calculate_return(self, data, days):
        """Calculate return over a period"""
        if len(data) <= days:
            return 0
        
        current_price = data['Close'].iloc[-1]
        past_price = data['Close'].iloc[-min(days, len(data)-1)]
        
        return ((current_price / past_price) - 1) * 100
    
    def _calculate_max_drawdown(self, data):
        """Calculate maximum drawdown"""
        # Calculate the cumulative maximum
        running_max = data['Close'].cummax()
        # Calculate the drawdown
        drawdown = (data['Close'] - running_max) / running_max
        # Get the maximum drawdown
        max_drawdown = drawdown.min()
        
        return max_drawdown
    
    def _check_api_rate_limit(self):
        """Check API rate limit and wait if necessary"""
        current_time = datetime.now()
        
        # Reset counter if a minute has passed
        if (current_time - self.api_call_reset_time).total_seconds() > 60:
            self.api_call_count = 0
            self.api_call_reset_time = current_time
        
        # If we're near the rate limit, wait
        if self.api_call_count >= 5:  # Most free APIs have 5-10 calls per minute limit
            wait_time = 60 - (current_time - self.api_call_reset_time).total_seconds()
            if wait_time > 0:
                print(f"Rate limit reached, waiting {wait_time:.1f} seconds...")
                time.sleep(wait_time)
                self.api_call_count = 0
                self.api_call_reset_time = datetime.now()
        
        self.api_call_count += 1


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Stock Analysis Tool')
    
    parser.add_argument('-m', '--mode',
                      help='Analysis mode (single, industry, portfolio)',
                      type=str, choices=['single', 'industry', 'portfolio'],
                      default='single')
    
    parser.add_argument('-s', '--symbol',
                      help='Stock symbol to analyze (for single mode)',
                      type=str)
    
    parser.add_argument('-i', '--industry',
                      help='Industry to analyze (for industry mode)',
                      type=str, choices=list(INDUSTRY_KEYWORDS.keys()))
    
    parser.add_argument('-p', '--portfolio',
                      help='Portfolio file path (for portfolio mode)',
                      type=str)
    
    parser.add_argument('-o', '--output',
                      help='Output format (text, json, html)',
                      type=str, choices=['text', 'json', 'html'],
                      default='text')
    
    parser.add_argument('-c', '--chart',
                      help='Generate charts',
                      action='store_true')
    
    parser.add_argument('--min-cap',
                      help='Minimum market cap (in billions)',
                      type=float)
    
    parser.add_argument('--max-cap',
                      help='Maximum market cap (in billions)',
                      type=float)
    
    return parser.parse_args()


def main():
    """Main function"""
    args = parse_args()
    
    analyzer = StockAnalyzer()
    
    if args.mode == 'single':
        if not args.symbol:
            print("Error: Symbol required for single mode")
            return
        
        print(f"Analyzing {args.symbol}...")
        analysis = analyzer.analyze_stock(args.symbol)
        report = analyzer.generate_report(analysis, args.output)
        
        if args.output == 'text':
            print(report)
        elif args.output == 'json':
            print(report)
        elif args.output == 'html':
            output_file = f"{analysis['symbol']}_report.html"
            with open(output_file, 'w') as f:
                f.write(report)
            print(f"Report saved to {output_file}")
        
        if args.chart:
            chart_file = f"{analysis['symbol']}_chart.png"
            analyzer.plot_stock_charts(analysis, chart_file)
            print(f"Chart saved to {chart_file}")
    
    elif args.mode == 'industry':
        if not args.industry:
            print("Error: Industry required for industry mode")
            return
        
        print(f"Finding investment opportunities in {args.industry}...")
        min_cap = args.min_cap * 1e9 if args.min_cap else None
        max_cap = args.max_cap * 1e9 if args.max_cap else None
        
        opportunities = analyzer.find_investment_opportunities(args.industry, min_cap, max_cap)
        
        if not opportunities:
            print(f"No investment opportunities found in {args.industry}")
            return
        
        print(f"\nTop investment opportunities in {args.industry}:")
        for i, opp in enumerate(opportunities[:5], 1):  # Show top 5
            print(f"{i}. {opp['symbol']} - {opp['name']} (Score: {opp['score']}/100)")
        
        # Generate detailed report for the top opportunity
        top_opp = opportunities[0]
        print(f"\nDetailed analysis for top pick: {top_opp['symbol']}")
        report = analyzer.generate_report(top_opp['analysis'], args.output)
        
        if args.output == 'text':
            print(report)
        elif args.output == 'json':
            print(report)
        elif args.output == 'html':
            output_file = f"{top_opp['symbol']}_report.html"
            with open(output_file, 'w') as f:
                f.write(report)
            print(f"Report saved to {output_file}")
        
        if args.chart:
            chart_file = f"{top_opp['symbol']}_chart.png"
            analyzer.plot_stock_charts(top_opp['analysis'], chart_file)
            print(f"Chart saved to {chart_file}")
    
    elif args.mode == 'portfolio':
        if not args.portfolio:
            print("Error: Portfolio file required for portfolio mode")
            return
        
        try:
            with open(args.portfolio, 'r') as f:
                portfolio = json.load(f)
            
            symbols = portfolio.get('symbols', [])
            if not symbols:
                print("Error: No symbols found in portfolio file")
                return
            
            print(f"Analyzing portfolio of {len(symbols)} stocks...")
            analyses = analyzer.batch_analyze_stocks(symbols)
            
            # Print summary
            print("\nPortfolio Summary:")
            total_score = 0
            for symbol, analysis in analyses.items():
                score = analyzer._calculate_investment_score(analysis)
                total_score += score
                print(f"{symbol}: Score {score}/100, YTD Return: {analysis['returns']['1-year']:.2f}%")
            
            avg_score = total_score / len(analyses)
            print(f"\nAverage Portfolio Score: {avg_score:.2f}/100")
            
            # Generate detailed reports if requested
            if args.output != 'text' or args.chart:
                for symbol, analysis in analyses.items():
                    if args.output != 'text':
                        report = analyzer.generate_report(analysis, args.output)
                        output_file = f"{symbol}_report.{args.output}"
                        with open(output_file, 'w') as f:
                            f.write(report)
                    
                    if args.chart:
                        chart_file = f"{symbol}_chart.png"
                        analyzer.plot_stock_charts(analysis, chart_file)
                
                print(f"Reports and charts saved to current directory")
        
        except Exception as e:
            print(f"Error analyzing portfolio: {e}")
    
    print("\nAnalysis complete!")


if __name__ == "__main__":
    main() 