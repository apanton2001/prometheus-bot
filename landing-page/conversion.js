/**
 * Landing Page to Next.js SaaS Starter Conversion Guide
 * 
 * This script helps identify key components that need to be migrated from
 * the static landing page to the Next.js SaaS starter template.
 */

// Component mapping between our custom CSS components and shadcn/ui
const componentMapping = {
  // Navigation
  'header nav': {
    nextjsComponent: 'app/components/landing/navbar.tsx',
    shadcnComponents: ['Sheet', 'Button', 'NavigationMenu'],
    notes: 'Replace static navigation with NavigationMenu component, mobile menu with Sheet'
  },
  
  // Hero Section
  '.hero': {
    nextjsComponent: 'app/page.tsx',
    shadcnComponents: ['Container', 'Button', 'Badge'],
    notes: 'Use Container for layout, Button for CTAs, and adapt hero stats to custom components'
  },
  
  // Features Section
  '.features': {
    nextjsComponent: 'app/components/landing/features.tsx',
    shadcnComponents: ['Card', 'Container'],
    notes: 'Convert feature cards to shadcn Card components with custom icons'
  },
  
  // How It Works Section
  '.how-it-works': {
    nextjsComponent: 'app/components/landing/how-it-works.tsx',
    shadcnComponents: ['Container', 'Card'],
    notes: 'Create a custom steps component using Container and styling'
  },
  
  // Pricing Section
  '.pricing': {
    nextjsComponent: 'app/pricing/page.tsx',
    shadcnComponents: ['Card', 'Button', 'Badge'],
    notes: 'Use built-in pricing page but customize with our tiers. Connect to Stripe products.'
  },
  
  // Testimonials Section
  '.testimonials': {
    nextjsComponent: 'app/components/landing/testimonials.tsx',
    shadcnComponents: ['Card', 'Avatar', 'Carousel'],
    notes: 'Create custom testimonial cards, optionally add a carousel component'
  },
  
  // FAQ Section
  '.faq': {
    nextjsComponent: 'app/components/landing/faq.tsx',
    shadcnComponents: ['Accordion', 'Container'],
    notes: 'Convert FAQ items to Accordion component items'
  },
  
  // Signup Section
  '.signup': {
    nextjsComponent: 'app/register/page.tsx',
    shadcnComponents: ['Form', 'Input', 'Select', 'Button'],
    notes: 'Use built-in registration form but customize fields and styling'
  },
  
  // Footer Section
  'footer': {
    nextjsComponent: 'app/components/landing/footer.tsx',
    shadcnComponents: ['Container', 'Separator'],
    notes: 'Adapt footer columns to match our structure and links'
  }
};

// Color scheme mapping
const colorMapping = {
  // Original colors
  '--color-primary': '#40E0D0', // Pantone Turquoise
  '--color-primary-dark': '#35B8AB',
  '--color-primary-light': '#7CEAE0',
  '--color-secondary': '#F5F5DC', // Light Tan
  '--color-secondary-dark': '#E8E8C8',
  
  // Next.js shadcn integration (in globals.css and tailwind.config.js)
  'implementation': `
  // In app/globals.css:
  :root {
    --background: 0 0% 100%;
    --foreground: 222.2 84% 4.9%;
    
    --card: 0 0% 100%;
    --card-foreground: 222.2 84% 4.9%;
    
    --popover: 0 0% 100%;
    --popover-foreground: 222.2 84% 4.9%;
    
    --primary: 174 75% 53%; /* Pantone Turquoise */
    --primary-foreground: 210 40% 98%;
    
    --secondary: 60 67% 94%; /* Light Tan */
    --secondary-foreground: 222.2 47.4% 11.2%;
    
    --muted: 210 40% 96.1%;
    --muted-foreground: 215.4 16.3% 46.9%;
    
    --accent: 210 40% 96.1%;
    --accent-foreground: 222.2 47.4% 11.2%;
    
    --destructive: 0 84.2% 60.2%;
    --destructive-foreground: 210 40% 98%;
    
    --border: 214.3 31.8% 91.4%;
    --input: 214.3 31.8% 91.4%;
    --ring: 222.2 84% 4.9%;
    
    --radius: 0.5rem;
  }
  `
};

// Form conversion for Next.js
const formConversion = {
  'original': 'formhandler.php uses direct PHP processing and CSV storage',
  'nextjs': `
  // In app/api/register/route.ts:
  import { db } from "@/lib/db";
  import { NextResponse } from "next/server";
  import { z } from "zod";
  
  // Create zod schema for validation
  const registerSchema = z.object({
    name: z.string().min(1, "Name is required"),
    email: z.string().email("Valid email is required"),
    tradingExperience: z.enum(["beginner", "intermediate", "advanced"]),
    plan: z.enum(["free", "professional", "enterprise", "performance"]),
  });
  
  export async function POST(req: Request) {
    try {
      const body = await req.json();
      const { name, email, tradingExperience, plan } = registerSchema.parse(body);
      
      // Store user data (simplified, actual implementation would include auth)
      const user = await db.user.create({
        data: {
          name,
          email,
          tradingExperience,
          plan,
        },
      });
      
      // Send notification email
      await sendNotificationEmail(email, name, plan);
      
      return NextResponse.json({ success: true, user });
    } catch (error) {
      if (error instanceof z.ZodError) {
        return NextResponse.json({ success: false, error: error.errors }, { status: 400 });
      }
      
      return NextResponse.json(
        { success: false, error: "Internal Server Error" },
        { status: 500 }
      );
    }
  }
  `
};

// Deployment steps
const deploymentSteps = [
  '1. Clone Next.js SaaS starter template from GitHub',
  '2. Set up development environment with pnpm',
  '3. Configure PostgreSQL database locally',
  '4. Create key components mapped above',
  '5. Implement color scheme in globals.css',
  '6. Create Stripe products/prices for our pricing tiers',
  '7. Adapt signup forms to Next.js API routes',
  '8. Test all user flows locally',
  '9. Deploy to Vercel with proper environment variables',
  '10. Set up GitHub repository for CI/CD'
];

// Required environment variables
const environmentVariables = [
  'DATABASE_URL=postgresql://username:password@localhost:5432/mydb',
  'STRIPE_SECRET_KEY=sk_test_...',
  'STRIPE_WEBHOOK_SECRET=whsec_...',
  'AUTH_SECRET=random_string_generated_with_openssl',
  'BASE_URL=http://localhost:3000'
];

// Export mapping for use in conversion process
module.exports = {
  componentMapping,
  colorMapping,
  formConversion,
  deploymentSteps,
  environmentVariables
}; 