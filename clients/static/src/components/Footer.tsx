const Footer = () => {
  return (
    <footer className="bg-white border-t border-border">
      <div className="container mx-auto px-4 py-16">
        <div className="grid md:grid-cols-5 gap-12 mb-12">
          <div className="md:col-span-2">
            <span className="text-2xl font-bold tracking-tight mb-4 block">kluttr.</span>
            <p className="text-muted-foreground text-sm max-w-xs leading-relaxed">
              On-demand waste pickup for a cleaner, simpler life.
            </p>
          </div>
          
          <div>
            <h3 className="font-semibold mb-4 text-sm">Product</h3>
            <ul className="space-y-3 text-sm text-muted-foreground">
              <li><a href="#" className="hover:text-foreground transition-colors">How it works</a></li>
              <li><a href="#" className="hover:text-foreground transition-colors">Pricing</a></li>
              <li><a href="#" className="hover:text-foreground transition-colors">Service areas</a></li>
            </ul>
          </div>
          
          <div>
            <h3 className="font-semibold mb-4 text-sm">Company</h3>
            <ul className="space-y-3 text-sm text-muted-foreground">
              <li><a href="#" className="hover:text-foreground transition-colors">About</a></li>
              <li><a href="#" className="hover:text-foreground transition-colors">Careers</a></li>
              <li><a href="#" className="hover:text-foreground transition-colors">Contact</a></li>
            </ul>
          </div>
          
          <div>
            <h3 className="font-semibold mb-4 text-sm">Legal</h3>
            <ul className="space-y-3 text-sm text-muted-foreground">
              <li><a href="#" className="hover:text-foreground transition-colors">Privacy</a></li>
              <li><a href="#" className="hover:text-foreground transition-colors">Terms</a></li>
              <li><a href="#" className="hover:text-foreground transition-colors">Cookies</a></li>
            </ul>
          </div>
        </div>
        
        <div className="pt-8 border-t border-border text-sm text-muted-foreground">
          <p>&copy; 2024 Kluttr. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
