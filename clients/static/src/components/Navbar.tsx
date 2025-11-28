import { Button } from "@/components/ui/button";

const Navbar = () => {
  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-xl border-b border-border/50">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center">
            <span className="text-2xl font-bold tracking-tight">kluttr.</span>
          </div>
          
          <div className="hidden md:flex items-center gap-8">
            <a href="#how" className="text-sm text-foreground/70 hover:text-foreground transition-colors">
              How it works
            </a>
            <a href="#why" className="text-sm text-foreground/70 hover:text-foreground transition-colors">
              Why Kluttr
            </a>
            <a href="#pricing" className="text-sm text-foreground/70 hover:text-foreground transition-colors">
              Pricing
            </a>
          </div>
          
          <div className="flex items-center gap-3">
            <Button variant="ghost" size="sm" className="text-sm">
              Sign in
            </Button>
            <Button size="sm" className="text-sm rounded-lg">
              Get Started
            </Button>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
