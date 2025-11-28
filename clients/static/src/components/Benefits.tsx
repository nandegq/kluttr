import { Zap, Shield, Leaf, DollarSign } from "lucide-react";

const benefits = [
  {
    icon: Zap,
    title: "Lightning fast",
    description: "Average pickup time of just 5 minutes. No more waiting around.",
  },
  {
    icon: Shield,
    title: "Fully insured",
    description: "Background-checked team members and comprehensive insurance.",
  },
  {
    icon: Leaf,
    title: "Eco-conscious",
    description: "95% of collected waste diverted from landfills through recycling.",
  },
  {
    icon: DollarSign,
    title: "Transparent pricing",
    description: "Know exactly what you'll pay. No hidden fees or surprises.",
  },
];

const Benefits = () => {
  return (
    <section className="py-32 bg-gray-50">
      <div className="container mx-auto px-4">
        <div className="text-center mb-20">
          <div className="inline-block px-4 py-1.5 rounded-full bg-primary/10 text-primary text-sm font-medium mb-4">
            Why Kluttr
          </div>
          <h2 className="text-5xl md:text-6xl font-bold mb-6">Built for simplicity</h2>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Everything you need, nothing you don't
          </p>
        </div>
        
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8 max-w-7xl mx-auto">
          {benefits.map((benefit, index) => (
            <div 
              key={index} 
              className="group p-8 rounded-2xl bg-white border border-border hover:border-primary/30 transition-all duration-300 hover:shadow-lg"
            >
              <div className="w-12 h-12 mb-6 rounded-xl bg-primary/10 flex items-center justify-center group-hover:bg-primary/20 transition-colors">
                <benefit.icon className="w-6 h-6 text-primary" strokeWidth={1.5} />
              </div>
              <h3 className="text-xl font-bold mb-3">{benefit.title}</h3>
              <p className="text-muted-foreground leading-relaxed text-sm">{benefit.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Benefits;
