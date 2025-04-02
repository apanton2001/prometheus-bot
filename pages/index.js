import Head from 'next/head'
import styles from '../styles/Home.module.css'

export default function Home() {
  return (
    <div className={styles.container}>
      <Head>
        <title>Prometheus Bot</title>
        <meta name="description" content="Advanced trading algorithms for consistent returns" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main className={styles.main}>
        <h1 className={styles.title}>
          Welcome to <span className={styles.highlight}>Prometheus Bot</span>
        </h1>

        <p className={styles.description}>
          Sophisticated algorithmic trading with 66.7% win rate and minimal drawdown
        </p>

        <div className={styles.grid}>
          <a href="#features" className={styles.card}>
            <h2>Features &rarr;</h2>
            <p>Learn about the advanced capabilities of our trading algorithms.</p>
          </a>

          <a href="#performance" className={styles.card}>
            <h2>Performance &rarr;</h2>
            <p>See our impressive track record and consistent returns.</p>
          </a>

          <a href="#signup" className={styles.card}>
            <h2>Join Beta &rarr;</h2>
            <p>Get early access to our trading platform with special pricing.</p>
          </a>
        </div>
      </main>

      <footer className={styles.footer}>
        <p>&copy; 2025 Prometheus Bot. All rights reserved.</p>
      </footer>
    </div>
  )
} 