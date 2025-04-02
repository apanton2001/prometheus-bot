import Head from 'next/head';
import Link from 'next/link';
import styles from '../styles/Home.module.css';

export default function ThankYou() {
  return (
    <div className={styles.container}>
      <Head>
        <title>Thank You | Prometheus</title>
        <meta name="description" content="Thank you for your interest in Prometheus" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main className={styles.main}>
        <div className={styles.hero}>
          <h1 className={styles.title}>Thank You!</h1>
          <p className={styles.description}>
            We've received your request for early access to Prometheus.
          </p>
          <p className={styles.description}>
            We'll be in touch soon with more information about our launch and how you can get started.
          </p>
          
          <div className={styles.cta} style={{ marginTop: '2rem' }}>
            <Link href="/">
              <div className={styles.button}>
                Return to Home
              </div>
            </Link>
          </div>
        </div>
      </main>

      <footer className={styles.footer}>
        <p>© {new Date().getFullYear()} Prometheus. All rights reserved.</p>
      </footer>
    </div>
  );
} 