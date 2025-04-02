import Head from 'next/head';
import { useState } from 'react';
import styles from '../styles/Home.module.css';

export default function Home() {
  const [email, setEmail] = useState('');
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    // Handle form submission (you can add API call here later)
    console.log('Submitted email:', email);
    // For now just redirect to thank you page
    window.location.href = '/thank-you';
  };

  return (
    <div className={styles.container}>
      <Head>
        <title>Prometheus | Advanced Trading & Market Research Platform</title>
        <meta name="description" content="AI-powered platform for stock and crypto market research and automated trading" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main className={styles.main}>
        <div className={styles.hero}>
          <h1 className={styles.title}>
            Prometheus
          </h1>
          <p className={styles.description}>
            Advanced AI-Powered Trading & Market Research Platform
          </p>
          
          <div className={styles.cta}>
            <form onSubmit={handleSubmit} className={styles.signupForm}>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Enter your email"
                required
                className={styles.emailInput}
              />
              <button type="submit" className={styles.button}>
                Get Early Access
              </button>
            </form>
          </div>
        </div>

        <section className={styles.features}>
          <h2>Key Features</h2>
          <div className={styles.featureGrid}>
            <div className={styles.featureCard}>
              <h3>AI-Powered Market Analysis</h3>
              <p>Real-time insights and predictions based on advanced machine learning algorithms</p>
            </div>
            <div className={styles.featureCard}>
              <h3>Automated Trading</h3>
              <p>Set sophisticated trading rules and let our platform execute trades with precision</p>
            </div>
            <div className={styles.featureCard}>
              <h3>Stock & Crypto Research</h3>
              <p>Comprehensive research tools for both traditional stocks and cryptocurrency markets</p>
            </div>
            <div className={styles.featureCard}>
              <h3>Risk Management</h3>
              <p>Advanced risk assessment and portfolio management tools to protect your investments</p>
            </div>
          </div>
        </section>
      </main>

      <footer className={styles.footer}>
        <p>© {new Date().getFullYear()} Prometheus. All rights reserved.</p>
      </footer>
    </div>
  );
} 