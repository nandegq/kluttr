import { Button } from "@/components/ui/button";
import { ArrowRight } from "lucide-react";

const CTA = () => {
  return (
    <section className="py-32 bg-white relative overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-transparent" />
      
      <div className="container mx-auto px-4 relative z-10">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-5xl md:text-6xl lg:text-7xl font-bold mb-8 tracking-tight">
            Ready to declutter?
          </h2>
          <p className="text-xl text-muted-foreground mb-12 max-w-2xl mx-auto leading-relaxed">
            Join thousands who've simplified their lives with Kluttr.
          </p>
          
          <Button size="lg" variant="hero" className="text-base h-12 px-8 rounded-lg">
            Get Started
            <ArrowRight className="w-4 h-4" />
          </Button>
          
          <div className="mt-8 flex items-center justify-center gap-6 text-sm text-muted-foreground">
            <span>✓ No credit card required</span>
            <span>✓ Cancel anytime</span>
            <span>✓ 24/7 support</span>
          </div>
        </div>
      </div>
    </section>
  );
};

export default CTA;
