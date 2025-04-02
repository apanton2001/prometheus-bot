# HTML to Next.js/shadcn Component Conversion Guide

## Core Landing Page Components

### 1. Navigation Bar

**HTML Structure:**
```html
<nav class="navbar">
  <div class="logo">
    <img src="images/logo.png" alt="Logo">
  </div>
  <ul class="nav-links">
    <li><a href="#features">Features</a></li>
    <li><a href="#pricing">Pricing</a></li>
    <li><a href="#testimonials">Testimonials</a></li>
    <li><a href="#contact">Contact</a></li>
  </ul>
  <button class="login-btn">Login</button>
  <button class="signup-btn">Sign Up</button>
</nav>
```

**Next.js/shadcn Implementation:**
```tsx
// components/site/Navbar.tsx
import Link from "next/link";
import Image from "next/image";
import { Button } from "@/components/ui/button";
import {
  NavigationMenu,
  NavigationMenuItem,
  NavigationMenuLink,
  NavigationMenuList,
  navigationMenuTriggerStyle,
} from "@/components/ui/navigation-menu";

export function Navbar() {
  return (
    <header className="sticky top-0 z-40 w-full border-b bg-background">
      <div className="container flex h-16 items-center justify-between py-4">
        <Link href="/" className="flex items-center">
          <Image src="/images/logo.png" alt="Logo" width={120} height={36} />
        </Link>
        
        <NavigationMenu>
          <NavigationMenuList>
            <NavigationMenuItem>
              <Link href="#features" legacyBehavior passHref>
                <NavigationMenuLink className={navigationMenuTriggerStyle()}>
                  Features
                </NavigationMenuLink>
              </Link>
            </NavigationMenuItem>
            <NavigationMenuItem>
              <Link href="#pricing" legacyBehavior passHref>
                <NavigationMenuLink className={navigationMenuTriggerStyle()}>
                  Pricing
                </NavigationMenuLink>
              </Link>
            </NavigationMenuItem>
            <NavigationMenuItem>
              <Link href="#testimonials" legacyBehavior passHref>
                <NavigationMenuLink className={navigationMenuTriggerStyle()}>
                  Testimonials
                </NavigationMenuLink>
              </Link>
            </NavigationMenuItem>
            <NavigationMenuItem>
              <Link href="#contact" legacyBehavior passHref>
                <NavigationMenuLink className={navigationMenuTriggerStyle()}>
                  Contact
                </NavigationMenuLink>
              </Link>
            </NavigationMenuItem>
          </NavigationMenuList>
        </NavigationMenu>
        
        <div className="flex gap-2">
          <Button variant="outline" asChild>
            <Link href="/login">Login</Link>
          </Button>
          <Button asChild>
            <Link href="/register">Sign Up</Link>
          </Button>
        </div>
      </div>
    </header>
  );
}
```

### 2. Hero Section

**HTML Structure:**
```html
<section class="hero">
  <div class="hero-content">
    <h1>Algorithmic Trading Made Simple</h1>
    <p>Our sophisticated trading bot delivers 66.7% win rates with minimal drawdown.</p>
    <button class="cta-btn">Start Trading Now</button>
  </div>
  <div class="hero-image">
    <img src="images/trading-dashboard.png" alt="Trading Dashboard">
  </div>
</section>
```

**Next.js/shadcn Implementation:**
```tsx
// components/site/Hero.tsx
import Image from "next/image";
import Link from "next/link";
import { Button } from "@/components/ui/button";

export function Hero() {
  return (
    <section className="container px-4 py-16 md:py-24 lg:py-32">
      <div className="grid gap-6 lg:grid-cols-2 lg:gap-12 items-center">
        <div className="space-y-4">
          <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold tracking-tighter">
            Algorithmic Trading Made Simple
          </h1>
          <p className="text-xl text-muted-foreground">
            Our sophisticated trading bot delivers 66.7% win rates with minimal drawdown.
          </p>
          <div className="mt-6">
            <Button size="lg" asChild>
              <Link href="/register">Start Trading Now</Link>
            </Button>
          </div>
        </div>
        <div className="relative h-[400px] lg:h-[600px]">
          <Image 
            src="/images/trading-dashboard.png" 
            alt="Trading Dashboard" 
            fill 
            className="object-contain"
            priority
          />
        </div>
      </div>
    </section>
  );
}
```

### 3. Features Section

**HTML Structure:**
```html
<section id="features" class="features">
  <h2>Our Trading Bot Features</h2>
  <div class="feature-grid">
    <div class="feature-card">
      <div class="feature-icon">📈</div>
      <h3>Multi-Timeframe Analysis</h3>
      <p>Analyze market trends across 5m, 15m, 1h, and 4h timeframes for accurate signals.</p>
    </div>
    <!-- More feature cards -->
  </div>
</section>
```

**Next.js/shadcn Implementation:**
```tsx
// components/site/Features.tsx
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const features = [
  {
    icon: "📈",
    title: "Multi-Timeframe Analysis",
    description: "Analyze market trends across 5m, 15m, 1h, and 4h timeframes for accurate signals."
  },
  // Add more features here
];

export function Features() {
  return (
    <section id="features" className="bg-slate-50 dark:bg-slate-900 py-16 md:py-24">
      <div className="container px-4">
        <div className="text-center mb-12">
          <h2 className="text-3xl md:text-4xl font-bold">Our Trading Bot Features</h2>
        </div>
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {features.map((feature, index) => (
            <Card key={index} className="bg-white dark:bg-slate-800">
              <CardHeader>
                <div className="text-4xl mb-4">{feature.icon}</div>
                <CardTitle>{feature.title}</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">{feature.description}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
}
```

### 4. Pricing Tables

**HTML Structure:**
```html
<section id="pricing" class="pricing">
  <h2>Choose Your Trading Plan</h2>
  <div class="pricing-grid">
    <div class="pricing-card">
      <h3>Starter</h3>
      <div class="price">$49/month</div>
      <ul class="features-list">
        <li>Core trading strategy</li>
        <li>Up to 5 trading pairs</li>
        <li>Daily performance reports</li>
        <li>Email support</li>
      </ul>
      <button class="pricing-btn">Get Started</button>
    </div>
    <!-- More pricing cards -->
  </div>
</section>
```

**Next.js/shadcn Implementation:**
```tsx
// components/site/Pricing.tsx
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Check } from "lucide-react";

const pricingPlans = [
  {
    name: "Starter",
    price: "$49",
    description: "Perfect for beginners and casual traders",
    features: [
      "Core trading strategy",
      "Up to 5 trading pairs",
      "Daily performance reports",
      "Email support"
    ]
  },
  // Add Professional and Enterprise plans
];

export function Pricing() {
  return (
    <section id="pricing" className="py-16 md:py-24">
      <div className="container px-4">
        <div className="text-center mb-12">
          <h2 className="text-3xl md:text-4xl font-bold">Choose Your Trading Plan</h2>
        </div>
        <div className="grid gap-6 md:grid-cols-3">
          {pricingPlans.map((plan, index) => (
            <Card key={index} className={index === 1 ? "border-primary shadow-lg" : ""}>
              <CardHeader>
                <CardTitle>{plan.name}</CardTitle>
                <CardDescription>{plan.description}</CardDescription>
                <div className="mt-4 flex items-baseline text-3xl font-bold">
                  {plan.price}
                  <span className="ml-1 text-base font-normal text-muted-foreground">/month</span>
                </div>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2">
                  {plan.features.map((feature, i) => (
                    <li key={i} className="flex items-center">
                      <Check className="mr-2 h-4 w-4 text-primary" />
                      <span>{feature}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
              <CardFooter>
                <Button className="w-full" asChild>
                  <Link href="/register">Get Started</Link>
                </Button>
              </CardFooter>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
}
```

### 5. Contact Form

**HTML Structure:**
```html
<section id="contact" class="contact">
  <h2>Ready to Start Trading?</h2>
  <form class="contact-form">
    <div class="form-group">
      <label for="name">Name</label>
      <input type="text" id="name" name="name" required>
    </div>
    <div class="form-group">
      <label for="email">Email</label>
      <input type="email" id="email" name="email" required>
    </div>
    <div class="form-group">
      <label for="message">Message</label>
      <textarea id="message" name="message" rows="4"></textarea>
    </div>
    <button type="submit" class="submit-btn">Send Message</button>
  </form>
</section>
```

**Next.js with v0 Implementation:**
```tsx
// components/site/ContactForm.tsx
"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { useToast } from "@/components/ui/use-toast";

export function ContactForm() {
  const { toast } = useToast();
  const [isLoading, setIsLoading] = useState(false);
  
  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsLoading(true);
    
    const formData = new FormData(event.currentTarget);
    
    try {
      const response = await fetch("/v0/api/contact", {
        method: "POST",
        body: JSON.stringify({
          name: formData.get("name"),
          email: formData.get("email"),
          message: formData.get("message"),
        }),
        headers: {
          "Content-Type": "application/json",
        },
      });
      
      if (!response.ok) {
        throw new Error("Something went wrong");
      }
      
      toast({
        title: "Message sent!",
        description: "We'll get back to you as soon as possible.",
      });
      
      // Reset form
      event.currentTarget.reset();
    } catch (error) {
      toast({
        title: "Error",
        description: "There was a problem sending your message.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  }
  
  return (
    <section id="contact" className="bg-slate-50 dark:bg-slate-900 py-16 md:py-24">
      <div className="container px-4 max-w-md mx-auto">
        <div className="text-center mb-12">
          <h2 className="text-3xl md:text-4xl font-bold">Ready to Start Trading?</h2>
        </div>
        <form onSubmit={onSubmit} className="space-y-6">
          <div className="space-y-2">
            <Label htmlFor="name">Name</Label>
            <Input id="name" name="name" required />
          </div>
          <div className="space-y-2">
            <Label htmlFor="email">Email</Label>
            <Input id="email" name="email" type="email" required />
          </div>
          <div className="space-y-2">
            <Label htmlFor="message">Message</Label>
            <Textarea id="message" name="message" rows={4} />
          </div>
          <Button type="submit" className="w-full" disabled={isLoading}>
            {isLoading ? "Sending..." : "Send Message"}
          </Button>
        </form>
      </div>
    </section>
  );
}
```

## Main Page Integration

**Next.js Main Page:**
```tsx
// app/page.tsx
import { Navbar } from "@/components/site/Navbar";
import { Hero } from "@/components/site/Hero";
import { Features } from "@/components/site/Features";
import { Pricing } from "@/components/site/Pricing";
import { ContactForm } from "@/components/site/ContactForm";
import Footer from "@/components/site/Footer";

export default function Home() {
  return (
    <>
      <Navbar />
      <main>
        <Hero />
        <Features />
        <Pricing />
        <ContactForm />
      </main>
      <Footer />
    </>
  );
}
```

## v0 Function for Contact Form

```typescript
// /v0/api/contact.ts
import { type Config } from '@vercel/functions';

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { name, email, message } = req.body;
    
    // Validate input
    if (!name || !email) {
      return res.status(400).json({ error: 'Name and email are required' });
    }
    
    // Process contact form (example)
    // 1. Store in database
    // 2. Send notification email
    
    // For example, you might call a helper function:
    // await sendEmailNotification({
    //   to: "support@yourcompany.com",
    //   subject: "New Contact Form Submission",
    //   html: `<p>Name: ${name}</p><p>Email: ${email}</p><p>Message: ${message}</p>`,
    // });
    
    return res.status(200).json({ success: true });
  } catch (error) {
    console.error('Contact form error:', error);
    return res.status(500).json({ error: 'Internal server error' });
  }
}

export const config: Config = {
  runtime: 'edge',
};
```

## Implementation Steps

1. Set up Next.js project with shadcn/ui components
2. Create the UI components in the order shown above
3. Set up v0 functions for backend processing
4. Connect components to v0 endpoints
5. Style with custom theme colors (turquoise and tan)
6. Test all interactive elements and responsive behavior
7. Deploy to Vercel 