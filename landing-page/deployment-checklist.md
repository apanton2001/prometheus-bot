# PrometheusAI Landing Page Deployment Checklist

## 1. Development Environment Setup

- [ ] Clone the Next.js SaaS starter template
  ```bash
  git clone https://github.com/nextjs/saas-starter.git prometheusai
  cd prometheusai
  ```

- [ ] Install dependencies
  ```bash
  pnpm install
  ```

- [ ] Set up PostgreSQL database
  ```bash
  pnpm db:setup
  pnpm db:migrate
  ```

- [ ] Create .env file with required variables
  ```
  DATABASE_URL=postgresql://username:password@localhost:5432/prometheusai
  STRIPE_SECRET_KEY=sk_test_...
  STRIPE_WEBHOOK_SECRET=whsec_...
  AUTH_SECRET=random_string_generated_with_openssl
  BASE_URL=http://localhost:3000
  ```

- [ ] Run development server to verify setup
  ```bash
  pnpm dev
  ```

## 2. Component Migration

### Landing Page Components

- [ ] **Navbar**: Convert to `app/components/landing/navbar.tsx`
  - Implement mobile menu with Sheet component
  - Update navigation links with our pages

- [ ] **Hero Section**: Update `app/page.tsx`
  - Integrate turquoise and tan color scheme
  - Add our hero content, stats, and CTA buttons
  - Add trading dashboard screenshot

- [ ] **Features Section**: Create `app/components/landing/features.tsx`
  - Convert feature cards using shadcn/ui Card component
  - Implement feature icons with proper styling

- [ ] **How It Works**: Create `app/components/landing/how-it-works.tsx`
  - Implement step component with custom styling
  - Add process arrows between steps

- [ ] **Pricing Section**: Update `app/pricing/page.tsx`
  - Configure our four tiers (Free, Starter, Professional, Enterprise)
  - Add "Performance Fee Option" section
  - Connect to Stripe products/prices

- [ ] **Testimonials**: Create `app/components/landing/testimonials.tsx`
  - Implement testimonial cards with customer photos
  - Add carousel functionality if needed

- [ ] **FAQ Section**: Create `app/components/landing/faq.tsx`
  - Convert FAQ items to Accordion component
  - Populate with our questions and answers

- [ ] **Signup Form**: Update `app/register/page.tsx`
  - Add trading experience and plan selection fields
  - Implement form validation
  - Connect to API route for data handling

- [ ] **Footer**: Update `app/components/landing/footer.tsx`
  - Implement our footer columns and links
  - Add social media links
  - Add legal disclaimers

### Dashboard Components

- [ ] **Dashboard Overview**: Update `app/dashboard/page.tsx`
  - Design trading performance dashboard
  - Add portfolio value chart
  - Create trading statistics display

- [ ] **Strategy Configuration**: Create `app/dashboard/strategies/page.tsx`
  - Implement strategy parameter controls
  - Add trading pair selection

- [ ] **Account Settings**: Update `app/dashboard/settings/page.tsx`
  - Add API key management
  - Add notification preferences

## 3. API Routes & Backend

- [ ] **Registration API**: Create/update `app/api/register/route.ts`
  - Implement form validation with Zod
  - Store user data in PostgreSQL
  - Send welcome emails

- [ ] **Subscription Management**: Update Stripe integration
  - Configure webhook handler for subscription events
  - Set up subscription status checking

- [ ] **Authentication**: Configure auth system
  - Set up JWT token handling
  - Configure user roles and permissions
  - Implement protected routes

## 4. Design & Styling

- [ ] **Color Scheme**: Update `app/globals.css`
  - Set primary color to Pantone Turquoise (#40E0D0)
  - Set secondary color to Light Tan (#F5F5DC)

- [ ] **Typography**: Configure font settings
  - Keep Inter as the primary font
  - Adjust font weights and sizes

- [ ] **Component Styling**: Update shadcn/ui theme
  - Customize button styling
  - Adjust card styling
  - Update form input appearance

## 5. Testing

- [ ] **Functionality Testing**
  - Test user registration flow
  - Test Stripe checkout process
  - Verify JWT authentication works correctly

- [ ] **Responsive Design**
  - Test on mobile devices
  - Test on tablets
  - Test on desktop browsers

- [ ] **Performance Testing**
  - Run Lighthouse audit
  - Check page load times
  - Optimize images and assets

## 6. Deployment Preparation

- [ ] **Configure Stripe**
  - Create products and price points in Stripe dashboard
  - Set up webhook endpoint
  - Test checkout flow

- [ ] **Set Up GitHub Repository**
  - Create new repository 
  - Push codebase to repository
  - Configure GitHub Actions for CI/CD

- [ ] **Environmental Variables**
  - Create production .env variables
  - Set up secrets in GitHub/Vercel

## 7. Vercel Deployment

- [ ] **Connect Vercel to GitHub**
  - Link repository to Vercel project
  - Configure build settings

- [ ] **Configure Domain**
  - Set up custom domain
  - Configure SSL

- [ ] **Deploy Production**
  - Run production build
  - Monitor deployment logs
  - Verify site is working correctly

## 8. Post-Deployment

- [ ] **Analytics Setup**
  - Configure Google Analytics or Plausible
  - Set up conversion tracking
  - Implement event tracking

- [ ] **Testing in Production**
  - Verify all forms work correctly
  - Test Stripe payments in production
  - Check email notifications

- [ ] **SEO**
  - Verify meta tags
  - Submit sitemap
  - Configure robots.txt

## 9. Monitoring & Maintenance

- [ ] **Set Up Monitoring**
  - Configure uptime monitoring
  - Set up error tracking
  - Configure performance monitoring

- [ ] **Backup Strategy**
  - Set up database backups
  - Configure backup verification

## 10. Launch Preparation

- [ ] **Marketing Materials**
  - Prepare social media announcements
  - Draft email newsletter
  - Prepare blog post

- [ ] **Documentation**
  - Finalize user documentation
  - Create internal documentation for maintenance

- [ ] **Support System**
  - Set up customer support email
  - Configure help desk system if needed
  - Prepare support response templates 